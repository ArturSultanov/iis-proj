from typing import Annotated

from fastapi import APIRouter, Request, Form, UploadFile, Depends, HTTPException
from fastapi.params import Query
from pydantic import BaseModel
from starlette.responses import RedirectResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_202_ACCEPTED

from app.database import db_dependency, AnimalsOrm
from app.database.models import VolunteerApplicationsOrm, ApplicationStatus, Role
from app.utils import staff_dependency, templates, get_staff, application_status_to_int

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

@staff_router.get("/dashboard", status_code=HTTP_200_OK)
async def staff_dashboard(request: Request, staff: staff_dependency):
    return templates.TemplateResponse("staff/dashboard.html", {"request": request, "staff": staff})

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

@staff_router.get("/animals/{animal_id}/edit", status_code=HTTP_200_OK)
async def edit_animal_page(request: Request, animal: animal_dependency):
    return templates.TemplateResponse("animal/edit_page.html", {"request": request, "animal": animal})

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

@staff_router.patch("/animals/{animal_id}/hide", status_code=HTTP_200_OK)
async def hide_animal(db: db_dependency, animal: animal_dependency, hidden: bool):
    animal.hidden = hidden
    db.commit()
    return {"message": "Animal hidden successfully"}

@staff_router.get("/volunteer_applications")
async def volunteer_applications(request: Request, db: db_dependency, limit: int = Query(10), page: int = Query(1)):
    applications_list = db.query(VolunteerApplicationsOrm).all()
    # sort by status, then by date, then by id
    applications_list.sort(key=lambda x: (application_status_to_int(x.status.value), x.date, x.id), reverse=True)
    display_applications = applications_list[(page-1)*limit:page*limit]
    pages = len(applications_list) // limit + 1
    if page > pages or page < 1:
        return RedirectResponse(url="/volunteer_applications")
    return templates.TemplateResponse("staff/volunteer_applications.html",
                                      {
                                          "request": request,
                                          "applications": display_applications,
                                          "pages": pages,
                                          "page": page
                                      })

@staff_router.patch("/volunteer_applications/{application_id}", status_code=HTTP_200_OK)
async def update_application_status(db: db_dependency, application_id: int, status: ApplicationStatus = Query(...)):
    application = db.query(VolunteerApplicationsOrm).filter(VolunteerApplicationsOrm.id == application_id).first()

    if not application:
        # application not found
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Application not found")
    if application.status != ApplicationStatus.pending:
        # application already processed
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Application already processed")

    # update user role if application is accepted
    application.status = status

    if status == ApplicationStatus.accepted:
        if application.user.is_registered and not application.user.is_volunteer:
            # user is already registered and not a volunteer already
            application.user.role = Role.volunteer
        elif not application.user.is_volunteer:
            # user is
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User already has a role")

    db.commit()
    return {"message": "Application status updated successfully", "status": status.value}


