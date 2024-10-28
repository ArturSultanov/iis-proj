import bcrypt
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from typing_extensions import Self

from database import db_dependency
from db_models import UsersOrm

tokens_session = {}

user = APIRouter(prefix="/user", tags=["user"])

templates = Jinja2Templates(directory="templates")

salt = b'$2b$12$wE.fRv4cUoMjU45RIn2iD.'

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

def create_token(username: str):
    return username

def get_cookie(request: Request):
    return request.cookies.get("access_token")

@user.get("/signup", status_code=status.HTTP_200_OK)
async def register_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@user.post("/signup", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, form: RegisterFormIn):
    try:
        form.validate_password()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    if UsersOrm.get_user(db, form.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with such username already exists")

    new_user = UsersOrm(username=form.username, password=bcrypt.hashpw(form.password.encode('utf-8'), salt).decode('utf-8'))
    db.add(new_user)
    db.commit()


@user.get("/signin", status_code=status.HTTP_200_OK)
async def login_page(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})

@user.post("/signin", status_code=status.HTTP_200_OK)
async def login_user(db: db_dependency, form: LoginFormIn):
    user = UsersOrm.get_user(db, form.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    if user.password != bcrypt.hashpw(form.password.encode('utf-8'), salt).decode('utf-8'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    token = create_token(form.username)
    response = JSONResponse(content={"access_token": token, "token_type": "bearer"})
    response.set_cookie(key="access_token", value=token)
    tokens_session[token] = form.username
    return response

@user.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(key="access_token")
    return response

@user.get("/profile", status_code=status.HTTP_200_OK)
async def profile_page(request: Request, token: str = Depends(get_cookie)):
    if token not in tokens_session:
        return RedirectResponse(url="/user/signin")
    return templates.TemplateResponse("profile.html", {"request": request, "username": tokens_session[token]})

