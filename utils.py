# utils.py
import asyncio
import websockets
import json
from urllib.parse import urlencode

async def send_user_notification(user_id: int, message: str, token: str, path: str, type_n:str = "alerta"):
    query = urlencode({"token": token, "user_id": user_id, "type":"internal_notification"})
    uri = f"{path}?{query}"

    async with websockets.connect(uri, ping_interval=None) as ws:
        payload = {
                    'type':'send_notification',
                    'user_id':user_id,
                    "message": message,
                    "type_notification":  type_n
                }
        await ws.send(json.dumps(payload))

        response = await asyncio.wait_for(ws.recv(), timeout=5.0)
        return response