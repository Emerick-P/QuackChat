from typing import Any, Dict, Mapping, Set, Callable, Tuple
from fastapi import HTTPException
from app.core.state import DUCKS, PALETTE
from app.utils.patch import apply_patch
from app.services.overlay import send_event, make_duck_update_event

# Champs éditables côté client
EDITABLE_FIELDS: Set[str] = {"color"}  

# --- Validateurs par champ --- #

def _validate_color(value: str) -> None:
    allowed = {c["hex"] for c in PALETTE["public"]} | {c["hex"] for c in PALETTE["locked"]}
    if value not in allowed:
        raise HTTPException(status_code=400, detail="Unknown color")
    
VALIDATORS: Dict[str, Callable[[Any], None]] = {
    "color": _validate_color,
}


# --- Application du patch + side effects events --- #

async def apply_duck_patch(uid: str, 
                           patch: Mapping[str, Any], *, 
                           channel: str = "default"
                           ) -> Dict[str, Any]:
    duck = DUCKS.get(uid, {"color": "#8A2BE2"})

    # 1) validation des champs
    for key, val in patch.items():
        fn = VALIDATORS.get(key)
        if fn:
            fn(val)
    
    # 2) application du patch
    changed = apply_patch(duck, patch)
    DUCKS[uid] = duck  

    # 3) Emettre les events si besoin
    if "color" in changed:
        await send_event(channel, make_duck_update_event(uid, duck["color"]))
    return duck