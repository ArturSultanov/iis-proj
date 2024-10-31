from fastapi import APIRouter, Request, Form, UploadFile
from starlette.status import HTTP_200_OK, HTTP_201_CREATED
from starlette.templating import Jinja2Templates

from app.database import db_dependency, AnimalsOrm
from app.utils import staff_dependency, templates

staff_router = APIRouter(prefix="/staff", tags=["staff"])

@staff_router.get("/animals")
async def staff_animals_page(request: Request, db: db_dependency, staff: staff_dependency):
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
