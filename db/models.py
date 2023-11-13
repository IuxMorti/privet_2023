import datetime
import uuid

import sqlalchemy as alchemy
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import ForeignKey, UniqueConstraint, Table, Column
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


user_language_level = Table("user_language_level", Base.metadata,
                            Column("user_id", alchemy.UUID, ForeignKey("user.id")),
                            Column("language_level_id", alchemy.UUID, ForeignKey("language_level.id"))
                            )

student_arrival = Table("student_arrival", Base.metadata,
                        Column("student_id", alchemy.UUID, ForeignKey("user.id")),
                        Column("arrival_id", alchemy.UUID, ForeignKey("arrival.id"))
                        )

buddy_arrival = Table("buddy_arrival", Base.metadata,
                      Column("buddy_id", alchemy.UUID, ForeignKey("user.id")),
                      Column("arrival_id", alchemy.UUID, ForeignKey("arrival.id"))
                      )


# пример
class User(SQLAlchemyBaseUserTableUUID, Base):
    # Общее
    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(alchemy.String(length=127), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, ForeignKey("role.id"), nullable=False)
    url_photo: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    birthdate: Mapped[datetime.date] = mapped_column(alchemy.DATE, nullable=True)
    institute: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    native_language: Mapped[str] = mapped_column(alchemy.String(length=30), nullable=True)
    # ИС
    citizenship: Mapped[str] = mapped_column(alchemy.String(length=100), nullable=True)
    gender: Mapped[str] = mapped_column(alchemy.String(length=10), nullable=True)
    payment_status: Mapped[bool] = mapped_column(alchemy.Boolean, default=False)
    study_direction: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    visa_end_date: Mapped[datetime.date] = mapped_column(alchemy.DATE, nullable=True)
    living_place: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    # Buddy
    city: Mapped[str] = mapped_column(alchemy.String(length=100), nullable=True)
    buddy_active: Mapped[bool] = mapped_column(alchemy.Boolean, default=False)

    role = relationship("Role", back_populates="users")
    languages_level = relationship("LanguageLevel", secondary=user_language_level, back_populates="user")


class LanguageLevel(Base):
    __tablename__ = "language_level"
    __table_args__ = (UniqueConstraint('language', 'level'),)

    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    language: Mapped[str] = mapped_column(alchemy.String(length=30), nullable=False)
    level: Mapped[str] = mapped_column(alchemy.String(length=2), nullable=False)

    user = relationship("User", secondary=user_language_level, back_populates="languages_level")


class Role(Base):
    __tablename__ = "role"

    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(alchemy.String(length=130), nullable=False, unique=True)

    users = relationship("User", back_populates="role", cascade="all, delete")


class Arrival(Base):
    __tablename__ = "arrival"

    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    date_time: Mapped[datetime.datetime] = mapped_column(alchemy.TIMESTAMP, nullable=False)
    flight_number: Mapped[str] = mapped_column(alchemy.String, nullable=False)
    point: Mapped[str] = mapped_column(alchemy.String, nullable=False)
    url_ticket: Mapped[str] = mapped_column(alchemy.String, nullable=False)
    comment: Mapped[str] = mapped_column(alchemy.String, nullable=True)

    students = relationship("User", secondary=student_arrival, backref="arrival")
    buddy = relationship("User", secondary=buddy_arrival, back_populates="arrival")


class Task(Base):
    __tablename__ = "task"

    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(alchemy.String(length=130), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(alchemy.String, nullable=True)
