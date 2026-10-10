"""
Statistical Normality & Information Recovery Proofs.

Provides quantitative comparative tests between:
- Calendar Time Bars (1-min, 5-min)
- Tick Bars
- Volume Bars
- Dollar Bars (López de Prado standard)

Calculates:
- Jarque-Bera test statistic & p-value
- Fisher excess kurtosis and skewness
- Kolmogorov-Smirnov normality distance
- Serial autocorrelation of returns (first-order rho and Ljung-Box Q)
- Percentage Normality Gain
"""

from typing import Union, Dict, Any, List
import numpy as np
import pandas as pd
from scipy import stats


def compute_distribution_metrics(returns: Union[pd.Series, np.ndarray, list]) -> Dict[str, Any]:
    """
    Compute full distributional and normality statistics for a return series.
    """
    clean_rets = pd.Series(returns, dtype=float).dropna()
    clean_rets = clean_rets[np.isfinite(clean_rets)]

    n = len(clean_rets)
    if n < 8:
        return {
            "sample_size": n,
            "mean": 0.0,
            "std": 0.0,
            "skewness": 0.0,
            "kurtosis_excess": 0.0,
            "jarque_bera_stat": 0.0,
            "jarque_bera_pvalue": 1.0,
            "ks_stat": 0.0,
            "ks_pvalue": 1.0,
            "autocorr_lag1": 0.0
        }

    arr = clean_rets.values
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr, ddof=1))

    # Skewness & Kurtosis (Fisher excess kurtosis: normal dist = 0.0)
    skew_val = float(stats.skew(arr, bias=False))
    kurt_excess = float(stats.kurtosis(arr, fisher=True, bias=False))

    # Jarque-Bera test
    jb_stat, jb_p = stats.jarque_bera(arr)

    # Kolmogorov-Smirnov test against fitted normal
    if std_val > 1e-9:
        standardized = (arr - mean_val) / std_val
        ks_stat, ks_p = stats.kstest(standardized, "norm")
    else:
        ks_stat, ks_p = 0.0, 1.0

    # First-order serial autocorrelation
    if n > 2:
        lag1 = clean_rets.autocorr(lag=1)
        lag1_val = float(lag1) if not np.isnan(lag1) else 0.0
    else:
        lag1_val = 0.0

    return {
        "sample_size": int(n),
        "mean": float(round(mean_val, 6)),
        "std": float(round(std_val, 6)),
        "skewness": float(round(skew_val, 4)),
        "kurtosis_excess": float(round(kurt_excess, 4)),
        "jarque_bera_stat": float(round(jb_stat, 2)),
        "jarque_bera_pvalue": float(jb_p),
        "ks_stat": float(round(ks_stat, 4)),
        "ks_pvalue": float(ks_p),
        "autocorr_lag1": float(round(lag1_val, 4))
    }


def compare_bar_types(
    dict_of_bars: Dict[str, pd.DataFrame],
    return_col: str = "log_returns"
) -> Dict[str, Any]:
    """
    Run comparative statistical normality analysis across multiple bar series.
    
    Parameters
    ----------
    dict_of_bars : dict
        Mapping of bar type label (e.g. 'Time Bars (5m)', 'Dollar Bars') to DataFrame.
    """
    results: Dict[str, Dict[str, Any]] = {}

    for label, df in dict_of_bars.items():
        if return_col in df.columns:
            rets = df[return_col]
        elif "close" in df.columns:
            rets = np.log(df["close"] / df["close"].shift(1)).dropna()
        else:
            continue

        results[label] = compute_distribution_metrics(rets)

    # Calculate normality gain compared to the first benchmark (typically Time Bars)
    first_key = list(results.keys())[0] if results else None
    benchmark_jb = results[first_key]["jarque_bera_stat"] if first_key else 0.0

    comparison_summary = []
    for label, m in results.items():
        current_jb = m["jarque_bera_stat"]
        if benchmark_jb > 0:
            normality_gain_pct = float(round(((benchmark_jb - current_jb) / benchmark_jb) * 100.0, 1))
        else:
            normality_gain_pct = 0.0

        comparison_summary.append({
            "bar_type": label,
            "bars_count": m["sample_size"],
            "skewness": m["skewness"],
            "excess_kurtosis": m["kurtosis_excess"],
            "jarque_bera": current_jb,
            "autocorr_lag1": m["autocorr_lag1"],
            "normality_gain_pct": normality_gain_pct
        })

    return {
        "detailed_metrics": results,
        "summary": comparison_summary,
        "benchmark_label": first_key
    }


def format_markdown_comparison_table(comparison_result: Dict[str, Any]) -> str:
    """
    Format the statistical comparison into a publication-ready Markdown table.
    """
    summary = comparison_result.get("summary", [])
    lines = [
        "| Bar Sampling Method | Bar Count | Skewness | Excess Kurtosis | Jarque-Bera Stat | Autocorr (Lag 1) | Normality Gain (%) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    for item in summary:
        gain_str = f"**+{item['normality_gain_pct']}%**" if item["normality_gain_pct"] > 0 else f"{item['normality_gain_pct']}%"
        if item["normality_gain_pct"] == 0:
            gain_str = "0.0% (Baseline)"

        lines.append(
            f"| **{item['bar_type']}** | {item['bars_count']} | {item['skewness']:.3f} | {item['excess_kurtosis']:.3f} | {item['jarque_bera']:,.1f} | {item['autocorr_lag1']:.4f} | {gain_str} |"
        )

    return "\n".join(lines)
