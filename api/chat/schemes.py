from datetime import datetime
from typing import List
from uuid import UUID

from api.user.schemes import UserRead
from pydantic import BaseModel


class MessageRead(BaseModel):
    user_id: UUID
    body: str
    created_at: datetime


class ChatCreate(BaseModel):
    users: List[UUID]


class ChatRead(BaseModel):
    chat_id: UUID
    chat_users: List[UserRead]
    chat_messages: List[MessageRead]

