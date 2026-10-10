"""
Volume-Synchronized Probability of Toxicity (VPIN) & Kyle's Lambda Price Impact Engine.

Implements:
- Easley, López de Prado & O'Hara (2012) VPIN formulation.
- Kyle's Lambda (1985) market microstructure price impact coefficient.
"""

from typing import Union, Dict, Any, List, Optional
import numpy as np
import pandas as pd
from scipy import stats
from .aggressor import classify_trade_direction_lee_ready


class VPINEngine:
    """
    Computes VPIN (Volume-Synchronized Probability of Toxicity).
    
    Parameters
    ----------
    bucket_volume : float
        Fixed volume size V of each transaction bucket.
    window_buckets : int, default 50
        Number of buckets N used in rolling VPIN summation.
    """

    def __init__(
        self,
        bucket_volume: float = 10000.0,
        window_buckets: int = 50
    ):
        if bucket_volume <= 0:
            raise ValueError("bucket_volume must be positive.")
        if window_buckets < 1:
            raise ValueError("window_buckets must be >= 1.")

        self.bucket_volume = float(bucket_volume)
        self.window_buckets = int(window_buckets)

    def compute_vpin(
        self,
        df_ticks: pd.DataFrame,
        price_col: str = "price",
        volume_col: str = "volume",
        time_col: str = "timestamp"
    ) -> pd.DataFrame:
        """
        Slice continuous tick stream into equal-volume buckets and calculate rolling VPIN.
        """
        prices = df_ticks[price_col].values.astype(float)
        volumes = df_ticks[volume_col].values.astype(float)
        times = pd.to_datetime(df_ticks[time_col]).values

        n = len(prices)
        if n == 0:
            return pd.DataFrame(columns=["bucket_idx", "timestamp", "buy_volume", "sell_volume", "order_imbalance", "vpin"])

        directions = classify_trade_direction_lee_ready(prices)

        # Bucket accumulation
        buckets: List[Dict[str, Any]] = []
        curr_vol = 0.0
        curr_buy_vol = 0.0
        curr_sell_vol = 0.0
        bucket_time = None
        bucket_idx = 0

        for i in range(n):
            v_rem = volumes[i]
            p = prices[i]
            d = directions[i]
            t = pd.to_datetime(times[i])

            while v_rem > 0:
                space = self.bucket_volume - curr_vol
                v_fill = min(space, v_rem)

                if d == 1:
                    curr_buy_vol += v_fill
                else:
                    curr_sell_vol += v_fill

                curr_vol += v_fill
                v_rem -= v_fill
                bucket_time = t

                if curr_vol >= self.bucket_volume:
                    # Finalize bucket
                    imbalance = abs(curr_buy_vol - curr_sell_vol)
                    buckets.append({
                        "bucket_idx": bucket_idx,
                        "timestamp": bucket_time,
                        "buy_volume": curr_buy_vol,
                        "sell_volume": curr_sell_vol,
                        "order_imbalance": imbalance
                    })
                    bucket_idx += 1
                    curr_vol = 0.0
                    curr_buy_vol = 0.0
                    curr_sell_vol = 0.0

        if not buckets:
            return pd.DataFrame(columns=["bucket_idx", "timestamp", "buy_volume", "sell_volume", "order_imbalance", "vpin"])

        df_buckets = pd.DataFrame(buckets)
        
        # Rolling VPIN calculation: sum(imbalance) / (N * V)
        rolling_imb = df_buckets["order_imbalance"].rolling(
            window=self.window_buckets,
            min_periods=1
        ).sum()

        actual_window = df_buckets["order_imbalance"].rolling(
            window=self.window_buckets,
            min_periods=1
        ).count()

        df_buckets["vpin"] = (rolling_imb / (actual_window * self.bucket_volume)).fillna(0.0)
        df_buckets["vpin"] = df_buckets["vpin"].clip(0.0, 1.0)
        df_buckets["vpin_pct"] = df_buckets["vpin"] * 100.0

        return df_buckets

    @staticmethod
    def compute_kyles_lambda(
        df_bars_or_buckets: pd.DataFrame,
        price_change_col: str = "price_change",
        imbalance_col: str = "order_imbalance"
    ) -> Dict[str, Any]:
        """
        Estimate Kyle's Lambda (1985) price impact coefficient via OLS regression:
        Delta P = lambda * Imbalance + epsilon
        """
        if price_change_col not in df_bars_or_buckets.columns:
            if "close" in df_bars_or_buckets.columns:
                df_bars_or_buckets = df_bars_or_buckets.copy()
                df_bars_or_buckets[price_change_col] = df_bars_or_buckets["close"].diff()
            else:
                raise ValueError(f"Need either '{price_change_col}' or 'close' in DataFrame.")

        sub = df_bars_or_buckets[[price_change_col, imbalance_col]].dropna()
        if len(sub) < 5:
            return {"lambda": 0.0, "r_squared": 0.0, "p_value": 1.0, "t_stat": 0.0}

        x = sub[imbalance_col].values
        y = sub[price_change_col].values

        res = stats.linregress(x, y)

        return {
            "lambda": float(res.slope),
            "intercept": float(res.intercept),
            "r_squared": float(res.rvalue ** 2),
            "p_value": float(res.pvalue),
            "std_err": float(res.stderr)
        }
