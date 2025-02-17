from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import repository
from app.config import config
from app.repository.sqlalchemy import sarepositories


engine = create_async_engine(config.async_dsn)
pg_async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class SAUnitOfWork(repository.AbstractUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.user = sarepositories.UserRepository(self.session)
        self.user_action = sarepositories.UserActionRepository(self.session)
        self.format = sarepositories.FormatRepository(self.session)
        self.format_cross = sarepositories.FormatCrossRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
