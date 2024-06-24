import asyncio
from core.config import PRIVATE_KEY
from services.raydium.swap.buy import buy_token
from services.dexscreener.run_screener import find_tokens_addresses


tokens = asyncio.run(find_tokens_addresses())
    