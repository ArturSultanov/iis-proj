from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_201_CREATED, \
    HTTP_307_TEMPORARY_REDIRECT
from starlette.templating import Jinja2Templates
from typing import Annotated as typingAnnotated

from database import get_db, db_dependency
from db_models import UsersOrm, Role, AnimalsOrm
from user import user_from_cookie

staff_router = APIRouter(prefix="/staff", tags=["staff"])

templates = Jinja2Templates(directory="templates")

def get_staff(logged_user: UsersOrm = Depends(user_from_cookie)) -> UsersOrm:
    if not logged_user:
        raise HTTPException(status_code=HTTP_307_TEMPORARY_REDIRECT, detail="You need to login", headers={"Location": "/user/signin"})
    if logged_user.role != Role.staff and logged_user.role != Role.admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    return logged_user

staff_dependency = typingAnnotated[UsersOrm, Depends(get_staff)]


@staff_router.get("/animals")
async def staff_animals_page(request: Request, db: db_dependency, staff: UsersOrm = Depends(get_staff)):
    animals_list = db.query(AnimalsOrm).all()
    return templates.TemplateResponse("animals.html",
                                      {"request": request, "user": staff, "animals": animals_list},
                                      status_code=HTTP_200_OK)

@staff_router.post("/animals/new", status_code=HTTP_201_CREATED)
async def add_animal(db: db_dependency,
                     staff: staff_dependency,
                     name: str = Form(...),
                     species: str = Form(...),
                     age: int = Form(...),
                     description: str = Form(...),
                     photo: UploadFile | None = None):
    new_animal = AnimalsOrm(name=name, species=species, age=age, description=description, photo=photo.file.read() if photo else None)
    db.add(new_animal)
    db.commit()
