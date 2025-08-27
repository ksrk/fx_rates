from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, Field


class Settings(BaseSettings):
    BINANCE_BASE_URL: AnyHttpUrl = Field(..., env="BINANCE_BASE_URL")
    CACHE_TTL_SECONDS: int = Field(..., env="CACHE_TTL_SECONDS")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()