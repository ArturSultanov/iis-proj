from datetime import datetime, timedelta, timezone
from uuid import uuid5, uuid4, UUID

from fastapi import APIRouter, Request, Depends, HTTPException, Form
from pydantic import BaseModel, UUID5
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from database import db_dependency
from db_models import UsersOrm, Role, SessionsOrm
from password import hash_password

user_router = APIRouter(prefix="/user", tags=["user"])

templates = Jinja2Templates(directory="templates")

session_id_cookie = "session_id"

session_duration = timedelta(minutes=2)

class RegisterFormIn(BaseModel):
    name: str = Form(...)
    username: str = Form(...)
    password: str = Form(...)
    confirm_password: str = Form(...)

    def validate_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")

class LoginFormIn(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_session(username: str, db: db_dependency) -> (UUID, datetime):
    session_id = uuid4()
    user = UsersOrm.get_user(db, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    expiration_date = datetime.now() + session_duration
    return user.add_session(db, session_id, expiration_date), expiration_date

def user_from_cookie(request: Request, db: db_dependency) -> UsersOrm | None:
    if session_id_cookie not in request.cookies:
        return None
    if not request.cookies.get(session_id_cookie):
        return None

    session_id = UUID(request.cookies.get(session_id_cookie))
    session : SessionsOrm | None = db.query(SessionsOrm).filter(SessionsOrm.token == session_id).first()
    if not session:
        return None
    if session.expiration < datetime.now():
        db.delete(session)
        db.commit()
        return None
    user = session.user
    if not user:
        return None
    if user.disabled:
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,  # 303 See Other is suitable for redirects after a forbidden access
            detail="User is disabled",
            headers={"Location": "/user/signin"}
        )
    return user

@user_router.get("/signup", status_code=status.HTTP_200_OK)
async def register_page(request: Request, user: UsersOrm = Depends(user_from_cookie)):
    if user:
        return RedirectResponse(url="/user/profile")
    return templates.TemplateResponse("signup.html", {"request": request})

@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, form: RegisterFormIn, user : UsersOrm = Depends(user_from_cookie)):
    if user:
        return {"message": "Already logged in"}
    try:
        form.validate_password()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    if UsersOrm.get_user(db, form.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with such username already exists")

    new_user = UsersOrm(username=form.username,
                        name=form.name,
                        password=hash_password(form.password))
    db.add(new_user)
    db.commit()


@user_router.get("/signin", status_code=status.HTTP_200_OK)
async def login_page(request: Request, user : UsersOrm = Depends(user_from_cookie)):
    if user:
        return RedirectResponse(url="/user/profile")
    return templates.TemplateResponse("signin.html", {"request": request})

@user_router.post("/signin", status_code=status.HTTP_200_OK)
async def login_user(db: db_dependency, form: LoginFormIn, user_before: UsersOrm = Depends(user_from_cookie)):
    if user_before:
        return {"message": "Already logged in"}
    user = UsersOrm.get_user(db, form.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    if user.password != hash_password(form.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    if user.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")

    session_id, expiration = create_session(form.username, db)
    response = JSONResponse(content={session_id_cookie: session_id.hex})
    utc_expiration = expiration.astimezone(timezone.utc)
    response.set_cookie(key=session_id_cookie, value=session_id.hex, expires=utc_expiration)
    return response

@user_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(key=session_id_cookie)
    return response

@user_router.get("/profile", status_code=status.HTTP_200_OK)
async def profile_page(request: Request, logged_user: UsersOrm = Depends(user_from_cookie)):
    if not logged_user:
        return RedirectResponse(url="/user/signin")
    return templates.TemplateResponse("profile.html", {"request": request, "user": logged_user})

