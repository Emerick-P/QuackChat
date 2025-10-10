from collections.abc import Mapping
from typing import Union, Dict, Any, Set, DefaultDict
import json
from collections import defaultdict
from fastapi import WebSocket
from pydantic import BaseModel

from app.schemas.duck import DuckOut
from app.schemas.events import ChatEvent, DuckUpdateEvent, WSEvent


class Rooms:
    """
    Manages WebSocket rooms for overlay channels.
    """
    def __init__(self):
        self.rooms: DefaultDict[str, Set[WebSocket]] = defaultdict(set)

    async def add(self, ws: WebSocket, channel: str):
        """
        Accepts a WebSocket connection and adds it to the specified channel.

        Args:
            ws (WebSocket): Client WebSocket connection.
            channel (str): Channel name.
        """
        await ws.accept()
        self.rooms[channel].add(ws)

    async def remove(self, ws: WebSocket, channel: str):
        """
        Removes a WebSocket connection from the specified channel.

        Args:
            ws (WebSocket): Client WebSocket connection.
            channel (str): Channel name.
        """
        self.rooms[channel].discard(ws)

    async def broadcast(self, channel: str, payload: Dict[str, Any]):
        """
        Broadcasts a message to all clients connected to the given channel.

        Args:
            channel (str): Channel name.
            payload (Dict[str, Any]): Data to send.
        """
        txt = json.dumps(payload)
        for ws in list(self.rooms[channel]):  # snapshot to allow removal during iteration
            try:
                await ws.send_text(txt)
            except Exception:
                self.rooms[channel].discard(ws)

# Simple singleton instance
rooms = Rooms()

EventLike = Union[WSEvent, Mapping[str, Any]]

def _as_payload(event: EventLike) -> Dict:
    """
    Converts an event to a dictionary payload for broadcasting.

    Args:
        event (EventLike): The event to convert.

    Returns:
        Dict: The event as a dictionary.

    Raises:
        TypeError: If the event type is unsupported.
    """
    if isinstance(event, BaseModel):
        return event.model_dump()
    elif isinstance(event, Mapping):
        return dict(event)
    raise TypeError(f"Unsupported event type: {type(event)!r}")

async def send_event(channel: str, event: EventLike):
    """
    Broadcasts an arbitrary event on the overlay channel.

    Args:
        channel (str): Overlay channel name.
        event (EventLike): Event to broadcast (formatted for the overlay).
    """
    await rooms.broadcast(channel, _as_payload(event))

def make_chat_event(display: str, 
                    message: str, 
                    user_id: str | int, 
                    duck_color: str = "#8A2BE2") -> ChatEvent:
    """
    Creates a chat event to broadcast on the overlay.

    Args:
        display (str): User display name.
        message (str): Message to display.
        user_id (str | int): User identifier.
        duck_color (str): Duck color.

    Returns:
        ChatEvent: Event formatted for the overlay.
    """
    return ChatEvent(
        type="chat",
        user_id=user_id,
        display=display,
        message=message,
        duck=DuckOut(duck_color=duck_color)
    )

def make_duck_update_event(user_id: str | int, duck_color: str) -> DuckUpdateEvent:
    """
    Creates a duck update event for the overlay.

    Args:
        user_id (str | int): User identifier.
        duck_color (str): New duck color.

    Returns:
        DuckUpdateEvent: Event formatted for the overlay.
    """
    return DuckUpdateEvent(
        type="duck_update",
        user_id=user_id,
        duck=DuckOut(duck_color=duck_color)
    )

