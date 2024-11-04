from datetime import timezone
from uuid import UUID

from fastapi import APIRouter, Request, HTTPException, Form, Depends
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse

from app.database import db_dependency, UsersOrm
from app.password import hash_password, verify_password
from app.utils import session_dependency, session_id_cookie, create_session, templates

user_router = APIRouter(prefix="/user",
                        tags=["user"])

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
async def register_page(request: Request, session: session_dependency):
    if session:
        return RedirectResponse(url="/user/profile")
    return templates.TemplateResponse("signup.html", {"request": request})

@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, form: RegisterFormIn, session: session_dependency):
    if session:
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
async def login_page(request: Request, session: session_dependency):
    if session:
        return RedirectResponse(url="/user/profile")
    return templates.TemplateResponse("signin.html", {"request": request})

@user_router.post("/signin", status_code=status.HTTP_200_OK)
async def login_user(db: db_dependency, form: LoginFormIn, session: session_dependency):
    if session:
        return {"message": "Already logged in"}
    user = UsersOrm.get_user(db, form.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    if not verify_password(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    if user.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")

    session_id, expiration = create_session(form.username, db)
    response = JSONResponse(content={session_id_cookie: session_id.hex})
    utc_expiration = expiration.astimezone(timezone.utc)
    response.set_cookie(key=session_id_cookie, value=session_id.hex, expires=utc_expiration)
    return response

@user_router.delete("/logout", status_code=status.HTTP_200_OK)
async def logout_user(request: Request, db: db_dependency, session: session_dependency):
    if not session:
        return {"message": "Not logged in"}
    db.delete(session)
    db.commit()
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(key=session_id_cookie)
    return response

@user_router.delete("/logout/all", status_code=status.HTTP_200_OK)
async def logout_all(request: Request, db: db_dependency, session: session_dependency, except_current: bool = False):
    if not session:
        return {"message": "Not logged in"}
    for other_sessions in session.user.sessions:
        if except_current and session.token == other_sessions.token:
            continue
        db.delete(session)
    db.commit()
    response = JSONResponse(content={"message": "Logged out from all devices"})
    response.delete_cookie(key=session_id_cookie)
    return response

@user_router.get("/profile", status_code=status.HTTP_200_OK)
async def profile_page(request: Request, session: session_dependency):
    if not session:
        return RedirectResponse(url="/user/signin")
    return templates.TemplateResponse("profile.html", {"request": request, "user": session.user})

