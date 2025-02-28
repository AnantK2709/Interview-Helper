from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Dict, List

class WebRTCConnection:
    def __init__(self, websocket: WebSocket, user_id: str):
        self.websocket = websocket
        self.user_id = user_id
        self.is_active = True

class WebRTCService:
    def __init__(self):
        self.active_connections: Dict[str, WebRTCConnection] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = WebRTCConnection(websocket, user_id)
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].is_active = False
            del self.active_connections[user_id]
    
    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].websocket.send_json(message)
    
    async def broadcast(self, message: dict, exclude: List[str] = None):
        exclude = exclude or []
        for user_id, connection in self.active_connections.items():
            if user_id not in exclude:
                await connection.websocket.send_json(message)