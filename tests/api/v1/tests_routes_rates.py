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