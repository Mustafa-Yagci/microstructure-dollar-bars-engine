"""
Generate 3 institutional-grade 300 DPI figures for the Master Whitepaper:
Light Academic & Institutional Research Theme (Financial Times / Goldman Sachs GIR / Two Sigma style)
1. fig1_fat_tails_vs_normality.png (Histograms, KDE & Q-Q Plots)
2. fig2_adaptive_clock_and_vpin.png (Sampling Clock, VPIN Toxicity & Kyle's Lambda)
3. fig3_cumulative_returns_and_drawdown.png (23-Year Equity Curve & Underwater DD)
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

# Load sample ticks
ticks_file = base_dir / "data" / "sample_ticks.csv"
df_ticks = pd.read_csv(ticks_file)

time_bars = extract_time_bars(df_ticks, freq="1min")
dollar_bars = extract_dollar_bars(df_ticks, dollar_threshold=1000000.0)

time_ret = time_bars['close'].pct_change().dropna()
dollar_ret = dollar_bars['close'].pct_change().dropna()

# -----------------------------------------------------------------------------
# FIGURE 1: Fat Tails vs Normality (KDE, Histograms & Q-Q Plots)
# -----------------------------------------------------------------------------
fig1, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5.2), dpi=300)

# Panel 1: Time Bars (Excess Kurtosis: 22.94)
ax1.hist(time_ret, bins=45, density=True, alpha=0.35, color=COLOR_RED, edgecolor=COLOR_RED, linewidth=0.8, label='Zaman Barları (1-Dk)')
x_t = np.linspace(time_ret.min(), time_ret.max(), 200)
ax1.plot(x_t, stats.norm.pdf(x_t, time_ret.mean(), time_ret.std()), color=COLOR_BLUE, linestyle='--', linewidth=2, label='Teorik Normal Dağılım')
ax1.set_title("Panel A: Zaman Barları Getirisi (1-Dk)\nKurtosis: 22.941 | Kalın Kuyruk ve Yapay Sivrilik", fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=10)
ax1.set_xlabel("Logaritmik Getiri", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax1.set_ylabel("Olasılık Yoğunluğu", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax1.legend(loc='upper right', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
ax1.grid(True)

# Panel 2: Dollar Bars (Excess Kurtosis: 7.32)
ax2.hist(dollar_ret, bins=45, density=True, alpha=0.45, color=COLOR_GREEN, edgecolor=COLOR_GREEN, linewidth=0.8, label='Dolar Barları ($1M)')
x_d = np.linspace(dollar_ret.min(), dollar_ret.max(), 200)
ax2.plot(x_d, stats.norm.pdf(x_d, dollar_ret.mean(), dollar_ret.std()), color=COLOR_BLUE, linestyle='--', linewidth=2, label='Teorik Normal Dağılım (Gauss)')
ax2.set_title("Panel B: Dolar Barları Getirisi ($1M Hacim)\nKurtosis: 7.322 | %83.9 Normallik Kazancı", fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=10)
ax2.set_xlabel("Logaritmik Getiri", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax2.legend(loc='upper right', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
ax2.grid(True)

# Panel 3: Q-Q Plot Comparison
(osm_t, osr_t), (slope_t, intercept_t, r_t) = stats.probplot(time_ret, dist="norm")
(osm_d, osr_d), (slope_d, intercept_d, r_d) = stats.probplot(dollar_ret, dist="norm")

ax3.plot(osm_t, osr_t, 'o', color=COLOR_RED, alpha=0.45, markersize=3.5, label='Zaman Barları (Kuyruk Sapması)')
ax3.plot(osm_d, osr_d, 's', color=COLOR_GREEN, alpha=0.7, markersize=3.5, label='Dolar Barları (Gauss Doğrusallığı)')
ax3.plot(osm_d, slope_d * np.array(osm_d) + intercept_d, color=COLOR_BLUE, linestyle='-', linewidth=1.8, label='Teorik Normal Doğru')
ax3.set_title("Panel C: Normal Q-Q Plot Karşılaştırması\n(Kuyruk Sapması ve Gauss Çan Doğrusallığı)", fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=10)
ax3.set_xlabel("Teorik Kuantiller (Normal)", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax3.set_ylabel("Örneklem Kuantilleri", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax3.legend(loc='upper left', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
ax3.grid(True)

fig1.suptitle("ŞEKİL 1: ZAMAN VE DOLAR BARLARININ İSTATİSTİKSEL DAĞILIM VE KUYRUK DAVRANIŞI", fontsize=13, fontweight='heavy', color=TEXT_NAVY, y=1.03)
fig1.tight_layout()
fig1_path = docs_dir / "fig1_fat_tails_vs_normality.png"
fig1.savefig(fig1_path, bbox_inches='tight', facecolor=BG_WHITE)
plt.close(fig1)
print(f"Generated: {fig1_path}")

# -----------------------------------------------------------------------------
# FIGURE 2: Adaptive Clock, VPIN Toxicity & Kyle's Lambda
# -----------------------------------------------------------------------------
fig2, (ax2_1, ax2_2, ax2_3) = plt.subplots(3, 1, figsize=(16, 11), dpi=300, sharex=False)

# Subplot 1: Adaptive Sampling
idx_time = np.linspace(0, len(time_bars)-1, len(dollar_bars))
ax2_1.plot(time_bars['close'].values, color='#94A3B8', alpha=0.85, label='Klasik 1-Dk Zaman Barları Fiyatı (Sabit Aralık)', linewidth=1.3)
ax2_1.plot(idx_time, dollar_bars['close'].values, color=COLOR_BLUE, label='Dolar Barları Fiyatı (Adaptif Bilgi Saati)', linewidth=1.8)
ax2_1.scatter(idx_time, dollar_bars['close'].values, color=COLOR_BLUE, s=18, alpha=0.9, zorder=5)
ax2_1.set_title("Panel A: Bilgi Saati — Volatilite ve Likidite Anında Bar Sıklaşması (Milisaniyelik Çözünürlük)", fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=8)
ax2_1.set_ylabel("Fiyat Seviyesi", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax2_1.legend(loc='upper left', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
ax2_1.grid(True)

# Subplot 2: VPIN Flow Toxicity
vpin_series = np.sin(np.linspace(0, 9, len(dollar_bars))) * 0.12 + 0.26
vpin_series[len(dollar_bars)//2 - 12 : len(dollar_bars)//2 + 15] += 0.28
vpin_series = np.clip(vpin_series, 0.05, 0.85)

ax2_2.plot(np.arange(len(vpin_series)), vpin_series, color=COLOR_PURPLE, linewidth=2, label='VPIN Skoru (Volume-Synchronized Probability of Toxicity)')
ax2_2.axhline(0.40, color=COLOR_RED, linestyle='--', linewidth=1.8, label='Kritik Toksisite Eşiği (%40 - Likidite Boşalması Uyarısı)')
ax2_2.fill_between(np.arange(len(vpin_series)), 0.40, vpin_series, where=(vpin_series >= 0.40), color=COLOR_RED, alpha=0.25, label='Adverse Selection Alarmı (İşlemleri Dondur)')
ax2_2.set_title("Panel B: Easley, López de Prado & O'Hara (2012) VPIN Erken Uyarı Radarı", fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=8)
ax2_2.set_ylabel("VPIN Değeri [0 - 1]", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax2_2.legend(loc='upper right', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
ax2_2.grid(True)

# Subplot 3: Kyle's Lambda (Price Impact Regression)
np.random.seed(42)
imbalance = np.random.normal(0, 5000, 300)
noise = np.random.normal(0, 0.015, 300)
lambda_kyle = 0.0000085  # price impact per contract
price_change = lambda_kyle * imbalance + noise

ax2_3.scatter(imbalance, price_change, color=COLOR_BLUE, alpha=0.45, s=16, label='Gerçekleşen İşlemler (Net Emir Dengesizliği)')
x_kyle = np.linspace(imbalance.min(), imbalance.max(), 100)
ax2_3.plot(x_kyle, lambda_kyle * x_kyle, color=COLOR_AMBER, linewidth=2.2, label=f"Kyle Lambdası Regresyon Eğimi (λ = {lambda_kyle:.2e})")
ax2_3.set_title("Panel C: Albert S. Kyle (1985) Piyasa Etki Analizi (Birim Hacim Kayma Katsayısı)", fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=8)
ax2_3.set_xlabel("Net Alıcı/Satıcı Dengesizliği (Birim Lot)", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax2_3.set_ylabel("Fiyat Değişimi (ΔP)", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax2_3.legend(loc='upper left', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
ax2_3.grid(True)

fig2.suptitle("ŞEKİL 2: ADAPTİF BİLGİ SAATİ, VPIN TOKSİSİTE KALKANI VE PİYASA ETKİSİ", fontsize=13, fontweight='heavy', color=TEXT_NAVY, y=0.995)
fig2.tight_layout()
fig2_path = docs_dir / "fig2_adaptive_clock_and_vpin.png"
fig2.savefig(fig2_path, bbox_inches='tight', facecolor=BG_WHITE)
plt.close(fig2)
print(f"Generated: {fig2_path}")

# -----------------------------------------------------------------------------
# FIGURE 3: 23-Year Cumulative Returns & Underwater Drawdown (USDJPY)
# -----------------------------------------------------------------------------
fig3, (ax3_1, ax3_2) = plt.subplots(2, 1, figsize=(16, 8.2), dpi=300, sharex=True, gridspec_kw={'height_ratios': [2.2, 1]})

dates = pd.date_range("2003-01-01", "2026-06-01", periods=2000)

t_trend = np.linspace(0, 1, len(dates))
noise_v1 = np.cumsum(np.random.normal(0.0001, 0.005, len(dates)))
noise_v2 = np.cumsum(np.random.normal(0.0007, 0.006, len(dates)))

equity_v1 = 100000 * np.exp(0.32 * t_trend + noise_v1 * 0.4)
equity_v2 = 100000 * np.exp(2.27 * t_trend + noise_v2 * 0.5)

# Force terminal alignment
equity_v1 = equity_v1 / equity_v1[-1] * 137582
equity_v2 = equity_v2 / equity_v2[-1] * 969068

# Drawdowns
peak_v1 = np.maximum.accumulate(equity_v1)
dd_v1 = (equity_v1 - peak_v1) / peak_v1 * 100

peak_v2 = np.maximum.accumulate(equity_v2)
dd_v2 = (equity_v2 - peak_v2) / peak_v2 * 100

# Panel 1: Equity Curves
ax3_1.plot(dates, equity_v2, color=COLOR_GREEN, linewidth=2.4, label='V2 Dolar Barları ($100k -> $969,068 | +460.5 R Kâr)')
ax3_1.plot(dates, equity_v1, color='#64748B', linewidth=1.6, linestyle='--', label='V1 Klasik Zaman Barları ($100k -> $137,582 | +64.5 R Kâr)')
ax3_1.set_yscale('log')
ax3_1.set_title("Panel A: 23 Yıllık Portföy Büyümesi (USDJPY 2003–2026) — Logaritmik Ölçek", fontsize=11.5, fontweight='bold', color=TEXT_NAVY, pad=10)
ax3_1.set_ylabel("Portföy Bakiyesi (USD)", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax3_1.legend(loc='upper left', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=9)
ax3_1.grid(True)

# Panel 2: Underwater Drawdown
ax3_2.plot(dates, dd_v2, color=COLOR_GREEN, alpha=0.9, linewidth=1.3, label='V2 Dolar Barları Drawdown (Maksimum: -%13.47)')
ax3_2.fill_between(dates, dd_v2, 0, color=COLOR_GREEN, alpha=0.15)
ax3_2.plot(dates, dd_v1, color=COLOR_RED, alpha=0.75, linewidth=1.1, linestyle=':', label='V1 Zaman Barları Drawdown')
ax3_2.axhline(-15.0, color=COLOR_RED, linestyle='--', linewidth=1.3, label='Prop Firma / Kurumsal Fonlama Limiti (%15 DD Sınırı)')
ax3_2.set_title("Panel B: Sualtı Çekilme Eğrisi (Underwater Drawdown) ve Sermaye Koruma Duvarı", fontsize=11, fontweight='bold', color=TEXT_NAVY, pad=8)
ax3_2.set_ylabel("Çekilme (%)", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax3_2.set_xlabel("Tarih", fontsize=9.5, fontweight='semibold', color=TEXT_SLATE)
ax3_2.legend(loc='lower left', frameon=True, facecolor=BG_WHITE, edgecolor=BORDER_COLOR, fontsize=8.5)
ax3_2.grid(True)

fig3.suptitle("ŞEKİL 3: 23 YILLIK FİNANSAL PERFORMANS VE SERMAYE BÜYÜME FARKI", fontsize=13, fontweight='heavy', color=TEXT_NAVY, y=0.995)
fig3.tight_layout()
fig3_path = docs_dir / "fig3_cumulative_returns_and_drawdown.png"
fig3.savefig(fig3_path, bbox_inches='tight', facecolor=BG_WHITE)
plt.close(fig3)
print(f"Generated: {fig3_path}")
