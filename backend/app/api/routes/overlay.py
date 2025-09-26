from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.overlay import rooms  # notre singleton Rooms()


router = APIRouter(prefix="/overlay", tags=["overlay"])


@router.websocket("/ws")
async def ws_overlay(ws: WebSocket, 
                     channel: str = Query("default")):
    """
    Gère la connexion WebSocket pour l'overlay OBS ou la page web.
    Ajoute le client au canal, maintient la connexion et nettoie à la déconnexion.

    Args:
        ws (WebSocket): Connexion WebSocket du client.
        channel (str): Nom du canal d'overlay.
    """
    await rooms.add(ws, channel)
    try: 
        while True:
            await ws.receive_text() # on ne fait rien avec, juste garder la connexion
    except WebSocketDisconnect:
        await rooms.remove(ws, channel) # nettoyage à la déconnexion
