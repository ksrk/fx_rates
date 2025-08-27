from structlog.stdlib import get_logger
from app.services.binance_provider import BinanceWrapper
from app.models.schemas import FxResponse

logger = get_logger()

class RateService:
    def __init__(self):
        self.binance = BinanceWrapper()

    async def get_rate(self, from_ccy: str, to_ccy: str, quantity: int) -> FxResponse:
        logger.info(f"Fetching rate",
                    from_ccy = from_ccy,
                    to_ccy = to_ccy,
                    quantity=quantity)
        from_ccy = from_ccy.upper()
        to_ccy = to_ccy.upper()

        # edge case
        if from_ccy == to_ccy:
            return FxResponse(currency=to_ccy, quantity=1.0 )

        source_ccy_price = await self.binance.get_currency_price(from_ccy)
        target_ccy_price = await self.binance.get_currency_price(to_ccy)
        result = (target_ccy_price / source_ccy_price) * quantity
        return FxResponse(currency=to_ccy, quantity=round(result,2) )
