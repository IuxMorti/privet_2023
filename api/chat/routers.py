import json
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy import select

from api.utils.exceptions import is_found_check
from api.auth.routers import fastapi_users
from api.chat.connect_manager import connect_manager, Connection
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Chat, Message, UserChat
from db.session import get_async_session
from api.chat.schemes import ChatCreate, ChatRead, UserRead, MessageRead

from fastapi.responses import HTMLResponse

chat_api = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:6370/api/v1/chat/ws/783d6142-7a79-4005-9152-7825256796ee/fc08434d-9627-41fd-9222-db968f53141f");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@chat_api.get("/check_chat")
async def get():
    return HTMLResponse(html)


@chat_api.websocket("/ws/{chat_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket,
                             chat_id: UUID,
                             client_id: UUID,
                             db: AsyncSession = Depends(get_async_session)):
    connection = Connection(client_id, websocket)
    await connect_manager.connect(chat_id, connection)
    try:
        while True:
            data = await websocket.receive_text()
            message = Message(user_id=client_id, chat_id=chat_id, body=data)
            print(message.to_dict())
            await connect_manager.broadcast(chat_id, json.dumps(message.to_dict()))
            db.add(message)
            await db.commit()

    except WebSocketDisconnect:
        connect_manager.disconnect(chat_id, connection)


@chat_api.post("", response_model=ChatRead)
async def create_chat(chat_info: ChatCreate,
                      db: AsyncSession = Depends(get_async_session),
                      user: User = Depends(fastapi_users.current_user(active=True, verified=True))):
    query = select(Chat).where(Chat.users.any(User.id == user.id))
    chats = await db.scalars(query)
    for chat in chats:
        is_same_chat = True
        for user_id in chat_info.users:
            if user_id not in [user_in_chat.id for user_in_chat in chat.users]:
                is_same_chat = False
                break
        if is_same_chat:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'chat with such users already exists')

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
