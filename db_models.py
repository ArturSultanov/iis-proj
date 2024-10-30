import enum
from datetime import datetime
from enum import unique
from typing import Self
from uuid import UUID

from sqlalchemy import Integer, ForeignKey, LargeBinary, DateTime, false
from sqlalchemy.orm import Mapped, Session, foreign, relationship
from sqlalchemy.testing.schema import mapped_column
from database import Base, Str256, Str2048


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
    def get_user(cls, db: Session, username: str) -> Self | None:
        return db.query(UsersOrm).filter(UsersOrm.username == username).first()

    def add_session(self, db: Session, session_id: UUID, expiration: datetime) -> UUID:
        session = SessionsOrm(user_id=self.id, token=session_id, expiration=expiration)
        db.add(session)
        db.commit()
        return session.token

class SessionsOrm(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    token: Mapped[UUID] = mapped_column(unique=True, nullable=False)
    expiration: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="sessions")

class AnimalsOrm(Base):
    __tablename__ = 'animals'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Str256] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column()
    species: Mapped[Str256] = mapped_column()
    photo: Mapped[bytes] = mapped_column(LargeBinary(length=2**24-1), nullable=True)
    description: Mapped[Str2048] = mapped_column()

    medical_history: Mapped["MedicalHistoriesOrm"] = relationship("MedicalHistoriesOrm", back_populates="animal")
    scheduled_walks:  Mapped[list["WalksOrm"]] = relationship("WalksOrm", back_populates="animal")

class WalksOrm(Base):
    __tablename__ = 'walks'

    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey('animals.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    location: Mapped[Str256] = mapped_column()

    animal: Mapped["AnimalsOrm"] = relationship("AnimalsOrm", back_populates="scheduled_walks")

class MedicalHistoriesOrm(Base):
    __tablename__ = 'medical_histories'

    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey('animals.id'), nullable=False)
    start_date:Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Str2048] = mapped_column()

    animal: Mapped["AnimalsOrm"] = relationship("AnimalsOrm", back_populates="medical_history")

    treatments: Mapped[list["TreatmentsOrm"]] = relationship("TreatmentsOrm", back_populates="medical_history")
    vaccinations: Mapped[list["VaccinationsOrm"]] = relationship("VaccinationsOrm", back_populates="medical_history")

class TreatmentsOrm(Base):
    __tablename__ = 'treatments'

    id: Mapped[int] = mapped_column(primary_key=True)
    medical_history_id: Mapped[int] = mapped_column(ForeignKey('medical_histories.id'), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Str2048] = mapped_column()

    medical_history: Mapped["MedicalHistoriesOrm"] = relationship("MedicalHistoriesOrm", back_populates="treatments")

class VaccinationsOrm(Base):
    __tablename__ = 'vaccinations'

    id: Mapped[int] = mapped_column(primary_key=True)
    medical_history_id: Mapped[int] = mapped_column(ForeignKey('medical_histories.id'), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Str2048] = mapped_column()

    medical_history: Mapped["MedicalHistoriesOrm"] = relationship("MedicalHistoriesOrm", back_populates="vaccinations")


