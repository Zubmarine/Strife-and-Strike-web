import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta

from .session import GameSession

class GameManager:
    def __init__(self, max_sessions: int = 100):
        self.sessions: Dict[str, GameSession] = {}
        self.session_semaphore = asyncio.Semaphore(max_sessions)
        self.cleanup_task = None
    
    async def create_session(self, session_id: str) -> Optional[GameSession]:
        """创建新的游戏会话"""
        if not await self.session_semaphore.acquire():
            return None
            
        if session_id in self.sessions:
            self.session_semaphore.release()
            return None
            
        try:
            session = GameSession(session_id)
            self.sessions[session_id] = session
            asyncio.create_task(session.run())
            return session
        except Exception:
            self.session_semaphore.release()
            return None
            
    async def end_session(self, session_id: str):
        """结束游戏会话"""
        if session := self.sessions.get(session_id):
            await session.cleanup()
            del self.sessions[session_id]
            self.session_semaphore.release()
            
    async def cleanup_inactive_sessions(self):
        """清理不活跃的会话"""
        while True:
            now = datetime.now()
            expired_sessions = [
                sid for sid, session in self.sessions.items()
                if now - session.created_at > timedelta(hours=1)  # 1小时超时
            ]
            for sid in expired_sessions:
                await self.end_session(sid)
            await asyncio.sleep(300)  # 每5分钟检查一次
