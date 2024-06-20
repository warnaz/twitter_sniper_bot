import time
from typing import AsyncGenerator

from sqlalchemy import (
    Column,
    CursorResult,
    Insert,
    Integer,
    BigInteger,
    Select,
    String,
    Update,
    ForeignKey,
)
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


from core.config import settings

DATABASE_URL = str(settings.DATABASE_URL)

async_engine = create_async_engine(DATABASE_URL)
Base_a = declarative_base()


class Base(Base_a):
    __abstract__ = True

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


metadata = Base.metadata


class TweetToken(Base):
    __tablename__ = "tweet_token"

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(Integer, ForeignKey("tweet.id"))
    token_id = Column(Integer, ForeignKey("token.id"))


class Tweet(Base):
    __tablename__ = "tweet"

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(BigInteger, unique=True, nullable=False)
    text = Column(String, nullable=False)
    create_at = Column(Integer, nullable=False)


class Token(Base):
    __tablename__ = "token"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    mention_count = Column(Integer, default=0, nullable=False)

    update_at = Column(Integer, default=lambda: int(time.time()), nullable=False)


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, nullable=False)
    private_key = Column(String, unique=True, nullable=False)


class TransactionHistory(Base):
    __tablename__ = "transaction_history"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("account.id"))
    token_id = Column(Integer, ForeignKey("token.id"))
    amount = Column(Integer, nullable=False)
    gas = Column(Integer, nullable=False)
    transaction_hash = Column(String, unique=True, nullable=False)

    create_at = Column(Integer, default=lambda: int(time.time()), nullable=False)


async def fetch_one(select_query: Select | Insert | Update):
    async with async_engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return cursor.first() if cursor.rowcount > 0 else None


async def fetch_all(select_query: Select | Insert | Update) -> list:
    async with async_engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return [r for r in cursor.all()]


async def execute(select_query: Insert | Update) -> None:
    async with async_engine.begin() as conn:
        return await conn.execute(select_query)


SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[SessionLocal, None]:
    async with SessionLocal() as session:
        yield session
