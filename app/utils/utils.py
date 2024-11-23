from datetime import datetime, timedelta
from typing import Annotated as typingAnnotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException
from fastapi.params import Cookie
from pydantic import BaseModel
from starlette.status import HTTP_403_FORBIDDEN, HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from starlette.templating import Jinja2Templates

from app.config import settings
from app.database import UsersOrm, db_dependency, SessionsOrm, AdoptionRequestsOrm
from app.database.models import ApplicationStatus, AnimalsOrm, WalksOrm, VetRequestOrm

# This is default session duration
session_duration = timedelta(hours=1)

# This is the name of the cookie that will be used to store the session_id
session_id_cookie = "session_id"


# This is a class that will be used when there is no session gotten from the database / cookies
class NoneSession(SessionsOrm):

    @property
    def user(self):
        return None

    def __bool__(self):
        return False


# Cookies structure to be used in the app
class Cookies(BaseModel):
    session_id: UUID | None = None


# This is the instance of the NoneSession class
none_session = NoneSession()


# This function creates a new session for a user
def create_session(username: str, db: db_dependency) -> (UUID, datetime):
    session_id = uuid4()
    user = UsersOrm.get_user(db, username)
    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")
    expiration_date = datetime.now() + session_duration
    # Add the session to the database and return the session_id and expiration_date
    return user.add_session(db, session_id, expiration_date), expiration_date


def get_session(cookies: typingAnnotated[Cookies, Cookie()], db: db_dependency) -> SessionsOrm:
    if not cookies.session_id:
        return none_session

    session: SessionsOrm | None = db.query(SessionsOrm).filter(SessionsOrm.token == cookies.session_id).first()

    # If there is no session, return the instance of the NoneSession class
    if not session:
        return none_session

    # If the session has expired, delete the session from the database and return the instance of the NoneSession class
    if session.expiration < datetime.now():
        db.delete(session)
        db.commit()
        return none_session

    # If the user is disabled, delete the session from the database and return the instance of the NoneSession class
    # Also, redirect the user to the signin page
    if session.user.disabled:
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=HTTP_303_SEE_OTHER,  # 303 See Other is suitable for redirects after a forbidden access
            detail="User is disabled",
            headers={"Location": "/user/signin"}
        )
    return session


# This is a dependency that will be used to get the request session
session_dependency = typingAnnotated[SessionsOrm | None, Depends(get_session)]

# This is an exception that will be raised when a user needs to log in
need_login_exception = HTTPException(
    status_code=HTTP_303_SEE_OTHER,
    detail="You need to login",
    headers={"Location": "/user/signin"}
)

# This is an exception that will be raised when a user is forbidden to access a page
forbidden_exception = HTTPException(
    status_code=HTTP_403_FORBIDDEN,
    detail="You are not allowed to access this"
)


# This is a dependency that will be used to get the user from the session
def get_user(session: session_dependency) -> UsersOrm:
    if not session:
        raise need_login_exception
    return session.user


# This is a dependency that will be used to get the user from the session
user_dependency = typingAnnotated[UsersOrm, Depends(get_user)]


# This is a dependency that will be used to get the admin user from the session
def get_admin(user: user_dependency) -> UsersOrm:
    if not user.is_admin:
        raise forbidden_exception
    return user


# This is a dependency that will be used to get the staff user from the session
def get_staff(user: user_dependency) -> UsersOrm:
    if not user.is_staff:
        raise forbidden_exception
    return user


# This is a dependency that will be used to get the vet user from the session
def get_vet(user: user_dependency) -> UsersOrm:
    if not user.is_vet:
        raise forbidden_exception
    return user


# This is a dependency that will be used to get the volunteer user from the session
def get_volunteer(user: user_dependency) -> UsersOrm:
    if not user.is_volunteer:
        raise forbidden_exception
    return user


# This function converts the application status to an integer
def application_status_to_int(status: ApplicationStatus) -> int:
    # pending = 0, accepted = 1, rejected = 2
    if status == ApplicationStatus.pending:
        return 0
    elif status == ApplicationStatus.accepted:
        return 1
    elif status == ApplicationStatus.rejected:
        return 2


# Dependency to get an animal by id
def get_animal(animal_id: int, db: db_dependency) -> AnimalsOrm:
    animal = db.query(AnimalsOrm).filter(AnimalsOrm.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Animal not found")
    return animal


def get_walk(walk_id: int, db: db_dependency) -> WalksOrm:
    walk = db.query(WalksOrm).filter(WalksOrm.id == walk_id).first()
    if not walk:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Walk not found")
    return walk


def get_vet_request(request_id: int, db: db_dependency) -> VetRequestOrm:
    vet_request = db.query(VetRequestOrm).filter(VetRequestOrm.id == request_id).first()
    if not vet_request:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Request not found")
    return vet_request


# This is a dependency that will be used to get the animal by id
animal_dependency = typingAnnotated[AnimalsOrm, Depends(get_animal)]


def get_adoption_request(session: session_dependency, animal: animal_dependency) -> AdoptionRequestsOrm | None:
    if not session:
        raise need_login_exception
    return next(filter(lambda x: x.animal_id == animal.id, session.user.adoption_requests), None)


# This is a dependency that will be used to get the admin user from the session
admin_dependency = typingAnnotated[UsersOrm, Depends(get_admin)]
# This is a dependency that will be used to get the staff user from the session
staff_dependency = typingAnnotated[UsersOrm, Depends(get_staff)]
# This is a dependency that will be used to get the vet user from the session
vet_dependency = typingAnnotated[UsersOrm, Depends(get_vet)]
# This is a dependency that will be used to get the volunteer user from the session
volunteer_dependency = typingAnnotated[UsersOrm, Depends(get_volunteer)]
# This is a dependency that will be used to get the walk by id
walk_dependency = typingAnnotated[WalksOrm, Depends(get_walk)]
# This is a dependency that will be used to get the vet request by id
vet_request_dependency = typingAnnotated[VetRequestOrm, Depends(get_vet_request)]
# This is a dependency that will be used to get the adoption request
user_animal_adoption_dependency = typingAnnotated[AdoptionRequestsOrm | None, Depends(get_adoption_request)]

# This is the instance of the Jinja2Templates class that will be used to render html templates
templates = Jinja2Templates(directory=settings.APP_TEMPLATES_PATH)
