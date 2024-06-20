import random
from solders.pubkey import Pubkey


LAMPORTS_PER_SOL = 1000000000
MAX_RETRIES = 5
RETRY_DELAY = 3

AMM_PROGRAM_ID = Pubkey.from_string('675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8')
SERUM_PROGRAM_ID = Pubkey.from_string('srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX')

GAS_PRICE = random.randint(200_000, 300_000)
GAS_LIMIT = random.randint(1_000_000, 2_000_000)