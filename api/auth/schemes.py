import typing
import uuid
from typing import Optional

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate
from pydantic import EmailStr

from db.models import Role


class UserRead(BaseUser[uuid.UUID]):
    full_name: str
    url_photo: typing.Union[str, None]


class UserCreate(BaseUserCreate):
    full_name: str
    password: str
    email: EmailStr
    role: Role


class UserUpdate(BaseUserUpdate):
    full_name: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]
