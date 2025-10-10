from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.db.uow import UnitOfWork, get_uow
from app.models.user import User
from app.core.jwt import decode_access_token

# Reads Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        uow: UnitOfWork = Depends(get_uow)
        ) -> User: 
    """
    Retrieves the current authenticated user from the JWT token.

    Args:
        token (str): JWT access token extracted from the Authorization header.
        uow (UnitOfWork): Unit of Work instance for database operations.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the token is missing, invalid, or the user is not found.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await uow.users.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

async def auth_context(request: Request, user: CurrentUser):
    """
    Adds the user identifier (uid) to the request context (request.state).
    Makes the uid available throughout the router's routes.

    Args:
        request (Request): FastAPI request object containing the context.
        uid (str): Authenticated user identifier.
    """
    request.state.user = user  # Available everywhere in this router
