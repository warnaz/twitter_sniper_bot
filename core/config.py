import os
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    API_KEY: str

    LOG_LEVEL: str = "INFO"


settings = Settings()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PROXY = os.getenv("PROXY")

FAKE_TOKENS = [
    'BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'ADA', 'DOGE', 'XRP', 'DOT', 'UNI',
    'LTC', 'SOL', 'LINK', 'BCH', 'XLM', 'THETA', 'FIL', 'TRX', 'USDP', 'WBTC',
    'AAVE', 'EOS', 'XTZ', 'SNX', 'XMR', 'VET', 'ETC', 'QNT', 'DAI', 'NEO',
    'ATOM', 'MKR', 'AVAX', 'CRV', 'ALGO', 'COMP', 'ZEC', 'ENJ', 'MANA', 'BAT',
    'SUSHI', 'YFI', 'UMA', 'BTT', 'ONT', 'FTT', 'AXS', 'WAVES', 'HT', 'CAKE'
]