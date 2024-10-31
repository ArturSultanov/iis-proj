from datetime import timezone
from uuid import UUID

from fastapi import APIRouter, Request, HTTPException, Form
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse

from app.database import db_dependency, UsersOrm, SessionsOrm
from app.password import hash_password
from app.utils import user_or_none_dependency, session_id_cookie, create_session, templates

user_router = APIRouter(prefix="/user", tags=["user"])

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

@user_router.get("/signup", status_code=status.HTTP_200_OK)
async def register_page(request: Request, user: user_or_none_dependency):
    if user:
        return RedirectResponse(url="/user/profile")
    return templates.TemplateResponse("signup.html", {"request": request})

@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, form: RegisterFormIn, user: user_or_none_dependency):
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
async def login_page(request: Request, user: user_or_none_dependency):
    if user:
        return RedirectResponse(url="/user/profile")
    return templates.TemplateResponse("signin.html", {"request": request})

@user_router.post("/signin", status_code=status.HTTP_200_OK)
async def login_user(db: db_dependency, form: LoginFormIn, user_before: user_or_none_dependency):
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
async def logout_user(request: Request, db: db_dependency, logged_user: user_or_none_dependency):
    if not logged_user:
        return {"message": "Not logged in"}
    session_id = UUID(request.cookies.get(session_id_cookie))
    session = db.query(SessionsOrm).filter(SessionsOrm.token == session_id).first()
    if session:
        db.delete(session)
        db.commit()
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(key=session_id_cookie)
    return response

@user_router.post("/logout/all", status_code=status.HTTP_200_OK)
async def logout_all(request: Request, db: db_dependency, logged_user: user_or_none_dependency, except_current: bool = False):
    if not logged_user:
        return {"message": "Not logged in"}
    for session in logged_user.sessions:
        if except_current and session.token == UUID(request.cookies.get(session_id_cookie)):
            continue
        db.delete(session)
    db.commit()
    response = JSONResponse(content={"message": "Logged out from all devices"})
    response.delete_cookie(key=session_id_cookie)
    return response

@user_router.get("/profile", status_code=status.HTTP_200_OK)
async def profile_page(request: Request, logged_user: user_or_none_dependency):
    if not logged_user:
        return RedirectResponse(url="/user/signin")
    return templates.TemplateResponse("profile.html", {"request": request, "user": logged_user})

