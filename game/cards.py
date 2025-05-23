from dataclasses import dataclass
from typing import List, Callable, Optional
from .events import GameEventType

@dataclass
class Card:
    id: str
    name: str
    description: str
    effects: List[Callable]
    
    async def play(self, game_state, player_id):
        pass