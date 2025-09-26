from pydantic import BaseModel, ConfigDict, Field

class DuckPatch(BaseModel):
    color: str | None = Field(default=None, pattern=r"^#[A-Fa-f0-9]{6}$", description="Hex color code")
    model_config = ConfigDict(extra="forbid") # Forbid extra fields

class DuckOut(BaseModel):
    color: str