from dataclasses import dataclass, field
from typing import Dict, Optional, List, Set
from collections import deque

from .core import GameCore
from .character import Character

@dataclass
class GameState:
    id: Optional[str] = None
    current_round: int = 0
    current_turn_index: int = 0
    current_turn: Optional[str] = None
    logs: List[Dict] = field(default_factory=list)

    character_selected: List[str] = field(default_factory=list)
    deck: deque = field(default_factory=deque)
    skill_deck: deque = field(default_factory=deque)

    players: Dict[str, Character] = field(default_factory=dict)
    player_in_order: List[str] = field(default_factory=list)
    is_team_system_active: bool = False
    if is_team_system_active:
        teams: Set[Dict[str, int]] = field(default_factory=dict)
    

    async def log(self, message: str):
        """日志"""
        self.logs.append(message)
        print(f"[GameState Log]: {message}")

    def __init__(self, core: GameCore):
        self.core = core
        self.players = {}
        self.current_turn = None
    
    async def process_turn(self):
        # 通过core访问其他组件
        await self.core.combat_system.process_combat()