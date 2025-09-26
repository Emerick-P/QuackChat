from fastapi import APIRouter
from app.services.overlay import send_event, make_chat_event

router = APIRouter(prefix="/_dev/overlay", tags=["dev"])

@router.get("/testpush")
async def testpush(display: str = "Viewer",
                   message: str = "Hello!",
                   user_id: str = "twitch:test",
                   channel: str = "default"):
    """
    Simule l'envoi d'un message chat pour tester l'overlay.

    Args:
        display (str): Nom d'affichage du testeur.
        message (str): Message à afficher.
        user_id (str): Identifiant utilisateur fictif.
        channel (str): Canal de test.

    Returns:
        dict: Indique si le message a été envoyé.
    """
    await send_event(channel, make_chat_event(display, message, user_id))
    return {"sent": True}