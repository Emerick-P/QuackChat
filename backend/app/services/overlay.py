import json
from typing import Dict, Any, Set, DefaultDict
from collections import defaultdict
from fastapi import WebSocket


class Rooms:
    def __init__(self):
        """
        Initialise le gestionnaire de rooms pour les WebSockets.
        """
        self.rooms: DefaultDict[str, Set[WebSocket]] = defaultdict(set)

    async def add(self, ws: WebSocket, channel: str):
        """
        Accepte une connexion WebSocket et l'ajoute au canal spécifié.

        Args:
            ws (WebSocket): Connexion WebSocket du client.
            channel (str): Nom du canal.
        """
        await ws.accept()
        self.rooms[channel].add(ws)

    async def remove(self, ws: WebSocket, channel: str):
        """
        Retire une connexion WebSocket du canal spécifié.

        Args:
            ws (WebSocket): Connexion WebSocket du client.
            channel (str): Nom du canal.
        """
        self.rooms[channel].discard(ws)

    async def broadcast(self, channel: str, payload: Dict[str, Any]):
        """
        Diffuse un message à tous les clients connectés sur le canal donné.

        Args:
            channel (str): Nom du canal.
            payload (Dict[str, Any]): Données à envoyer.
        """
        txt = json.dumps(payload)
        for ws in list(self.rooms[channel]):  # snapshot pour pouvoir supprimer pendant la boucle
            try:
                await ws.send_text(txt)
            except Exception:
                self.rooms[channel].discard(ws)

# singleton simple
rooms = Rooms()

async def send_event(channel: str, event: dict):
    """
    Diffuse un événement arbitraire sur le canal overlay.

    Args:
        channel (str): Nom du canal overlay.
        event (dict): Événement à diffuser (formaté pour l'overlay).
    """
    await rooms.broadcast(channel, event)

def make_chat_event(display: str, 
                    message: str, 
                    user_id: str|int, 
                    color: str = "#8A2BE2") -> Dict:
    """
    Crée un événement de chat à diffuser sur l'overlay.

    Args:
        display (str): Nom d'affichage de l'utilisateur.
        message (str): Message à afficher.
        user_id (str|int): Identifiant utilisateur.
        color (str): Couleur du canard.

    Returns:
        Dict: Événement formaté pour l'overlay.
    """
    return {
        "type": "chat",
        "user_id": user_id,
        "display": display,
        "message": message,
        "duck": {"color": color},
    }

def make_duck_update_event(user_id: str | int, color: str) -> dict:
    """
    Crée un événement de mise à jour de canard pour l'overlay.

    Args:
        user_id (str|int): Identifiant utilisateur.
        color (str): Nouvelle couleur du canard.

    Returns:
        dict: Événement formaté pour l'overlay.
    """
    return {"type": "duck_update", "user_id": user_id, "duck": {"color": color}}