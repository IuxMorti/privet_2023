from typing import List, Dict
from uuid import UUID

from fastapi import WebSocket


class Connection:
    def __init__(self, user_id: UUID, websocket: WebSocket):
        self.user_id = user_id
        self.websocket = websocket


class ConnectionManager:

    def __init__(self) -> None:
        self.active_connections: Dict[UUID:List[Connection]] = {}

    async def connect(self, chat_id: UUID, connection: Connection):
        await connection.websocket.accept()
        if chat_id not in self.active_connections.keys():
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(connection)

    def disconnect(self, chat_id: UUID, connection: Connection):
        self.active_connections[chat_id].remove(connection)

    async def send_personal_message(self, message: str, connection: Connection):
        await connection.websocket.send_text('user_id ' + str(connection.user_id) + ': ' + message)

    async def broadcast(self, chat_id: UUID, message: str):
        for connection in self.active_connections[chat_id]:
            await connection.websocket.send_text(message)


connect_manager = ConnectionManager()
