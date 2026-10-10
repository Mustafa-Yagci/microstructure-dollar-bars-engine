"""
Tests for Statistical Normality & Information Recovery Proofs.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from src.statistical_proofs import (
    compute_distribution_metrics,
    compare_bar_types,
    format_markdown_comparison_table,
)
from src.bars import extract_time_bars, extract_dollar_bars, extract_tick_bars, extract_volume_bars


@pytest.fixture
def sample_ticks():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "sample_ticks.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    
    np.random.seed(42)
    n = 2000
    times = pd.date_range("2026-10-01 09:30:00", periods=n, freq="200ms")
    prices = 150.0 + np.cumsum(np.random.normal(0, 0.02, size=n))
    volumes = np.random.randint(50, 500, size=n)
    return pd.DataFrame({"timestamp": times, "price": prices, "volume": volumes})


def test_distribution_metrics_gaussian():
    # True normal distribution should have near-zero excess kurtosis and low JB stat
    np.random.seed(42)
    gaussian_rets = np.random.normal(loc=0.0, scale=0.01, size=1000)
    metrics = compute_distribution_metrics(gaussian_rets)

    assert abs(metrics["skewness"]) < 0.2
    assert abs(metrics["kurtosis_excess"]) < 0.5
    assert metrics["jarque_bera_pvalue"] > 0.05  # Cannot reject normality


def test_distribution_metrics_fat_tailed():
    # Student's t distribution with df=3 (heavy fat tails)
    np.random.seed(42)
    fat_tailed_rets = np.random.standard_t(df=3, size=1000) * 0.01
    metrics = compute_distribution_metrics(fat_tailed_rets)

    assert metrics["kurtosis_excess"] > 2.0
    assert metrics["jarque_bera_stat"] > 50.0
    assert metrics["jarque_bera_pvalue"] < 0.01  # Normality strongly rejected


def test_compare_bar_types_on_ticks(sample_ticks):
    time_bars = extract_time_bars(sample_ticks, freq="1min")
    tick_bars = extract_tick_bars(sample_ticks, ticks_per_bar=100)
    vol_bars = extract_volume_bars(sample_ticks, volume_threshold=10000.0)
    dollar_bars = extract_dollar_bars(sample_ticks, dollar_threshold=1000000.0)

    comparison = compare_bar_types({
        "Time Bars (1m)": time_bars,
        "Tick Bars (100t)": tick_bars,
        "Volume Bars (10k)": vol_bars,
        "Dollar Bars ($1M)": dollar_bars
    })

    assert "summary" in comparison
    assert len(comparison["summary"]) == 4

    table_md = format_markdown_comparison_table(comparison)
    assert "| Bar Sampling Method |" in table_md
    assert "Dollar Bars ($1M)" in table_md
