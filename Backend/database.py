from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/cv_db")

# Asynchronous engine for database interaction
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async def init_db():
    """Creates database tables on application startup."""
    async with engine.begin() as conn:
        # Uncomment to reset the database
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    """Dependency to get a database session for each request."""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session