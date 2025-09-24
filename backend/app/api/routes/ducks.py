from typing import Annotated, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.state import PALETTE, DUCKS
from app.core.auth import get_current_uid
from app.services.overlay import send_duck_update

router = APIRouter(prefix="/me", tags=["me"], dependencies=[Depends(get_current_uid)]) # Protege tout le router

@router.get("/duck")
async def me_duck(request: Request):
    uid = request.state.uid
    return {"user_id": uid, "duck": DUCKS.get(uid, {"color": "#8A2BE2"})}

@router.patch("/duck")
async def update_duck(request: Request, 
                      data: Dict[str, Any],
                      channel: str = "default"):
    uid = request.state.uid
    color = data.get("color")
    allowed = {c["hex"] for c in PALETTE["public"]} | {c["hex"] for c in PALETTE["locked"]}
    if color not in allowed:
        raise HTTPException(status_code=400, detail="Unknown color")
    DUCKS[uid] = {"color": color}
    await send_duck_update(channel=channel, user_id=uid, color=color)
    return {"ok": True, "duck": {"color": color}}