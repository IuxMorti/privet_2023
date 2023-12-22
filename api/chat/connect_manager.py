from uuid import UUID

from fastapi import WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Message
from db.session import get_async_session


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID:WebSocket] = {}

    async def connect(self, chat_id: UUID, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[chat_id] = websocket

    def disconnect(self, websocket: WebSocket):
        websocket_list = list(self.active_connections.values())
        id_list = list(self.active_connections.keys())
        pos = websocket_list.index(websocket)
        id = id_list[pos]
        del self.active_connections[id]
        return id

    async def send_personal_message(self, message: str, websocket: WebSocket):
        websocket.user()
        await websocket.send_text(message)

    async def broadcast(self, data: str,
                        user_id: UUID,
                        chat_id: UUID,
                        db: AsyncSession = Depends(get_async_session)):
        for connection in self.active_connections.values():
            message = Message(user_id=user_id, chat_id=chat_id, body=data)
            db.add(message)
            await db.commit()
            await connection.send_text(message)


connect_manager = ConnectionManager()
