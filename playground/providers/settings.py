from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Configure application settings. These should be filled from envvars first, .env files second.
    """
    database_echo: bool = Field(False)
    database_url: str = "./database.db"


@lru_cache(None)
def get_settings():
    return Settings()
