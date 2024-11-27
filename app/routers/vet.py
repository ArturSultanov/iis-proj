from datetime import datetime, timezone

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.params import Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.database import db_dependency, VetRequestOrm, VetRequestStatus, MedicalHistoriesOrm, TreatmentsOrm, \
    VaccinationsOrm
from app.utils import animal_dependency, vet_request_dependency
from app.utils import get_vet, vet_dependency, templates, session_dependency

vet_router = APIRouter(prefix="/vet",
                       tags=["vet"],
                       dependencies=[Depends(get_vet)])


@vet_router.get("/dashboard", status_code=HTTP_200_OK)
async def vet_dashboard(request: Request, session: session_dependency):
    return templates.TemplateResponse("vet/dashboard.html", {"request": request, "user": session.user})


@vet_router.get("/requests", status_code=HTTP_200_OK)
async def get_vet_requests(request: Request, db: db_dependency, vet: vet_dependency,
                           status: VetRequestStatus = Form(None)):
    if status:
        vet_requests = db.query(VetRequestOrm).filter(VetRequestOrm.status == status).all()
    else:
        vet_requests = db.query(VetRequestOrm).all()

    return templates.TemplateResponse("vet/vet_requests.html", {
        "request": request,
        "vet": vet,
        "user": vet,
        "vet_requests": vet_requests,
        "status": status
    })


@vet_router.get("/request/{request_id}", status_code=HTTP_200_OK)
async def view_vet_request(request: Request, vet_request: vet_request_dependency, vet: vet_dependency):
    return templates.TemplateResponse("vet/vet_request_details.html", {
        "request": request,
        "vet": vet,
        "user": vet,
        "vet_request": vet_request
    })


@vet_router.post("/request/{request_id}/accept", status_code=HTTP_200_OK)
async def accept_vet_request(vet_request: vet_request_dependency, db: db_dependency):
    if vet_request.status != VetRequestStatus.pending:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Request is not in a pending state")
    vet_request.status = VetRequestStatus.accepted
    db.commit()
    return {"message": "Request accepted successfully"}


@vet_router.post("/request/{request_id}/complete", status_code=HTTP_200_OK)
async def complete_vet_request(vet_request: vet_request_dependency, db: db_dependency):
    if vet_request.status != VetRequestStatus.accepted and vet_request.status != VetRequestStatus.pending:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Request is not in an accepted or pending state")
    vet_request.status = VetRequestStatus.rejected
    db.commit()
    return {"message": "Request completed successfully"}


@vet_router.get("/new_treatment/{animal_id}", status_code=HTTP_200_OK)
async def treatment(request: Request, animal: animal_dependency, vet: vet_dependency):
    return templates.TemplateResponse("vet/treatment.html",
                                      {
                                          "request": request,
                                          "animal": animal,
                                          "user": vet
                                      })


@vet_router.post("/new_treatment/{animal_id}", status_code=HTTP_201_CREATED)
async def create_treatment(db: db_dependency, animal: animal_dependency, date: datetime = Form(...),
                           description: str = Form(...)):
    med_history = animal.medical_history
    if not med_history:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please create medical history first.")

    new_treatment = TreatmentsOrm(
        medical_history_id=med_history.id,
        date=date,
        description=description
    )
    db.add(new_treatment)
    db.commit()
    return {"message": "Treatment added successfully"}


@vet_router.get("/new_vaccination/{animal_id}", status_code=HTTP_200_OK)
async def vaccination(request: Request, animal: animal_dependency, vet: vet_dependency):
    return templates.TemplateResponse("vet/vaccination.html",
                                      {
                                          "request": request,
                                          "animal": animal,
                                          "user": vet
                                      })


@vet_router.post("/new_vaccination/{animal_id}", status_code=HTTP_201_CREATED)
async def create_vaccination(db: db_dependency, animal: animal_dependency, date: datetime = Form(...),
                             description: str = Form(...)):
    med_history = animal.medical_history
    if not med_history:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Please create medical history first.")

    new_vaccination = VaccinationsOrm(
        medical_history_id=med_history.id,
        date=date,
        description=description
    )
    db.add(new_vaccination)
    db.commit()
    return {"message": "Vaccination added successfully"}


@vet_router.get("/new_medical_history/{animal_id}", status_code=HTTP_200_OK)
async def medical_history(request: Request, animal: animal_dependency, vet: vet_dependency):
    return templates.TemplateResponse("vet/medical_history.html",
                                      {
                                          "request": request,
                                          "animal": animal,
                                          "user": vet
                                      })


@vet_router.post("/new_medical_history/{animal_id}", status_code=HTTP_201_CREATED)
async def create_medical_history(db: db_dependency, animal: animal_dependency, description: str = Form(...)):
    med_history = animal.medical_history
    if med_history:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Medical history already exists for this animal.")

    new_medical_history = MedicalHistoriesOrm(
        animal_id=animal.id,
        start_date=datetime.now(timezone.utc),
        description=description
    )

    db.add(new_medical_history)
    db.commit()
    return {"message": "Medical history created successfully"}


@vet_router.get("/medical_history_profile/{animal_id}", status_code=HTTP_200_OK)
async def get_medical_history(request: Request, animal: animal_dependency, vet: vet_dependency):
    return templates.TemplateResponse("vet/medical_history_profile.html", {
        "request": request,
        "animal": animal,
        "user": vet,
        "medical_history": animal.medical_history
    })


@vet_router.get("/requests/{animal_id}", status_code=HTTP_200_OK)
async def get_vet_requests(request: Request, animal: animal_dependency, vet: vet_dependency,
                           status: VetRequestStatus = Form(None)):
    vet_requests = animal.vet_requests
    if status:
        vet_requests = list(filter(lambda x: x.status == status, vet_requests))

    return templates.TemplateResponse("vet/vet_requests.html", {
        "request": request,
        "vet": vet,
        "user": vet,
        "vet_requests": vet_requests,
        "status": status,
        "animal_name": animal.name
    })
