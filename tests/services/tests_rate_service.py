import pytest
from unittest.mock import AsyncMock

from app.services.rate_service import RateService

@pytest.mark.asyncio
async def test_get_rate_usd_to_gbp_success(monkeypatch):
    svc = RateService()
    svc.binance.get_currency_price = AsyncMock(side_effect=[111126.78, 86653.33])

    resp = await svc.get_rate("USD", "GBP", 1000)

    assert resp.currency == "GBP"
    assert resp.quantity == pytest.approx(779.77, rel=0, abs=1e-9)

    calls = svc.binance.get_currency_price.call_args_list
    assert calls[0].args[0] == "USD"
    assert calls[1].args[0] == "GBP"


@pytest.mark.asyncio
async def test_get_rate_uppercases_inputs(monkeypatch):
    svc = RateService()
    svc.binance.get_currency_price = AsyncMock(side_effect=[111126.78, 86653.33])

    _ = await svc.get_rate("usd", "gbp", 1000)

    calls = svc.binance.get_currency_price.call_args_list
    assert calls[0].args[0] == "USD"
    assert calls[1].args[0] == "GBP"


@pytest.mark.asyncio
async def test_get_rate_rounds_to_two_decimals(monkeypatch):
    svc = RateService()
    svc.binance.get_currency_price = AsyncMock(side_effect=[100.0, 77.777])

    resp = await svc.get_rate("USD", "GBP", 1)

    assert resp.currency == "GBP"
    assert resp.quantity == 0.78


@pytest.mark.asyncio
async def test_get_rate_same_currency_edge_case(monkeypatch):
    svc = RateService()
    svc.binance.get_currency_price = AsyncMock()

    resp = await svc.get_rate("eur", "eur", 1234)

    assert resp.currency == "EUR"
    assert resp.quantity == 1234.0
    svc.binance.get_currency_price.assert_not_called()


@pytest.mark.asyncio
async def test_get_rate_raises_on_binance_error(monkeypatch):
    svc = RateService()
    svc.binance.get_currency_price = AsyncMock(side_effect=RuntimeError("binance down"))

    with pytest.raises(RuntimeError, match="binance down"):
        await svc.get_rate("USD", "GBP", 1000)
