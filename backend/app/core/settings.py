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

settings = Settings()