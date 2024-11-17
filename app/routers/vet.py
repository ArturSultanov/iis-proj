from fastapi import APIRouter, Request
from fastapi.params import Depends
from starlette.status import HTTP_200_OK

from app.utils import get_vet, vet_dependency, templates

vet_router = APIRouter(prefix="/vet",
                       tags=["vet"],
                       dependencies=[Depends(get_vet)])

@vet_router.get("/dashboard", status_code=HTTP_200_OK)
async def vet_dashboard(request: Request):
    return templates.TemplateResponse("vet/dashboard.html", {"request": request})


