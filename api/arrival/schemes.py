import uuid
import datetime
from typing import Union, Optional

from pydantic import BaseModel
from db import models


class UserRead(BaseModel):
    id: uuid.UUID
    full_name: str


class ArrivalCreate(BaseModel):
    date_time: datetime.datetime
    flight_number: str
    point: str
    url_ticket: str
    comment: Optional[str]
    students: Optional[list[uuid.UUID]]


class ArrivalRead(BaseModel):
    id: uuid.UUID
    date_time: datetime.datetime
    number: str
    flight_number: str
    point: str
    url_ticket: str
    comment: Optional[str]
    status: models.ArrivalStatus
    citizenship: list[str]
    arrival_students: list[UserRead]
    arrival_buddies: list[UserRead]
