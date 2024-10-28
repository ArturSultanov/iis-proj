from fastapi import APIRouter, Request, Depends, HTTPException
from starlette.responses import RedirectResponse
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, HTTP_200_OK, \
    HTTP_404_NOT_FOUND, HTTP_202_ACCEPTED
from starlette.templating import Jinja2Templates

from database import db_dependency
from db_models import UsersOrm, Role
from user import user_from_cookie

admin_router = APIRouter(prefix="/admin", tags=["admin"])

templates = Jinja2Templates(directory="templates")

def get_admin(logged_user: UsersOrm = Depends(user_from_cookie)) -> UsersOrm:
    if not logged_user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    if logged_user.role != Role.admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    return logged_user

@admin_router.get("/dashboard")
async def admin_page(request: Request, admin: UsersOrm = Depends(get_admin)):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "admin": admin}, status_code=HTTP_200_OK)

@admin_router.get("/users")
async def users_page(request: Request, db: db_dependency, admin: UsersOrm = Depends(get_admin)):
    users = db.query(UsersOrm).all()
    return templates.TemplateResponse("admin_users.html", {"request": request, "admin": admin, "users": users, "roles": Role.get_roles()}, status_code=HTTP_200_OK)

@admin_router.patch("/users/{user_id}/state")
async def user_state(user_id: int, active: bool, db: db_dependency, admin: UsersOrm = Depends(get_admin)):
    user = db.query(UsersOrm).filter(UsersOrm.id == user_id).first()
    if user == admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You can't change your own state")
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    user.disabled = active
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=HTTP_202_ACCEPTED)

@admin_router.patch("/users/{user_id}/role")
async def user_role(user_id: int, role: Role, db: db_dependency, admin: UsersOrm = Depends(get_admin)):
    user = db.query(UsersOrm).filter(UsersOrm.id == user_id).first()
    if user == admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You can't change your own role")
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    user.role = role
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=HTTP_202_ACCEPTED)