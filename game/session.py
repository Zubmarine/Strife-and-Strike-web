import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .core import GameCore

state = GameCore.state

@dataclass
class GameSession:
    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    game_state: state = field(default_factory=state)
    event_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    
    def __post_init__(self):
        self.lock = asyncio.Lock()
        self.is_active = True
        self.logger = logging.getLogger(f"Session_{self.session_id}")

    async def process_events(self):
        while self.is_active:
            event = await self.event_queue.get()
            await self.handle_event(event)

    async def player_join(self, player_id: str):
        async with self.lock:
            if player_id not in self.game_state.players:
                self.game_state.player_in_order.append(player_id)
                self.logger.info(f"Player joined: {player_id}")
            else:
                self.logger.warning(f"Player {player_id} is already in the game.")

    async def player_exit(self, player_id: str):
        async with self.lock:
            if player_id in self.game_state.players:
                del self.game_state.players[player_id]
                self.game_state.player_in_order.remove(player_id)
                self.logger.info(f"Player exited: {player_id}")
            else:
                self.logger.warning(f"Player {player_id} not found.")

    async def team_system_activate(self):
        async with self.lock:
            if not self.game_state.is_team_system_active:
                self.game_state.is_team_system_active = True
                self.logger.info("Team system activated.")
            else:
                self.logger.warning("Team system is already active.")

    async def team_system_deactivate(self):
        async with self.lock:
            if self.game_state.is_team_system_active:
                self.game_state.is_team_system_active = False
                self.logger.info("Team system deactivated.")
            else:
                self.logger.warning("Team system is not active.")

    async def player_character_select(self, player_id: str, character_name: str):
        async with self.lock:
            if character_name in self.game_state.character_selected:
                self.logger.warning(f"Character {character_name} is already selected.")
                return
            elif player_id in self.game_state.players:
                if self.game_state.players[player_id].name:
                    self.game_state.character_selected.remove(self.game_state.players[player_id].name)
                self.game_state.players[player_id] = GameCore.character
                self.logger.info(f"Player {player_id} selected character: {character_name}")
            else:
                self.logger.warning(f"Player {player_id} not found.")