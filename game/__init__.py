#
# -*- coding: UTF-8 -*-
# @project Strife-and-Strike_web
# @file __init__.py
#

"""
Module for main game progress
主游戏逻辑模块，包含核心游戏系统组件
"""

__version__ = '0.1.0'
__author__ = 'Zubmarine & Icecube'

# 导出核心组件
from .events import GameEvent, GameEventType, EventDispatcher
from .state import GameState
from .session import GameSession
from .manager import GameManager
from .server import GameServer
from .combat import CombatSystem
from .cards import Card
from .character import Character
from .traits import Trait

__all__ = [
    'GameEvent',
    'GameEventType',
    'EventDispatcher',
    'GameState',
    'GameSession',
    'GameManager',
    'GameServer',
    'CombatSystem',
    'Card',
    'Character',
    'Trait'
]

# 配置日志
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

def get_version():
    """返回当前版本号"""
    return __version__

