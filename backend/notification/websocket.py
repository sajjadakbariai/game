# backend/notification/websocket.py
from fastapi import WebSocket, WebSocketDisconnect, status
from typing import Dict, List
import uuid
import json
import asyncio
from ..core import auth, models
from ..core.database import Session
from ..core.config import settings

class ConnectionManager:
    """مدیریت اتصالات WebSocket"""
    
    def __init__(self):
        self.active_connections: Dict[uuid.UUID, WebSocket] = {}
        self.user_connections: Dict[uuid.UUID, List[uuid.UUID]] = {}
        self.connection_user_map: Dict[uuid.UUID, uuid.UUID] = {}
    
    async def connect(self, websocket: WebSocket, user_id: uuid.UUID, connection_id: uuid.UUID):
        """اتصال جدید WebSocket"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.connection_user_map[connection_id] = user_id
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
    
    def disconnect(self, connection_id: uuid.UUID):
        """قطع اتصال WebSocket"""
        if connection_id in self.active_connections:
            user_id = self.connection_user_map[connection_id]
            self.user_connections[user_id].remove(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
            del self.connection_user_map[connection_id]
            del self.active_connections[connection_id]
    
    async def send_personal_message(self, message: dict, user_id: uuid.UUID):
        """ارسال پیام به کاربر خاص"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_json(message)
                    except:
                        self.disconnect(connection_id)
    
    async def broadcast(self, message: dict):
        """ارسال پیام به تمام اتصالات فعال"""
        for connection_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_json(message)
            except:
                self.disconnect(connection_id)

manager = ConnectionManager()

async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session
):
    """Endpoint اصلی WebSocket"""
    try:
        # احراز هویت کاربر
        user = await auth.get_current_user_from_token(token, db)
        connection_id = uuid.uuid4()
        
        # اتصال به سیستم
        await manager.connect(websocket, user.id, connection_id)
        
        # ارسال پیام خوش‌آمدگویی
        await manager.send_personal_message({
            "type": "connection_established",
            "message": "WebSocket connection established",
            "user_id": str(user.id)
        }, user.id)
        
        # حلقه دریافت پیام‌ها
        while True:
            try:
                data = await websocket.receive_json()
                await handle_websocket_message(data, user, db)
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    except HTTPException as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Exception as e:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        manager.disconnect(connection_id)

async def handle_websocket_message(data: dict, user: models.User, db: Session):
    """پردازش پیام‌های دریافتی از WebSocket"""
    message_type = data.get("type")
    
    if message_type == "ping":
        await manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }, user.id)
    
    elif message_type == "subscribe":
        # TODO: پیاده‌سازی سیستم subscribe به رویدادها
        await manager.send_personal_message({
            "type": "subscribed",
            "channels": data.get("channels", []),
            "message": "Successfully subscribed to channels"
        }, user.id)
    
    elif message_type == "unsubscribe":
        # TODO: پیاده‌سازی سیستم unsubscribe از رویدادها
        await manager.send_personal_message({
            "type": "unsubscribed",
            "channels": data.get("channels", []),
            "message": "Successfully unsubscribed from channels"
        }, user.id)
    
    else:
        await manager.send_personal_message({
            "type": "error",
            "message": "Unknown message type"
        }, user.id)

async def notify_user(user_id: uuid.UUID, message: dict):
    """ارسال نوتیفیکیشن به کاربر خاص"""
    await manager.send_personal_message({
        "type": "notification",
        "timestamp": datetime.utcnow().isoformat(),
        **message
    }, user_id)

async def broadcast_system_message(message: dict):
    """ارسال پیام سیستمی به تمام کاربران"""
    await manager.broadcast({
        "type": "system_message",
        "timestamp": datetime.utcnow().isoformat(),
        **message
    })
