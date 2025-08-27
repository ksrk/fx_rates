import time
from typing import Any
from structlog.stdlib import get_logger

log = get_logger()


class FxCache:
    def __init__(self, seconds: int=3):
        self.ttl: int = seconds
        self._cache: dict[str, tuple[float, Any]] = {}

    def set(self, key: str, value: float) -> None:
        log.info(f"Setting cache '{key}' to '{value}'")
        self._cache[key] = (time.time(), value)

    def get(self, key: str) -> float | None:
        values = self._cache.get(key)
        if not values:
            return None

        ts, value = values
        if time.time() - ts > self.ttl:
            log.info(f"Cache expired for '{key}'")
            self._cache.pop(key, None)
            return None

        log.info(f"Getting value from cache '{key}' to '{value}'")
        return value
