from typing import Iterable, Mapping, MutableMapping, Set, Dict, Any
from pydantic import BaseModel

def extract_patch(body: BaseModel, *, allowed: Iterable[str]) -> Dict[str, Any]:
    """
    Extrait les champs modifiés d'un modèle Pydantic par rapport à son état initial.
    Ne conserve que les champs autorisés et dont la valeur diffère de l'original.

    Args:
        body: Instance d'un modèle Pydantic.
        allowed (Iterable[str]): Champs autorisés à être extraits.

    Returns:
        Dict[str, Any]: Dictionnaire contenant uniquement les champs modifiés et autorisés.
    """
    raw = body.model_dump(exclude_unset=True) # ne garde que les champs fournis
    allowed_set = set(allowed)
    extra = set(raw) - allowed_set
    if extra:
        raise ValueError(f"Forbidden fields: {', '.join(sorted(extra))}")
    return raw

def apply_patch(current: MutableMapping[str, Any], patch: Mapping[str, Any]) -> Set[str]:
    """
    Applique un patch (dictionnaire de modifications) à un dictionnaire existant.
    Met à jour uniquement les champs présents dans le patch et retourne les champs modifiés.

    Args:
        current (MutableMapping[str, Any]): Dictionnaire à mettre à jour.
        patch (Mapping[str, Any]): Dictionnaire contenant les modifications.

    Returns:
        Set[str]: Ensemble des clés qui ont été modifiées.
    """
    changed: Set[str] = set()
    for k, v in patch.items():
        if current.get(k) != v:
            current[k] = v
            changed.add(k)
    return changed