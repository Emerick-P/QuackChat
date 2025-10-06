from typing import Any, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

DEFAULT_COLOR = "#8A2BE2"
ALLOWED_PATCH = {"display", "duck_color"}

async def get_user(session: AsyncSession, user_id: str) -> Optional[User]:
    res = await session.execute(
        select(User)
        .where(User.id == user_id)
        )
    return res.scalar_one_or_none()

async def ensure_user_for_login(session: AsyncSession, user_id: str, display: str, *, default_color: str = DEFAULT_COLOR) -> User:
    """Login-only upsert: create if missing, otherwise only refresh 'display' (does not modify duck_color)."""
    user = await get_user(session, user_id)
    if user:
        if user.display != display:
            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(display=display)
            )
            await session.commit()
            user.display = display
        return user
    user = User(id=user_id, display=display, duck_color=default_color)
    session.add(user)
    await session.commit()
    return user

# async def set_duck_color(session: AsyncSession, user_id: str, color: str) -> None:
#     await session.execute(
#         update(User)
#         .where(User.id == user_id)
#         .values(duck_color=color)
#     )
#     await session.commit()

async def patch_user(session: AsyncSession, user_id: str, changes: dict[str, Any]) -> User:
    """Patch whitelisté (display, duck_color). Renvoie l'objet à jour."""
    user = await get_user(session, user_id)
    if user is None:
        raise ValueError("User not found")
    for k, v in changes.items():
        if k in ALLOWED_PATCH:
            setattr(user, k, v)
    await session.commit()
    return user