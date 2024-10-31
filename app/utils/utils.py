from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from starlette.templating import Jinja2Templates

from app.config import settings
from app.database import UsersOrm, Role, db_dependency, SessionsOrm
from typing import Annotated as typingAnnotated

session_duration = timedelta(hours=1)

session_id_cookie = "session_id"

def create_session(username: str, db: db_dependency) -> (UUID, datetime):
    session_id = uuid4()
    user = UsersOrm.get_user(db, username)
    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")
    expiration_date = datetime.now() + session_duration
    return user.add_session(db, session_id, expiration_date), expiration_date

def user_from_cookie(request: Request, db: db_dependency) -> UsersOrm | None:
    if session_id_cookie not in request.cookies:
        return None
    if not request.cookies.get(session_id_cookie):
        return None

    session_id = UUID(request.cookies.get(session_id_cookie))
    session : SessionsOrm | None = db.query(SessionsOrm).filter(SessionsOrm.token == session_id).first()
    if not session:
        return None
    if session.expiration < datetime.now():
        db.delete(session)
        db.commit()
        return None
    user = session.user
    if not user:
        return None
    if user.disabled:
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=HTTP_303_SEE_OTHER,  # 303 See Other is suitable for redirects after a forbidden access
            detail="User is disabled",
            headers={"Location": "/user/signin"}
        )
    return user

def get_user(logged_user: UsersOrm = Depends(user_from_cookie)) -> UsersOrm:
    if not logged_user:
        raise HTTPException(status_code=HTTP_303_SEE_OTHER, detail="You need to login", headers={"Location": "/user/signin"})
    return logged_user

def get_admin(logged_user: UsersOrm = Depends(user_from_cookie)) -> UsersOrm:
    if not logged_user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    if logged_user.role != Role.admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    return logged_user

def get_staff(logged_user: UsersOrm = Depends(user_from_cookie)) -> UsersOrm:
    if not logged_user:
        raise HTTPException(status_code=HTTP_303_SEE_OTHER, detail="You need to login", headers={"Location": "/user/signin"})
    if logged_user.role != Role.staff and logged_user.role != Role.admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    return logged_user

user_or_none_dependency = typingAnnotated[UsersOrm | None, Depends(user_from_cookie)]
user_dependency = typingAnnotated[UsersOrm, Depends(get_user)]
admin_dependency = typingAnnotated[UsersOrm, Depends(get_admin)]
staff_dependency = typingAnnotated[UsersOrm, Depends(get_staff)]

templates = Jinja2Templates(directory=settings.APP_TEMPLATES_PATH)

