import datetime
import typing
import uuid
from typing import Optional

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel, BaseUser
from pydantic import EmailStr


class UserRead(BaseUser[uuid.UUID]):
    full_name: str
    url_photo: typing.Union[str, None]


class UserCreate(CreateUpdateDictModel):
    full_name: str
    password: str
    email: EmailStr
    role_id: uuid.UUID


class UserUpdate(CreateUpdateDictModel):
    full_name: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]
