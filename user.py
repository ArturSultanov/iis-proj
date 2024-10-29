from fastapi import APIRouter, Request, Depends, HTTPException, Form
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from database import db_dependency
from db_models import UsersOrm, Role
from password import hash_password

user_router = APIRouter(prefix="/user", tags=["user"])

templates = Jinja2Templates(directory="templates")

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

def user_from_cookie(request: Request, db: db_dependency) -> UsersOrm | None:
    token = request.cookies.get("access_token") # todo token is username now!!
    user = UsersOrm.get_user(db, token)
    if not user:
        return None
    if user.disabled:
        # Clear the cookie by setting an expired Set-Cookie header
        headers = {
            "Set-Cookie": "access_token=; Path=/; HttpOnly; Expires=Thu, 01 Jan 1970 00:00:00 GMT",
            "Location": "/"
        }
        # Raise an exception to redirect to the login page
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,  # 303 See Other is suitable for redirects after a forbidden access
            detail="User is disabled",
            headers=headers
        )
    return user

@user_router.get("/signup", status_code=status.HTTP_200_OK)
async def register_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register_user(db: db_dependency, form: RegisterFormIn):
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
async def login_page(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})

@user_router.post("/signin", status_code=status.HTTP_200_OK)
async def login_user(db: db_dependency, form: LoginFormIn):
    user = UsersOrm.get_user(db, form.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    if user.password != hash_password(form.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    if user.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")

    token = create_token(form.username)
    response = JSONResponse(content={"access_token": token, "token_type": "bearer"})
    response.set_cookie(key="access_token", value=token)
    return response

@user_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(key="access_token")
    return response

@user_router.get("/profile", status_code=status.HTTP_200_OK)
async def profile_page(request: Request, logged_user: UsersOrm = Depends(user_from_cookie)):
    if not logged_user:
        return RedirectResponse(url="/user/signin")
    return templates.TemplateResponse("profile.html", {"request": request, "user": logged_user})

