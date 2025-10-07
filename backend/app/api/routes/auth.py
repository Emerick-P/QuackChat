from fastapi import APIRouter, Depends
from typing import Optional
import secrets
from app.core.state import TOKENS
from app.db.uow import UnitOfWork, get_uow

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/dev/login")
async def dev_login(display: str, user_id: Optional[str] = None, uow: UnitOfWork = Depends(get_uow)):
    """
    Creates a development user and generates an authentication token.
    If user_id is not provided, a random Twitch identifier is generated.
    Initializes the user, token, and associated duck.

    Args:
        display (str): Display name of the user.
        user_id (Optional[str]): Optional user identifier.

    Returns:
        dict: Contains the token, user identifier, and display name.
    """
    uid = user_id or f"twitch:{secrets.token_hex(4)}"
    user = await uow.users.ensure_for_login(uid, display)

    tok = secrets.token_urlsafe(24)
    TOKENS[tok] = uid
    
    return {"token": tok, "user_id": uid, "display": user.display}