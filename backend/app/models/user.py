from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class User(Base):
    """
    SQLAlchemy model representing a user of the application.

    Attributes:
        id (str): Unique identifier for the user (e.g., "twitch:abcd").
        display (str): Display name of the user.
        duck_color (str): Color associated with the user's duck.
        created_at (datetime): Timestamp when the user was created.
        updated_at (datetime): Timestamp when the user was last updated.
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # ex: "twitch:abcd"
    display: Mapped[str] = mapped_column(String(40), nullable=False)
    duck_color: Mapped[str] = mapped_column(String(7), nullable=False, default="#8A2BE2")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!r} display={self.display!r} duck_color={self.duck_color!r}>"