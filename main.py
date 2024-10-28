from fastapi import FastAPI, Request
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_202_ACCEPTED, HTTP_200_OK

from config import settings
from starlette.middleware.cors import CORSMiddleware

from database import get_db
from db_models import UsersOrm, Role
from orm import create_tables
from password import hash_password
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

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

create_tables()
# add admin user if not exists
db = next(get_db())
if not UsersOrm.get_user(db, "admin"):
    db.add(UsersOrm(username="admin", name="admin", password=hash_password("admin"), role=Role.admin))
    db.commit()


@app.get("/")
async def index(request: Request, user: UsersOrm = Depends(user_from_cookie)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user}, status_code=HTTP_200_OK)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.WEB_HOST, port=settings.WEB_PORT)