from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select
from starlette import status

from api.utils.exceptions import is_found_check
from api.auth.routers import fastapi_users
from api.chat.connect_manager import connect_manager
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Chat, Message, UserChat
from db.session import get_async_session
from api.chat.schemes import ChatCreate, ChatRead, UserRead, MessageRead, MessageCreate

chat_api = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@chat_api.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket,
                             db: AsyncSession = Depends(get_async_session),
                             user: User = Depends(fastapi_users.current_user(active=True, verified=True))):
    await connect_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await connect_manager.send_personal_message(f"You wrote: {data}", websocket)
            await connect_manager.broadcast(f"Client #{user.id} says: {data}")
    except WebSocketDisconnect:
        connect_manager.disconnect(websocket)
        await connect_manager.broadcast(f"Client #{user.id} has left the chat")


@chat_api.post("/message/", status_code=status.HTTP_201_CREATED)
async def create_message(message: MessageCreate,
                         db: AsyncSession = Depends(get_async_session),
                         user: User = Depends(fastapi_users.current_user(active=True, verified=True))):
    message_db = Message(**message.__dict__, user_id=user.id)
    db.add(message_db)
    await db.commit()
    print(message_db.__dict__)


@chat_api.post("", response_model=ChatRead)
async def create_chat(chat_info: ChatCreate,
                      db: AsyncSession = Depends(get_async_session),
                      user: User = Depends(fastapi_users.current_user(active=True, verified=True))):
    chat = Chat()
    db.add(chat)
    await db.flush()
    db.add(UserChat(chat_id=chat.id, user_id=user.id))
    for user_id in chat_info.users:
        db.add(UserChat(chat_id=chat.id, user_id=user_id))
    await db.commit()
    await db.refresh(chat)
    return ChatRead(chat_id=chat.id,
                    chat_users=[UserRead(**user.__dict__, user_role=user.role.value) for user in chat.users],
                    chat_messages=[MessageRead(**message.__dict__) for message in chat.messages])


@chat_api.get("/{chat_id}", response_model=ChatRead)
async def get_chat(chat_id: UUID,
                   db: AsyncSession = Depends(get_async_session),
                   user: User = Depends(fastapi_users.current_user(active=True, verified=True))):
    query = select(Chat).where(Chat.id == chat_id)
    chat = await db.scalar(query)
    is_found_check(chat)
    print(chat.__dict__)
    return ChatRead(chat_id=chat.id,
                    chat_users=[UserRead(**user.__dict__, user_role=user.role.value) for user in chat.users],
                    chat_messages=[MessageRead(**message.__dict__) for message in chat.messages])


@chat_api.get("/user_chats/")
async def get_user_chats(user: User = Depends(fastapi_users.current_user(active=True, verified=True))):
    chats = user.chats
    print([chat.__dict__ for chat in chats])
    return [chat.id for chat in chats]
