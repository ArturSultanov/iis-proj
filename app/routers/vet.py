from fastapi import APIRouter
from fastapi.params import Depends

from app.utils import get_vet, vet_dependency

vet_router = APIRouter(prefix="/vet",
                       tags=["vet"],
                       dependencies=[Depends(get_vet)])

@vet_router.get("/dashboard")
async def vet_dashboard():
    return {"message": "Vet dashboard"}


