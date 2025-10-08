from datetime import datetime, timedelta, timezone
from jose import jwt, ExpiredSignatureError, JWTError
from app.core.settings import settings
from fastapi import HTTPException, status

def create_access_token(payload: dict) -> str:
    """
    Creates a JWT access token with the given payload.

    Args:
        payload (dict): The payload to include in the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    """
    Decodes a JWT access token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded payload.

    Raises:
        jwt.JWTError: If the token is invalid or expired.
    """
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        