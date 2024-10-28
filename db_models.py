import enum
from enum import unique
from typing import Self

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, Session, foreign, relationship
from sqlalchemy.testing.schema import mapped_column
from database import Base, Str256



class Role(enum.Enum):
    admin = 'admin'
    staff = 'staff'
    vet = 'vet'
    volunteer = 'volunteer'
    registered = 'registered'
    # unregistered = 'unregistered' todo ??

    @classmethod
    def get_roles(cls) -> list[Self]:
        return [role for role in cls]

class UsersOrm(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Str256] = mapped_column()
    username: Mapped[Str256] = mapped_column(unique=True)
    password: Mapped[Str256]
    role: Mapped[Role] = mapped_column(default=Role.registered)
    disabled: Mapped[bool] = mapped_column(default=False)

    sessions: Mapped[list["SessionsOrm"]] = relationship("SessionsOrm", back_populates="user")

    @classmethod
    def get_user(cls, db: Session, username: str):
        return db.query(UsersOrm).filter(UsersOrm.username == username).first()

class SessionsOrm(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    token: Mapped[Str256] = mapped_column(unique=True, nullable=False)

    user: Mapped["UsersOrm"] = relationship(back_populates="sessions")




