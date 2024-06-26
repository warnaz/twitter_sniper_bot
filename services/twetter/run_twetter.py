import asyncio

from services.twetter.schemas import Tweet
from services.crud import insert_tweets, get_infls, add_infl
from services.twetter.parser import Twetter
from services.twetter.schemas import ProcessedTweet
from services.twetter.gpt_processr import TweetProcessor

from core.logger import logger


async def process_tweets():
    logger.info("Start Process Tweets")
    twetter = Twetter(
        # "6fa050bcee25e01b416533cd44775793fac1eb5c",
        None,
        "alimamedzzz:kHbm8ZCqqc@185.248.51.48:59100",
    )
    await twetter.start()

    # infls = [
    #     "cozypront",
    #     "Solana_Emperor",
    #     "CryptoGodJohn",
    #     "leonardnftpage",
    #     "MoonOverlord",
    #     "CryptoAnglio",
    #     "solana_king",
    #     "SolJakey",
    #     "0xDekadente",
    #     "ASTAlavistaSOL",
    #     "SolanaSensei",
    #     "SOLBigBrain",
    #     "SolanaLegend",
    #     "3orovik",
    #     "sibeleth",
    #     "Rewkang",
    #     "crypto_bitlord7",
    #     "farokh",
    #     "rajgokal",
    #     "seedphrase",
    #     "0xMert_",
    #     "GordonGoner",
    #     "notthreadguy",
    #     "beaniemaxi",
    #     "IvanOnTech",
    #     "SpiderCrypto0x",
    #     "Noahhweb3",
    #     "kenwgmi",
    #     "oCalebSol",
    #     "itstylersays",
    #     "MrBigWhaleREAL",
    #     "shahh",
    #     "MinisterOfNFTs",
    # ]

    # for infl in infls:
    #     await add_infl(infl)

    infls = await get_infls()
    infls_tweets = await twetter.get_butch_posts(infls, posts_count=2)

    processor = TweetProcessor()
    processed_tweets: list[ProcessedTweet] = []

    for tweets in infls_tweets:
        processed_tweets.extend(await processor.process(tweets))

    logger.info("Insert Tweets to DataBase")
    await insert_tweets(processed_tweets)
