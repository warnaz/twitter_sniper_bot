import time

from database import Tweet, TweetToken, Token, SessionLocal, TransactionHistory, Account
from .twetter.schemas import ProcessedTweet
from .twetter.schemas import Tweet as TweetSchema
from core.logger import logger

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession


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
    result = await session.execute(
        select(TransactionHistory).where(TransactionHistory.token_id.in_(token_ids))
    )
    return result.scalars().all()


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
