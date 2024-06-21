import asyncio

from services.dexscreener.run_screener import find_tokens_addresses, check_tokens_price
from services.twetter.run_twetter import process_tweets
from services.raydium.swap.buy import buy_token, sell

from core.config import PRIVATE_KEY
from core.logger import logger


async def start():
    while True:
        logger.info("Start")
        await process_tweets()
        token_addresses = await find_tokens_addresses()

        for token_address in token_addresses:
            await buy_token(
                token_address=token_address,
                amount_in=0.001115797,
                private_key=PRIVATE_KEY,
            )

        sell_tokens = await check_tokens_price()
        for token in sell_tokens:
            amount = token.amount * token.buy_price
            curetn_amount = token.price_native * token.amount

            sell_amount = curetn_amount - (curetn_amount - amount)

            await sell(
                token_address=token.address,
                amount_in=sell_amount,
                private_key=PRIVATE_KEY,
            )

        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(start())
