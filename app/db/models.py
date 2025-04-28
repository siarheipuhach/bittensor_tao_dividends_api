from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declared_attr
from sqlalchemy import Column, Integer, String, Float, DateTime

from app.config import settings

engine = create_async_engine(
    settings.postgres_dsn,
    echo=False,
    future=True,
)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class CustomBase:
    """Base class for all models with default table naming."""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


Base = declarative_base(cls=CustomBase)


class StakeAdjustment(Base):
    """Model for recording stake/unstake adjustments."""

    netuid = Column(Integer, nullable=False)
    hotkey = Column(String, nullable=False)
    sentiment_score = Column(Integer, nullable=False)
    action = Column(String, nullable=False)  # 'stake' or 'unstake'
    amount_tao = Column(Float, nullable=False)


async def get_db() -> AsyncSession:
    """FastAPI dependency to provide a database session."""
    async with async_session() as session:
        yield session


async def init_db() -> None:
    """Init database tables (should be called on startup)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
