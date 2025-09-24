from fastapi import APIRouter
from app.services.overlay import send_chat

router = APIRouter(prefix="/_dev/overlay", tags=["dev"])

@router.get("/testpush")
async def testpush(display: str = "Viewer",
                   message: str = "Hello!",
                   user_id: str = "twitch:test",
                   channel: str = "default"):
    """
    Simule un message chat pour tester l'overlay.
    """
    await send_chat(channel, display, message, user_id)
    return {"sent": True}