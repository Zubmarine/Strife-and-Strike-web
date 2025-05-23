import logging
import json
import uuid
from aiohttp import web
from typing import Optional, Dict, Any

from .manager import GameManager
from .events import GameEvent, GameEventType
from .session import GameSession

class GameServer:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.manager = GameManager(
            max_sessions=self.config.get('max_sessions', 100)
        )
        self.logger = logging.getLogger('GameServer')
    
    async def websocket_handler(self, request):
        """WebSocket处理器"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        session_id = str(uuid.uuid4())
        session = await self.manager.create_session(session_id)
        
        if not session:
            await ws.close()
            return ws
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    message = json.loads(msg.data)
                    response = await self.handle_client_message(session_id, message)
                    await ws.send_str(json.dumps(response))
                elif msg.type == web.WSMsgType.ERROR:
                    self.logger.error("WebSocket连接错误")
                    
        finally:
            await self.manager.end_session(session_id)
            await ws.close()
            
        return ws
        
    async def handle_client_message(self, 
                                  session_id: str, 
                                  message: dict) -> Dict[str, Any]:
        """处理客户端消息"""
        try:
            session = await self._get_or_create_session(session_id)
            if not session:
                return {"error": "会话创建失败"}
                
            event = self._create_event_from_message(message)
            await session.process_event(event)
            
            return {"success": True}
            
        except Exception as e:
            self.logger.error(f"消息处理失败: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def _get_or_create_session(self, session_id: str) -> Optional[GameSession]:
        """获取或创建游戏会话"""
        session = self.manager.sessions.get(session_id)
        if not session:
            session = await self.manager.create_session(session_id)
        return session
    
    def _create_event_from_message(self, message: dict) -> GameEvent:
        """从消息创建游戏事件"""
        event_type = GameEventType[message.get("event_type", "UNKNOWN")]
        data = message.get("data", {})
        return GameEvent(event_type=event_type, data=data)