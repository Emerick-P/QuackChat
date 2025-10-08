from typing import Optional
from datetime import datetime, timezone, timedelta
import secrets
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pairing import PairingCode
from app.repository.user import UsersRepository

DEFAULT_TTL_S = 300  # Default time-to-live for pairing codes in seconds

def _now() -> datetime:
    """
    Returns the current UTC datetime.

    Returns:
        datetime: Current UTC time.
    """
    return datetime.now(timezone.utc)

def generate_code() -> str:
    """
    Generates a random, readable pairing code.

    Returns:
        str: A 6-character uppercase hexadecimal code.
    """
    return secrets.token_hex(3).upper()

class PairingRepository:
    """
    Repository for pairing code-related database operations.

    Args:
        session (AsyncSession): The database session to use.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, duck_color: str, channel: str, ttl_s: int = DEFAULT_TTL_S) -> PairingCode:
        """
        Creates and adds a new pairing code to the database.

        Args:
            duck_color (str): The duck color to pair.
            channel (str): The overlay channel.
            ttl_s (int): Time-to-live in seconds (default: 300).

        Returns:
            PairingCode: The created pairing code object.
        """
        rec = PairingCode(
            code=generate_code(),
            duck_color=duck_color,
            channel=channel,
            expires_at=_now() + timedelta(seconds=ttl_s),
        )
        self.session.add(rec)
        return rec

    async def get(self, code: str) -> Optional[PairingCode]:
        """
        Retrieves a pairing code by its code value.

        Args:
            code (str): The pairing code to look up.

        Returns:
            Optional[PairingCode]: The pairing code object if found, else None.
        """
        res = await self.session.execute(select(PairingCode).where(PairingCode.code == code))
        return res.scalar_one_or_none()

    async def delete(self, code: str) -> None:
        """
        Deletes a pairing code from the database.

        Args:
            code (str): The pairing code to delete.
        """
        await self.session.execute(delete(PairingCode).where(PairingCode.code == code))