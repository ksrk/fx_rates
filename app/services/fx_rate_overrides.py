from structlog.stdlib import get_logger

logger = get_logger()

class FxRateOverrides:
    def __init__(self):
        self._ccy_pairs: dict[str, float] = {}

    def set(self, key: str, value: float) -> None:
        logger.info("set", ccy=self._ccy_pairs)
        logger.info(f"Setting fx rate '{key}' to '{value}'")
        self._ccy_pairs[key] = value

    def get(self, key: str) -> float | None:
        logger.info("get", ccy=self._ccy_pairs)
        logger.info("Getting overrided currency pair value", currency=key)
        return self._ccy_pairs.get(key)

    def clear(self, ccy_pair):
        logger.info("clear", ccy=self._ccy_pairs)
        logger.info("Clear the fx rate overrided", currency_pair=ccy_pair)
        if ccy_pair in self._ccy_pairs:
            del self._ccy_pairs[ccy_pair]