from fastapi import APIRouter
from app.core.state import PALETTE

router = APIRouter(tags=["public"])

@router.get("/palette")
async def get_palette():
    """
    Retourne la palette de couleurs disponible pour les utilisateurs.

    Returns:
        dict: Dictionnaire contenant les couleurs publiques et verrouillées.
    """
    return PALETTE