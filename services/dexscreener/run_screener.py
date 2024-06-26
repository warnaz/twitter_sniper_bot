import datetime

from core.logger import logger
from database import TransactionHistory
from services.dexscreener import DexscreenerClient
from services.crud import get_actual_tokens, get_transaction_history, get_tokens_by_ids
from services.dexscreener.models import SellToken

from .utils.check_fake_tokens import check_tokens


async def check_tokens_price() -> list[SellToken]:
    result = []

    tx = await get_transaction_history()
    logger.info("Found {} transactions".format(len(tx)))
    tokens = await get_tokens_by_ids([i.token_id for i in tx])

    for token in tokens:
        price_native, price_usd, address = await get_token_price(token.name)

        if not price_usd:
            continue

        for i in tx:
            if i.token_id == token.id and i.price / price_usd > 2:
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


class TestToken:
    def __init__(self) -> None:
        self.name = "BTC"


async def find_tokens_addresses() -> dict:
    client = DexscreenerClient()
    tokens = await get_actual_tokens()
    # tokens = [TestToken()]

    tokens_addr_price = {}

    for token in tokens:
        token_info = await client.search_pairs_async(token.name)

        for i in token_info:
            if not i.pair_created_at:
                continue

            token_date = i.pair_created_at.replace(tzinfo=None)

            if i.chain_id == "solana" and token_date > datetime.datetime.now() - datetime.timedelta(days=3):
                if check_tokens(i.base_token.symbol):
                    logger.info(f"Token Symbol: {token.name}")
                    logger.info(f"Token Address: {i.base_token.address}")
                    tokens_addr_price[token.name] = {"token_addr": i.base_token.address, "price_usd": i.price_usd}
                    break

    return tokens_addr_price
