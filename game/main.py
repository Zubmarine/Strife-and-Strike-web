#
# -*- coding: UTF-8 -*-
# @project Strife-and-Strike_web
# @file main.py
#

"""
None
"""

import asyncio
import random
import logging

from collections import deque
from enum import Enum, auto
from typing import Tuple, Dict, List, Callable, Any
from dataclasses import dataclass

from character import Character


class GameEventType(Enum):
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


@dataclass
class GameEvent:
    def __init__(self, event_type: GameEventType, data: Dict[str, Any]):
        self.event_type: GameEventType = event_type
        self.data: Dict[str, Any] = data
        self.cancel: bool = False  # 用于取消事件的标志
        self.result: Dict[str, Any] = {}
        self.error: str = ""  # 错误信息


class EventDispatcher:
    def __init__(self):
        self.listeners: Dict[GameEventType, List[Tuple[Callable[[GameEvent], dict], int]]] = {}
        self.logger = logging.getLogger(__name__)

    async def fire_event(self, event: GameEvent, data: dict) -> dict:
        """触发事件并处理返回结果"""
        if event not in self.listeners:
            return data
            
        try:
            event = GameEvent(type=event, data=data)
            for callback, _ in self.listeners[event]:
                try:
                    result = await callback(event)
                    if isinstance(result, dict):
                        data.update(result)
                except Exception as e:
                    self.logger.error(f"事件处理器执行失败: {e}", exc_info=True)
            return data
        except Exception as e:
            self.logger.error(f"事件分发失败: {e}", exc_info=True)
            return data

    def add_listener(self, event: GameEventType, 
                    callback: Callable[[GameEvent], dict], 
                    priority: int = 0) -> None:
        """添加事件监听器"""
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append((callback, priority))
        self.listeners[event].sort(key=lambda x: x[1], reverse=True)


class GameState:
    def __init__(self):
        self.dispatcher = EventDispatcher()
        self.combat_system = None  # 将在初始化时设置
        self._initialize()
        
    def _initialize(self):
        self.logs = []
        self.id = None
        self.deck = deque()
        self.players: Dict[str, Character] = {}
        self.current_turn = None
        self._register_core_events()
        
    def _register_core_events(self):
        core_events = {
            GameEventType.PRE_ATTACK: self._on_pre_attack,
            GameEventType.DAMAGE_CALC: self._on_damage_calc,
            GameEventType.DICE_ROLL: self._on_dice_roll
        }
        
        for event_type, handler in core_events.items():
            self.dispatcher.add_listener(event_type, handler)
            
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



@dataclass
class Trait:
    def __init__(self, name: str, game_state: GameState = None):
        self.name = name
        self.game_state = game_state


class SelfEncouragement(Trait):
    def __init__(self, game_state: GameState = None):
        super().__init__("SelfEncouragement", game_state=game_state)
        game_state.dispatcher.add_listener(
            GameEventType.DAMAGE_APPLY, self.self_encouragement, priority=50)

    async def self_encouragement(self, event: GameEvent):
        """自勉特质的事件处理"""
        player = self.game_state.players.get(event.data.get("player"))
        if player.hp <= player.hp_max * 0.5 and player.hp > 0:
            await self.game_state.dispatcher.fire_event(
                GameEventType.HEAL_APPLY, {
                    'player': player,
                    'hp': player.hp_max * 0.8 - player.hp
                })
            await self.game_state.log(f"{player.name}的自勉触发，恢复5点生命值")
        return event


class CombatSystem:
    def __init__(self, game_state: GameState):
        self.state = game_state
    
    async def send_error(self, player_id: str, message: str):
        """发送错误消息"""
        error_event = {
            'player': player_id,
            'message': message
        }
        await self.state.dispatcher.fire_event(GameEventType.MP_MODIFIED, error_event)
    
    async def broadcast_state(self):
        """广播游戏状态"""
        state_event = {
            'players': {pid: player.__dict__ for pid, player in self.state.players.items()},
            'current_turn': self.state.current_turn
        }
        await self.state.dispatcher.fire_event(GameEventType.MP_MODIFIED, state_event)
        await self.state.log(f"Game state updated: {state_event}")
        
    async def execute_attack(self, attacker_id: str, defender_id: str):
        """执行攻击流程"""
        if not await self._validate_attack(attacker_id, defender_id):
            return
            
        roll_result = await self._perform_attack_roll(attacker_id)
        damage = await self._calculate_damage(attacker_id, defender_id, roll_result)
        await self._damage_apply(defender_id, damage)
        
    async def _validate_attack(self, attacker_id: str, defender_id: str) -> bool:
        pre_event = {
            'attacker': attacker_id,
            'defender': defender_id,
            'cancel': False
        }
        await self.state.dispatcher.fire_event(GameEventType.PRE_ATTACK, pre_event)
        if pre_event.get('cancel'):
            await self.state.log(f"{attacker_id}的攻击被取消")
            return False
        return True
        
    async def _perform_attack_roll(self, attacker_id: str) -> int:
        max_val = self.get_modified_dice_max(attacker_id)
        return await self.roll_dice(attacker_id, max_val=max_val)
        
    async def _calculate_damage(self, attacker_id: str, defender_id: str, roll_result: int) -> int:
        base_damage = roll_result * (
            self.state.players[attacker_id].attack -
            self.state.players[defender_id].defense
        )
        
        dmg_event = {
            'original': base_damage,
            'modified': base_damage,
            'source': attacker_id,
            'target': defender_id
        }
        await self.state.dispatcher.fire_event(GameEventType.DAMAGE_CALC, dmg_event)
        return max(0, dmg_event['modified'])

    async def roll_dice(self, player_id: str, min_val=1, max_val=4):
        """可观测的骰子判定"""
        roll = random.randint(min_val, max_val)
        
        # 触发骰子结果事件
        roll_event = {
            'player': player_id,
            'min': min_val,
            'max': max_val,
            'result': roll,
            'modified': roll
        }
        await self.state.dispatcher.fire_event(
            GameEventType.DICE_ROLL, roll_event)
        
        # 应用最终修改结果
        traits = self.state.players[player_id].traits
        if traits and isinstance(traits, list):
            for trait in traits:
                if hasattr(trait, 'modify_dice_max') and callable(trait.modify_dice_max):
                    base_max = trait.modify_dice_max(base_max)

    def get_modified_dice_max(self, player_id: str):
        """获取骰子上限（考虑特质影响）"""
        base_max = 4
        for trait in self.state.players[player_id].traits:
            base_max = trait.modify_dice_max(base_max)
        return base_max
    
    
    async def process_event(self, event: GameEventType):
        handler = {
            GameEventType.PLAY_CARD: self.handle_play_card,
            GameEventType.DRAW_CARD: self.handle_draw_card,
            GameEventType.TURN_END: self.handle_end_turn
        }.get(event)

        if handler:
            await handler(event)
    
    async def handle_draw_card(self, player_id: str, num_cards: int = 1):
        """处理抽牌事件"""
        player_state = self.state.players[player_id]
        if len(player_state.hand) + num_cards > 5:
            return await self.send_error(player_id, "Hand limit reached")

        drawn_cards = []
        for _ in range(num_cards):
            card = self.state.deck.popleft()
            player_state.hand.append(card)
            drawn_cards.append(card)

        await self.broadcast_state()
        await self.state.log(f"{player_id} drew cards: {drawn_cards}")
        await self.state.dispatcher.fire_event(GameEventType.DRAW_CARD, {'card': drawn_cards})

    async def handle_play_card(self, player_id: str, event: GameEventType):
        """处理出牌事件"""
        player_state = self.state.players[player_id]
        card = event.data['card']
        
        if card not in player_state.hand:
            return await self.send_error(player_id, "Invalid card")

        if self.state.current_turn != player_id:
            return await self.send_error(player_id, "Not your turn")

        # 执行出牌逻辑
        player_state.hand.remove(card)
        await self.broadcast_state()
        await self.state.log(f"{player_id} played {card}")
        await self.state.dispatcher.fire_event(GameEventType.PLAY_CARD, event.data)
    
    async def _damage_apply(self, defender_id: str, damage: int):
        """应用伤害"""
        defender = self.state.players[defender_id]
        defender.hp -= damage
        if defender.hp <= 0:
            defender.is_alive = False
            await self.state.log(f"{defender_id} has been defeated!")
            await self.state.dispatcher.fire_event(GameEventType.DAMAGE_APPLY, {'defender': defender_id})
        else:
            await self.state.log(f"{defender_id} took {damage} damage, remaining HP: {defender.hp}")
    
    async def _heal_apply(self, target_id: str, heal_amount: int):
        """应用治疗"""
        target = self.state.players[target_id]
        target.hp += heal_amount
        if target.hp > target.hp_max:
            target.hp = target.hp_max
        await self.state.log(f"{target_id} healed for {heal_amount}, current HP: {target.hp}")
        await self.state.dispatcher.fire_event(GameEventType.HEAL_APPLY, {'target': target_id})
    
    async def handle_end_turn(self, player_id: str):
        """处理回合结束事件"""
        if self.state.current_turn != player_id:
            return await self.send_error(player_id, "Not your turn")
        
        # 结束当前回合
        self.state.current_turn = None
        await self.broadcast_state()
        await self.state.log(f"{player_id} ended their turn")
        await self.state.dispatcher.fire_event(GameEventType.TURN_END, {'player': player_id})


class GameServer:
    def __init__(self):
        self.players = {}  # 玩家连接池
        self.game_state = GameState()
        self.event_queue = asyncio.Queue()  # 异步事件队列

    async def main_loop(self):
        """主游戏循环"""
        while True:
            # 处理事件队列
            while not self.event_queue.empty():
                event = await self.event_queue.get()
                await self.process_event(event)

            # 更新游戏状态
            await self.update_game_state()
            
            await asyncio.sleep(0.1)  # 防止CPU过载

    async def process_event(self, event: GameEventType.value):
        """处理游戏事件"""
        # 实现事件处理逻辑
        pass

    async def update_game_state(self):
        """更新并广播游戏状态"""
        # 实现状态更新逻辑
        pass