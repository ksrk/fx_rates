import pytest
import httpx
import respx

from app.services.binance_provider import BinanceWrapper

@pytest.mark.asyncio
async def test_get_currency_price_usd_maps_to_usdt_success():
    wrapper = BinanceWrapper(base_url="https://example.com", ttl_seconds=10)
    with respx.mock(assert_all_called=True) as router:
        route = router.get("https://example.com/api/v3/ticker/price").mock(
            return_value=httpx.Response(200, json={"price": "12345.67"})
        )

        price = await wrapper.get_currency_price("USD")

        assert price == 12345.67
        assert route.called

        req = route.calls[0].request
        assert req.url.params.get("symbol") == "BTCUSDT"

@pytest.mark.anyio
async def test_get_currency_price_non_usd_symbol_success():
    wrapper = BinanceWrapper(base_url="https://example.com", ttl_seconds=10)

    with respx.mock(assert_all_called=True) as router:
        route = router.get("https://example.com/api/v3/ticker/price").mock(
            return_value=httpx.Response(200, json={"price": "888.99"})
        )

        price = await wrapper.get_currency_price("GBP")

        assert price == 888.99
        assert route.called

        req = route.calls[0].request
        assert req.url.params.get("symbol") == "BTCGBP"

@pytest.mark.anyio
async def test_get_currency_price_uses_cache_on_second_call(monkeypatch):
    wrapper = BinanceWrapper(base_url="https://example.com", ttl_seconds=60)

    class DummyCache:
        def __init__(self):
            self.store = {}

        def get(self, key):
            return self.store.get(key)

        def set(self, key, value):
            self.store[key] = value

    wrapper.cache = DummyCache()

    with respx.mock() as router:
        route = router.get("https://example.com/api/v3/ticker/price").mock(
            return_value=httpx.Response(200, json={"price": "100.00"})
        )

        # First call -> network + cache set
        p1 = await wrapper.get_currency_price("EUR")
        assert p1 == 100.0
        assert route.call_count == 1

        # Second call -> should hit cache, not network
        p2 = await wrapper.get_currency_price("EUR")
        assert p2 == 100.0
        assert route.call_count == 1  # unchanged


@pytest.mark.anyio
async def test_get_currency_price_non_200_raises():
    wrapper = BinanceWrapper(base_url="https://example.com", ttl_seconds=10)

    with respx.mock(assert_all_called=True) as router:
        router.get("https://example.com/api/v3/ticker/price").mock(
            return_value=httpx.Response(500, json={"msg": "oops"})
        )

        with pytest.raises(RuntimeError) as exc:
            await wrapper.get_currency_price("USD")

        assert "Failed to get currency price for USD" in str(exc.value)