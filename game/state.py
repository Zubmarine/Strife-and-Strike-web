from dataclasses import dataclass, field
from typing import Dict, Optional, List
from collections import deque

from .events import EventDispatcher
from .combat import CombatSystem
from .character import Character

@dataclass
class GameState:
    id: Optional[str] = None
    players: Dict[str, Character] = field(default_factory=dict)
    deck: deque = field(default_factory=deque)
    current_turn: Optional[str] = None
    logs: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        self.dispatcher = EventDispatcher()
        self.combat_system = CombatSystem(self)

    async def log(self, message: str):
        """Log a message for the game."""
        self.logs.append(message)
        print(f"[GameState Log]: {message}")