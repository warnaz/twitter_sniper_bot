import time

from database import (
    Tweet,
    TweetToken,
    Token,
    SessionLocal,
    TransactionHistory,
    Account,
    Infl,
)
from .twetter.schemas import ProcessedTweet
from .twetter.schemas import Tweet as TweetSchema
from core.logger import logger

from sqlalchemy import delete, select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession


async def delete_data_from_db() -> None:
    flag = input("Are you sure you want to delete all data?: (y/n) ")

    if flag != "y":
        async with SessionLocal() as session:
            await session.execute(delete(TweetToken))
            await session.execute(delete(Tweet))
            await session.execute(delete(Token))
            await session.execute(delete(TransactionHistory))
            await session.execute(delete(Account))
            await session.commit()


async def check_tweet_exists(session: AsyncSession, tweet_id: int) -> bool:
    result = await session.execute(select(Tweet).where(Tweet.tweet_id == tweet_id))
    return result.scalars().first() is not None


async def insert_tweet(session: AsyncSession, tweet: ProcessedTweet) -> Tweet:
    tweet_obj = Tweet(tweet_id=tweet.id, create_at=tweet.created_at, text=tweet.text)
    session.add(tweet_obj)
    await session.flush()
    return tweet_obj


async def handle_mentions(
    session: AsyncSession, tweet_id: int, created_at, mentions: list[str]
) -> None:
    for mention in mentions:
        result = await session.execute(select(Token).where(Token.name == mention))
        token = result.scalars().first()
        if token:
            stmt = (
                update(Token)
                .where(Token.id == token.id)
                .values(
                    mention_count=Token.mention_count + 1, update_at=int(time.time())
                )
            )
            await session.execute(stmt)
        else:
            token = Token(name=mention, mention_count=1, update_at=int(created_at))
            session.add(token)
            await session.flush()

        tweet_token = TweetToken(tweet_id=tweet_id, token_id=token.id)
        session.add(tweet_token)


async def insert_tweets(tweets: list[ProcessedTweet]) -> list[Tweet]:
    async with SessionLocal() as session:
        for tweet in tweets:
            if await check_tweet_exists(session, tweet.id):
                continue

            tweet_obj = await insert_tweet(session, tweet)

            await handle_mentions(
                session, tweet_obj.id, tweet_obj.create_at, tweet.mentions
            )

        await session.commit()

    return tweets


async def insert_transaction_history(
    token_id: str,
    amount: int,
    price: int,
    type: str,
    status: str,
    transaction_hash: str,
) -> None:
    async with SessionLocal() as session:
        account = await get_first_account_from_db()
        token = await session.execute(select(Token).where(Token.id == token_id))

        transaction = TransactionHistory(
            account=account,
            token_id=token,
            amount=amount,
            price=price,
            gas=1_000_000,
            type=type,
            status=status,
            transaction_hash=transaction_hash,
        )

        session.add(transaction)
        await session.commit()


async def get(obj, session: AsyncSession, **kwargs) -> list:
    result = await session.execute(select(obj).filter_by(**kwargs))
    return result.scalars().all()


async def get_first_account_from_db() -> Account:
    async with SessionLocal() as session:
        result = await session.execute(select(Account))
        return result.scalars().first()


async def get_all_tweets() -> list[Tweet]:
    async with SessionLocal() as session:
        result = await session.execute(select(Tweet))
        return result.scalars().all()


async def get_tokens_by_ids(token_ids: list[int]) -> list[Token]:
    async with SessionLocal() as session:
        result = await session.execute(select(Token).where(Token.id.in_(token_ids)))
        return result.scalars().all()


async def get_transactions(
    session: AsyncSession, token_ids: list[int]
) -> list[TransactionHistory]:
    try:
        result = await session.execute(
            select(TransactionHistory).where(TransactionHistory.token_id.in_(token_ids))
        )
        return result.scalars().all()
    except Exception as e:
        return []


async def get_actual_tokens() -> list[Token]:
    time_range = int(time.time()) - 2 * 60 * 60

    async with SessionLocal() as session:
        result = await session.execute(
            select(Token).where(
                and_(time_range < Token.update_at, Token.update_at < int(time.time()))
            )
        )

        tokens = result.scalars().all()

        transaction = await get_transactions(
            session=session, token_ids=[t.id for t in tokens]
        )

        return [t for t in tokens if t.id not in [t.token_id for t in transaction]]


async def valid_tweets(tweets: list[TweetSchema]) -> list[TweetSchema]:
    valid_tweets = []
    db_tweets = [tweet.tweet_id for tweet in await get_all_tweets()]
    for tweet in tweets:
        if tweet.id in db_tweets:
            continue
        else:
            logger.info(f"Find new tweet: {tweet.id}")
            valid_tweets.append(tweet)

    return valid_tweets


async def get_accounts() -> list[Account]:
    async with SessionLocal() as session:
        result = await session.execute(select(Account))
        return result.scalars().all()


async def get_transaction_history() -> list[TransactionHistory]:
    try:
        async with SessionLocal() as session:
            result = await session.execute(
                select(TransactionHistory).where(
                    and_(
                        TransactionHistory.type == "buy",
                        TransactionHistory.status == "READY_TO_SELL",
                    )
                )
            )
            return result.scalars().all()
    except Exception as e:
        return []


async def get_infls() -> list[str]:
    async with SessionLocal() as session:
        result = await session.execute(select(Infl.name).where(Infl.status == True))
        return result.scalars().all()


async def add_infl(name: str) -> None:
    async with SessionLocal() as session:
        infl = Infl(name=name, status=True)
        session.add(infl)
        await session.commit()
