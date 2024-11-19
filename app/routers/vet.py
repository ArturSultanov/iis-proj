from fastapi import APIRouter, Request
from fastapi.params import Depends
from starlette.status import HTTP_200_OK

from app.utils import get_vet, vet_dependency, templates
from app.database import db_dependency, VetRequestOrm, VetRequestStatus
from app.utils import get_vet, vet_dependency, templates

vet_router = APIRouter(prefix="/vet",
                       tags=["vet"],
                       dependencies=[Depends(get_vet)])

@vet_router.get("/dashboard", status_code=HTTP_200_OK)
async def vet_dashboard(request: Request):
    return templates.TemplateResponse("vet/dashboard.html", {"request": request})



@vet_router.get("/requests", status_code=HTTP_200_OK)
async def get_pending_vet_requests(request: Request, db: db_dependency, vet: vet_dependency):
    vet_requests = db.query(VetRequestOrm).filter(VetRequestOrm.status == VetRequestStatus.pending).all()
    return templates.TemplateResponse("vet/vet_requests.html", {
        "request": request,
        "vet": vet,
        "vet_requests": vet_requests
    })
