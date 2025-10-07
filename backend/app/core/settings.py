import os
from typing import List

def _parse_csv(val: str | None) -> List[str]:
    """
    Parses a comma-separated string into a list of trimmed strings.

    Args:
        val (str | None): The CSV string to parse.

    Returns:
        List[str]: List of trimmed values, or an empty list if input is None.
    """
    return [s.strip() for s in val.split(",")] if val else []

class Settings:
    """
    Application settings loaded from environment variables.

    Attributes:
        ENV (str): Current environment ("dev" by default).
        CORS_ORIGINS (List[str]): Allowed CORS origins.
        DATABASE_URL (str): Database connection URL.
        PAIRING_CODE_EXPIRY_SECONDS (int): Validity duration for pairing codes (seconds).
    """
    def __init__(self) -> None:
        self.ENV: str = os.getenv("ENV", "dev").lower()
        self.CORS_ORIGINS: List[str] = _parse_csv(os.getenv("CORS_ORIGINS")) or ["http://localhost:5173"]
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./var/dev.db")
        self.PAIRING_CODE_EXPIRY_SECONDS: int = int(os.getenv("PAIRING_CODE_EXPIRY_SECONDS", "300"))

settings = Settings()