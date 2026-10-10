"""
Information-Driven Bar Sampling Engine.

Implements Marcos López de Prado's standard and advanced bar sampling methods:
- Standard: Time Bars, Tick Bars, Volume Bars, Dollar Bars
- Information-Driven: Dollar Imbalance Bars (DIB), Volume Imbalance Bars (VIB)
"""

from typing import Union, Optional, Dict, Any, List
import numpy as np
import pandas as pd
from .aggressor import classify_trade_direction_lee_ready


def _format_bar_records(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """Helper to convert list of bar dictionaries into a formatted DataFrame."""
    if not records:
        return pd.DataFrame(columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "dollar_volume", "vwap", "tick_count", "duration_seconds", "log_returns"
        ])

    df = pd.DataFrame(records)
    df["log_returns"] = np.log(df["close"] / df["close"].shift(1))
    df["log_returns"] = df["log_returns"].fillna(0.0)
    return df


def extract_time_bars(
    df_ticks: pd.DataFrame,
    freq: str = "5min",
    time_col: str = "timestamp",
    price_col: str = "price",
    volume_col: str = "volume"
) -> pd.DataFrame:
    """
    Standard calendar time bars resampled at fixed frequency (e.g., '1min', '5min').
    """
    df = df_ticks.copy()
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.sort_values(time_col).set_index(time_col)

    df["dollar_vol"] = df[price_col] * df[volume_col]

    resampled = df.resample(freq)

    o = resampled[price_col].first()
    h = resampled[price_col].max()
    l = resampled[price_col].min()
    c = resampled[price_col].last()
    v = resampled[volume_col].sum()
    dv = resampled["dollar_vol"].sum()
    cnt = resampled[price_col].count()

    bars = pd.DataFrame({
        "timestamp": o.index,
        "open": o.values,
        "high": h.values,
        "low": l.values,
        "close": c.values,
        "volume": v.values,
        "dollar_volume": dv.values,
        "tick_count": cnt.values
    }).dropna(subset=["open", "close"])

    bars["vwap"] = np.where(bars["volume"] > 0, bars["dollar_volume"] / bars["volume"], bars["close"])
    bars["duration_seconds"] = pd.to_timedelta(freq).total_seconds()
    bars["log_returns"] = np.log(bars["close"] / bars["close"].shift(1)).fillna(0.0)

    return bars.reset_index(drop=True)


def extract_tick_bars(
    df_ticks: pd.DataFrame,
    ticks_per_bar: int = 100,
    time_col: str = "timestamp",
    price_col: str = "price",
    volume_col: str = "volume"
) -> pd.DataFrame:
    """
    Tick bars sampled every N transactions.
    """
    times = pd.to_datetime(df_ticks[time_col]).values
    prices = df_ticks[price_col].values.astype(float)
    volumes = df_ticks[volume_col].values.astype(float)

    n = len(prices)
    records = []

    for start_idx in range(0, n, ticks_per_bar):
        end_idx = min(start_idx + ticks_per_bar, n)
        if start_idx >= end_idx:
            break

        chunk_prices = prices[start_idx:end_idx]
        chunk_vols = volumes[start_idx:end_idx]
        chunk_dv = chunk_prices * chunk_vols

        t_start = pd.to_datetime(times[start_idx])
        t_end = pd.to_datetime(times[end_idx - 1])
        dur = max(0.0, (t_end - t_start).total_seconds())

        sum_vol = float(np.sum(chunk_vols))
        sum_dv = float(np.sum(chunk_dv))
        vwap = float(sum_dv / sum_vol) if sum_vol > 0 else float(chunk_prices[-1])

        records.append({
            "timestamp": t_end,
            "open": float(chunk_prices[0]),
            "high": float(np.max(chunk_prices)),
            "low": float(np.min(chunk_prices)),
            "close": float(chunk_prices[-1]),
            "volume": sum_vol,
            "dollar_volume": sum_dv,
            "vwap": vwap,
            "tick_count": end_idx - start_idx,
            "duration_seconds": dur
        })

    return _format_bar_records(records)


def extract_volume_bars(
    df_ticks: pd.DataFrame,
    volume_threshold: float = 10000.0,
    time_col: str = "timestamp",
    price_col: str = "price",
    volume_col: str = "volume"
) -> pd.DataFrame:
    """
    Volume bars sampled every V units of volume traded.
    """
    times = pd.to_datetime(df_ticks[time_col]).values
    prices = df_ticks[price_col].values.astype(float)
    volumes = df_ticks[volume_col].values.astype(float)

    n = len(prices)
    records = []

    cum_vol = 0.0
    cum_dv = 0.0
    bar_ticks = 0
    bar_open = None
    bar_high = -np.inf
    bar_low = np.inf
    bar_start_time = None

    for i in range(n):
        p = prices[i]
        v = volumes[i]
        dv = p * v
        t = pd.to_datetime(times[i])

        if bar_open is None:
            bar_open = p
            bar_start_time = t

        bar_high = max(bar_high, p)
        bar_low = min(bar_low, p)
        cum_vol += v
        cum_dv += dv
        bar_ticks += 1

        if cum_vol >= volume_threshold:
            dur = max(0.0, (t - bar_start_time).total_seconds())
            vwap = cum_dv / cum_vol if cum_vol > 0 else p

            records.append({
                "timestamp": t,
                "open": bar_open,
                "high": bar_high,
                "low": bar_low,
                "close": p,
                "volume": cum_vol,
                "dollar_volume": cum_dv,
                "vwap": vwap,
                "tick_count": bar_ticks,
                "duration_seconds": dur
            })

            # Reset
            cum_vol = 0.0
            cum_dv = 0.0
            bar_ticks = 0
            bar_open = None
            bar_high = -np.inf
            bar_low = np.inf
            bar_start_time = None

    return _format_bar_records(records)


def extract_dollar_bars(
    df_ticks: pd.DataFrame,
    dollar_threshold: float = 1000000.0,
    time_col: str = "timestamp",
    price_col: str = "price",
    volume_col: str = "volume"
) -> pd.DataFrame:
    """
    Dollar bars sampled every D dollars traded (Price * Volume).
    
    López de Prado Standard: Restores statistical normality (IID),
    reduces heteroskedasticity, and adjusts bar sampling dynamically
    to market information arrival.
    """
    times = pd.to_datetime(df_ticks[time_col]).values
    prices = df_ticks[price_col].values.astype(float)
    volumes = df_ticks[volume_col].values.astype(float)

    n = len(prices)
    records = []

    cum_dv = 0.0
    cum_vol = 0.0
    bar_ticks = 0
    bar_open = None
    bar_high = -np.inf
    bar_low = np.inf
    bar_start_time = None

    for i in range(n):
        p = prices[i]
        v = volumes[i]
        dv = p * v
        t = pd.to_datetime(times[i])

        if bar_open is None:
            bar_open = p
            bar_start_time = t

        bar_high = max(bar_high, p)
        bar_low = min(bar_low, p)
        cum_vol += v
        cum_dv += dv
        bar_ticks += 1

        if cum_dv >= dollar_threshold:
            dur = max(0.0, (t - bar_start_time).total_seconds())
            vwap = cum_dv / cum_vol if cum_vol > 0 else p

            records.append({
                "timestamp": t,
                "open": bar_open,
                "high": bar_high,
                "low": bar_low,
                "close": p,
                "volume": cum_vol,
                "dollar_volume": cum_dv,
                "vwap": vwap,
                "tick_count": bar_ticks,
                "duration_seconds": dur
            })

            # Reset
            cum_dv = 0.0
            cum_vol = 0.0
            bar_ticks = 0
            bar_open = None
            bar_high = -np.inf
            bar_low = np.inf
            bar_start_time = None

    return _format_bar_records(records)


def extract_dollar_imbalance_bars(
    df_ticks: pd.DataFrame,
    expected_imbalance_window: int = 50,
    initial_threshold: float = 100000.0,
    time_col: str = "timestamp",
    price_col: str = "price",
    volume_col: str = "volume"
) -> pd.DataFrame:
    """
    Information-Driven Dollar Imbalance Bars (DIB).
    
    Bar is triggered when accumulated signed dollar imbalance
    exceeds dynamic expected dollar imbalance |theta_T| >= E[T] * |2 P[b=1] - 1|.
    """
    times = pd.to_datetime(df_ticks[time_col]).values
    prices = df_ticks[price_col].values.astype(float)
    volumes = df_ticks[volume_col].values.astype(float)

    n = len(prices)
    if n == 0:
        return _format_bar_records([])

    directions = classify_trade_direction_lee_ready(prices)

    records = []
    cum_imbalance = 0.0
    cum_dv = 0.0
    cum_vol = 0.0
    bar_ticks = 0
    bar_open = None
    bar_high = -np.inf
    bar_low = np.inf
    bar_start_time = None

    current_threshold = initial_threshold
    past_imbalances = []

    for i in range(n):
        p = prices[i]
        v = volumes[i]
        b = directions[i]
        dv = p * v
        signed_dv = b * dv
        t = pd.to_datetime(times[i])

        if bar_open is None:
            bar_open = p
            bar_start_time = t

        bar_high = max(bar_high, p)
        bar_low = min(bar_low, p)
        cum_vol += v
        cum_dv += dv
        cum_imbalance += signed_dv
        bar_ticks += 1

        if abs(cum_imbalance) >= current_threshold:
            dur = max(0.0, (t - bar_start_time).total_seconds())
            vwap = cum_dv / cum_vol if cum_vol > 0 else p

            records.append({
                "timestamp": t,
                "open": bar_open,
                "high": bar_high,
                "low": bar_low,
                "close": p,
                "volume": cum_vol,
                "dollar_volume": cum_dv,
                "vwap": vwap,
                "tick_count": bar_ticks,
                "duration_seconds": dur,
                "imbalance": cum_imbalance
            })

            past_imbalances.append(abs(cum_imbalance))
            if len(past_imbalances) >= 5:
                # Update rolling threshold via exponentially weighted moving average
                recent = past_imbalances[-expected_imbalance_window:]
                current_threshold = max(initial_threshold * 0.2, float(np.mean(recent)))

            # Reset
            cum_imbalance = 0.0
            cum_dv = 0.0
            cum_vol = 0.0
            bar_ticks = 0
            bar_open = None
            bar_high = -np.inf
            bar_low = np.inf
            bar_start_time = None

    return _format_bar_records(records)
