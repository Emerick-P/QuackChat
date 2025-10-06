from typing import Any, Dict, Mapping, Set, Callable, Tuple
from fastapi import HTTPException
from app.core.state import DUCKS, PALETTE
from app.schemas.duck import DuckOut
from app.utils.patch import apply_patch
from app.services.overlay import send_event, make_duck_update_event
from app.repository.user import get_user, patch_user
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

# Champs éditables côté client
EDITABLE_FIELDS: Set[str] = {"duck_color"}  

# --- Validateurs par champ --- #

def _validate_color(value: str) -> str:
    allowed = {c["hex"] for c in PALETTE["public"]} | {c["hex"] for c in PALETTE["locked"]}
    if value not in allowed:
        raise HTTPException(status_code=400, detail="Unknown color")
    return value
    
VALIDATORS: Dict[str, Callable[[Any], None]] = {
    "duck_color": _validate_color,
}

ALLOWED_KEYS = set(VALIDATORS.keys())  

def _aggregate_validate(patch: Mapping[str, Any]) -> dict[str, Any]:
    """
    Valide TOUT le patch.
    - Erreur si champs inattendus
    - Exécute tous les validateurs; agrège les erreurs
    - Retourne un dict 'validated' si tout va bien
    """
    # 1) strict: refuse les extras
    extras = set(patch) - ALLOWED_KEYS
    if extras:
        details = [{"loc": ["body", k], "msg": "unexpected field", "type": "value_error.extra"}
                   for k in sorted(extras)]
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=details)

    # 2) valider chaque champ et collecter les erreurs
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
        session: AsyncSession,
        uid: str,
        patch: Mapping[str, Any], *,
        channel: str = "default"
        ) -> Tuple[dict, dict]:
    """
    Applique un patch duck (aujourd'hui: duck_color).
    Tout-ou-rien: on n'écrit en DB que si toutes les validations passent.
    Retourne (duck_dict, changed_fields).
    """
    user = await get_user(session, uid)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    if not patch:
        return DuckOut(duck_color=user.duck_color).model_dump(), {}

    # Phase 1: valider entièrement (peut lever 422 avec liste d'erreurs)
    clean = _aggregate_validate(patch)

    # Phase 2: appliquer uniquement ce qui change réellement
    changed = {k: v for k, v in clean.items() if getattr(user, k) != v}
    if changed:
        user = await patch_user(session, uid, changed)      
        if "duck_color" in changed:
            await send_event(channel, make_duck_update_event(uid, changed["duck_color"]))

    return DuckOut(duck_color=user.duck_color).model_dump(), changed