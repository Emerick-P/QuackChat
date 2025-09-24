from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.core.state import TOKENS

# Lit Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/dev/login")

def get_current_uid(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
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
    return TOKENS.get(token) if token else None

CurrentUID = Annotated[str, Depends(get_current_uid)]

async def auth_context(request: Request, uid: CurrentUID):
    request.state.uid = uid  # dispo partout dans ce router