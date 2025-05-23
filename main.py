#
# -*- coding: UTF-8 -*-
# @project Strife-and-Strike_web
# @file main.py
#

"""
The main progress of SnS Game, including server, game precess, etc.
"""

import asyncio
from aiohttp import web
from game.server import GameServer


async def main():
    server = GameServer()
    app = web.Application()
    app.router.add_get('/ws', server.websocket_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())