import datetime

from core.logger import logger
from database import TransactionHistory
from services.dexscreener import DexscreenerClient
from services.crud import get_actual_tokens, get_transaction_history, get_tokens_by_ids
from services.dexscreener.models import SellToken


async def check_tokens_price() -> list[SellToken]:
    result = []

    tx = await get_transaction_history()
    tokens = await get_tokens_by_ids([i.token_id for i in tx])

    for token in tokens:
        price_native, price_usd, address = await get_token_price(token.name)

        if not price_native:
            continue

        for i in tx:
            if i.token_id == token.id and i.price / price_native > 2:
                result.append(
                    SellToken(
                        address=address,
                        name=token.name,
                        amount=i.amount,
                        buy_price=i.price,
                        price_native=price_native,
                        price_usd=price_usd,
                    )
                )

    return result


async def get_token_price(token_name: str):
    client = DexscreenerClient()

    token_info = await client.search_pairs_async(token_name)

    if not token_info:
        return None

    for i in token_info:
        if i.chain_id == "solana" and i.quote_token == "SOL":
            return i.price_native, i.price_usd, i.base_token.address


class Token:
    def __init__(self) -> None:
        self.name = "DUKO"


async def find_tokens_addresses() -> dict:
    client = DexscreenerClient()
    # tokens = await get_actual_tokens()
    tokens = [Token()]

    non_existent_tokens = []
    tokens_to_buy = []
    tokens_addr_price = {}

    total = 0
    for token in tokens:
        logger.critical(total)
        total += 1
        print(token.name)

        token_info = await client.search_pairs_async(token.name)

        if not token_info:
            non_existent_tokens.append(token.name)
            continue

        for i in token_info:
            if not i.pair_created_at:
                continue

            logger.info(f"Price: Native: {i.price_native} | USD: {i.price_usd}")

            token_date = i.pair_created_at.replace(tzinfo=None)
            print('token_data', token_date, "chain", i.chain_id)

            if i.chain_id == "solana" and token_date < datetime.datetime.now() - datetime.timedelta(days=3):
                print(i.pair_created_at)
                logger.info(f"Token Symbol: {token.name}")
                logger.info(f"Token Address: {i.base_token.address}")
                tokens_addr_price[token.name] = {"token_addr": i.base_token.address, "price_usd": i.price_usd}
                tokens_to_buy.append(token)
                break

            # non_existent_tokens.append(token)

    return tokens_addr_price
