from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Configure application settings. These should be filled from envvars first, .env files second.
    """

    database_echo: bool = Field(False)
    database_url: str = "./database.db"


@lru_cache(None)
def get_settings() -> Settings:
    """
    Get an instance of the `Settings`.

    @lru_cache ensures that there is only a single `Settings` that we can use
    :return:
    """
    return Settings()
