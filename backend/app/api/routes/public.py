from fastapi import APIRouter
from app.core.state import PALETTE

router = APIRouter(tags=["public"])

@router.get("/palette")
async def get_palette():
    """
    Returns the available color palette for users.

    Returns:
        dict: Dictionary containing public and locked colors.
    """
    return PALETTE