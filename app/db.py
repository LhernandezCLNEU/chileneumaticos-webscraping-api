from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


# Choose DB engine based on environment
if settings.ENVIRONMENT.lower() == "development":
    # Use a local sqlite file for development to simplify setup
    DATABASE_URL = "sqlite+aiosqlite:///./dev.db"
    engine = create_async_engine(DATABASE_URL, future=True)
else:
    # Production: MySQL async driver
    DATABASE_URL = (
        f"mysql+asyncmy://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
    )
    engine = create_async_engine(DATABASE_URL, future=True)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
