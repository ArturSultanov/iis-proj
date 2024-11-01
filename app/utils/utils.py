from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from starlette.templating import Jinja2Templates

from app.config import settings
from app.database import UsersOrm, Role, db_dependency, SessionsOrm
from typing import Annotated as typingAnnotated

session_duration = timedelta(hours=1)

session_id_cookie = "SESSION"

class NoneSession(SessionsOrm):

    @property
    def user(self):
        return None

    def __bool__(self):
        return False

none_session = NoneSession()

def create_session(username: str, db: db_dependency) -> (UUID, datetime):
    session_id = uuid4()
    user = UsersOrm.get_user(db, username)
    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")
    expiration_date = datetime.now() + session_duration
    return user.add_session(db, session_id, expiration_date), expiration_date

def get_session(request: Request, db: db_dependency) -> SessionsOrm:
    if session_id_cookie not in request.cookies:
        return none_session
    if not request.cookies.get(session_id_cookie):
        return none_session

    session_id = UUID(request.cookies.get(session_id_cookie))
    session : SessionsOrm | None = db.query(SessionsOrm).filter(SessionsOrm.token == session_id).first()
    if not session:
        return none_session
    if session.expiration < datetime.now():
        db.delete(session)
        db.commit()
        return none_session
    user = session.user
    if not user:
        return none_session
    if user.disabled:
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=HTTP_303_SEE_OTHER,  # 303 See Other is suitable for redirects after a forbidden access
            detail="User is disabled",
            headers={"Location": "/user/signin"}
        )
    return session

session_dependency = typingAnnotated[SessionsOrm | None, Depends(get_session)]

def get_user(session: session_dependency) -> UsersOrm:
    if not session:
        raise HTTPException(status_code=HTTP_303_SEE_OTHER, detail="You need to login", headers={"Location": "/user/signin"})
    return session.user

def get_admin(session: session_dependency) -> UsersOrm:
    if not session:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    if session.user.role != Role.admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    return session.user

def get_staff(session: session_dependency) -> UsersOrm:
    if not session:
        raise HTTPException(status_code=HTTP_303_SEE_OTHER, detail="You need to login", headers={"Location": "/user/signin"})
    if session.user.role != Role.staff and session.user.role != Role.admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    return session.user

def get_vet(session: session_dependency) -> UsersOrm:
    if not session:
        raise HTTPException(status_code=HTTP_303_SEE_OTHER, detail="You need to login", headers={"Location": "/user/signin"})
    if session.user.role != Role.vet and session.user.role != Role.admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    return session.user

def get_volunteer(session: session_dependency) -> UsersOrm:
    if not session:
        raise HTTPException(status_code=HTTP_303_SEE_OTHER, detail="You need to login", headers={"Location": "/user/signin"})
    if session.user.role != Role.volunteer and session.user.role != Role.admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    return session.user

user_dependency = typingAnnotated[UsersOrm, Depends(get_user)]
admin_dependency = typingAnnotated[UsersOrm, Depends(get_admin)]
staff_dependency = typingAnnotated[UsersOrm, Depends(get_staff)]
vet_dependency = typingAnnotated[UsersOrm, Depends(get_vet)]
volunteer_dependency = typingAnnotated[UsersOrm, Depends(get_volunteer)]

templates = Jinja2Templates(directory=settings.APP_TEMPLATES_PATH)

