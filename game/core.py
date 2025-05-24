from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class GameCore:
    """游戏核心组件容器，用于解决循环依赖"""
    state: Any = None  # 将在运行时设置具体类型
    combat_system: Any = None
    event_dispatcher: Any = None
    session_manager: Any = None
    character: Any = None
    trait: Any = None
    card: Any = None
    
    # 用于存储共享数据
    shared_data: Dict[str, Any] = field(default_factory=dict)

    def __init__(self):
        self._initialize()
    
    def _initialize(self):
        """初始化核心组件"""
        from .state import GameState
        from .combat import CombatSystem
        from .events import EventDispatcher, GameEventType
        from .manager import GameManager
        from .character import Character
        from .traits import TraitManager
        from .cards import Card
        
        self.event_dispatcher = EventDispatcher()
        self.event_type = GameEventType()
        self.state = GameState(core=self)
        self.combat_system = CombatSystem(core=self)
        self.session_manager = GameManager(core=self)
        self.character = Character(core=self)
        self.trait = TraitManager()
        self.card = Card(core=self)