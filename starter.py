import asyncio

from services.dexscreener.run_screener import find_tokens_addresses, check_tokens_price
from services.twetter.run_twetter import process_tweets
from services.raydium.swap.buy import buy_token

from services.crud import insert_transaction_history

from core.config import PRIVATE_KEY
from core.logger import logger


async def start():
    while True:
        logger.info("Start")
        await process_tweets()
        tokens_addr_price: dict = await find_tokens_addresses()
        logger.info(f"Find new tokens from twitter: {tokens_addr_price}")

        # return
        amount_in = 0.0001115797

        for token in tokens_addr_price:
            message, txid_string_sig = await buy_token(
                token_address=tokens_addr_price[token]["token_addr"],
                amount_in=amount_in,
                private_key=PRIVATE_KEY,
            )

            await insert_transaction_history(
                token_id=tokens_addr_price[token]["token_addr"],
                price=tokens_addr_price[token]["price_usd"],
                amount=amount_in,
                type="buy",
                status="READY_TO_SELL",
                transaction_hash=txid_string_sig
            )

        sell_tokens = await check_tokens_price()
        for token in sell_tokens:
            amount = token.amount * token.buy_price
            curetn_amount = token.price_native * token.amount

            sell_amount = curetn_amount - (curetn_amount - amount)

            await buy_token(
                token_address=token.address,
                amount_in=sell_amount,
                private_key=PRIVATE_KEY,
                sell=True
            )
        
        time_sleep = 60
        logger.info(f"Sleep: {time_sleep}")
        await asyncio.sleep(time_sleep)


if __name__ == "__main__":
    asyncio.run(start())
