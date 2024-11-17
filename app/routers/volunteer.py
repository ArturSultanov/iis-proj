from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.status import HTTP_403_FORBIDDEN, HTTP_200_OK

from app.database import db_dependency, WalksOrm, AnimalsOrm
from app.utils import get_volunteer, volunteer_dependency, templates

volunteer_router = APIRouter(prefix="/volunteer",
                             tags=["volunteer"],
                             dependencies=[Depends(get_volunteer)])


@volunteer_router.get("/dashboard", status_code=HTTP_200_OK)
async def volunteer_dashboard(request: Request):
    return templates.TemplateResponse("volunteer/dashboard.html", {"request": request})


# See the history of their walks
@volunteer_router.get("/walks-history", status_code=HTTP_200_OK)
async def volunteer_history(
    request: Request,
    volunteer: volunteer_dependency,
    db: db_dependency,
):
    # Query walks associated with the volunteer
    walks = db.query(WalksOrm).filter(WalksOrm.user_id == volunteer.id).all()

    walk_data = [
        {
            "animal_name": walk.animal.name,
            "date": walk.date,
            "duration": walk.duration,
            "location": walk.location,
        }
        for walk in walks
    ]

    return templates.TemplateResponse(
        "volunteer/history.html",
        {"request": request, "walks": walk_data},
    )


@volunteer_router.get("/available-animals", status_code=HTTP_200_OK)
async def available_animals(
    request: Request,
    db: db_dependency,
):
    """
    List all animals available for walking.
    """
    animals = db.query(AnimalsOrm).filter(AnimalsOrm.status == "available").all()

    # Format data to pass to the template
    animal_data = [
        {"id": animal.id, "name": animal.name, "species": animal.species, "description": animal.description}
        for animal in animals
    ]

    return templates.TemplateResponse(
        "volunteer/available_animals.html",
        {"request": request, "animals": animal_data},
    )


@volunteer_router.post("/reserve-walk/{animal_id}", status_code=HTTP_200_OK)
async def reserve_animal(
    animal_id: int,
    db: db_dependency,
    volunteer: volunteer_dependency,
    duration_minutes: int = 60,
    location: str = "Park",
):
    """
    Reserve an animal for walking.
    """

    animal = db.query(AnimalsOrm).filter(AnimalsOrm.id == animal_id, AnimalsOrm.status == "available").first()
    if not animal:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Animal is not available for walking.")

    return {"message": f"Successfully reserved {animal.name} for walking."}


