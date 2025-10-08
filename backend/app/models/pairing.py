from datetime import datetime, timezone, timedelta
from sqlalchemy import String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.settings import settings
from app.db.base import Base

def default_expiry() -> datetime:
    return utcnow() + timedelta(seconds=settings.PAIRING_CODE_EXPIRY_SECONDS)

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class PairingCode(Base):
    __tablename__ = "pairing_codes"

    # code displayed to guests (e.g., "A1B2C3")
    code: Mapped[str] = mapped_column(String(12), primary_key=True)

    # color chosen by the guest
    duck_color: Mapped[str] = mapped_column(String(7), nullable=False)

    # channel overlay to notify (to keep your current logic)
    channel: Mapped[str] = mapped_column(String(40), nullable=False, default="default")

    # expirations & timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=default_expiry, nullable=False)

    # once claimed, we note who took it (FK users.id)
    claimed_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        Index("ix_pairing_expires_at", "expires_at"),
    )
