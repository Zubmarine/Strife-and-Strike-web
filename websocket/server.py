from aiohttp import web
from game.server import GameServer
from .register import AccountManager

class WSServer:
    def __init__(self):
        self.game_server = GameServer()
        self.account_manager = AccountManager()
        
    async def handle_connection(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # 根据路径分发到不同处理器
        path = request.path
        if path == '/game':
            return await self.game_server.websocket_handler(request)
        elif path == '/account':
            return await self.handle_account(ws)