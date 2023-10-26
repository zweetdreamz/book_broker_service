from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from config import settings

engine = create_async_engine(f'{settings.DATABASE_URI}/{settings.DATABASE_NAME}', echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
