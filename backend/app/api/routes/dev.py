from fastapi import APIRouter
from app.services.overlay import send_event, make_chat_event

router = APIRouter(prefix="/_dev/overlay", tags=["dev"])

@router.get("/testpush")
async def testpush(display: str = "Viewer",
                   message: str = "Hello!",
                   user_id: str = "twitch:test",
                   channel: str = "default"):
    """
    Simulates sending a chat message to test the overlay.

    Args:
        display (str): Display name of the tester.
        message (str): Message to display.
        user_id (str): Fake user identifier.
        channel (str): Test channel.

    Returns:
        dict: Indicates whether the message was sent.
    """
    await send_event(channel, make_chat_event(display, message, user_id))
    return {"sent": True}