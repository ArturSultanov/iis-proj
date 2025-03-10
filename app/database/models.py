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

    @classmethod
    def get_roles(cls) -> list[Self]:
        return [role for role in cls]


class UsersOrm(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Str256] = mapped_column()
    username: Mapped[Str256] = mapped_column(unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary(length=2 ** 10), nullable=False)
    role: Mapped[Role] = mapped_column(default=Role.registered)
    disabled: Mapped[bool] = mapped_column(default=False)

    sessions: Mapped[list["SessionsOrm"]] = (
        relationship("SessionsOrm", back_populates="user", cascade="all, delete"))
    adoption_requests: Mapped[list["AdoptionRequestsOrm"]] = (
        relationship("AdoptionRequestsOrm", back_populates="user", cascade="all, delete"))
    volunteer_application: Mapped["VolunteerApplicationsOrm"] = (
        relationship("VolunteerApplicationsOrm", back_populates="user", cascade="all, delete"))
    walks: Mapped[list["WalksOrm"]] = (  # New Relationship
        relationship("WalksOrm", back_populates="user", cascade="all, delete"))

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

    @property
    def is_registered(self) -> bool:
        return self.role == Role.registered or self.is_admin

    def add_session(self, db: Session, session_id: UUID, expiration: datetime) -> UUID:
        session = SessionsOrm(user_id=self.id, token=session_id, expiration=expiration)
        db.add(session)
        db.commit()
        return session.token


class ApplicationStatus(enum.Enum):
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'

    @classmethod
    def get_application_statuses(cls) -> list[Self]:
        return [status for status in cls]


class VolunteerApplicationsOrm(Base):
    __tablename__ = 'volunteer_applications'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(default=ApplicationStatus.pending, nullable=False)
    message: Mapped[Str2048] = mapped_column(nullable=False)

    user: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="volunteer_application")


class SessionsOrm(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
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
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    animal_id: Mapped[int] = mapped_column(ForeignKey('animals.id'), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[AdoptionStatus] = mapped_column(default=AdoptionStatus.pending)
    message: Mapped[Str2048] = mapped_column(nullable=True)

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
    photo: Mapped[bytes] = mapped_column(LargeBinary(length=2 ** 24 - 1), nullable=True)
    description: Mapped[Str2048] = mapped_column()
    status: Mapped[AnimalStatus] = mapped_column(default=AnimalStatus.available)
    hidden: Mapped[bool] = mapped_column(default=False)

    medical_history: Mapped["MedicalHistoriesOrm"] = (
        relationship("MedicalHistoriesOrm", back_populates="animal", cascade="all, delete"))
    scheduled_walks: Mapped[list["WalksOrm"]] = (
        relationship("WalksOrm", back_populates="animal", cascade="all, delete"))
    adoption_requests: Mapped[list["AdoptionRequestsOrm"]] = (
        relationship("AdoptionRequestsOrm", back_populates="animal", cascade="all, delete"))
    vet_requests: Mapped[list["VetRequestOrm"]] = (
        relationship("VetRequestOrm", back_populates="animal", cascade="all, delete"))


class WalkStatus(enum.Enum):
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'
    started = 'started'
    finished = 'finished'
    cancelled = 'cancelled'


class WalksOrm(Base):
    __tablename__ = 'walks'

    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey('animals.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    location: Mapped[Str256] = mapped_column()
    status: Mapped[WalkStatus] = mapped_column(default=WalkStatus.pending)

    animal: Mapped["AnimalsOrm"] = relationship("AnimalsOrm", back_populates="scheduled_walks")
    user: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="walks")


class MedicalHistoriesOrm(Base):
    __tablename__ = 'medical_histories'

    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey('animals.id'), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Str2048] = mapped_column()

    animal: Mapped["AnimalsOrm"] = relationship("AnimalsOrm", back_populates="medical_history")

    treatments: Mapped[list["TreatmentsOrm"]] = (
        relationship("TreatmentsOrm", back_populates="medical_history", cascade="all, delete"))
    vaccinations: Mapped[list["VaccinationsOrm"]] = (
        relationship("VaccinationsOrm", back_populates="medical_history", cascade="all, delete"))
    # notes: Mapped[list["MedicalHistoryNotesOrm"]] = (
    #     relationship("MedicalHistoryNotesOrm", back_populates="medical_history", cascade="all, delete"))


# class MedicalHistoryNotesOrm(Base):
#     __tablename__ = 'medical_history_notes'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     medical_history_id: Mapped[int] = mapped_column(ForeignKey('medical_histories.id'),
#                                                     nullable=False)
#     date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
#     description: Mapped[Str2048] = mapped_column()
#
#     medical_history: Mapped["MedicalHistoriesOrm"] = relationship("MedicalHistoriesOrm", back_populates="notes")


class TreatmentsOrm(Base):
    __tablename__ = 'treatments'

    id: Mapped[int] = mapped_column(primary_key=True)
    medical_history_id: Mapped[int] = mapped_column(ForeignKey('medical_histories.id'),
                                                    nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Str2048] = mapped_column()

    medical_history: Mapped["MedicalHistoriesOrm"] = relationship("MedicalHistoriesOrm", back_populates="treatments")


class VaccinationsOrm(Base):
    __tablename__ = 'vaccinations'

    id: Mapped[int] = mapped_column(primary_key=True)
    medical_history_id: Mapped[int] = mapped_column(ForeignKey('medical_histories.id'),
                                                    nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Str2048] = mapped_column()

    medical_history: Mapped["MedicalHistoriesOrm"] = relationship("MedicalHistoriesOrm", back_populates="vaccinations")


class VetRequestStatus(enum.Enum):
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'completed'

    @classmethod
    def get_vet_request_statuses(cls) -> list[Self]:
        return [status for status in cls]


class VetRequestOrm(Base):
    __tablename__ = 'vet_requests'

    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey('animals.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Str2048] = mapped_column()
    status: Mapped[VetRequestStatus] = mapped_column(default=VetRequestStatus.pending)

    animal: Mapped["AnimalsOrm"] = relationship("AnimalsOrm", back_populates="vet_requests")
    user: Mapped["UsersOrm"] = relationship("UsersOrm")
