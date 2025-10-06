from fastapi import APIRouter, Depends
from typing import Optional
import secrets
from app.core.state import USERS, DUCKS, TOKENS
from app.repository.user import ensure_user_for_login
from app.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/dev/login")
async def dev_login(display: str, user_id: Optional[str] = None, session: AsyncSession = Depends(get_session)):
    """
    Crée un utilisateur de développement et génère un token d'authentification.
    Si user_id n'est pas fourni, un identifiant Twitch aléatoire est généré.
    Initialise l'utilisateur, le token et le canard associé.

    Args:
        display (str): Nom d'affichage de l'utilisateur.
        user_id (Optional[str]): Identifiant utilisateur optionnel.

    Returns:
        dict: Contient le token, l'identifiant utilisateur et le display.
    """
    uid = user_id or f"twitch:{secrets.token_hex(4)}"
    user = await ensure_user_for_login(session, uid, display)

    USERS[uid] = {"display": display}
    DUCKS.setdefault(uid, {"duck_color": user.duck_color})

    tok = secrets.token_urlsafe(24)
    TOKENS[tok] = uid
    
    return {"token": tok, "user_id": uid, "display": user.display}