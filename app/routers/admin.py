from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.status import HTTP_403_FORBIDDEN, HTTP_200_OK, \
    HTTP_404_NOT_FOUND, HTTP_202_ACCEPTED

from app.database import db_dependency, UsersOrm, Role, SessionsOrm
from app.utils import admin_dependency, templates, get_admin, session_dependency

admin_router = APIRouter(prefix="/admin",
                         tags=["admin"],
                         dependencies=[Depends(get_admin)])


# Validation function to check if the user can be modified
def validate_user_operation(user: UsersOrm, admin: UsersOrm):
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if user == admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You can't change your own state")
    if user.username == "admin":
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="You can't change the root admin state")


@admin_router.get("/dashboard", status_code=HTTP_200_OK)
async def admin_page(request: Request, admin: admin_dependency):
    return templates.TemplateResponse("admin/dashboard.html",
                                      {
                                          "request": request,
                                          "admin": admin,
                                          "user": admin
                                      })


@admin_router.get("/users", status_code=HTTP_200_OK)
async def users_page(request: Request, db: db_dependency, admin: admin_dependency):
    users = db.query(UsersOrm).all()
    return templates.TemplateResponse("admin/users.html",
                                      {
                                          "request": request,
                                          "admin": admin,
                                          "user": admin,
                                          "users": users,
                                          "roles": Role.get_roles()
                                      })


@admin_router.patch("/users/{user_id}/state", status_code=HTTP_202_ACCEPTED)
async def user_state(user_id: int, active: bool, db: db_dependency, admin: admin_dependency):
    user = db.query(UsersOrm).filter(UsersOrm.id == user_id).first()
    validate_user_operation(user, admin)
    # Update the user state
    user.disabled = active
    db.commit()


@admin_router.patch("/users/{user_id}/role", status_code=HTTP_202_ACCEPTED)
async def user_role(user_id: int, role: Role, db: db_dependency, admin: admin_dependency):
    user = db.query(UsersOrm).filter(UsersOrm.id == user_id).first()
    validate_user_operation(user, admin)
    # Update the user role
    user.role = role
    db.commit()


@admin_router.delete("/users/{user_id}", status_code=HTTP_202_ACCEPTED)
async def delete_user(user_id: int, db: db_dependency, admin: admin_dependency):
    user = db.query(UsersOrm).filter(UsersOrm.id == user_id).first()
    validate_user_operation(user, admin)
    db.delete(user)
    db.commit()


@admin_router.delete("/sessions", status_code=HTTP_202_ACCEPTED)
async def delete_sessions(db: db_dependency, cur_session: session_dependency):
    sessions = db.query(SessionsOrm).all()
    sessions_count = len(sessions)
    # terminate all users' sessions except the current admin session
    for session in sessions:
        if session.id == cur_session.id:
            continue
        db.delete(session)
    db.commit()
    return {"message": f"Deleted {sessions_count - 1} sessions"}
