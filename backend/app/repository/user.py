from typing import Any, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

DEFAULT_COLOR = "#8A2BE2"
ALLOWED_PATCH = {"display", "duck_color"}

class UsersRepository:
    """
    Repository for user-related database operations.

    Args:
        session (AsyncSession): The database session to use.
    """
    def __init__(self, session: AsyncSession):
        """
        Initializes the UsersRepository with a database session.

        Args:
            session (AsyncSession): The database session to use.
        """
        self.session = session

    async def get(self, user_id: str) -> Optional[User]:
        """
        Retrieves a user by their ID.

        Args:
            user_id (str): The user's unique identifier.

        Returns:
            Optional[User]: The user object if found, else None.
        """
        res = await self.session.execute(
            select(User)
            .where(User.id == user_id)
        )
        return res.scalar_one_or_none()
    
    async def create(self, uid: str, display: str, duck_color: str) -> User:
        """
        Adds a new user to the database.

        Args:
            uid (str): The user's unique identifier.
            display (str): The user's display name.
            duck_color (str): The user's duck color.

        Returns:
            User: The created user object.
        """
        user = User(id=uid, display=display, duck_color=duck_color)
        self.session.add(user)
        return user

    async def ensure_for_login(self, user_id: str, display: str, *, default_color: str = DEFAULT_COLOR) -> User:
        """
        Upsert for login: creates the user if missing, otherwise refreshes 'display'.
        Does not modify duck_color if the user already exists.

        Args:
            user_id (str): The user's unique identifier.
            display (str): The user's display name.
            default_color (str, optional): Default duck color if creating a new user.

        Returns:
            User: The user object (created or updated).
        """
        user = await self.get(user_id)
        if user:
            if user.display != display:
                await self.session.execute(
                    update(User)
                    .where(User.id == user_id)
                    .values(display=display)
                )
                user.display = display
            return user
        user = User(id=user_id, display=display, duck_color=default_color)
        self.session.add(user)
        return user

    async def patch(self, user_id: str, changes: dict[str, Any]) -> User:
        """
        Applies a whitelist patch to the user (only 'display' and 'duck_color').
        Returns the updated user object.

        Args:
            user_id (str): The user's unique identifier.
            changes (dict[str, Any]): Dictionary of changes to apply.

        Returns:
            User: The updated user object.

        Raises:
            ValueError: If the user is not found.
        """
        user = await self.get(user_id)
        if user is None:
            raise ValueError("User not found")
        for k, v in changes.items():
            if k in ALLOWED_PATCH:
                setattr(user, k, v)
        return user