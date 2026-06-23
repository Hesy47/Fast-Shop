from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from application.shared import env_variables

db_url = env_variables.DATABASE_URL
db_echo = True if env_variables.DEBUG else False

engine = create_async_engine(
    db_url,
    echo=db_echo,
    pool_pre_ping=True,
    future=True,
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        try:
            yield session

        except Exception as database_error:
            await session.rollback()
            raise database_error

        finally:
            await session.close()
