from fastapi import APIRouter
from typing import Optional
import secrets
from app.core.state import USERS, DUCKS, TOKENS

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/dev/login")
async def dev_login(display: str, user_id: Optional[str] = None):
    uid = user_id or f"twitch:{secrets.token_hex(4)}"
    USERS[uid] = {"display": display}
    token = secrets.token_urlsafe(24)
    TOKENS[token] = uid
    DUCKS.setdefault(uid, {"color": "#8A2BE2"})
    return {"token": token, "user_id": uid, "display": display}