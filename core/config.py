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
