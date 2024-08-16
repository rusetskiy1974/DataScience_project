from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL


engine = create_async_engine(DATABASE_URL, echo=False)


async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_database() -> async_session:
    async with async_session() as session:
        yield session
