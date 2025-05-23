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
        self._initialize()
    
    def _initialize(self):
        """初始化游戏状态"""
        self._register_core_events()
        
    async def update(self):
        """更新游戏状态"""
        if self.current_turn:
            await self._update_current_player()
            
    async def update(self):
        """更新游戏状态"""
        # 实现游戏状态更新逻辑
        pass

    async def log(self, message: str):
        """Log a message for the game."""
        self.logs.append(message)
        print(f"[GameState Log]: {message}")  # Optional: Print to console for debugging

    def initialize_deck(self):
        pass

    async def _on_pre_attack(self, data):
        # 处理攻击前事件
        pass

    async def _on_damage_calc(self, data):
        # 处理伤害计算事件
        pass

    async def _on_dice_roll(self, data):
        # 处理骰子判定事件
        pass