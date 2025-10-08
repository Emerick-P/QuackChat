from typing import Any, Dict, Mapping, Set, Callable, Tuple
from fastapi import HTTPException
from app.core.state import PALETTE
from app.db.uow import UnitOfWork
from app.schemas.duck import DuckOut
from app.services.overlay import send_event, make_duck_update_event
from starlette import status

# Editable fields on the client side
EDITABLE_FIELDS: Set[str] = {"duck_color"}  

# --- Field validators --- #

def _validate_color(value: str) -> str:
    """
    Validates that the provided color is in the allowed palette.

    Args:
        value (str): The color hex code to validate.

    Returns:
        str: The validated color hex code.

    Raises:
        HTTPException: If the color is not allowed.
    """
    allowed = {c["hex"] for c in PALETTE["public"]} | {c["hex"] for c in PALETTE["locked"]}
    if value not in allowed:
        raise HTTPException(status_code=400, detail="Unknown color")
    return value
    
VALIDATORS: Dict[str, Callable[[Any], Any]] = {
    "duck_color": _validate_color,
}

ALLOWED_KEYS = set(VALIDATORS.keys())  

def _aggregate_validate(patch: Mapping[str, Any]) -> dict[str, Any]:
    """
    Validates the entire patch.
    - Raises error if unexpected fields are present.
    - Runs all validators and aggregates errors.
    - Returns a 'validated' dict if all checks pass.

    Args:
        patch (Mapping[str, Any]): The patch data to validate.

    Returns:
        dict[str, Any]: The validated patch data.

    Raises:
        HTTPException: If there are unexpected fields or validation errors.
    """
    # 1) Strict: refuse extras
    extras = set(patch) - ALLOWED_KEYS
    if extras:
        details = [{"loc": ["body", k], "msg": "unexpected field", "type": "value_error.extra"}
                   for k in sorted(extras)]
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=details)

    # 2) Validate each field and collect errors
    errors = []
    validated: dict[str, Any] = {}
    for k, v in patch.items():
        validator = VALIDATORS.get(k)
        if validator is None:
            validated[k] = v
            continue
        try:
            validated[k] = validator(v)
        except HTTPException as e:
            msg = e.detail if isinstance(e.detail, str) else "invalid value"
            errors.append({"loc": ["body", k], "msg": msg, "type": "value_error"})

    if errors:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=errors)

    return validated

async def apply_duck_patch(
        uow: UnitOfWork,
        uid: str,
        patch: Mapping[str, Any], *,
        channel: str = "default"
        ) -> Tuple[dict, dict]:
    """
    Applies a duck patch (currently: duck_color).
    All-or-nothing: writes to the DB only if all validations pass.
    Returns (duck_dict, changed_fields).

    Args:
        uow (UnitOfWork): The unit of work for DB operations.
        uid (str): The user identifier.
        patch (Mapping[str, Any]): The patch data to apply.
        channel (str, optional): Overlay channel name.

    Returns:
        Tuple[dict, dict]: The updated duck data and the changed fields.

    Raises:
        HTTPException: If the user is not found or validation fails.
    """
    user = await uow.users.get(uid)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    if not patch:
        return DuckOut(duck_color=user.duck_color).model_dump(), {}

    # Phase 1: fully validate (may raise 422 with error list)
    clean = _aggregate_validate(patch)

    # Phase 2: apply only actual changes
    changed = {k: v for k, v in clean.items() if getattr(user, k) != v}
    if changed:
        user = await uow.users.patch(uid, changed)
        if "duck_color" in changed:
            await send_event(channel, make_duck_update_event(uid, changed["duck_color"]))

    await uow.commit()
    return DuckOut(duck_color=user.duck_color).model_dump(), changed