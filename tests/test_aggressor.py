"""
Tests for Trade Direction & Aggressor Order Flow Engine.
"""

import numpy as np
import pandas as pd
import pytest
from src.aggressor import (
    classify_trade_direction_lee_ready,
    classify_trade_direction_quote_rule,
    calculate_signed_order_flow,
)


def test_lee_ready_basic_rule():
    prices = np.array([100.0, 100.5, 100.5, 100.2, 100.2, 100.8])
    signs = classify_trade_direction_lee_ready(prices, initial_direction=1)

    # 1st trade: 1 (initial)
    # 2nd trade: 100.5 > 100.0 -> +1 (uptick)
    # 3rd trade: 100.5 == 100.5 -> +1 (zero-uptick: retains previous +1)
    # 4th trade: 100.2 < 100.5 -> -1 (downtick)
    # 5th trade: 100.2 == 100.2 -> -1 (zero-downtick: retains previous -1)
    # 6th trade: 100.8 > 100.2 -> +1 (uptick)
    expected = np.array([1, 1, 1, -1, -1, 1])
    np.testing.assert_array_equal(signs, expected)


def test_quote_rule():
    prices = np.array([100.5, 99.8, 100.0])
    bids = np.array([100.0, 99.5, 99.9])
    asks = np.array([100.2, 100.1, 100.1])
    # Midpoints: [100.1, 99.8, 100.0]
    # Trade 1: 100.5 > 100.1 -> +1
    # Trade 2: 99.8 == 99.8 -> quote midpoint match -> falls back to Lee-Ready (99.8 < 100.5) -> -1
    # Trade 3: 100.0 == 100.0 -> falls back to Lee-Ready (100.0 > 99.8) -> +1
    signs = classify_trade_direction_quote_rule(prices, bids, asks, initial_direction=1)
    np.testing.assert_array_equal(signs, np.array([1, -1, 1]))


def test_signed_order_flow_dataframe():
    df = pd.DataFrame({
        "timestamp": ["2026-10-01 10:00:00", "2026-10-01 10:00:01", "2026-10-01 10:00:02"],
        "price": [150.0, 150.5, 150.2],
        "volume": [100, 200, 300]
    })

    res = calculate_signed_order_flow(df)
    assert "direction" in res.columns
    assert "signed_volume" in res.columns
    assert "dollar_volume" in res.columns
    assert "signed_dollar_volume" in res.columns

    # Check signed volumes: [100, 200, -300]
    np.testing.assert_array_equal(res["signed_volume"].values, [100, 200, -300])
    assert res["dollar_volume"].iloc[0] == 150.0 * 100
