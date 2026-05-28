from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from src.core.config import settings



# engine = create_async_engine(DATABASE_URL)
# new_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class DataBaseHelper:
    def __init__(
            self,
            url : str,
            echo : bool = False,
            echo_pool : bool = False,
            max_overflow : int = 10,
            pool_size : int = 5,
                ):
        self.engine : AsyncEngine = create_async_engine(
            url = url,
            echo = echo,
            echo_pool = echo_pool,
            max_overflow = max_overflow,
            pool_size = pool_size,
        )

        self.session_factory : async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush = False,
            autocommit = False,
            expire_on_commit=False,
        )

    async def dispose_engine(self,):
        await self.engine.dispose()
            

    async def get_session(self,) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session


database = DataBaseHelper(
    url = settings.database.url,
    echo = settings.database.echo,
    echo_pool = settings.database.echo_pool,
    max_overflow = settings.database.max_overflow,
    pool_size = settings.database.pool_size
)

class Base(DeclarativeBase):
    pass