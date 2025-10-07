from typing import Iterable, Mapping, MutableMapping, Set, Dict, Any
from pydantic import BaseModel

def extract_patch(body: BaseModel, *, allowed: Iterable[str]) -> Dict[str, Any]:
    """
    Extracts the modified fields from a Pydantic model compared to its initial state.
    Keeps only allowed fields whose value differs from the original.

    Args:
        body (BaseModel): Instance of a Pydantic model.
        allowed (Iterable[str]): Fields allowed to be extracted.

    Returns:
        Dict[str, Any]: Dictionary containing only the modified and allowed fields.

    Raises:
        ValueError: If forbidden fields are present in the input.
    """
    raw = body.model_dump(exclude_unset=True)  # keeps only provided fields
    allowed_set = set(allowed)
    extra = set(raw) - allowed_set
    if extra:
        raise ValueError(f"Forbidden fields: {', '.join(sorted(extra))}")
    return raw

def apply_patch(current: MutableMapping[str, Any], patch: Mapping[str, Any]) -> Set[str]:
    """
    Applies a patch (dictionary of changes) to an existing dictionary.
    Updates only the fields present in the patch and returns the modified keys.

    Args:
        current (MutableMapping[str, Any]): Dictionary to update.
        patch (Mapping[str, Any]): Dictionary containing the changes.

    Returns:
        Set[str]: Set of keys that were modified.
    """
    changed: Set[str] = set()
    for k, v in patch.items():
        if current.get(k) != v:
            current[k] = v
            changed.add(k)
    return changed