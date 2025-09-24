import json
from typing import Dict, Any, Set, DefaultDict
from collections import defaultdict
from fastapi import WebSocket


class Rooms:
    def __init__(self):
        self.rooms: DefaultDict[str, Set[WebSocket]] = defaultdict(set)

    async def add(self, ws: WebSocket, channel: str):
        await ws.accept()
        self.rooms[channel].add(ws)

    async def remove(self, ws: WebSocket, channel: str):
        self.rooms[channel].discard(ws)

    async def broadcast(self, channel: str, payload: Dict[str, Any]):
        txt = json.dumps(payload)
        for ws in list(self.rooms[channel]):  # snapshot pour pouvoir supprimer pendant la boucle
            try:
                await ws.send_text(txt)
            except Exception:
                self.rooms[channel].discard(ws)

# singleton simple
rooms = Rooms()


def make_chat_event(display: str, 
                    message: str, 
                    user_id: str|int, 
                    color: str = "#8A2BE2") -> Dict:
    return {
        "type": "chat",
        "user_id": user_id,
        "display": display,
        "message": message,
        "duck": {"color": color},
    }
    

async def send_chat(channel: str, display: str, message: str, user_id: str|int, color: str = "#8A2BE2"):
    await rooms.broadcast(channel, make_chat_event(display, message, user_id, color))


def make_duck_update_event(user_id: str | int, color: str) -> dict:
    return {"type": "duck_update", "user_id": user_id, "duck": {"color": color}}


async def send_duck_update(channel: str, user_id: str | int, color: str):
    await rooms.broadcast(channel, make_duck_update_event(user_id, color))