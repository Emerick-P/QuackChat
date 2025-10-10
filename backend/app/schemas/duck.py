from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class DuckPatch(BaseModel):
    """Schema for updating duck color via PATCH requests."""
    duck_color: Optional[str] = Field(default=None, pattern=r"^#[A-Fa-f0-9]{6}$", description="Hex color code")
    model_config = ConfigDict(extra="forbid") # Forbid extra fields

class DuckOut(BaseModel):
    """Schema for duck color response data."""
    duck_color: str