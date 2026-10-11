"""
microstructure-dollar-bars-engine: High-Frequency Market Microstructure & Dollar Bars Engine.

Author: Mustafa Yağcı (https://github.com/Mustafa-Yagci)
License: MIT
"""

__version__ = "1.0.0"

from .aggressor import (
    classify_trade_direction_lee_ready,
    classify_trade_direction_quote_rule,
    calculate_signed_order_flow,
)
from .bars import (
    extract_time_bars,
    extract_tick_bars,
    extract_volume_bars,
    extract_dollar_bars,
    extract_dollar_imbalance_bars,
)
from .vpin import VPINEngine
from .statistical_proofs import (
    compute_distribution_metrics,
    compare_bar_types,
    format_markdown_comparison_table,
)

__all__ = [
    "classify_trade_direction_lee_ready",
    "classify_trade_direction_quote_rule",
    "calculate_signed_order_flow",
    "extract_time_bars",
    "extract_tick_bars",
    "extract_volume_bars",
    "extract_dollar_bars",
    "extract_dollar_imbalance_bars",
    "VPINEngine",
    "compute_distribution_metrics",
    "compare_bar_types",
    "format_markdown_comparison_table",
]
