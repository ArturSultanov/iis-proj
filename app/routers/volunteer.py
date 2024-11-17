from fastapi import APIRouter, Request
from fastapi.params import Depends
from starlette.status import HTTP_200_OK

from app.utils import get_volunteer, volunteer_dependency, templates

volunteer_router = APIRouter(prefix="/volunteer",
                       tags=["volunteer"],
                       dependencies=[Depends(get_volunteer)])

@volunteer_router.get("/dashboard", status_code=HTTP_200_OK)
async def volunteer_dashboard(request: Request):
    return templates.TemplateResponse("volunteer/dashboard.html", {"request": request})