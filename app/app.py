from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.status import HTTP_200_OK

from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import get_db, db_dependency, UsersOrm, Role, AnimalsOrm, create_all_tables
from app.password import hash_password
from app.routers import *
from app.utils import session_dependency, templates

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create all tables if not exists
    create_all_tables()
    # create a session to add the admin user if not exists
    start_db = next(get_db())
    # add admin user if not exists
    if not UsersOrm.get_user(start_db, "admin"):
        # add admin user with password "admin"
        start_db.add(UsersOrm(username="admin", name="admin", password=hash_password("admin"), role=Role.admin))
    if not UsersOrm.get_user(start_db, "staff"):
        # add staff user with password "staff"
        start_db.add(UsersOrm(username="staff", name="staff", password=hash_password("staff"), role=Role.staff))
    if not UsersOrm.get_user(start_db, "vet"):
        # add vet user with password "vet"
        start_db.add(UsersOrm(username="vet", name="vet", password=hash_password("vet"), role=Role.vet))
    if not UsersOrm.get_user(start_db, "volunteer"):
        # add volunteer user with password "volunteer"
        start_db.add(UsersOrm(username="volunteer", name="volunteer", password=hash_password("volunteer"), role=Role.volunteer))
    if not UsersOrm.get_user(start_db, "registered"):
        # add user registered with password "registered"
        start_db.add(UsersOrm(username="registered", name="registered", password=hash_password("registered"), role=Role.registered))
    start_db.commit()
    start_db.close()
    yield

# Create the FastAPI app
app = FastAPI(lifespan=lifespan)

# Add routers to the app
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(staff_router)
app.include_router(vet_router)
app.include_router(volunteer_router)

# Add static files to the app
app.mount(settings.APP_STATIC_PATH, StaticFiles(directory="static"), name="static")

# Add middleware to the app
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

@app.get("/", status_code=HTTP_200_OK)
async def index_page(request: Request, session: session_dependency):
    return templates.TemplateResponse("index.html",
                                      {
                                          "request": request,
                                          "user": session.user
                                      })

@app.get("/animals", status_code=HTTP_200_OK)
async def animals_page(request: Request, db: db_dependency, session: session_dependency, page: int = 1):
    animals_list = db.query(AnimalsOrm).all()
    # sort animals by hidden status, so hidden animals will be displayed at the end
    animals_list.sort(key=lambda x: x.hidden)
    # slice the list to display only the animals on the current page
    display_animals = animals_list[(page-1)*settings.PAGE_SIZE:page*settings.PAGE_SIZE]
    pages = len(animals_list) // settings.PAGE_SIZE + 1
    if page > pages or page < 1:
        # if the page is out of range, redirect to the first page
        return RedirectResponse(url="/animals")
    return templates.TemplateResponse("animals.html",
                                      {
                                          "request": request,
                                          "user": session.user,
                                          "animals": display_animals,
                                          "pages": pages,
                                          "page": page
                                      })

@app.get("/animals/{animal_id}/photo", status_code=HTTP_200_OK)
async def animal_photo(animal_id: int, db: db_dependency):
    animal = db.query(AnimalsOrm).filter(AnimalsOrm.id == animal_id).first()
    if not animal or not animal.photo:
        return RedirectResponse(url="/static/no-image-available.jpg")
    return HTMLResponse(content=animal.photo, media_type="image/jpeg")

@app.get("/animals/{animal_id}/profile")
async def animal_profile(request: Request, animal_id: int, db: db_dependency, session: session_dependency):
    animal = db.query(AnimalsOrm).filter(AnimalsOrm.id == animal_id).first()
    if not animal:
        return RedirectResponse(url="/animals")
    return templates.TemplateResponse("animal/profile.html",
                                      {
                                          "request": request,
                                          "user": session.user,
                                          "animal": animal
                                      })

@app.get("/dashboard")
async def dashboard(request: Request, session: session_dependency):
    if not session.user:
        return RedirectResponse(url="/")
    if session.user.is_admin:
        return RedirectResponse(url="/admin/dashboard")
    if session.user.is_staff:
        return RedirectResponse(url="/staff/dashboard")
    if session.user.is_vet:
        return RedirectResponse(url="/vet/dashboard")
    if session.user.is_volunteer:
        return RedirectResponse(url="/volunteer/dashboard")


@app.get("/favicon.ico")
async def favicon(request: Request):
    return RedirectResponse(url="/static/favicon.ico")
