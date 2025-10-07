from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.core.state import TOKENS

# Reads Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/dev/login")

def get_current_uid(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """
    Retrieves the user identifier (uid) from the authentication token.
    Checks token validity and raises HTTP 401 if the token is missing or invalid.

    Args:
        token (str): Authentication token extracted from the Authorization header.

    Returns:
        str: User identifier associated with the token.

    Raises:
        HTTPException: If the token is missing or invalid.
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
    Optional variant for public endpoints.
    Returns the uid if the token is present and valid, otherwise None.

    Args:
        token (Optional[str]): Authentication token (may be absent).

    Returns:
        Optional[str]: User identifier or None if not authenticated.
    """
    return TOKENS.get(token) if token else None

CurrentUID = Annotated[str, Depends(get_current_uid)]

async def auth_context(request: Request, uid: CurrentUID):
    """
    Adds the user identifier (uid) to the request context (request.state).
    Makes the uid available throughout the router's routes.

    Args:
        request (Request): FastAPI request object containing the context.
        uid (str): Authenticated user identifier.
    """
    request.state.uid = uid  # Available everywhere in this router