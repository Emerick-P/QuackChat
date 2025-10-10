from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.auth import auth_context
from app.db.uow import UnitOfWork, get_uow
from app.schemas.duck import DuckOut, DuckPatch
from app.services.ducks import EDITABLE_FIELDS, apply_duck_patch
from app.utils.patch import extract_patch

router = APIRouter(prefix="/me", tags=["me"], dependencies=[Depends(auth_context)]) # Protege tout le router

@router.get("/duck")
async def me_duck(request: Request):
    """
    Returns information about the duck associated with the authenticated user.

    Args:
        request (Request): FastAPI request object containing the request context.

    Returns:
        dict: Information about the user and their duck.

    Raises:
        HTTPException: If the user is not found (404).
    """
    user = request.state.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    color = user.duck_color
    return {"user_id": user.id, "duck": DuckOut(duck_color=color).model_dump()}


@router.patch("/duck")
async def patch_duck(request: Request, body: DuckPatch, channel: str = "default", uow: UnitOfWork = Depends(get_uow)):
    """
    Partially updates the duck for the authenticated user.
    Editable fields are defined in EDITABLE_FIELDS (imported from app.services.ducks).
    Validates fields, applies the patch via apply_duck_patch, and notifies the overlay if necessary.

    Steps:
    1. Extracts only the fields sent and allowed via extract_patch (EDITABLE_FIELDS).
    2. Validates the color if present in the patch (allowed palette).
    3. Applies the patch to the duck with apply_duck_patch (returns final state and changes).
    4. Notifies the overlay if the color has changed.

    Args:
        request (Request): FastAPI request object containing the request context.
        body (DuckPatch): Pydantic model containing fields to patch.
        channel (str): Overlay channel name.
        uow (UnitOfWork): Unit of Work instance for database operations.

    Returns:
        dict: Confirmation and final duck state (serialized via DuckOut).

    Raises:
        HTTPException: If the user is not found (404) or if patch validation fails (400).
    """
    user = request.state.user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # 1) Extract only the sent and allowed fields
    try:
        patch = extract_patch(body, allowed=EDITABLE_FIELDS)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not patch:
        # No changes, return current duck color
        return {"ok": True, "duck": {"duck_color": user.duck_color}}
    updated, _ = await apply_duck_patch(uow, user.id, patch, channel=channel)
    # Unpack the updated dict into DuckOut for serialization
    return {"ok": True, "duck": DuckOut(**updated).model_dump()}
