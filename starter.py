import asyncio

from services.dexscreener.run_screener import find_tokens_addresses
from services.twetter.run_twetter import process_tweets
from services.raydium.swap.buy import buy_token

from core.config import PRIVATE_KEY
from core.logger import logger



async def start():
    while True:
        logger.info("Start")
        # await process_tweets()
        token_addresses = await find_tokens_addresses()

        # for token_address in token_addresses:
        #     await buy_token(
        #         token_address=token_address,
        #         amount_in=0.001115797,
        #         private_key=PRIVATE_KEY
        #     )


if __name__ == "__main__":
    asyncio.run(start())
