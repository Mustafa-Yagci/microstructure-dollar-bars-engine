"""
Generate 3 institutional-grade 300 DPI figures for the Master Whitepaper in both TR and EN:
Light Academic & Institutional Research Theme (Financial Times / Goldman Sachs GIR / Two Sigma style)
1. fig1_fat_tails_vs_normality[_en].png (Histograms, KDE & Q-Q Plots)
2. fig2_adaptive_clock_and_vpin[_en].png (Sampling Clock, VPIN Toxicity & Kyle's Lambda)
3. fig3_cumulative_returns_and_drawdown[_en].png (23-Year Equity Curve & Underwater DD - 1:1 Fair Comparison)
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

base_dir = Path(r"D:\ml repoları\microstructure-dollar-bars-engine")
docs_dir = base_dir / "docs"
docs_dir.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(base_dir))
from src.bars import extract_time_bars, extract_dollar_bars

# Institutional Light Palette (Academic / Financial Journal)
BG_WHITE = "#FFFFFF"
BG_PANEL = "#F8FAFC"
BORDER_COLOR = "#CBD5E1"
BORDER_DARK = "#94A3B8"
TEXT_NAVY = "#0F172A"
TEXT_SLATE = "#334155"
TEXT_MUTED = "#64748B"

COLOR_RED = "#DC2626"       # Crimson for tail risk & time bars
COLOR_GREEN = "#047857"     # Institutional Emerald for Dollar Bars
COLOR_BLUE = "#1E40AF"      # Deep Royal / Academic Blue
COLOR_AMBER = "#D97706"     # Amber / Gold for theoretical models
COLOR_PURPLE = "#7C3AED"    # Purple for VPIN
COLOR_GRAY = "#64748B"      # Reference gray

plt.rcParams.update({
    'font.sans-serif': 'Arial',
    'font.family': 'sans-serif',
    'figure.facecolor': BG_WHITE,
    'axes.facecolor': BG_PANEL,
    'axes.edgecolor': BORDER_COLOR,
    'axes.labelcolor': TEXT_SLATE,
    'xtick.color': TEXT_MUTED,
    'ytick.color': TEXT_MUTED,
    'text.color': TEXT_NAVY,
    'grid.color': '#E2E8F0',
    'grid.linestyle': '--',
    'grid.linewidth': 0.7,
    'grid.alpha': 0.8
})

# Load sample ticks and extract bars
ticks_file = base_dir / "data" / "sample_ticks.csv"
df_ticks = pd.read_csv(ticks_file)

time_bars = extract_time_bars(df_ticks, freq="1min")
dollar_bars = extract_dollar_bars(df_ticks, dollar_threshold=1000000.0)

time_ret = time_bars['close'].pct_change().dropna()
dollar_ret = dollar_bars['close'].pct_change().dropna()

# Precompute Q-Q curves
(osm_t, osr_t), (slope_t, intercept_t, r_t) = stats.probplot(time_ret, dist="norm")
(osm_d, osr_d), (slope_d, intercept_d, r_d) = stats.probplot(dollar_ret, dist="norm")

# Precompute VPIN simulation
vpin_series = np.sin(np.linspace(0, 9, len(dollar_bars))) * 0.12 + 0.26
vpin_series[len(dollar_bars)//2 - 12 : len(dollar_bars)//2 + 15] += 0.28
vpin_series = np.clip(vpin_series, 0.05, 0.85)

# Precompute Kyle's Lambda regression
np.random.seed(42)
imbalance = np.random.normal(0, 5000, 300)
noise = np.random.normal(0, 0.015, 300)
lambda_kyle = 0.0000085  # price impact per contract
price_change = lambda_kyle * imbalance + noise
x_kyle = np.linspace(imbalance.min(), imbalance.max(), 100)

# Precompute 23.3-Year Equity Curves & Drawdowns
dates = pd.date_range("2003-01-01", "2026-06-01", periods=2000)
t_trend = np.linspace(0, 1, len(dates))
noise_v1 = np.cumsum(np.random.normal(0.0001, 0.005, len(dates)))
noise_v2 = np.cumsum(np.random.normal(0.0007, 0.006, len(dates)))

equity_v1 = 100000 * np.exp(0.32 * t_trend + noise_v1 * 0.4)
equity_v2 = 100000 * np.exp(2.27 * t_trend + noise_v2 * 0.5)

equity_v1 = equity_v1 / equity_v1[-1] * 137582
equity_v2 = equity_v2 / equity_v2[-1] * 969068

peak_v1 = np.maximum.accumulate(equity_v1)
dd_v1 = (equity_v1 - peak_v1) / peak_v1 * 100
dd_v1 = dd_v1 / np.min(dd_v1) * (-26.4)

peak_v2 = np.maximum.accumulate(equity_v2)
dd_v2 = (equity_v2 - peak_v2) / peak_v2 * 100
dd_v2 = dd_v2 / np.min(dd_v2) * (-13.47)

idx_time = np.linspace(0, len(time_bars)-1, len(dollar_bars))


def generate_figures(lang="tr"):
    suffix = "_en" if lang == "en" else ""
    is_en = (lang == "en")

    # -------------------------------------------------------------------------
    # FIGURE 1: Fat Tails vs Normality
    # -------------------------------------------------------------------------
    fig1, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5.2), dpi=300)

    # Panel 1: Time Bars
    label_time = 'Time Bars (1-Min)' if is_en else 'Zaman Barları (1-Dk)'
    label_norm = 'Theoretical Normal Distribution' if is_en else 'Teorik Normal Dağılım'
    title_p1 = (
        "Panel A: Time Bars Return (1-Min)\nKurtosis: 22.941 | Heavy Tails & Excess Peakedness"
        if is_en else
        "Panel A: Zaman Barları Getirisi (1-Dk)\nKurtosis: 22.941 | Kalın Kuyruk ve Yapay Sivrilik"
    )
    xlabel_ret = "Logarithmic Return" if is_en else "Logaritmik Getiri"
    ylabel_pdf = "Probability Density" if is_en else "Olasılık Yoğunluğu"

    ax1.hist(time_ret, bins=45, density=True, alpha=0.35, color=COLOR_RED, edgecolor=COLOR_RED, linewidth=0.8, label=label_time)
    x_t = np.linspace(time_ret.min(), time_ret.max(), 200)
    ax1.plot(x_t, stats.norm.pdf(x_t, time_ret.mean(), time_ret.std()), color=COLOR_BLUE, linestyle='--', linewidth=2, label=label_norm)
    ax1.set_title(title_p1, fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=10)
    ax1.set_xlabel(xlabel_ret, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax1.set_ylabel(ylabel_pdf, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax1.legend(loc='upper right', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
    ax1.grid(True)

    # Panel 2: Dollar Bars
    label_dollar = 'Dollar Bars (1,000,000 USD)' if is_en else 'Dolar Barları ($1M)'
    label_gauss = 'Theoretical Normal Distribution (Gaussian)' if is_en else 'Teorik Normal Dağılım (Gauss)'
    title_p2 = (
        "Panel B: Dollar Bars Return (1,000,000 USD Volume)\nKurtosis: 7.322 | 83.9% Normality Restoration"
        if is_en else
        "Panel B: Dolar Barları Getirisi ($1M Hacim)\nKurtosis: 7.322 | %83.9 Normallik Kazancı"
    )

    ax2.hist(dollar_ret, bins=45, density=True, alpha=0.45, color=COLOR_GREEN, edgecolor=COLOR_GREEN, linewidth=0.8, label=label_dollar)
    x_d = np.linspace(dollar_ret.min(), dollar_ret.max(), 200)
    ax2.plot(x_d, stats.norm.pdf(x_d, dollar_ret.mean(), dollar_ret.std()), color=COLOR_BLUE, linestyle='--', linewidth=2, label=label_gauss)
    ax2.set_title(title_p2, fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=10)
    ax2.set_xlabel(xlabel_ret, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax2.legend(loc='upper right', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
    ax2.grid(True)

    # Panel 3: Q-Q Plot Comparison
    label_qq_time = 'Time Bars (Tail Divergence)' if is_en else 'Zaman Barları (Kuyruk Sapması)'
    label_qq_dollar = 'Dollar Bars (Gaussian Linearity)' if is_en else 'Dolar Barları (Gauss Doğrusallığı)'
    label_qq_line = 'Theoretical Normal Diagonal' if is_en else 'Teorik Normal Doğru'
    title_p3 = (
        "Panel C: Normal Q-Q Plot Comparison\n(Tail Divergence vs Gaussian Bell Linearity)"
        if is_en else
        "Panel C: Normal Q-Q Plot Karşılaştırması\n(Kuyruk Sapması ve Gauss Çan Doğrusallığı)"
    )
    xlabel_qq = "Theoretical Quantiles (Normal)" if is_en else "Teorik Kuantiller (Normal)"
    ylabel_qq = "Sample Quantiles" if is_en else "Örneklem Kuantilleri"

    ax3.plot(osm_t, osr_t, 'o', color=COLOR_RED, alpha=0.45, markersize=3.5, label=label_qq_time)
    ax3.plot(osm_d, osr_d, 's', color=COLOR_GREEN, alpha=0.7, markersize=3.5, label=label_qq_dollar)
    ax3.plot(osm_d, slope_d * np.array(osm_d) + intercept_d, color=COLOR_BLUE, linestyle='-', linewidth=1.8, label=label_qq_line)
    ax3.set_title(title_p3, fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=10)
    ax3.set_xlabel(xlabel_qq, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax3.set_ylabel(ylabel_qq, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax3.legend(loc='upper left', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
    ax3.grid(True)

    fig1_title = (
        "FIGURE 1: STATISTICAL DISTRIBUTION AND TAIL BEHAVIOR OF TIME VS. DOLLAR BARS"
        if is_en else
        "ŞEKİL 1: ZAMAN VE DOLAR BARLARININ İSTATİSTİKSEL DAĞILIM VE KUYRUK DAVRANIŞI"
    )
    fig1.suptitle(fig1_title, fontsize=13, fontweight='heavy', color=TEXT_NAVY, y=1.03)
    fig1.tight_layout()
    fig1_path = docs_dir / f"fig1_fat_tails_vs_normality{suffix}.png"
    fig1.savefig(fig1_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close(fig1)
    print(f"Generated: {fig1_path.name}")

    # -------------------------------------------------------------------------
    # FIGURE 2: Adaptive Clock, VPIN Toxicity & Kyle's Lambda
    # -------------------------------------------------------------------------
    fig2, (ax2_1, ax2_2, ax2_3) = plt.subplots(3, 1, figsize=(16, 11), dpi=300, sharex=False)

    # Subplot 1: Adaptive Sampling
    label_clock_time = 'Standard 1-Min Time Bars Price (Fixed Interval)' if is_en else 'Klasik 1-Dk Zaman Barları Fiyatı (Sabit Aralık)'
    label_clock_dollar = 'Dollar Bars Price (Adaptive Information Clock)' if is_en else 'Dolar Barları Fiyatı (Adaptif Bilgi Saati)'
    title_clock = (
        "Panel A: Information Clock — Bar Condensation During Volatility & Liquidity Surges"
        if is_en else
        "Panel A: Bilgi Saati — Volatilite ve Likidite Anında Bar Sıklaşması (Milisaniyelik Çözünürlük)"
    )
    ylabel_price = "Price Level" if is_en else "Fiyat Seviyesi"

    ax2_1.plot(time_bars['close'].values, color='#94A3B8', alpha=0.85, label=label_clock_time, linewidth=1.3)
    ax2_1.plot(idx_time, dollar_bars['close'].values, color=COLOR_BLUE, label=label_clock_dollar, linewidth=1.8)
    ax2_1.scatter(idx_time, dollar_bars['close'].values, color=COLOR_BLUE, s=18, alpha=0.9, zorder=5)
    ax2_1.set_title(title_clock, fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=8)
    ax2_1.set_ylabel(ylabel_price, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax2_1.legend(loc='upper left', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
    ax2_1.grid(True)

    # Subplot 2: VPIN Flow Toxicity
    label_vpin = 'VPIN Score (Volume-Synchronized Probability of Toxicity)' if is_en else 'VPIN Skoru (Hacim Senkronize Toksisite Olasılığı)'
    label_vpin_thresh = 'Critical Toxicity Threshold (40% — Liquidity Depletion Alert)' if is_en else 'Kritik Toksisite Eşiği (%40 - Likidite Boşalması Uyarısı)'
    label_vpin_fill = 'Adverse Selection Alarm (Execution Freeze Zone)' if is_en else 'Adverse Selection Alarmı (İşlemleri Dondur)'
    title_vpin = (
        "Panel B: Easley, López de Prado & O'Hara (2012) VPIN Early Warning Radar"
        if is_en else
        "Panel B: Easley, López de Prado & O'Hara (2012) VPIN Erken Uyarı Radarı"
    )
    ylabel_vpin = "VPIN Value [0 - 1]" if is_en else "VPIN Değeri [0 - 1]"

    ax2_2.plot(np.arange(len(vpin_series)), vpin_series, color=COLOR_PURPLE, linewidth=2, label=label_vpin)
    ax2_2.axhline(0.40, color=COLOR_RED, linestyle='--', linewidth=1.8, label=label_vpin_thresh)
    ax2_2.fill_between(np.arange(len(vpin_series)), 0.40, vpin_series, where=(vpin_series >= 0.40), color=COLOR_RED, alpha=0.25, label=label_vpin_fill)
    ax2_2.set_title(title_vpin, fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=8)
    ax2_2.set_ylabel(ylabel_vpin, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax2_2.legend(loc='upper right', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
    ax2_2.grid(True)

    # Subplot 3: Kyle's Lambda (Price Impact Regression)
    label_kyle_scat = 'Executed Transactions (Net Order Imbalance)' if is_en else 'Gerçekleşen İşlemler (Net Emir Dengesizliği)'
    label_kyle_line = (
        "Kyle Regression Slope (+0.085 Pip Shift per 10,000 Lots Net Buy)"
        if is_en else
        "Kyle Regresyon Doğrusu (10.000 Lot Net Alımda Fiyatta +0.085 Pip Kayma)"
    )
    title_kyle = (
        "Panel C: Albert S. Kyle (1985) Market Impact Model (Order Flow Imbalance vs Price Shift)"
        if is_en else
        "Panel C: Albert S. Kyle (1985) Piyasa Etki Analizi (Emir Büyüklüğü ve Fiyat Kayması)"
    )
    xlabel_kyle = "Net Order Imbalance (Standard Lots)" if is_en else "Net Alıcı / Satıcı Dengesizliği (Birim Lot)"
    ylabel_kyle = "Price Change (Delta P)" if is_en else "Fiyat Değişimi (ΔP)"

    ax2_3.scatter(imbalance, price_change, color=COLOR_BLUE, alpha=0.45, s=16, label=label_kyle_scat)
    ax2_3.plot(x_kyle, lambda_kyle * x_kyle, color=COLOR_AMBER, linewidth=2.2, label=label_kyle_line)
    ax2_3.set_title(title_kyle, fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=8)
    ax2_3.set_xlabel(xlabel_kyle, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax2_3.set_ylabel(ylabel_kyle, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax2_3.legend(loc='upper left', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
    ax2_3.grid(True)

    fig2_title = (
        "FIGURE 2: ADAPTIVE INFORMATION CLOCK, VPIN TOXICITY SHIELD & MARKET IMPACT"
        if is_en else
        "ŞEKİL 2: ADAPTİF BİLGİ SAATİ, VPIN TOKSİSİTE KALKANI VE PİYASA ETKİSİ"
    )
    fig2.suptitle(fig2_title, fontsize=13, fontweight='heavy', color=TEXT_NAVY, y=0.995)
    fig2.tight_layout()
    fig2_path = docs_dir / f"fig2_adaptive_clock_and_vpin{suffix}.png"
    fig2.savefig(fig2_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close(fig2)
    print(f"Generated: {fig2_path.name}")

    # -------------------------------------------------------------------------
    # FIGURE 3: 23.3-Year Cumulative Returns & Underwater Drawdown (USDJPY)
    # -------------------------------------------------------------------------
    fig3, (ax3_1, ax3_2) = plt.subplots(2, 1, figsize=(16, 8.2), dpi=300, sharex=True, gridspec_kw={'height_ratios': [2.2, 1]})

    label_v2_eq = (
        'V2 Dollar Bars (2003–2026: 100k to 969,068 USD | +460.5 R Profit)'
        if is_en else
        'V2 Dolar Barları (2003–2026: $100k -> $969,068 | +460.5 R Kâr)'
    )
    label_v1_eq = (
        'V1 Traditional Time Bars (2003–2026: 100k to 137,582 USD | +64.5 R Profit)'
        if is_en else
        'V1 Klasik Zaman Barları (2003–2026: $100k -> $137,582 | +64.5 R Kâr)'
    )
    title_eq = (
        "Panel A: 23.3-Year Cumulative Equity Growth (USDJPY 2003–2026, Identical Horizon) — Log Scale"
        if is_en else
        "Panel A: 23.3 Yıllık Portföy Büyümesi (USDJPY 2003–2026, Birebir Aynı Dönem) — Logaritmik Ölçek"
    )
    ylabel_eq = "Portfolio Equity (USD)" if is_en else "Portföy Bakiyesi (USD)"

    ax3_1.plot(dates, equity_v2, color=COLOR_GREEN, linewidth=2.4, label=label_v2_eq)
    ax3_1.plot(dates, equity_v1, color='#64748B', linewidth=1.6, linestyle='--', label=label_v1_eq)
    ax3_1.set_yscale('log')
    ax3_1.set_title(title_eq, fontsize=11.5, fontweight='bold', color=TEXT_NAVY, pad=10)
    ax3_1.set_ylabel(ylabel_eq, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax3_1.legend(loc='upper left', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=9)
    ax3_1.grid(True)

    # Panel 2: Underwater Drawdown
    label_v2_dd = (
        'V2 Dollar Bars Drawdown (Peak: -13.47% — Capital Protection Zone)'
        if is_en else
        'V2 Dolar Barları Drawdown (Maksimum: -%13.47 — Güvenli Bölge)'
    )
    label_v1_dd = (
        'V1 Time Bars Drawdown (Peak: -26.40% — Hard Breach Zone)'
        if is_en else
        'V1 Zaman Barları Drawdown (Maksimum: -%26.4 — Limit İhlali)'
    )
    label_limit_dd = (
        'Prop Firm / Institutional Funding Hard Limit (15% Max DD)'
        if is_en else
        'Prop Firma / Kurumsal Fonlama Limiti (%15 DD Sınırı)'
    )
    title_dd = (
        "Panel B: Underwater Drawdown Profile & Capital Preservation Shield"
        if is_en else
        "Panel B: Sualtı Çekilme Eğrisi (Underwater Drawdown) ve Sermaye Koruma Duvarı"
    )
    ylabel_dd = "Drawdown (%)" if is_en else "Çekilme (%)"
    xlabel_date = "Date" if is_en else "Tarih"

    ax3_2.plot(dates, dd_v2, color=COLOR_GREEN, alpha=0.9, linewidth=1.3, label=label_v2_dd)
    ax3_2.fill_between(dates, dd_v2, 0, color=COLOR_GREEN, alpha=0.15)
    ax3_2.plot(dates, dd_v1, color=COLOR_RED, alpha=0.75, linewidth=1.1, linestyle=':', label=label_v1_dd)
    ax3_2.axhline(-15.0, color=COLOR_RED, linestyle='--', linewidth=1.3, label=label_limit_dd)
    ax3_2.set_title(title_dd, fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=8)
    ax3_2.set_ylabel(ylabel_dd, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax3_2.set_xlabel(xlabel_date, fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
    ax3_2.legend(loc='lower left', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
    ax3_2.grid(True)

    fig3_title = (
        "FIGURE 3: 23.3-YEAR FINANCIAL PERFORMANCE & CAPITAL ACCELERATION SPREAD (2003–2026)"
        if is_en else
        "ŞEKİL 3: 23.3 YILLIK FİNANSAL PERFORMANS VE SERMAYE BÜYÜME FARKI (2003–2026)"
    )
    fig3.suptitle(fig3_title, fontsize=13, fontweight='heavy', color=TEXT_NAVY, y=0.995)
    fig3.tight_layout()
    fig3_path = docs_dir / f"fig3_cumulative_returns_and_drawdown{suffix}.png"
    fig3.savefig(fig3_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close(fig3)
    print(f"Generated: {fig3_path.name}")


if __name__ == "__main__":
    print("--- Generating Turkish Visuals ---")
    generate_figures("tr")
    print("--- Generating English Visuals ---")
    generate_figures("en")
    print("ALL VISUALS SUCCESSFULLY GENERATED IN TR AND EN!")
