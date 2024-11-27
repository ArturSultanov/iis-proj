import io
from datetime import datetime, timezone
from typing import Annotated, Optional

from PIL import Image
from fastapi import APIRouter, Request, Form, UploadFile, Depends, HTTPException
from fastapi.params import Query
from pydantic import BaseModel
from starlette.responses import RedirectResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.database import db_dependency, AnimalsOrm, AdoptionStatus, AnimalStatus
from app.database.models import VolunteerApplicationsOrm, ApplicationStatus, Role, VetRequestStatus, VetRequestOrm, \
    WalkStatus, WalksOrm, AdoptionRequestsOrm
from app.utils import staff_dependency, templates, get_staff, application_status_to_int, animal_dependency, \
    session_dependency, walk_dependency

staff_router = APIRouter(prefix="/staff",
                         tags=["staff"],
                         dependencies=[Depends(get_staff)])


def compress_photo(photo: bytes):
    """
    Compresses a photo to a smaller size.
    """
    image = Image.open(io.BytesIO(photo))
    image.thumbnail((500, 500))
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG", quality=70)
    return image_bytes.getvalue()


# Form to add a new animal
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
            "photo": compress_photo(self.photo.file.read()) if self.photo else None
        }


@staff_router.get("/dashboard", status_code=HTTP_200_OK)
async def staff_dashboard(request: Request, staff: staff_dependency, session: session_dependency):
    return templates.TemplateResponse("staff/dashboard.html",
                                      {
                                          "request": request,
                                          "staff": staff,
                                          "user": session.user
                                      })


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
async def edit_animal_page(request: Request, animal: animal_dependency, session: session_dependency):
    return templates.TemplateResponse("animal/edit_page.html",
                                      {
                                          "request": request,
                                          "animal": animal,
                                          "user": session.user
                                      })


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
    animal.photo = compress_photo(photo.file.read()) if photo else None
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
async def volunteer_applications(request: Request, session: session_dependency, db: db_dependency,
                                 limit: int = Query(10), page: int = Query(1)):
    applications_list = db.query(VolunteerApplicationsOrm).all()
    # sort by status, then by date, then by id
    applications_list.sort(key=lambda x: (application_status_to_int(x.status), x.date, x.id))
    display_applications = applications_list[(page - 1) * limit:page * limit]
    pages = len(applications_list) // limit + 1
    if page > pages or page < 1:
        return RedirectResponse(url="/volunteer_applications")
    return templates.TemplateResponse("staff/volunteer_applications.html",
                                      {
                                          "request": request,
                                          "applications": display_applications,
                                          "pages": pages,
                                          "page": page,
                                          "user": session.user
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


@staff_router.get("/new_request/{animal_id}", status_code=HTTP_200_OK)
async def vet_request_page(request: Request, animal: animal_dependency, session: session_dependency):
    return templates.TemplateResponse("animal/vet_request_page.html",
                                      {
                                          "request": request,
                                          "animal": animal,
                                          "user": session.user
                                      })


@staff_router.post("/new_request/{animal_id}", status_code=HTTP_201_CREATED)
async def create_vet_request(db: db_dependency, animal: animal_dependency, staff: staff_dependency,
                             description: str = Form(...)):
    new_request = VetRequestOrm(
        animal_id=animal.id,
        user_id=staff.id,
        date=datetime.now(timezone.utc),
        description=description,
        status=VetRequestStatus.pending
    )
    db.add(new_request)
    db.commit()
    return {"message": "Request created successfully"}


@staff_router.get("/walk_requests", status_code=HTTP_200_OK)
async def walk_requests_page(
        request: Request,
        db: db_dependency,
        session: session_dependency,
        status_filter: Optional[WalkStatus] = Query(default=None),
):
    """
    Displays the walk requests page with filtering.
    """

    walks = db.query(WalksOrm).all()

    if status_filter:
        walks = list(filter(lambda walk: walk.status == status_filter, walks))

    status_to_int = lambda status: {WalkStatus.started: 0, WalkStatus.accepted: 1, WalkStatus.pending: 2}.get(status, 4)
    walk_sort = lambda walk: (status_to_int(walk.status), walk.date, walk.id)

    walks.sort(key=walk_sort)

    return templates.TemplateResponse("staff/walk_requests.html",
                                      {
                                          "request": request,
                                          "user": session.user,
                                          "walks": walks,
                                          "status_filter": status_filter.value if status_filter else None
                                      })


@staff_router.patch("/walk_requests/{walk_id}/status", status_code=HTTP_200_OK)
async def update_walk_status(
        walk: walk_dependency,
        db: db_dependency,
        status: WalkStatus = Query(...),
):
    """
    Updates the status of a walk request.
    """

    walk.status = status
    db.commit()

    return {"message": "Walk request status updated successfully."}


@staff_router.get("/adoption_requests", status_code=HTTP_200_OK)
async def adoption_requests_page(
        request: Request,
        db: db_dependency,
        session: session_dependency,
        status_filter: Optional[ApplicationStatus] = Query(default=None),
):
    """
    Displays the adoption requests page with filtering.
    """

    adoption_requests = db.query(AdoptionRequestsOrm).all()

    if status_filter:
        adoption_requests = list(filter(lambda request: request.status == status_filter, adoption_requests))

    status_to_int = lambda status: {ApplicationStatus.pending: 0, ApplicationStatus.accepted: 1,
                                    ApplicationStatus.rejected: 2}.get(status, 4)
    request_sort = lambda request: (status_to_int(request.status), request.date, request.id)

    adoption_requests.sort(key=request_sort)

    return templates.TemplateResponse("staff/adoption_requests.html",
                                      {
                                          "request": request,
                                          "user": session.user,
                                          "adoption_requests": adoption_requests,
                                          "status_filter": status_filter.value if status_filter else None
                                      })


@staff_router.patch("/adoption_requests/{request_id}/status", status_code=HTTP_200_OK)
async def update_adoption_request_status(
        request_id: int,
        db: db_dependency,
        status: AdoptionStatus = Query(...),
):
    """
    Updates the status of an adoption request.
    """
    request = db.query(AdoptionRequestsOrm).filter(AdoptionRequestsOrm.id == request_id).first()
    if status == AdoptionStatus.accepted:
        if request.animal.status == AnimalStatus.adopted:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Animal already adopted")
        request.animal.hidden = True
        request.animal.status = AnimalStatus.adopted
        # reject all other requests for the same animal
        for req in request.animal.adoption_requests:
            if req.id != request_id:
                req.status = AdoptionStatus.rejected
    request.status = status
    db.commit()

    return {"message": "Adoption request status updated successfully."}
