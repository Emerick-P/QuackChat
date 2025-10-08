from datetime import datetime, timezone
from fastapi import HTTPException
from starlette import status
from app.core.state import PALETTE
from app.db.uow import UnitOfWork
from app.services.overlay import send_event, make_duck_update_event
from app.utils.timezone import ensure_aware

# Set of allowed public duck colors for guests
_ALLOWED = {c["hex"] for c in PALETTE["public"]}  # Guests: public only

def validate_public_color(hex_: str) -> str:
    """
    Validates that the provided color is allowed for guests.

    Args:
        hex_ (str): The color hex code to validate.

    Returns:
        str: The validated color hex code.

    Raises:
        HTTPException: If the color is not allowed for guests.
    """
    if hex_ not in _ALLOWED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Guests: public colors only")
    return hex_

async def create_pairing_code(uow: UnitOfWork, duck_color: str, channel: str = "default") -> dict:
    """
    Creates a new pairing code for a duck color and channel.

    Args:
        uow (UnitOfWork): Unit of Work instance for database operations.
        duck_color (str): The duck color to pair.
        channel (str, optional): The overlay channel (default: "default").

    Returns:
        dict: Contains the pairing code and its expiration time in seconds.
    """
    validate_public_color(duck_color)
    pairing_repo = uow.pairing
    rec = await pairing_repo.create(duck_color, channel)
    await uow.commit()
    return {
        "code": rec.code,
        "expires_in": max(0, int((ensure_aware(rec.expires_at) - datetime.now(timezone.utc)).total_seconds()))
    }

async def claim_pairing_code(uow: UnitOfWork, code: str, user_id: str, channel: str) -> dict:
    """
    Claims a pairing code and applies the duck color to the user.
    Handles all business logic and repository calls.

    Args:
        uow (UnitOfWork): UnitOfWork instance containing repositories and session.
        code (str): Pairing code to claim.
        user_id (str): User identifier.
        channel (str): Channel name.

    Returns:
        dict: Result of the claim operation (success or error).
    """
    pairing_repo = uow.pairing
    user_repo = uow.users

    rec = await pairing_repo.get(code)
    if not rec:
        return {"error": "Invalid code"}
    if rec.channel != channel:
        return {"error": "Wrong channel"}
    if ensure_aware(rec.expires_at) <= datetime.now(timezone.utc):
        await pairing_repo.delete(code)
        await uow.commit()
        return {"error": "Expired"}

    user = await user_repo.get(user_id)
    if not user:
        await user_repo.create(user_id, display=user_id, duck_color=rec.duck_color)
    else:
        await user_repo.patch(user_id, {"duck_color": rec.duck_color})
    await pairing_repo.delete(code)
    await uow.commit()
    await send_event(channel, make_duck_update_event(user_id, rec.duck_color))
    return {"ok": True, "duck_color": rec.duck_color}