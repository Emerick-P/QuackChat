from typing import AsyncIterator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.repository.user import UsersRepository

class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UsersRepository(session)

    async def commit(self):
        await self.session.commit()

async def get_uow(session: AsyncSession = Depends(get_session)) -> AsyncIterator[UnitOfWork]:
    uow = UnitOfWork(session)
    try:
        yield uow
    finally:
        # Cleanup if necessary; Session will be closed by the dependency
        ...