from typing import Annotated, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.state import PALETTE, DUCKS
from app.core.auth import get_current_uid
from app.services.overlay import send_event, make_duck_update_event

router = APIRouter(prefix="/me", tags=["me"], dependencies=[Depends(get_current_uid)]) # Protege tout le router

@router.get("/duck")
async def me_duck(request: Request):
    """
    Retourne les informations du canard associé à l'utilisateur authentifié.

    Args:
        request (Request): Objet FastAPI contenant le contexte de la requête.

    Returns:
        dict: Informations sur l'utilisateur et son canard.
    """
    uid = request.state.uid
    return {"user_id": uid, "duck": DUCKS.get(uid, {"color": "#8A2BE2"})}

@router.patch("/duck")
async def update_duck(request: Request, 
                      data: Dict[str, Any],
                      channel: str = "default"):
    """
    Met à jour la couleur du canard de l'utilisateur authentifié.
    Vérifie que la couleur est autorisée et diffuse la mise à jour via l'overlay.

    Args:
        request (Request): Objet FastAPI contenant le contexte de la requête.
        data (Dict[str, Any]): Données envoyées par le client (doit contenir 'color').
        channel (str): Canal de diffusion de l'overlay.

    Returns:
        dict: Confirmation et nouvelle couleur du canard.
    """
    uid = request.state.uid
    color = data.get("color")
    allowed = {c["hex"] for c in PALETTE["public"]} | {c["hex"] for c in PALETTE["locked"]}
    if color not in allowed:
        raise HTTPException(status_code=400, detail="Unknown color")
    DUCKS[uid] = {"color": color}
    await send_event(channel, make_duck_update_event(user_id=uid, color=color))
    return {"ok": True, "duck": {"color": color}}
