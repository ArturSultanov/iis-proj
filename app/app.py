from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.status import HTTP_200_OK

from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import get_db, db_dependency, UsersOrm, Role, AnimalsOrm, create_all_tables
from app.database import Base as dbBase
from app.password import hash_password
from app.routers import *
from app.utils import session_dependency, templates

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.include_router(user_router)
    app.include_router(admin_router)
    app.include_router(staff_router)

    app.mount(settings.APP_STATIC_PATH, StaticFiles(directory="static"), name="static")

    create_all_tables()
    start_db = next(get_db())
    dbBase.metadata.create_all(start_db.get_bind())
    # add admin user if not exists
    if not UsersOrm.get_user(start_db, "admin"):
        start_db.add(UsersOrm(username="admin", name="admin", password=hash_password("admin"), role=Role.admin))
        start_db.commit()
        start_db.close()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

@app.get("/")
async def index_page(request: Request, session: session_dependency):
    return templates.TemplateResponse("index.html", {"request": request, "user": session.user}, status_code=HTTP_200_OK)

@app.get("/animals")
async def animals_page(request: Request, db: db_dependency, session: session_dependency, page: int = 1):
    animals_list = db.query(AnimalsOrm).all()
    display_animals = animals_list[(page-1)*settings.PAGE_SIZE:page*settings.PAGE_SIZE]
    pages = len(animals_list) // settings.PAGE_SIZE + 1
    if page > pages or page < 1:
        return RedirectResponse(url="/animals")
    if not session:
        return templates.TemplateResponse("animals.html",
                                          {
                                              "request": request,
                                              "user": None,
                                              "animals": display_animals,
                                              "pages": pages,
                                              "page": page
                                          },
                                          status_code=HTTP_200_OK)
    if session.user.is_staff:
        return templates.TemplateResponse("animals.html",
                                          {
                                              "request": request,
                                              "user": session.user,
                                              "animals": display_animals,
                                              "pages": pages,
                                              "page": page
                                          })
    return templates.TemplateResponse("animals.html",
                                      {
                                          "request": request,
                                          "user": session.user,
                                          "animals": display_animals,
                                          "pages": pages,
                                          "page": page
                                      }, status_code=HTTP_200_OK)

placeholder_photo : bytes = open("static/no-image-available.jpg", "rb").read()

@app.get("/animals/{animal_id}/photo")
async def animal_photo(animal_id: int, db: db_dependency):
    animal = db.query(AnimalsOrm).filter(AnimalsOrm.id == animal_id).first()
    if not animal or not animal.photo:
        return HTMLResponse(content=placeholder_photo, status_code=200, media_type="image/jpeg")
    return HTMLResponse(content=animal.photo, status_code=200, media_type="image/jpeg")

@app.get("/animals/{animal_id}")
async def animal_profile(request: Request, animal_id: int, db: db_dependency, session: session_dependency):
    # animal profile
    pass