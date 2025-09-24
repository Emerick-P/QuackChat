from fastapi import APIRouter
from app.core.state import PALETTE

router = APIRouter(tags=["public"])

@router.get("/palette")
async def get_palette():
    return PALETTE