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

    total = 0
    for token in tokens:
        logger.critical(total)
        total += 1

        token_info = await client.search_pairs_async(token.name)

        if not token_info:
            non_existent_tokens.append(token.name)
            continue

        for i in token_info:
            if not i.pair_created_at:
                continue

            token_date = i.pair_created_at.replace(tzinfo=None)
            print('token_data', token_date, "chain", i.chain_id)

            if i.chain_id == "solana" and token_date > datetime.datetime.now() - datetime.timedelta(days=3):
                print('pair_created_at', i.pair_created_at)
                logger.info(f"Token Symbol: {token.name}")
                logger.info(f"Token Address: {i.base_token.address}")
                tokens_addr.append(i.base_token.address)
                tokens_to_buy.append(token)
                break

            # non_existent_tokens.append(token)

    return tokens_addr
