from fastapi import FastAPI, Request
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.status import HTTP_202_ACCEPTED, HTTP_200_OK

from config import settings
from starlette.middleware.cors import CORSMiddleware

from database import get_db, db_dependency
from db_models import UsersOrm, Role, AnimalsOrm
from orm import create_tables
from password import hash_password
from staff import staff_router
from user import user_router, user_from_cookie
from admin import admin_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(staff_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

create_tables()
# add admin user if not exists
start_db = next(get_db())
if not UsersOrm.get_user(start_db, "admin"):
    start_db.add(UsersOrm(username="admin", name="admin", password=hash_password("admin"), role=Role.admin))
    start_db.commit()


@app.get("/")
async def index(request: Request, user: UsersOrm = Depends(user_from_cookie)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user}, status_code=HTTP_200_OK)

@app.get("/animals")
async def animals(request: Request, db: db_dependency, user: UsersOrm = Depends(user_from_cookie)):
    animals_list = db.query(AnimalsOrm).all()
    if not user:
        return templates.TemplateResponse("animals.html", {"request": request, "user": None, "animals": animals_list}, status_code=HTTP_200_OK)
    if user.role == Role.staff or user.role == Role.admin:
        return RedirectResponse(url="/staff/animals")
    return templates.TemplateResponse("animals.html", {"request": request, "user": user, "animals": animals_list}, status_code=HTTP_200_OK)

@app.get("/animals/{animal_id}/photo")
async def animal_photo(animal_id: int, db: db_dependency):
    animal = db.query(AnimalsOrm).filter(AnimalsOrm.id == animal_id).first()
    if not animal or not animal.photo:
        # return photo from https://a1petmeats.com.au/wp-content/uploads/2019/11/no-image-available.jpg
        return RedirectResponse(url="https://a1petmeats.com.au/wp-content/uploads/2019/11/no-image-available.jpg")
    return HTMLResponse(content=animal.photo, status_code=200, media_type="image/jpeg")


if __name__ == "__main__":
    uvicorn.run(app, host=settings.WEB_HOST, port=settings.WEB_PORT)