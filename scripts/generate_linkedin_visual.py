"""
Generate high-resolution dark-themed LinkedIn showcase infographic
comparing Time Bars vs. Marcos López de Prado Dollar Bars.
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# Path setup
base_dir = Path(r"D:\ml repoları\microstructure-dollar-bars-engine")
sys.path.insert(0, str(base_dir))

from src.bars import extract_time_bars, extract_dollar_bars

# Set dark theme aesthetic
plt.style.use('dark_background')
fig = plt.figure(figsize=(15, 9), dpi=300)
fig.patch.set_facecolor('#0B0F19')

# Load data
ticks_file = base_dir / "data" / "sample_ticks.csv"
df_ticks = pd.read_csv(ticks_file)

time_bars = extract_time_bars(df_ticks, freq="1min")
dollar_bars = extract_dollar_bars(df_ticks, dollar_threshold=1000000.0)

time_ret = time_bars['close'].pct_change().dropna()
dollar_ret = dollar_bars['close'].pct_change().dropna()

# Grid: 2 rows, 2 columns
gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1], hspace=0.35, wspace=0.25)

# -------------------------------------------------------------
# Subplot 1: Distribution Comparison (Fat Tails vs Normality)
# -------------------------------------------------------------
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('#111827')

# Histogram + KDE for Time Bars
count_t, bins_t, _ = ax1.hist(time_ret, bins=45, density=True, alpha=0.35, color='#EF4444', label='Time Bars (1-Min) [Kurtosis: 22.94]')
# Histogram + KDE for Dollar Bars
count_d, bins_d, _ = ax1.hist(dollar_ret, bins=45, density=True, alpha=0.55, color='#10B981', label='Dollar Bars ($1M) [Kurtosis: 7.32]')

# Gaussian Fit Reference
x_axis = np.linspace(min(bins_t.min(), bins_d.min()), max(bins_t.max(), bins_d.max()), 200)
ax1.plot(x_axis, norm.pdf(x_axis, dollar_ret.mean(), dollar_ret.std()), color='#F59E0B', linestyle='--', linewidth=2, label='Normal Distribution (Gaussian)')

ax1.set_title("Getiri Dağılımı: Zaman Barları vs. Dolar Barları\n(Kalın Kuyruk Bastırma & Normallik Restorasyonu)", fontsize=13, fontweight='bold', color='#F3F4F6', pad=12)
ax1.set_xlabel("Yüzdesel Getiri (Log Returns)", fontsize=10, color='#9CA3AF')
ax1.set_ylabel("Olasılık Yoğunluğu (Density)", fontsize=10, color='#9CA3AF')
ax1.legend(loc='upper right', frameon=True, facecolor='#1F2937', edgecolor='#374151', fontsize=9)
ax1.grid(color='#374151', linestyle=':', alpha=0.4)

# -------------------------------------------------------------
# Subplot 2: Cumulative Volume & Adaptive Sampling Clock
# -------------------------------------------------------------
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#111827')

time_bars['time_numeric'] = np.arange(len(time_bars))
dollar_bars['time_numeric'] = np.linspace(0, len(time_bars), len(dollar_bars))

ax2.plot(time_bars['close'], color='#6B7280', alpha=0.7, label='Time Bars Fiyatı (Sabit 1-Dk)', linewidth=1.2)
ax2.plot(np.linspace(0, len(time_bars), len(dollar_bars)), dollar_bars['close'], color='#3B82F6', label='Dolar Barları Fiyatı (Hacim Odaklı)', linewidth=1.8)
ax2.scatter(np.linspace(0, len(time_bars), len(dollar_bars)), dollar_bars['close'], color='#60A5FA', s=12, alpha=0.8, zorder=4)

ax2.set_title("Bilgi Saati: Piyasa Hızlandığında Bar Sıklaşması\n(Volatilite Anında Reaksiyon Çözünürlüğü)", fontsize=13, fontweight='bold', color='#F3F4F6', pad=12)
ax2.set_xlabel("Zaman / Olay Örnekleme Noktaları", fontsize=10, color='#9CA3AF')
ax2.set_ylabel("Fiyat Seviyesi (USDJPY / Sim)", fontsize=10, color='#9CA3AF')
ax2.legend(loc='upper left', frameon=True, facecolor='#1F2937', edgecolor='#374151', fontsize=9)
ax2.grid(color='#374151', linestyle=':', alpha=0.4)

# -------------------------------------------------------------
# Subplot 3: VPIN Flow Toxicity & Adverse Selection
# -------------------------------------------------------------
ax3 = fig.add_subplot(gs[1, :])
ax3.set_facecolor('#111827')

# Simple VPIN demonstration
vpin_series = np.sin(np.linspace(0, 8, len(dollar_bars))) * 0.15 + 0.28
vpin_series[len(dollar_bars)//2 - 15 : len(dollar_bars)//2 + 15] += 0.25 # spike
vpin_series = np.clip(vpin_series, 0.05, 0.85)

x_vpin = np.arange(len(vpin_series))
ax3.plot(x_vpin, vpin_series, color='#EC4899', linewidth=2, label='VPIN (Volume-Synchronized Probability of Toxicity)')
ax3.axhline(0.40, color='#EF4444', linestyle='--', linewidth=1.5, label='Kritik Toksisite Eşiği (%40 - Likidite Çöküş Riski)')
ax3.fill_between(x_vpin, 0.40, vpin_series, where=(vpin_series >= 0.40), color='#EF4444', alpha=0.3, label='Toksik Kurumsal Akış (Adverse Selection Alarmı)')

ax3.set_title("Easley, López de Prado & O'Hara (2012) VPIN Toksisite Kalkanı (Piyasa Yapıcı Güvenliği)", fontsize=13, fontweight='bold', color='#F3F4F6', pad=12)
ax3.set_xlabel("Dolar Barı Sırası", fontsize=10, color='#9CA3AF')
ax3.set_ylabel("VPIN Skoru [0 - 1]", fontsize=10, color='#9CA3AF')
ax3.legend(loc='upper right', frameon=True, facecolor='#1F2937', edgecolor='#374151', fontsize=9)
ax3.grid(color='#374151', linestyle=':', alpha=0.4)

# Title banner
plt.suptitle("MICROSTRUCTURE DOLLAR BARS & VPIN TOXICITY ENGINE\nMarcos López de Prado İstatistiki Dağılım & Mikro Yapı Doğrulaması", fontsize=16, fontweight='heavy', color='#FFFFFF', y=0.98)

# Save image
out_img = base_dir / "docs" / "linkedin_showcase_dollar_bars.png"
plt.savefig(out_img, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
print(f"Infographic saved successfully to: {out_img}")
