#
# -*- coding: UTF-8 -*-
# @project Strife-and-Strike_web
# @file character.py
#

"""
None
"""

from dataclasses import dataclass
from enum import Enum
from typing import Set, List, Dict, Union



class Module(Enum):
    SUPPORTER = [1000,  80, 50]
    BALANCE = [1000, 95, 35]
    CHALLANGER = [1000, 105, 25]
    BEAST = [900, 125, 20]
    DEFENDER = [1000, 65, 65]
    HP = [1250, 75, 45]


class MPModule(Enum):
    HUMUS_HUMAN = [2, 1, 5]
    BEAST_CAT = [2, 1, 6]
    BEAST_SNOWFOX = [2, 1, 6]
    BEAST_GRIFFON = [3, 1, 4]
    BEAST_DRAGON = [3, 1, 6]
    BEAST_PIGEON = [2, 1, 4]
    BEAST_RAT = [3, 1, 3]
    CHIMERA_GRIFFONMAN = [3, 1, 5]
    CHIMERA_CATMAN = [2, 1, 6]
    CHIMERA_ARGON = [5, 2, 5]
    MACHINA_ROBOT = [10, 5, 10]
    MACHINA_CHARIOT = [-1, 0, 5]
    MACHINA_EXPER_CREATION = [2, 2, 4]
    MACHINA_PROGRAM = [0, 0, 4]
    TAMAKY_SOUL = [0, 1, 30]
    TAMAKY_GHOST = [-1, 0, 5]
    TAMAKY_BROKEN_SOUL = [1, 2, 20]
    ANGLO_AHHOLY_CREATION = [10, 3, 10]
    FERITRO_ELF = [2, 1, 8]
    LUXIV_MO = [4, 1, 7]
    LUXIV_TAIXI = [6, 2, 8]
    AGENT_ = [-1, 0, 5]


@dataclass
class Character():
    def __init__(self, player: str, module_type: str):
        self.player: str = player

        self.name: str = ""             # 角色名
        self.traits: Set[str] = {}      #
        self.is_alive: bool = True      #

        self.hp_max: int = Module[module_type].value[0]
        self.hp: int = self.hp_max
        self.attack: int = Module[module_type].value[1]
        self.defense: int = Module[module_type].value[2]

        self.mp_max: int = 0        #
        self.mp: int = 0            #
        self.mp_restore: int = 0    #
        self.mp_restore_cd: int = 0 #
        
        self.hand: List[str] = []   #
        self.skills: Set[str] = {}  #
        self.cooldowns: Dict[str, int] = {}                     #
        self.statuses: Dict[Dict[str, Union[int, bool]]] = {}   #

    

    async def trait(self, *args, **kwargs) -> None:
        pass

    def apply_status(self, effect: str, intensity: int, layer: int, decay: bool = True) -> None:
        pass


class CharacterList(Enum):
    yinzhu = ["茵竹", {Module.HP, MPModule.HUMUS_HUMAN}, {"SEFL_ENCOURAGING"}, [], ]