from datetime import timezone, datetime
from wsgiref.util import application_uri

from fastapi import APIRouter, Request, HTTPException, Form, Depends
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse

from app.database import db_dependency, UsersOrm
from app.database.models import VolunteerApplicationsOrm
from app.password import hash_password, verify_password
from app.utils import session_dependency, session_id_cookie, create_session, templates

user_router = APIRouter(prefix="/user",
                        tags=["user"])

# Form to register a new user
class RegisterFormIn(BaseModel):
    name: str = Form(...)
    username: str = Form(...)
    password: str = Form(...)
    confirm_password: str = Form(...)

    def validate_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")

# Form to login a user
class LoginFormIn(BaseModel):
    username: str
    password: str


@user_router.get("/signup", status_code=status.HTTP_200_OK)
async def register_page(request: Request, session: session_dependency):
    if session:
        return RedirectResponse(url="/user/profile")
    return templates.TemplateResponse("user/signup.html", {"request": request})


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
    return templates.TemplateResponse("user/signin.html", {"request": request})


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
    # Set the session_id cookie
    response.set_cookie(key=session_id_cookie,
                        value=session_id.hex,
                        expires=utc_expiration,
                        httponly=True,
                        secure=True,
                        samesite="strict")
    return response


@user_router.delete("/logout", status_code=status.HTTP_200_OK)
async def logout_user(db: db_dependency, session: session_dependency):
    if not session:
        return {"message": "Not logged in"}
    db.delete(session)
    db.commit()
    response = JSONResponse(content={"message": "Logged out"})
    # Delete the session_id cookie
    response.delete_cookie(key=session_id_cookie)
    return response


@user_router.delete("/logout/all", status_code=status.HTTP_200_OK)
async def logout_all(db: db_dependency, session: session_dependency, keep_current: bool = False):
    if keep_current:
        print("Keeping current session")
    if not session:
        return {"message": "Not logged in"}
    # Delete all user's sessions except the current session if keep_current is True
    for other_session in session.user.sessions:
        if keep_current and session.id == other_session.id:
            continue
        db.delete(other_session)
    db.commit()
    response = JSONResponse(content={"message": f"Logged out from all devices {"except current" if keep_current else ""}"})
    if not keep_current:
        response.delete_cookie(key=session_id_cookie)
    return response


@user_router.get("/profile", status_code=status.HTTP_200_OK)
async def profile_page(request: Request, session: session_dependency):
    if not session:
        return RedirectResponse(url="/user/signin")
    return templates.TemplateResponse("user/profile.html",
                                      {
                                          "request": request,
                                          "user": session.user
                                      })


@user_router.get("/volunteer_application", status_code=status.HTTP_200_OK)
async def volunteer_application_page(request: Request, session: session_dependency):
    if not session:
        return RedirectResponse(url="/user/signin")
    if not session.user.is_registered:
        return RedirectResponse(url="/user/profile")
    application = session.user.volunteer_application
    return templates.TemplateResponse("user/volunteer_application.html",
                                      {
                                          "request": request,
                                          "user": session.user,
                                          "application": application
                                      })

@user_router.post("/volunteer_application", status_code=status.HTTP_201_CREATED)
async def volunteer_application(db: db_dependency, session: session_dependency, description: str = Form(...)):
    if not session:
        return RedirectResponse(url="/user/signin")
    if not session.user.is_registered:
        return RedirectResponse(url="/user/profile")
    application = session.user.volunteer_application
    if application:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Application already submitted")
    application = VolunteerApplicationsOrm(user=session.user, date=datetime.now(), message=description)
    db.add(application)
    db.commit()


@user_router.get("/change_password", status_code=status.HTTP_200_OK)
async def change_password_page(request: Request, session: session_dependency):
    if not session:
        return RedirectResponse(url="/user/signin")
    return templates.TemplateResponse("user/change_password.html",
                                      {
                                          "request": request,
                                          "user": session.user
                                      })


@user_router.post("/change_password", status_code=status.HTTP_200_OK)
async def change_password(db: db_dependency, session: session_dependency, old_password: str = Form(...), new_password: str = Form(...), confirm_password: str = Form(...)):
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in")
    if not verify_password(old_password, session.user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    if new_password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    session.user.password = hash_password(new_password)
    db.commit()
    return {"message": "Password changed"}
