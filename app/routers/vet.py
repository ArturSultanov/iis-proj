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
async def get_vet_requests(request: Request, db: db_dependency, vet: vet_dependency, status: str = None):
    if status:
        vet_requests = db.query(VetRequestOrm).filter(VetRequestOrm.status == VetRequestStatus[status]).all()
    else:
        vet_requests = db.query(VetRequestOrm).all()

    return templates.TemplateResponse("vet/vet_requests.html", {
        "request": request,
        "vet": vet,
        "vet_requests": vet_requests,
        "status": status
    })

@vet_router.get("/request/{request_id}", status_code=HTTP_200_OK)
async def view_vet_request(request: Request, request_id: int, db: db_dependency, vet: vet_dependency):
    vet_request = db.query(VetRequestOrm).filter(VetRequestOrm.id == request_id).first()
    return templates.TemplateResponse("vet/vet_request_details.html", {
        "request": request,
        "vet": vet,
        "vet_request": vet_request
    })


@vet_router.post("/request/{request_id}/accept", status_code=HTTP_200_OK)
async def accept_vet_request(request_id: int, db: db_dependency):
    vet_request = db.query(VetRequestOrm).filter(VetRequestOrm.id == request_id).first()
    if vet_request.status != VetRequestStatus.pending:
        return {"message": "Request is not in a pending state"}
    vet_request.status = VetRequestStatus.accepted
    db.commit()
    return {"message": "Request accepted successfully"}

@vet_router.post("/request/{request_id}/complete", status_code=HTTP_200_OK)
async def complete_vet_request(request_id: int, db: db_dependency):
    vet_request = db.query(VetRequestOrm).filter(VetRequestOrm.id == request_id).first()
    if vet_request.status != VetRequestStatus.accepted and vet_request.status != VetRequestStatus.pending:
        return {"message": "Request is not in a pending or accepted state"}
    vet_request.status = VetRequestStatus.rejected
    db.commit()
    return {"message": "Request completed successfully"}

