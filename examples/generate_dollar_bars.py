"""
Demonstration: Extracting Dollar Bars and Imbalance Bars from Tick Data.

Shows raw ticks transformed into institutional OHLCV + VWAP Dollar Bars.
"""

from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.bars import extract_dollar_bars, extract_dollar_imbalance_bars


def main():
    ticks_file = Path(__file__).resolve().parent.parent / "data" / "sample_ticks.csv"
    if not ticks_file.exists():
        print(f"Error: {ticks_file} not found.")
        return

    df_ticks = pd.read_csv(ticks_file)
    print("=" * 110)
    print("  DOLLAR BARS & INFORMATION-DRIVEN DOLLAR IMBALANCE BARS EXTRACTION")
    print("=" * 110)

    # 1. Standard Dollar Bars ($1,000,000 per bar)
    print("\n[1] Standard Dollar Bars ($1,000,000 per bar):")
    dollar_bars = extract_dollar_bars(df_ticks, dollar_threshold=1000000.0)
    print(f"Total Dollar Bars Extracted: {len(dollar_bars)}")
    print(dollar_bars[["timestamp", "open", "high", "low", "close", "volume", "dollar_volume", "vwap", "tick_count"]].head(8).to_string(index=False))

    # 2. Dollar Imbalance Bars (DIB)
    print("\n" + "-" * 110)
    print("[2] Information-Driven Dollar Imbalance Bars (DIB):")
    dib_bars = extract_dollar_imbalance_bars(df_ticks, initial_threshold=150000.0)
    print(f"Total Dollar Imbalance Bars Extracted: {len(dib_bars)}")
    print(dib_bars[["timestamp", "open", "high", "low", "close", "volume", "dollar_volume", "vwap", "imbalance", "tick_count"]].head(8).to_string(index=False))
    print("=" * 110)


if __name__ == "__main__":
    main()
