"""
Tests for Information-Driven and Standard Bar Extractors.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from src.bars import (
    extract_time_bars,
    extract_tick_bars,
    extract_volume_bars,
    extract_dollar_bars,
    extract_dollar_imbalance_bars,
)


@pytest.fixture
def sample_ticks():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "sample_ticks.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    
    # Fallback synthetic ticks if file not present
    np.random.seed(42)
    n = 1000
    times = pd.date_range("2026-10-01 09:30:00", periods=n, freq="500ms")
    prices = 100.0 + np.cumsum(np.random.normal(0, 0.05, size=n))
    volumes = np.random.randint(10, 500, size=n)
    return pd.DataFrame({"timestamp": times, "price": prices, "volume": volumes})


def _assert_ohlc_invariants(df_bars: pd.DataFrame):
    assert not df_bars.empty, "Bars DataFrame must not be empty"
    for col in ["open", "high", "low", "close", "volume", "dollar_volume", "vwap", "log_returns"]:
        assert col in df_bars.columns, f"Missing required column: {col}"

    # OHLC Invariants: Low <= Open, Close <= High; Low <= High
    assert (df_bars["low"] <= df_bars["high"] + 1e-6).all(), "Low must be <= High"
    assert (df_bars["low"] <= df_bars["open"] + 1e-6).all(), "Low must be <= Open"
    assert (df_bars["low"] <= df_bars["close"] + 1e-6).all(), "Low must be <= Close"
    assert (df_bars["high"] >= df_bars["open"] - 1e-6).all(), "High must be >= Open"
    assert (df_bars["high"] >= df_bars["close"] - 1e-6).all(), "High must be >= Close"
    assert (df_bars["volume"] > 0).all(), "Volume must be strictly positive"


def test_time_bars(sample_ticks):
    bars = extract_time_bars(sample_ticks, freq="1min")
    _assert_ohlc_invariants(bars)
    assert len(bars) > 0


def test_tick_bars(sample_ticks):
    bars = extract_tick_bars(sample_ticks, ticks_per_bar=100)
    _assert_ohlc_invariants(bars)
    # Check that each bar (except possibly last) contains 100 ticks
    assert (bars["tick_count"].iloc[:-1] == 100).all()


def test_volume_bars(sample_ticks):
    bars = extract_volume_bars(sample_ticks, volume_threshold=5000.0)
    _assert_ohlc_invariants(bars)
    # Volume of each bar should be >= 5000
    assert (bars["volume"] >= 5000.0).all()


def test_dollar_bars(sample_ticks):
    bars = extract_dollar_bars(sample_ticks, dollar_threshold=500000.0)
    _assert_ohlc_invariants(bars)
    # Dollar volume of each bar should be >= 500,000
    assert (bars["dollar_volume"] >= 500000.0).all()


def test_dollar_imbalance_bars(sample_ticks):
    bars = extract_dollar_imbalance_bars(sample_ticks, initial_threshold=100000.0)
    _assert_ohlc_invariants(bars)
    assert len(bars) > 0
    assert "imbalance" in bars.columns
