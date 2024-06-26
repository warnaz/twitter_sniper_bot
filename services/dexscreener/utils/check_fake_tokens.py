import re
from core.config import FAKE_TOKENS


def check_tokens(token):
    clean_token1 = re.sub(r'[^A-Za-z0-9]', '', token)

    if clean_token1.upper() not in FAKE_TOKENS:
        return True
    else:
        return False
