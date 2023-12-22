from uuid import UUID
from typing import List

from sqlalchemy import select

from db.models import Chat
from db.session import AsyncSession


async def create_chat(users_id: List[UUID], db: AsyncSession):
    chat = {"users": users_id}
    res_chat = Chat(**chat)
    db.add(res_chat)
    await db.commit()
    await db.refresh(res_chat)


async def get_chat(chat_id: UUID, db: AsyncSession):
    query = select(Chat).where(Chat.id == chat_id)
    return await db.scalars(query)
