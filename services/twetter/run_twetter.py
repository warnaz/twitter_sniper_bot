import asyncio

from services.crud import insert_tweets
from services.twetter.parser import Twetter
from services.twetter.schemas import ProcessedTweet
from services.twetter.gpt_processr import TweetProcessor

from core.logger import logger


async def process_tweets():

    logger.info("Start Process Tweets")
    twetter = Twetter(
        "6fa050bcee25e01b416533cd44775793fac1eb5c",
        "dkhalidovstt:VBNsY2BRZW@185.248.51.166:59100",
    )
    await twetter.start()

    infls = [
        "SolanaSensei",
        "cozypront",
        "Solana_Emperor",
        "CryptoGodJohn",
        "leonardnftpage",
        "MoonOverlord",
        "CryptoAnglio",
        "SolanaLegend",
        "solana_king",
        "SolJakey",
        "0xDekadente",
        "ASTAlavistaSOL",
    ]

    infls_tweets = await twetter.get_butch_posts(infls, posts_count=2)
    processed_tweets: list[ProcessedTweet] = []

    for tweets in infls_tweets:
        processor = TweetProcessor()

        processed_tweets.extend(await processor.process(tweets))

    logger.info("Insert Tweets to DataBase")
    await insert_tweets(processed_tweets)