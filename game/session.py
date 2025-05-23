import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .state import GameState
from .events import GameEvent

@dataclass
class GameSession:
    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    game_state: GameState = field(default_factory=GameState)
    event_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    
    def __post_init__(self):
        self.lock = asyncio.Lock()
        self.is_active = True
        self.logger = logging.getLogger(f"Session_{self.session_id}")