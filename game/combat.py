import logging
import random
from .events import GameEventType, GameEvent

class CombatSystem:
    def __init__(self, game_state):
        self.state = game_state
        self.logger = logging.getLogger('CombatSystem')
    
    async def execute_attack(self, attacker_id: str, defender_id: str):
        """执行攻击流程"""
        try:
            if not await self._validate_attack(attacker_id, defender_id):
                return
                
            damage = await self._calculate_attack_damage(attacker_id, defender_id)
            await self._apply_damage(defender_id, damage)
            
        except Exception as e:
            self.logger.error(f"攻击执行失败: {e}", exc_info=True)
            await self.state.log(f"攻击执行失败: {e}")

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