from fastapi import APIRouter
from fastapi.params import Depends

from app.utils import get_volunteer, volunteer_dependency

volunteer_router = APIRouter(prefix="/vet",
                       tags=["vet"],
                       dependencies=[Depends(get_volunteer)])

@volunteer_router.get("/dashboard")
async def volunteer_dashboard():
    return {"message": "Volunteer dashboard"}