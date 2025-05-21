#
# -*- coding: UTF-8 -*-
# @project Strife-and-Strike_web
# @file main.py
#

"""
None
"""

import json

from aiohttp import web


class WSGameServer:
    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                await self.handle_message(ws, msg.data)
            elif msg.type == web.WSMsgType.ERROR:
                print("WebSocket连接错误")
                
        return ws

    async def handle_message(self, ws: web.WebSocketResponse, message: str):
        """处理客户端消息"""
        try:
            event = json.loads(message)
            await self.event_queue.put(event)
        except json.JSONDecodeError:
            await ws.send_str("Invalid message format")