import os

os.environ.setdefault("BINANCE_BASE_URL", "https://api.binance.com")
os.environ.setdefault("CACHE_TTL_SECONDS", "60")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

import app.api.v1.routes_rates as routes_rates
from app.api.v1.routes_rates import router

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_fx_rate_success(client, monkeypatch):
    monkeypatch.setattr(routes_rates.service,
                        "get_rate",
                        AsyncMock(return_value={"quantity": 779.77,
                                                "currency": "GBP"})
                        )
    resp = client.get("/rates/fx-rate",
                      params={"ccy_from": "USD",
                              "ccy_to": "GBP",
                              "quantity": 1000})
    assert resp.status_code == 200
    assert resp.json() == {"quantity": 779.77, "currency": "GBP"}


def test_fx_rate_validation_422_bad_ccy_length(client):
    resp = client.get("/rates/fx-rate",
                      params={"ccy_from": "US", "ccy_to": "GBP",
                              "quantity": 1000})
    assert resp.status_code == 422
    body = resp.json()
    assert body["detail"][0]["loc"][0] in {"query", "body"}
    assert ("at least 3 characters" in body["detail"][0]["msg"] or
           "ensure this value has at least 3 characters" in
            body["detail"][0]["msg"])

def test_fx_rate_validation_422_quantity_le_zero(client):
    resp = client.get("/rates/fx-rate",
                      params={"ccy_from": "USD", "ccy_to": "GBP",
                              "quantity": 0})
    assert resp.status_code == 422

def test_fx_rate_400_value_error_from_service(client, monkeypatch):
    monkeypatch.setattr(
        routes_rates.service,
        "get_rate",
        AsyncMock(side_effect=ValueError("Unsupported currency pair")),
    )

    resp = client.get("/rates/fx-rate",
                      params={"ccy_from": "USD", "ccy_to": "XYZ",
                              "quantity": 1000})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Unsupported currency pair"

def test_fx_rate_500_generic_exception(client, monkeypatch):
    monkeypatch.setattr(
        routes_rates.service,
        "get_rate",
        AsyncMock(side_effect=Exception("boom")),
    )

    resp = client.get("/rates/fx-rate",
                      params={"ccy_from": "USD", "ccy_to": "GBP",
                              "quantity": 1000})
    assert resp.status_code == 500
    assert resp.json()["detail"] == "boom"


def test_fx_rate_override_success(client, monkeypatch):
    monkeypatch.setattr(
        routes_rates.service,
        "ccy_override",
        AsyncMock(
            return_value={
                "code": 200,
                "status": "success"
            }
        ),
    )

    resp = client.post(
        "/rates/fx-rate/override",
        json={"ccy_from": "usd", "ccy_to": "eur", "fx_rate": 1.234},
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "code": 200,
        "status": "success"
    }


def test_fx_rate_override_400_value_error(client, monkeypatch):
    monkeypatch.setattr(
        routes_rates.service,
        "ccy_override",
        AsyncMock(side_effect=ValueError("Value not allowed")),
    )

    resp = client.post(
        "/rates/fx-rate/override",
        json={"ccy_from": "usd", "ccy_to": "eur", "fx_rate": 1.234},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Value not allowed"

def test_fx_rate_override_500_generic_exception(client, monkeypatch):
        monkeypatch.setattr(
            routes_rates.service,
            "ccy_override",
            AsyncMock(side_effect=Exception("dummy")),
        )

        resp = client.post(
            "/rates/fx-rate/override",
            json={"ccy_from": "usd", "ccy_to": "eur", "fx_rate": 1.234},
        )
        assert resp.status_code == 500
        assert resp.json()["detail"] == "dummy"


def test_fx_rate_clear_success_accepts_slash_and_lowercase(client, monkeypatch):
    # Service returns a payload that already matches FxRateOverrideResponse
    async_mock = AsyncMock(
        return_value={
            "code": 200,
            "status": "success"
        }
    )
    monkeypatch.setattr(routes_rates.service, "clear_fx_rate_override", async_mock)

    resp = client.delete("/rates/fx-rate/clear", params={"ccy_pair": "usd/eur"})
    assert resp.status_code == 200
    assert resp.json() == {
        "code": 200,
        "status": "success"
    }

    async_mock.assert_awaited_once_with("USDEUR")

def test_fx_rate_clear_400_value_error(client, monkeypatch):
    monkeypatch.setattr(
        routes_rates.service,
        "clear_fx_rate_override",
        AsyncMock(side_effect=ValueError("No override set")),
    )

    resp = client.delete("/rates/fx-rate/clear", params={"ccy_pair": "USDEUR"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "No override set"


def test_fx_rate_clear_500_generic_exception(client, monkeypatch):
    monkeypatch.setattr(
        routes_rates.service,
        "clear_fx_rate_override",
        AsyncMock(side_effect=Exception("storage down")),
    )

    resp = client.delete("/rates/fx-rate/clear", params={"ccy_pair": "USDEUR"})
    assert resp.status_code == 500
    assert resp.json()["detail"] == "storage down"