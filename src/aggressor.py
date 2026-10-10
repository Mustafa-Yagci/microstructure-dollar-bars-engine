"""
Microstructure Aggressor & Trade Direction Classification Engine.

Implements:
- Lee-Ready (1991) Tick Rule: b_t = sign(p_t - p_{t-1})
- Quote Midpoint Tick Rule (when bid/ask available)
- Signed Volume and Signed Dollar Value tracking
"""

from typing import Union, Optional
import numpy as np
import pandas as pd


def classify_trade_direction_lee_ready(
    prices: Union[pd.Series, np.ndarray],
    initial_direction: int = 1
) -> np.ndarray:
    """
    Classify trades into buyer-initiated (+1) or seller-initiated (-1)
    using the Lee & Ready (1991) tick rule algorithm.

    b_t = +1 if Delta p_t > 0
    b_t = -1 if Delta p_t < 0
    b_t = b_{t-1} if Delta p_t == 0

    Parameters
    ----------
    prices : pd.Series or np.ndarray
        Array of transaction prices.
    initial_direction : int, default 1
        Assumed sign for the initial trade (+1 for buy, -1 for sell).

    Returns
    -------
    np.ndarray
        Array of signs {-1, +1} with same length as prices.
    """
    p = np.asarray(prices, dtype=float)
    n = len(p)
    if n == 0:
        return np.array([], dtype=int)
    if n == 1:
        return np.array([initial_direction], dtype=int)

    diffs = np.diff(p)
    signs = np.zeros(n, dtype=int)
    signs[0] = initial_direction

    for i in range(1, n):
        d = diffs[i - 1]
        if d > 1e-9:
            signs[i] = 1
        elif d < -1e-9:
            signs[i] = -1
        else:
            signs[i] = signs[i - 1]

    return signs


def classify_trade_direction_quote_rule(
    prices: Union[pd.Series, np.ndarray],
    bids: Union[pd.Series, np.ndarray],
    asks: Union[pd.Series, np.ndarray],
    initial_direction: int = 1
) -> np.ndarray:
    """
    Classify trades using the quote midpoint rule with Lee-Ready fallback.

    If p_t > mid_t -> +1 (buyer-initiated)
    If p_t < mid_t -> -1 (seller-initiated)
    If p_t == mid_t -> apply Lee-Ready tick test
    """
    p = np.asarray(prices, dtype=float)
    b = np.asarray(bids, dtype=float)
    a = np.asarray(asks, dtype=float)
    n = len(p)

    if n == 0:
        return np.array([], dtype=int)

    midpoints = (b + a) / 2.0
    signs = np.zeros(n, dtype=int)
    signs[0] = initial_direction

    lr_signs = classify_trade_direction_lee_ready(p, initial_direction)

    for i in range(n):
        diff = p[i] - midpoints[i]
        if diff > 1e-9:
            signs[i] = 1
        elif diff < -1e-9:
            signs[i] = -1
        else:
            signs[i] = lr_signs[i]

    return signs


def calculate_signed_order_flow(
    df_ticks: pd.DataFrame,
    price_col: str = "price",
    volume_col: str = "volume"
) -> pd.DataFrame:
    """
    Enrich a tick dataframe with aggressor classification and signed flow.
    """
    df = df_ticks.copy()
    if price_col not in df.columns or volume_col not in df.columns:
        raise ValueError(f"Columns {price_col} and {volume_col} must exist in DataFrame.")

    prices = df[price_col].values
    volumes = df[volume_col].values

    direction = classify_trade_direction_lee_ready(prices)
    signed_vol = direction * volumes
    dollar_vol = prices * volumes
    signed_dollar_vol = direction * dollar_vol

    df["direction"] = direction
    df["signed_volume"] = signed_vol
    df["dollar_volume"] = dollar_vol
    df["signed_dollar_volume"] = signed_dollar_vol

    return df
