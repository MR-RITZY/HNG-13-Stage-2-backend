from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from contextlib import asynccontextmanager

from src import model
from src.config import settings
from src.log import app_error, app_info


DB_URL = (f"mysql+aiomysql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@"
          f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

async_engine = create_async_engine(DB_URL)
AsyncSessionMaker = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)

async def get_db():
    async with AsyncSessionMaker() as async_session:
        yield async_session



@asynccontextmanager
async def db_lifespan():
    try:
        app_info.info("Connecting to Database")
        async with async_engine.begin() as conn:
            app_info.info("Setting Up Database")
            await conn.run_sync(model.Base.metadata.create_all)
            await conn.commit()
            app_info.info("Database Set-up Successfully Completed")
            yield
    except Exception:
        app_error.error("Error Setting Up Database")
        raise
    finally:
        await async_engine.dispose()
        app_info.info("Disconnected from Database")
    