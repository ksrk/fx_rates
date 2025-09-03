from fastapi import status
from structlog.stdlib import get_logger

from app.services.binance_provider import BinanceWrapper
from app.services.fx_rate_overrides import FxRateOverrides
from app.models.schemas import FxResponse, OverrideFxRateResponse

logger = get_logger()

class RateService:
    def __init__(self):
        self.binance = BinanceWrapper()
        self.fx_rate_overrides = FxRateOverrides()

    async def get_rate(self, from_ccy: str, to_ccy: str, quantity: int) -> FxResponse:
        logger.info(f"Fetching rate",
                    from_ccy = from_ccy,
                    to_ccy = to_ccy,
                    quantity=quantity)
        from_ccy = from_ccy.upper()
        to_ccy = to_ccy.upper()

        # edge case
        if from_ccy == to_ccy:
            return FxResponse(currency=to_ccy, quantity=1.0 * quantity)

        if override_fx_rate := self.fx_rate_overrides.get(f"{from_ccy}{to_ccy}"):
            return FxResponse(currency=to_ccy,
                              quantity=override_fx_rate * quantity)

        source_ccy_price = await self.binance.get_currency_price(from_ccy)
        target_ccy_price = await self.binance.get_currency_price(to_ccy)

        result = (target_ccy_price / source_ccy_price) * quantity
        return FxResponse(currency=to_ccy, quantity=round(result,2) )

    async def ccy_override(self, ccy_pair, value):
        self.fx_rate_overrides.set(ccy_pair, value)
        return OverrideFxRateResponse(
            code=status.HTTP_200_OK,
            status=f"Fx rate for {ccy_pair} set to {value}"
        )

    async def clear_fx_rate_override(self, ccy_pair):
        self.fx_rate_overrides.clear(ccy_pair=ccy_pair)
        return OverrideFxRateResponse(
            code=status.HTTP_200_OK,
            status=f"Fx rate set for {ccy_pair} is cleared"
        )



