from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.state import PALETTE, DUCKS
from app.core.auth import auth_context
from app.schemas.duck import DuckOut, DuckPatch
from app.services.ducks import EDITABLE_FIELDS, apply_duck_patch
from app.services.overlay import send_event, make_duck_update_event
from app.utils.patch import apply_patch, extract_patch

router = APIRouter(prefix="/me", tags=["me"], dependencies=[Depends(auth_context)]) # Protege tout le router

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
async def patch_duck(request: Request, body: DuckPatch, channel: str = "default"):
    """
    Met à jour partiellement le canard de l'utilisateur authentifié.
    Les champs modifiables sont définis dans EDITABLE_FIELDS (importé depuis app.services.ducks).
    Valide les champs, applique le patch via apply_duck_patch et notifie l'overlay si nécessaire.

    Étapes :
    1. Récupère uniquement les champs envoyés et autorisés via extract_patch (EDITABLE_FIELDS).
    2. Valide la couleur si elle est présente dans le patch (palette autorisée).
    3. Applique le patch sur le canard avec apply_duck_patch (retourne l'état final et les changements).
    4. Notifie l'overlay si la couleur a changé.

    Args:
        request (Request): Objet FastAPI contenant le contexte de la requête.
        body (DuckPatch): Modèle Pydantic contenant les champs à patcher.
        channel (str): Canal de diffusion de l'overlay.

    Returns:
        dict: Confirmation et état final du canard (serialisé via DuckOut).
    """
    uid = request.state.uid
    current = DUCKS.get(uid, {"color": "#8A2BE2"})

    # 1) récupérer uniquement les champs envoyés et autorisés
    try:
        patch = extract_patch(body, allowed=EDITABLE_FIELDS)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not patch:
        return {"ok": True, "duck": current}
    
    updated = await apply_duck_patch(uid, patch, channel=channel)
    return {"ok": True, "duck": DuckOut(**updated).model_dump()} # Le **updated décompose le dictionnaire en arguments nommés pour le modèle Pydantic