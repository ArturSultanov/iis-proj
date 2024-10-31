from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
from starlette.status import HTTP_403_FORBIDDEN, HTTP_200_OK, \
    HTTP_404_NOT_FOUND, HTTP_202_ACCEPTED

from app.database import db_dependency, UsersOrm, Role
from app.utils import admin_dependency, templates

admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/dashboard")
async def admin_page(request: Request, admin: admin_dependency):
    return templates.TemplateResponse("admin/admin_dashboard.html",
                                      {"request": request, "admin": admin},
                                      status_code=HTTP_200_OK)

@admin_router.get("/users")
async def users_page(request: Request, db: db_dependency, admin: admin_dependency):
    users = db.query(UsersOrm).all()
    return templates.TemplateResponse("admin/admin_users.html",
                                      {"request": request, "admin": admin, "users": users,
                                       "roles": Role.get_roles()},
                                      status_code=HTTP_200_OK)

@admin_router.patch("/users/{user_id}/state")
async def user_state(user_id: int, active: bool, db: db_dependency, admin: admin_dependency):
    user = db.query(UsersOrm).filter(UsersOrm.id == user_id).first()
    if user == admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You can't change your own state")
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if user.username == "admin":
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You can't change the root admin state")
    user.disabled = active
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=HTTP_202_ACCEPTED)

@admin_router.patch("/users/{user_id}/role")
async def user_role(user_id: int, role: Role, db: db_dependency, admin: admin_dependency):
    user = db.query(UsersOrm).filter(UsersOrm.id == user_id).first()
    if user == admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You can't change your own role")
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if user.username == "admin":
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You can't change the root admin role")
    user.role = role
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=HTTP_202_ACCEPTED)

@admin_router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: db_dependency, admin: admin_dependency):
    user = db.query(UsersOrm).filter(UsersOrm.id == user_id).first()
    if user == admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You can't delete yourself")
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if user.username == "admin":
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You can't delete the root admin")
    db.delete(user)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=HTTP_202_ACCEPTED)