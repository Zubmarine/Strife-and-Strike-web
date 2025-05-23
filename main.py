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
from websocket.server import WSServer
from config.settings import Settings


async def main():
    # 加载配置
    settings = Settings()
    
    # 创建服务器
    ws_server = WSServer()
    
    # 设置路由
    app = web.Application()
    app.router.add_get('/game', ws_server.game_server.websocket_handler)
    app.router.add_get('/account', ws_server.handle_account)
    
    # 启动服务器
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner, 
        settings.config.get('host', 'localhost'),
        settings.config.get('port', 8080)
    )
    await site.start()
    
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())