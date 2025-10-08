from fastapi import APIRouter, Depends, Query, Form
from app.db.uow import UnitOfWork, get_uow
from app.services.pairing import create_pairing_code, claim_pairing_code

router = APIRouter(prefix="/pairing", tags=["pairing"])

@router.post("")
async def pairing_create(
    color: str = Form(...),
    channel: str = Query("default"),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Creates a new pairing code for a duck color and channel.

    Args:
        color (str): The duck color to pair.
        channel (str): The overlay channel (default: "default").
        uow (UnitOfWork): Unit of Work instance for database operations.

    Returns:
        dict: Contains the pairing code and its expiration.
    """
    # Guest: public only
    return await create_pairing_code(uow, duck_color=color, channel=channel)

@router.post("/claim")
async def pairing_claim(
    code: str = Form(...),
    twitch_user_id: str = Form(...),
    channel: str = Query("default"),
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Claims a pairing code for a Twitch user and applies the duck color.

    Args:
        code (str): The pairing code to claim.
        twitch_user_id (str): The Twitch user identifier.
        channel (str): The overlay channel (default: "default").
        uow (UnitOfWork): Unit of Work instance for database operations.

    Returns:
        dict: Result of the claim operation (success or error).
    """
    return await claim_pairing_code(uow, code=code, user_id=twitch_user_id, channel=channel)