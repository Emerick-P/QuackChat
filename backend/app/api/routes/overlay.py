from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.overlay import rooms  # notre singleton Rooms()
from app.services.overlay import send_chat


router = APIRouter(prefix="/overlay", tags=["overlay"])


@router.websocket("/ws")
async def ws_overlay(ws: WebSocket, 
                     channel: str = Query("default")):
    """
    Overlay OBS (ou page web) se connecte ici :
      ws://localhost:8000/ws/overlay?channel=default
    """
    await rooms.add(ws, channel)
    try: 
        while True:
            await ws.receive_text() # on ne fait rien avec, juste garder la connexion
    except WebSocketDisconnect:
        await rooms.remove(ws, channel) # nettoyage à la déconnexion


