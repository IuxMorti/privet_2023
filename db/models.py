import datetime
import uuid

import sqlalchemy as alchemy
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass

# пример
class User(SQLAlchemyBaseUserTableUUID, Base):
    id: Mapped[uuid.UUID] = mapped_column(alchemy.UUID, primary_key=True, default=uuid.uuid4)
    url_photo: Mapped[str] = mapped_column(alchemy.String, nullable=True)
    username: Mapped[str] = mapped_column(alchemy.String(length=127), nullable=False)
    register_date: Mapped[datetime.datetime] = mapped_column(alchemy.TIMESTAMP, default=datetime.datetime.utcnow)

    videos = relationship("Video", back_populates="user", cascade="all, delete")
    comments = relationship("Comment", back_populates="user", cascade="all, delete")
