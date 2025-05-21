#
# -*- coding: UTF-8 -*-
# @project Strife-and-Strike_web
# @file main.py
#

"""
The main progress of SnS Game, including server, game precess, etc.
"""

import asyncio
from game import GameServer

from aiohttp import web


async def main():
    server = GameServer()
    server.game_state.initialize_deck()
    
    # 创建aiohttp应用
    app = web.Application()
    app.add_routes([web.get('/ws', server.websocket_handler)])
    
    # 同时运行Web服务器和游戏循环
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    
    await asyncio.gather(
        site.start(),
        server.main_loop()
    )

if __name__ == "__main__":
    asyncio.run(main())