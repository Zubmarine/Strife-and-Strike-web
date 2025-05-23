from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class GameCore:
    """游戏核心组件，用于解决循环依赖"""
    state: Any = None
    combat: Any = None
    event_dispatcher: Any = None