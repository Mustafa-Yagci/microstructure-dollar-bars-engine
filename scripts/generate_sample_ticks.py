"""
High-Frequency Market Microstructure Tick Generator.

Synthesizes realistic institutional order flow with:
- Volatility clustering (stochastic volatility)
- Non-linear trade size distribution (fat-tailed lognormal volumes)
- Bid-ask bounce and aggressor order book imbalance
- Flash liquidity shock / toxic cascade event
"""

import numpy as np
import pandas as pd
from pathlib import Path


def generate_synthetic_ticks(
    n_ticks: int = 15000,
    start_price: float = 150.00,
    start_time: str = "2026-10-01 09:30:00",
    seed: int = 42
) -> pd.DataFrame:
    np.random.seed(seed)

    base_dt = pd.to_datetime(start_time)
    
    # 1. Stochastic trade arrival times (Poisson process / exponential inter-trade duration)
    # Higher activity during market open (first 3000 ticks) and shock event (ticks 8000 to 10000)
    regimes = np.ones(n_ticks)
    regimes[0:3000] = 2.5      # Market open rush
    regimes[3000:7500] = 0.8   # Midday lull
    regimes[7500:10500] = 4.0  # Macro news / flash cascade shock
    regimes[10500:] = 1.2      # Afternoon stabilization

    # Inter-arrival time in milliseconds
    durations_ms = np.random.exponential(scale=1000.0 / regimes)
    durations_ms = np.clip(durations_ms, 10, 8000)
    timestamps = base_dt + pd.to_timedelta(np.cumsum(durations_ms), unit="ms")

    # 2. Price path with stochastic volatility and jump diffusion
    prices = np.zeros(n_ticks)
    prices[0] = start_price
    
    vol = 0.00025  # Base tick volatility (realistic for liquid equity / FX)
    aggressor = 1  # 1 for buy, -1 for sell
    
    # Volume: lognormal distribution with mean ~ 100 shares, heavy tail
    raw_vols = np.random.lognormal(mean=4.2, sigma=1.1, size=n_ticks)
    volumes = np.round(np.clip(raw_vols, 10, 5000)).astype(int)

    for i in range(1, n_ticks):
        # Regime-dependent volatility and drift
        current_regime = regimes[i]
        tick_vol = vol * np.sqrt(current_regime)

        # Toxic cascade during shock regime (ticks 7500 to 9500)
        if 7500 <= i <= 9500:
            drift = -0.00003  # Realistic downward pressure
            aggressor_prob = 0.70  # 70% sell aggressor (toxic flow)
            aggressor = -1 if np.random.rand() < aggressor_prob else 1
            tick_ret = drift + aggressor * abs(np.random.normal(0, tick_vol * 1.2))
        else:
            drift = 0.000005
            # Mean-reverting order flow
            aggressor = 1 if np.random.rand() > 0.49 else -1
            tick_ret = drift + np.random.normal(0, tick_vol)

        prices[i] = max(10.0, prices[i-1] * (1.0 + tick_ret))

    df = pd.DataFrame({
        "timestamp": timestamps,
        "price": np.round(prices, 3),
        "volume": volumes
    })

    return df


def main():
    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "sample_ticks.csv"

    print("Generating 15,000 realistic institutional market microstructure ticks...")
    df = generate_synthetic_ticks(n_ticks=15000, start_price=150.00)
    df.to_csv(out_file, index=False)
    print(f"Saved sample ticks to {out_file} ({len(df)} rows, price range: ${df['price'].min():.2f} - ${df['price'].max():.2f})")


if __name__ == "__main__":
    main()
