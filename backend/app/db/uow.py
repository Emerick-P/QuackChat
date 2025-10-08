from typing import AsyncIterator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.repository.user import UsersRepository
from app.repository.pairing import PairingRepository

class UnitOfWork:
    """
    Unit of Work pattern for managing database transactions and repositories.

    Attributes:
        session (AsyncSession): The database session for this unit of work.
        users (UsersRepository): Repository for user operations.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UsersRepository(session)
        self.pairing = PairingRepository(session)

    async def commit(self):
        """Commits the current transaction."""
        await self.session.commit()

async def get_uow(session: AsyncSession = Depends(get_session)) -> AsyncIterator[UnitOfWork]:
    """
    Dependency provider for UnitOfWork.

    Yields:
        UnitOfWork: An instance with an active session.
    """
    uow = UnitOfWork(session)
    try:
        yield uow
    finally:
        # Cleanup if necessary; Session will be closed by the dependency
        ...