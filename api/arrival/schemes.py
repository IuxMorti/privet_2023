import uuid
import datetime
from typing import Union, Optional

from pydantic import BaseModel


class ArrivalCreate(BaseModel):
    date_time: datetime.datetime
    flight_number: str
    point: str
    url_ticket: str
    students: Optional[list[uuid.UUID]]


class ArrivalRead(BaseModel):
    id: uuid.UUID
    date_time: datetime.datetime
    flight_number: str
    point: str
    url_ticket: str
    # students: Optional[list[uuid.UUID]]
