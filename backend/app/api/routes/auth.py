from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import secrets
from app.core.settings import settings
from app.db.uow import UnitOfWork, get_uow
from app.core.jwt import create_access_token
from app.core.auth import CurrentUser

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me")
async def read_me(user: CurrentUser):
    """
    Returns information about the currently authenticated user.

    Args:
        user (CurrentUser): The authenticated user injected by the dependency.

    Returns:
        dict: Contains the user's ID, display name, and duck color.
    """
    return {
        "user_id": user.id,
        "display": user.display,
        "duck_color": user.duck_color
    }

@router.post("/login")
async def login(
    display: str,
    user_id: Optional[str] = None,
    uow: UnitOfWork = Depends(get_uow)
):
    """
    Authenticates a user in development mode and returns a JWT access token.

    Args:
        display (str): Display name of the user.
        user_id (Optional[str]): Optional user identifier. If not provided, a random Twitch ID is generated.
        uow (UnitOfWork): Unit of Work instance for database operations.

    Returns:
        dict: Contains the JWT access token and its type.

    Raises:
        HTTPException: If not in development mode (403).
    """
    if settings.ENV != "dev":
        raise HTTPException(status_code=403, detail="Login is only available in development mode")
    
    uid = user_id or f"twitch:{secrets.token_hex(4)}"
    user = await uow.users.ensure_for_login(uid, display)
    await uow.commit()

    token = create_access_token({"sub": uid, "display": display})
    return {"access_token": token, "token_type": "bearer"}
