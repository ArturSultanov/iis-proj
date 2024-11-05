import sys
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, Request
from fastapi.params import Cookie
from pydantic import BaseModel
from starlette.status import HTTP_403_FORBIDDEN, HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from starlette.templating import Jinja2Templates

from app.config import settings
from app.database import UsersOrm, Role, db_dependency, SessionsOrm
from typing import Annotated as typingAnnotated

session_duration = timedelta(hours=1)

session_id_cookie = "session_id"

class NoneSession(SessionsOrm):

    @property
    def user(self):
        return None

    def __bool__(self):
        return False

class Cookies(BaseModel):
    session_id: UUID | None = None

none_session = NoneSession()

def create_session(username: str, db: db_dependency) -> (UUID, datetime):
    session_id = uuid4()
    user = UsersOrm.get_user(db, username)
    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")
    expiration_date = datetime.now() + session_duration
    return user.add_session(db, session_id, expiration_date), expiration_date

def get_session(cookies: typingAnnotated[Cookies, Cookie()], db: db_dependency) -> SessionsOrm:
    print("Session dependency called", file=sys.stderr)
    if not cookies.session_id:
        return none_session

    session : SessionsOrm | None = db.query(SessionsOrm).filter(SessionsOrm.token == cookies.session_id).first()

    if not session:
        return none_session

    if session.expiration < datetime.now():
        db.delete(session)
        db.commit()
        return none_session

    if session.user.disabled:
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=HTTP_303_SEE_OTHER,  # 303 See Other is suitable for redirects after a forbidden access
            detail="User is disabled",
            headers={"Location": "/user/signin"}
        )
    return session

session_dependency = typingAnnotated[SessionsOrm | None, Depends(get_session)]

need_login_exception = HTTPException(
    status_code=HTTP_303_SEE_OTHER,
    detail="You need to login",
    headers={"Location": "/user/signin"}
)

forbidden_exception = HTTPException(
    status_code=HTTP_403_FORBIDDEN,
    detail="You are not allowed to access this"
)

def get_user(session: session_dependency) -> UsersOrm:
    if not session:
        raise need_login_exception
    return session.user

user_dependency = typingAnnotated[UsersOrm, Depends(get_user)]

def get_admin(user: user_dependency) -> UsersOrm:
    if not user.is_admin:
        raise forbidden_exception
    return user

def get_staff(user: user_dependency) -> UsersOrm:
    if not user.is_staff:
        raise forbidden_exception
    return user

def get_vet(user: user_dependency) -> UsersOrm:
    if not user.is_vet:
        raise forbidden_exception
    return user

def get_volunteer(user: user_dependency) -> UsersOrm:
    if not user.is_volunteer:
        raise forbidden_exception
    return user

admin_dependency = typingAnnotated[UsersOrm, Depends(get_admin)]
staff_dependency = typingAnnotated[UsersOrm, Depends(get_staff)]
vet_dependency = typingAnnotated[UsersOrm, Depends(get_vet)]
volunteer_dependency = typingAnnotated[UsersOrm, Depends(get_volunteer)]

templates = Jinja2Templates(directory=settings.APP_TEMPLATES_PATH)

