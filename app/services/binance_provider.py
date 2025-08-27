from http import HTTPStatus
import httpx
from urllib.parse import urljoin
from structlog.stdlib import get_logger
from app.utils.cache import FxCache
from app.core.config import settings

logger = get_logger()

class BinanceWrapper:
    def __init__(self,
                 base_url: str = settings.BINANCE_BASE_URL,
                 ttl_seconds: int = settings.CACHE_TTL_SECONDS):
        self.base_url: str = str(base_url).rstrip('/')
        self.ttl_seconds: int = ttl_seconds
        self.cache = FxCache(ttl_seconds)

    async def get_currency_price(self, currency: str) -> float:

        cached = self.cache.get(currency)
        if cached:
            logger.info(f"Cached currency price", currency = currency, cache = cached)
            return cached

        params = {"symbol": f"BTC{currency}T"
                  if currency == 'USD' else f"BTC{currency}"}
        async with httpx.AsyncClient(timeout=5.0) as client:
            logger.info(f"Fetching currency price from binance",
                        currency=currency,
                        params=params)

            response = await client.get(urljoin(self.base_url,
                                                "api/v3/ticker/price"),
                                        params=params)
            if response.status_code != HTTPStatus.OK:
                raise RuntimeError(f"Failed to get currency price for {currency}")
            price = float(response.json()['price'])
            self.cache.set(currency, price)
            logger.info(f"Currency price from binance", currency=currency, price=price)
            return price
