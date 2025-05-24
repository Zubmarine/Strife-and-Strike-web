from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, DefaultDict
from datetime import datetime
import uuid

class GameEventType(Enum):
    # 系统事件
    REGISTER = auto()
    UNREGISTER = auto()
    
    # 游戏流程事件
    GAME_START = auto()
    GAME_END = auto()
    GAME_PAUSE = auto()
    GAME_RESUME = auto()
    GAME_RESTART = auto()
    

    # 玩家相关事件
    PLAYER_JOIN = auto()
    PLAYER_LEAVE = auto()
    PLAYER_READY = auto()
    PLAYER_UNREADY = auto()
    SKILL_APPEND = auto()
    SKILL_REMOVE = auto()

    # 角色相关事件
    CHARACTER_SELECT = auto()
    CHARACTER_UNSELECT = auto()
    CHARACTER_UPDATE = auto()
    CHARACTER_DEATH = auto()
    CHARACTER_REVIVE = auto()

    # 回合控制事件
    TURN_START = auto()
    TURN_END = auto()
    ROUND_CHANGE = auto()
    
    # 卡牌相关事件
    DRAW_CARD = auto()
    PLAY_CARD = auto()
    
    # 战斗相关事件
    DICE_ROLL = auto()
    PRE_ATTACK = auto()
    DAMAGE_CALC = auto()
    DAMAGE_APPLY = auto()
    
    # 治疗相关事件
    PRE_HEAL = auto()
    HEAL_CALC = auto()
    HEAL_APPLY = auto()
    
    # 资源相关事件
    MP_MODIFIED = auto()

    SKILL_USE = auto()
    SKILL_CANCEL = auto()
    SKILl_CD_MODIFIED = auto()


@dataclass
class GameEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))    # 事件id
    event_time: datetime = field(default_factory=datetime.now)          # 事件时间
    event_type: GameEventType                                   # 事件类型
    data: Dict[str, Any] = field(default_factory=dict)          # 事件数据
    cancel: bool = False                                    # 是否取消事件
    result: Dict[str, Any] = field(default_factory=dict)    # 事件结果
    error: Optional[str] = None                             # 错误信息  

    def set_error(self, error: str):
        """设置错误信息"""
        self.error = error
        self.cancel = True


class EventDispatcher:
    def __init__(self):
        self.listeners: Dict[GameEventType, List[Callable]] = DefaultDict(list)

    def add_listener(self, event_type: GameEventType, listener: Callable):
        self.listeners[event_type].append(listener)

    async def dispatch(self, event: GameEvent):
        for listener in self.listeners.get(event.event_type, []):
            await listener(event)