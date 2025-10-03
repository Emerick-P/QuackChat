import os
from typing import List

def _parse_csv(val: str | None) -> List[str]:
    return [s.strip() for s in val.split(",")] if val else []

class Settings:
    def __init__(self) -> None:
        # "dev" par défaut
        self.ENV: str = os.getenv("ENV", "dev").lower()
        # Liste des origines CORS autorisées (CSV), ; default = front dev
        self.CORS_ORIGINS: List[str] = _parse_csv(os.getenv("CORS_ORIGINS")) or ["http://localhost:5173"] 
        # SQLite fallback for dev if not defined
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./var/dev.db")
        # Durée de validité des codes de jumelage en secondes
        self.PAIRING_CODE_EXPIRY_SECONDS: int = int(os.getenv("PAIRING_CODE_EXPIRY_SECONDS", "300"))

settings = Settings()