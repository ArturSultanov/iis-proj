import enum
from sqlalchemy.orm import Mapped, Session
from sqlalchemy.testing.schema import mapped_column
from database import Base, Str256



class Role(enum.Enum):
    admin = 'admin'
    staff = 'staff'
    vet = 'vet'
    volunteer = 'volunteer'
    registered = 'registered'
    # unregistered = 'unregistered' todo ??

class UsersOrm(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[Str256] = mapped_column(unique=True)
    password: Mapped[Str256]
    role: Mapped[Role] = mapped_column(default=Role.registered)

    @classmethod
    def get_user(cls, db: Session, username: str):
        return db.query(UsersOrm).filter(UsersOrm.username == username).first()




