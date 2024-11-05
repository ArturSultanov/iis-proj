from typing import Annotated, Any, Self

from fastapi import APIRouter, Request, Form, UploadFile, Depends, HTTPException
from fastapi.params import Query
from pydantic import BaseModel
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from app.config import settings
from app.database import db_dependency, AnimalsOrm
from app.utils import staff_dependency, templates, get_staff

staff_router = APIRouter(prefix="/staff",
                         tags=["staff"],
                         dependencies=[Depends(get_staff)])

class AnimalForm(BaseModel):
    name: str
    species: str
    age: int
    description: str
    photo: UploadFile | None = None

    @property
    def get_dict(self):
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "description": self.description,
            "photo": self.photo.file.read() if self.photo else None
        }

def get_animal(animal_id: int, db: db_dependency) -> AnimalsOrm:
    animal = db.query(AnimalsOrm).filter(AnimalsOrm.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Animal not found")
    return animal

animal_dependency = Annotated[AnimalsOrm, Depends(get_animal)]

# @staff_router.get("/animals", status_code=HTTP_200_OK)
# async def staff_animals_page(request: Request, db: db_dependency, staff: staff_dependency, page: int = 1):
#     animals_list = db.query(AnimalsOrm).all()
#     display_animals = animals_list[(page-1)*settings.PAGE_SIZE:page*settings.PAGE_SIZE]
#     pages = len(animals_list) // settings.PAGE_SIZE + 1
#     return templates.TemplateResponse("animals.html",
#                                       {
#                                           "request": request,
#                                           "user": staff,
#                                           "animals": display_animals,
#                                           "pages": pages,
#                                           "page": page
#                                       })

@staff_router.post("/animals/new", status_code=HTTP_201_CREATED)
async def add_animal(db: db_dependency, animal: Annotated[AnimalForm, Form()]):
    new_animal = AnimalsOrm(**animal.get_dict)
    db.add(new_animal)
    db.commit()
    return {"message": "Animal added successfully"}

@staff_router.delete("/animals/{animal_id}", status_code=HTTP_200_OK)
async def delete_animal(db: db_dependency, animal: animal_dependency):
    db.delete(animal)
    db.commit()
    return {"message": "Animal deleted successfully"}

@staff_router.patch("/animals/{animal_id}/edit", status_code=HTTP_200_OK)
async def edit_animal_page(request: Request, animal: animal_dependency):
    return templates.TemplateResponse("animal/animal_edit.html", {"request": request, "animal": animal})

@staff_router.patch("/animals/{animal_id}/name", status_code=HTTP_200_OK)
async def edit_animal_name(db: db_dependency, animal: animal_dependency, new_name: str = Query(...)):
    animal.name = new_name
    db.commit()
    return {"message": "Name updated successfully", "name": new_name}

@staff_router.patch("/animals/{animal_id}/species", status_code=HTTP_200_OK)
async def edit_animal_species(db: db_dependency, animal: animal_dependency, new_species: str = Query(...)):
    animal.species = new_species
    db.commit()
    return {"message": "Species updated successfully", "species": new_species}

@staff_router.patch("/animals/{animal_id}/age", status_code=HTTP_200_OK)
async def edit_animal_age(db: db_dependency, animal: animal_dependency, new_age: int = Query(...)):
    animal.age = new_age
    db.commit()
    return {"message": "Age updated successfully", "age": new_age}

@staff_router.patch("/animals/{animal_id}/description", status_code=HTTP_200_OK)
async def edit_animal_description(db: db_dependency, animal: animal_dependency, new_description: str = Query(...)):
    animal.description = new_description
    db.commit()
    return {"message": "Description updated successfully", "description": new_description}

@staff_router.patch("/animals/{animal_id}/photo", status_code=HTTP_200_OK)
async def edit_animal_photo(db: db_dependency, animal: animal_dependency, photo: UploadFile = Form(None)):
    animal.photo = photo.file.read() if photo else None
    db.commit()
    return {"message": "Photo updated successfully"}

@staff_router.delete("/animals/{animal_id}/photo", status_code=HTTP_200_OK)
async def delete_animal_photo(db: db_dependency, animal: animal_dependency):
    animal.photo = None
    db.commit()
    return {"message": "Photo deleted successfully"}

