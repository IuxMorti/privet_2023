import datetime
from enum import Enum
import uuid

import sqlalchemy as alchemy
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Role(Enum):
    student = 'student'
    maintainer = 'maintainer'
    team_leader = 'team_leader'


class ArrivalStatus(Enum):
    active = 'active'
    completed = 'completed'
    awaiting_approval = 'awaiting_approval'


class StudentArrival(Base):
    __tablename__ = "student_arrival"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "arrival_id",
            name="idx_unique_student_arrival",
        ),)
    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, ForeignKey("user.id"), nullable=False)
    arrival_id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, ForeignKey("arrival.id"), nullable=False)


class BuddyArrival(Base):
    __tablename__ = "buddy_arrival"
    __table_args__ = (
        UniqueConstraint(
            "buddy_id",
            "arrival_id",
            name="idx_unique_buddy_arrival",
        ),)
    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    buddy_id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, ForeignKey("user.id"), nullable=False)
    arrival_id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, ForeignKey("arrival.id"), nullable=False)


class User(SQLAlchemyBaseUserTableUUID, Base):
    # Общее
    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(alchemy.String(length=127), nullable=False)
    role: Mapped[Role] = mapped_column(ENUM(Role, name='role_enum', create_type=False),
                                       nullable=False, default=Role.student)
    url_photo: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    sex: Mapped[str] = mapped_column(alchemy.String(length=10), nullable=True)
    birthdate: Mapped[datetime.date] = mapped_column(alchemy.DATE, nullable=True)
    university: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    native_language: Mapped[str] = mapped_column(alchemy.String(length=30), nullable=True)
    phone: Mapped[str] = mapped_column(alchemy.String(length=12), nullable=True)
    telegram: Mapped[str] = mapped_column(alchemy.String(length=32), nullable=True)
    whatsapp: Mapped[str] = mapped_column(alchemy.String(length=12), nullable=True)
    vk: Mapped[str] = mapped_column(alchemy.String(length=32), nullable=True)
    # ИС
    citizenship: Mapped[str] = mapped_column(alchemy.String(length=100), nullable=True)
    is_escort_paid: Mapped[bool] = mapped_column(alchemy.Boolean, default=False)
    study_program: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    last_visa_expiration: Mapped[datetime.date] = mapped_column(alchemy.DATE, nullable=True)
    accommodation: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    comment: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    # Buddy
    city: Mapped[str] = mapped_column(alchemy.String(length=100), nullable=True)
    is_confirmed_buddy: Mapped[bool] = mapped_column(alchemy.Boolean, default=False)

    languages_levels = relationship("LanguageLevel", back_populates="user", lazy="selectin", cascade="all, delete")
    tasks = relationship("Task", back_populates="student")
    student_arrivals = relationship("Arrival", secondary="student_arrival", back_populates="students")
    buddy_arrivals = relationship("Arrival", secondary="buddy_arrival", back_populates="buddies")


class LanguageLevel(Base):
    __tablename__ = "language_level"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "language",
            "level",
            name="idx_unique_user_language_level",
        ),)

    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, ForeignKey("user.id"), nullable=False)
    language: Mapped[str] = mapped_column(alchemy.String(length=30), nullable=False)
    level: Mapped[str] = mapped_column(alchemy.String(length=2), nullable=False)

    user = relationship("User", back_populates="languages_levels")


class Arrival(Base):
    __tablename__ = "arrival"

    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    number: Mapped[str] = mapped_column(alchemy.String(length=12), unique=True, nullable=False)
    date_time: Mapped[datetime.datetime] = mapped_column(alchemy.TIMESTAMP, nullable=False)
    flight_number: Mapped[str] = mapped_column(alchemy.String, nullable=False)
    point: Mapped[str] = mapped_column(alchemy.String, nullable=False)
    url_ticket: Mapped[str] = mapped_column(alchemy.String, nullable=False)
    comment: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    status: Mapped[ArrivalStatus] = mapped_column(ENUM(ArrivalStatus, name='status_enum', create_type=False),
                                                  nullable=False, default=ArrivalStatus.awaiting_approval)
    students = relationship("User", secondary="student_arrival", back_populates="student_arrivals", lazy="selectin")
    buddies = relationship("User", secondary="buddy_arrival", back_populates="buddy_arrivals", lazy="selectin")
    tasks = relationship("Task", back_populates="arrival", lazy="selectin")


class Task(Base):
    __tablename__ = "task"

    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, ForeignKey("user.id"), nullable=False)
    arrival_id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, ForeignKey("arrival.id"), nullable=False)
    title: Mapped[str] = mapped_column(alchemy.String(length=130), nullable=False)
    description: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    is_active: Mapped[bool] = mapped_column(alchemy.Boolean, default=True)
    deadline: Mapped[datetime.date] = mapped_column(alchemy.DATE, nullable=True)

    student = relationship("User", back_populates="tasks")
    arrival = relationship("Arrival", back_populates="tasks")
