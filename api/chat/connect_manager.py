from typing import List, Dict
from uuid import UUID

from fastapi import WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Message
from db.session import get_async_session


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID:List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        # if chat_id not in self.active_connections.keys():
        #     self.active_connections[chat_id] = []
        # self.active_connections[chat_id].append(websocket)

    def disconnect(self, websocket: WebSocket):
        for chat_id in self.active_connections.keys():
            if websocket in self.active_connections[chat_id]:
                self.active_connections[chat_id].remove(websocket)
                return chat_id
        # print([web for web in self.active_connections.values()])
        # websocket_list = [web for web in self.active_connections.values()]
        # id_list = list(self.active_connections.keys())
        # pos = websocket_list.index(websocket)
        # id = id_list[pos]
        # del self.active_connections[id]
        # return id

    async def broadcast(self, data: str,
                        user_id: UUID,
                        chat_id: UUID,
                        db: AsyncSession):
        print(data, "DATA!!!!!!!!!!!!!!!!!!")
        for connection in self.active_connections[chat_id]:
            print(connection)
            message = Message(user_id=user_id, chat_id=chat_id, body=data)
            db.add(message)
            print(message.__dict__)
            await db.commit()
            print(message.__dict__)
            await connection.send_text(data)

    def add_chat(self, chat_id: UUID) -> None:
        if chat_id not in self.active_connections.keys():
            self.active_connections[chat_id] = []

    def append_chat_connection(self, chat_id: UUID, websocket: WebSocket):
        chat = self.active_connections[chat_id]
        if websocket not in chat:
            self.active_connections[chat_id].append(websocket)

    async def connect_room(self, chat_id: UUID, websocket: WebSocket) -> List[WebSocket]:
        chat = self.active_connections[chat_id]
        await self.connect(websocket)
        return chat


connect_manager = ConnectionManager()
