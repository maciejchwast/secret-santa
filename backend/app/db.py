from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, future=True, echo=False)
async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
