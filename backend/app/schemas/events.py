from typing import Union, Literal
from pydantic import BaseModel
from app.schemas.duck import DuckOut as DuckPayload  # réutilisation

class ChatEvent(BaseModel):
    """WebSocket event for chat messages."""
    type: Literal["chat"]
    user_id: str
    display: str
    message: str
    duck: DuckPayload
    v: int = 1

class DuckUpdateEvent(BaseModel):
    """WebSocket event for duck color updates."""
    type: Literal["duck_update"]
    user_id: str
    duck: DuckPayload
    v: int = 1

WSEvent = Union[ChatEvent, DuckUpdateEvent]