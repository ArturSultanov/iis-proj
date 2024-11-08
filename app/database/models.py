import enum
from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKey, LargeBinary, DateTime
from sqlalchemy.orm import Mapped, Session, relationship
from sqlalchemy.testing.schema import mapped_column
from .database import Base, Str256, Str2048


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
    password: Mapped[bytes] = mapped_column(LargeBinary(length=2**10), nullable=False)
    role: Mapped[Role] = mapped_column(default=Role.registered)
    disabled: Mapped[bool] = mapped_column(default=False)

    sessions: Mapped[list["SessionsOrm"]] = relationship("SessionsOrm", back_populates="user")
    adoption_requests: Mapped[list["AdoptionRequestsOrm"]] = relationship("AdoptionRequestsOrm", back_populates="user")
    volunteer_application: Mapped["VolunteerApplicationsOrm"] = relationship("VolunteerApplicationsOrm", back_populates="user")

    @classmethod
    def get_user(cls, db: Session, username: str) -> Self | None:
        return db.query(UsersOrm).filter(UsersOrm.username == username).first()

    @property
    def is_admin(self) -> bool:
        return self.role == Role.admin

    @property
    def is_staff(self) -> bool:
        return self.role == Role.staff or self.is_admin

    @property
    def is_vet(self) -> bool:
        return self.role == Role.vet or self.is_admin

    @property
    def is_volunteer(self) -> bool:
        return self.role == Role.volunteer or self.is_admin

    def add_session(self, db: Session, session_id: UUID, expiration: datetime) -> UUID:
        session = SessionsOrm(user_id=self.id, token=session_id, expiration=expiration)
        db.add(session)
        db.commit()
        return session.token

class VolunteerApplicationsOrm(Base):
    __tablename__ = 'volunteer_applications'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False) # todo cascade delete
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[bool] = mapped_column(default=False)
    message: Mapped[Str2048] = mapped_column(nullable=True)

    user: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="volunteer_application")

class SessionsOrm(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False) # todo cascade delete
    token: Mapped[UUID] = mapped_column(unique=True, nullable=False)
    expiration: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="sessions")

class AdoptionStatus(enum.Enum):
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'

    @classmethod
    def get_adoption_statuses(cls) -> list[Self]:
        return [status for status in cls]

class AdoptionRequestsOrm(Base):
    __tablename__ = 'adoption_requests'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False) # todo cascade delete
    animal_id: Mapped[int] = mapped_column(ForeignKey('animals.id'), nullable=False) # todo cascade delete
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[AdoptionStatus] = mapped_column(default=AdoptionStatus.pending)

    user: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="adoption_requests")
    animal: Mapped["AnimalsOrm"] = relationship("AnimalsOrm", back_populates="adoption_requests")

class AnimalStatus(enum.Enum):
    available = 'available'
    quarantine = 'quarantine'
    adopted = 'adopted'
    deceased = 'deceased'

    @classmethod
    def get_animal_statuses(cls) -> list[Self]:
        return [status for status in cls]

class AnimalsOrm(Base):
    __tablename__ = 'animals'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Str256] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column()
    species: Mapped[Str256] = mapped_column()
    photo: Mapped[bytes] = mapped_column(LargeBinary(length=2**24-1), nullable=True)
    description: Mapped[Str2048] = mapped_column()
    status: Mapped[AnimalStatus] = mapped_column(default=AnimalStatus.available)
    hidden: Mapped[bool] = mapped_column(default=False)

    medical_history: Mapped["MedicalHistoriesOrm"] = relationship("MedicalHistoriesOrm", back_populates="animal")
    scheduled_walks:  Mapped[list["WalksOrm"]] = relationship("WalksOrm", back_populates="animal")
    adoption_requests: Mapped[list["AdoptionRequestsOrm"]] = relationship("AdoptionRequestsOrm", back_populates="animal")

class WalksOrm(Base):
    __tablename__ = 'walks'

    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey('animals.id'), nullable=False) # todo cascade delete
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False) # todo cascade delete
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    location: Mapped[Str256] = mapped_column()

    animal: Mapped["AnimalsOrm"] = relationship("AnimalsOrm", back_populates="scheduled_walks")

class MedicalHistoriesOrm(Base):
    __tablename__ = 'medical_histories'

    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey('animals.id'), nullable=False) # todo cascade delete
    start_date:Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Str2048] = mapped_column()

    animal: Mapped["AnimalsOrm"] = relationship("AnimalsOrm", back_populates="medical_history")

    treatments: Mapped[list["TreatmentsOrm"]] = relationship("TreatmentsOrm", back_populates="medical_history")
    vaccinations: Mapped[list["VaccinationsOrm"]] = relationship("VaccinationsOrm", back_populates="medical_history")

class TreatmentsOrm(Base):
    __tablename__ = 'treatments'

    id: Mapped[int] = mapped_column(primary_key=True)
    medical_history_id: Mapped[int] = mapped_column(ForeignKey('medical_histories.id'), nullable=False) # todo cascade delete
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Str2048] = mapped_column()

    medical_history: Mapped["MedicalHistoriesOrm"] = relationship("MedicalHistoriesOrm", back_populates="treatments")

class VaccinationsOrm(Base):
    __tablename__ = 'vaccinations'

    id: Mapped[int] = mapped_column(primary_key=True)
    medical_history_id: Mapped[int] = mapped_column(ForeignKey('medical_histories.id'), nullable=False) # todo cascade delete
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Str2048] = mapped_column()

    medical_history: Mapped["MedicalHistoriesOrm"] = relationship("MedicalHistoriesOrm", back_populates="vaccinations")


