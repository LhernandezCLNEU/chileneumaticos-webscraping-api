from typing import List
import json

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        try:
            self.active.remove(websocket)
        except ValueError:
            pass

    async def send_personal(self, websocket: WebSocket, message: dict) -> None:
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict) -> None:
        text = json.dumps(message)
        for conn in list(self.active):
            try:
                await conn.send_text(text)
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass


manager = ConnectionManager()
