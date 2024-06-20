import datetime

from core.logger import logger
from services.dexscreener import DexscreenerClient
from services.crud import get_actual_tokens


async def find_tokens_addresses():
    client = DexscreenerClient()
    tokens = await get_actual_tokens()

    non_existent_tokens = []
    tokens_to_buy = []
    tokens_addr = []

    for token in tokens:
        token_info = await client.search_pairs_async(token.name)

        if not token_info:
            non_existent_tokens.append(token)
            continue

        for i in token_info:
            if not i.pair_created_at:
                continue

            token_date = i.pair_created_at.replace(tzinfo=None)
            print(token_date)

            if i.chain_id == "solana" and token_date > datetime.datetime.now() - datetime.timedelta(days=3):
                print(i.pair_created_at)
                logger.info(f"Token Symbol: {token.name}")
                logger.info(f"Token Address: {i.base_token.address}")
                tokens_addr.append(i.base_token.address)
                tokens_to_buy.append(token)
                break

            # non_existent_tokens.append(token)

    return tokens_addr
