"""
Tests for Volume-Synchronized Probability of Toxicity (VPIN) & Kyle's Lambda.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from src.vpin import VPINEngine


@pytest.fixture
def sample_ticks():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "sample_ticks.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    
    # Synthetic fallback
    np.random.seed(42)
    n = 2000
    times = pd.date_range("2026-10-01 09:30:00", periods=n, freq="200ms")
    prices = 150.0 + np.cumsum(np.random.normal(0, 0.02, size=n))
    volumes = np.random.randint(50, 500, size=n)
    return pd.DataFrame({"timestamp": times, "price": prices, "volume": volumes})


def test_vpin_bounded_between_zero_and_one(sample_ticks):
    engine = VPINEngine(bucket_volume=10000.0, window_buckets=20)
    df_vpin = engine.compute_vpin(sample_ticks)

    assert not df_vpin.empty
    assert "vpin" in df_vpin.columns
    assert "vpin_pct" in df_vpin.columns

    # VPIN must be strictly bounded in [0.0, 1.0]
    assert (df_vpin["vpin"] >= 0.0).all()
    assert (df_vpin["vpin"] <= 1.0).all()


def test_vpin_toxic_flow_sensitivity():
    """Test that pure one-directional selling pressure produces high VPIN."""
    n = 1000
    times = pd.date_range("2026-10-01 09:30:00", periods=n, freq="100ms")
    # Strictly descending price = 100% sell initiated trades
    prices = 100.0 - np.arange(n) * 0.05
    volumes = np.ones(n) * 100

    df_toxic = pd.DataFrame({"timestamp": times, "price": prices, "volume": volumes})

    engine = VPINEngine(bucket_volume=2000.0, window_buckets=10)
    df_vpin = engine.compute_vpin(df_toxic)

    # With 100% sell pressure, order imbalance per bucket is exactly V
    # So rolling VPIN should approach 1.0 (or 100%)
    final_vpin = df_vpin["vpin"].iloc[-1]
    assert final_vpin > 0.95


def test_kyles_lambda_regression():
    # Synthetic data with known positive price impact: delta P = 0.0005 * imbalance + noise
    np.random.seed(42)
    imbalances = np.random.normal(0, 1000, size=100)
    price_changes = 0.0005 * imbalances + np.random.normal(0, 0.05, size=100)

    df_test = pd.DataFrame({
        "order_imbalance": imbalances,
        "price_change": price_changes
    })

    res = VPINEngine.compute_kyles_lambda(df_test)
    assert "lambda" in res
    assert "r_squared" in res
    assert res["lambda"] > 0.0003
    assert res["r_squared"] > 0.50
