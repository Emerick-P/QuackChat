from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.core.state import TOKENS

# Lit Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/dev/login")

def get_current_uid(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """
    Récupère l'identifiant utilisateur (uid) à partir du token d'authentification.
    Vérifie la validité du token et lève une exception HTTP 401 si le token est absent ou invalide.

    Args:
        token (str): Token d'authentification extrait du header Authorization.

    Returns:
        str: Identifiant utilisateur associé au token.
    """
    uid = TOKENS.get(token)
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return uid

# variante "optionnelle" pour des endpoints publics qui connaissent l’user si présent
def get_optional_uid(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    """
    Variante optionnelle pour les endpoints publics.
    Retourne l'uid si le token est présent et valide, sinon None.

    Args:
        token (Optional[str]): Token d'authentification (peut être absent).

    Returns:
        Optional[str]: Identifiant utilisateur ou None si non authentifié.
    """
    return TOKENS.get(token) if token else None

CurrentUID = Annotated[str, Depends(get_current_uid)]

async def auth_context(request: Request, uid: CurrentUID):
    """
    Ajoute l'identifiant utilisateur (uid) dans le contexte de la requête (request.state).
    Permet d'accéder à l'uid dans toutes les routes du router.

    Args:
        request (Request): Objet FastAPI contenant le contexte de la requête.
        uid (str): Identifiant utilisateur authentifié.
    """
    request.state.uid = uid  # dispo partout dans ce router