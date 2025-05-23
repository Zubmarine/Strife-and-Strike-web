from .events import GameEventType, GameEvent
from .state import GameState

class Trait:
    def __init__(self, name: str, game_state: GameState = None):
        self.name = name
        self.game_state = game_state

class SelfEncouragement(Trait):
    def __init__(self, game_state: GameState = None):
        super().__init__("SelfEncouragement", game_state=game_state)
        game_state.dispatcher.add_listener(
            GameEventType.DAMAGE_APPLY, 
            self.self_encouragement, 
            priority=50
        )

    async def self_encouragement(self, event: GameEvent):
        """自勉特质的事件处理"""
        player = self.game_state.players.get(event.data.get("player"))
        if player.hp <= player.hp_max * 0.5 and player.hp > 0:
            await self.game_state.dispatcher.fire_event(
                GameEventType.HEAL_APPLY, {
                    'player': player,
                    'hp': player.hp_max * 0.8 - player.hp
                })
            await self.game_state.log(f"{player.name}的自勉触发，生命值恢复至{player.hp_max * 0.8}")
        return event