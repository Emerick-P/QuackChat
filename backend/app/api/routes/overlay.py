from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.overlay import rooms  # our singleton Rooms()


router = APIRouter(prefix="/overlay", tags=["overlay"])


@router.websocket("/ws")
async def ws_overlay(ws: WebSocket, 
                     channel: str = Query("default")):
    """
    Manages the WebSocket connection for the OBS overlay or web page.
    Adds the client to the channel, keeps the connection alive, and cleans up on disconnect.

    Args:
        ws (WebSocket): Client WebSocket connection.
        channel (str): Overlay channel name.
    """
    await rooms.add(ws, channel)
    try: 
        while True:
            await ws.receive_text()  # Keep the connection alive; incoming messages are ignored
    except WebSocketDisconnect:
        await rooms.remove(ws, channel)  # Clean up on disconnect
