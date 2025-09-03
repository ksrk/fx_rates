from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, Field
from structlog.stdlib import get_logger
logger = get_logger()

class Settings(BaseSettings):
    binance_base_url: AnyHttpUrl = Field(..., env="BINANCE_BASE_URL")
    cache_ttl_seconds: int = Field(..., env="CACHE_TTL_SECONDS")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()