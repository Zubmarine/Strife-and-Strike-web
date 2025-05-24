from enum import Enum

from .state import GameState

class Trait:
    def __init__(self, name: str, game_state: GameState = None):
        self.name = name
        self.game_state = game_state


class SelfEncouragement(Trait):
    def __init__(self, game_state: GameState = None):
        super().__init__("SelfEncouragement", game_state=game_state)
        game_state.event_dispatcher.add_listener(
            game_state.event_type.DAMAGE_APPLY,
            self.self_encouragement,
            priority=50
        )

    async def self_encouragement(self, event):
        """自勉特质的事件处理"""
        player = self.game_state.players.get(event.data.get("player"))
        if player.hp <= player.hp_max * 0.5 and player.hp > 0:
            await self.game_state.event_dispatcher.fire_event(
                self.game_state.event_type.HEAL_APPLY, {
                    'player': player,
                    'hp': player.hp_max * 0.8 - player.hp
                })
            await self.game_state.log(f"{player.name}的自勉触发，生命值恢复至{player.hp_max * 0.8}")
        return event

class TirelessObserver(Trait):
    def __init__(self, game_state: GameState = None):
        super().__init__("TirelessObserver", game_state=game_state)
        game_state.event_dispatcher.add_listener(
            game_state.event_type.SKILL_USE,
            self.tireless_observer,
            priority=50
        )

    async def tireless_observer(self, event):
        """勤勉观察者的事件处理"""
        player = self.game_state.players.get(event.data.get("player"))
        if player:
            await self.game_state.event_dispatcher.fire_event(
                self.game_state.event_type.SKILL_CD_MODIFIED, {
                    'player': player,
                    'skill': event.data.get("skill"),
                    'cd': -1
                })
            await self.game_state.log(f"{player.name}的勤勉观察者特质触发")
        return event

class ClearPathToCome(Trait):
    def __init__(self, game_state: GameState = None):
        super().__init__("ClearPathToCome", game_state=game_state)
        game_state.event_dispatcher.add_listener(
            game_state.event_type.GAME_START,
            self.clear_path_to_come,
            priority=50
        )

    async def clear_path_to_come(self, event):
        """开路先锋的事件处理"""
        player = self.game_state.players.get(event.data.get("player"))
        if player:
            await self.game_state.event_dispatcher.fire_event(
                self.game_state.event_type.SKILL_APPEND, {
                    'player': player,
                    'skill': event.data.get("skill")
                })
            await self.game_state.log(f"{player.name}的开路先锋特质触发")
        return event


class TraitManager(Enum):
    SELF_ENCOURAGEMENT = SelfEncouragement
    TIRELESS_OBSERVER = TirelessObserver
    CLEAR_PATH_TO_COME = ClearPathToCome