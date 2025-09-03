import pytest

from app.services.fx_rate_overrides import FxRateOverrides


@pytest.fixture
def overrides():
    return FxRateOverrides()


def test_set_and_get_returns_value(overrides):
    overrides.set("USDEUR", 1.2345)
    assert overrides.get("USDEUR") == 1.2345


def test_get_missing_returns_none(overrides):
    assert overrides.get("GBPUSD") is None


def test_set_overwrites_existing_value(overrides):
    overrides.set("USDEUR", 1.2)
    overrides.set("USDEUR", 1.3)
    assert overrides.get("USDEUR") == 1.3


def test_clear_removes_key(overrides):
    overrides.set("USDEUR", 1.25)
    overrides.clear("USDEUR")
    assert overrides.get("USDEUR") is None


def test_clear_nonexistent_is_noop(overrides):
    assert overrides.get("USDEUR") is None
    overrides.clear("USDEUR")
    assert overrides.get("USDEUR") is None


def test_keys_are_case_sensitive(overrides):
    overrides.set("USDEUR", 1.2)
    assert overrides.get("usdEur") is None
    assert overrides.get("USDEUR") == 1.2