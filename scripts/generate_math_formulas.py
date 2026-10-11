"""
Generate standalone high-resolution 300 DPI transparent mathematical formula images.
Renders flawlessly in both HTML and PDF with zero external CDN dependency.
Uses clean mathematical notation and institutional color-coding.
"""

from pathlib import Path
import matplotlib.pyplot as plt

base_dir = Path(r"D:\ml repoları\microstructure-dollar-bars-engine")
docs_dir = base_dir / "docs"
docs_dir.mkdir(parents=True, exist_ok=True)

# 1. DOLLAR BARS & VWAP
fig1 = plt.figure(figsize=(10.5, 1.2), dpi=300)
fig1.patch.set_alpha(0.0)
ax1 = fig1.add_subplot(111)
ax1.axis("off")
ax1.text(0.5, 0.5, r"$\sum_{i = T_{k-1} + 1}^{T_k} p_i \cdot v_i \geq D \qquad \left( \mathrm{VWAP}_k = \frac{\sum_{i \in B_k} p_i \cdot v_i}{\sum_{i \in B_k} v_i} \right)$", 
         fontsize=16, ha="center", va="center", color="#0F172A")
fig1.savefig(docs_dir / "math_eq1_dollar_bars.png", bbox_inches="tight", transparent=True, pad_inches=0.1)
plt.close(fig1)
print("Generated: math_eq1_dollar_bars.png")

# 2. LEE & READY (1991) TICK RULE
fig2, ax2 = plt.subplots(figsize=(9, 1.8), dpi=300)
fig2.patch.set_alpha(0.0)
ax2.axis("off")
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.text(0.5, 5, r"$b_i = $", fontsize=22, color="#0F172A", va="center")
ax2.text(1.7, 5, "{", fontsize=48, color="#0F172A", va="center", fontfamily="serif")
ax2.text(2.3, 7.5, r"$+1, \quad \Delta p_i > 0 \quad (\mathrm{Alici \: Agresor \: / \: Ask'e \: Vuran})$", fontsize=13.5, color="#047857", va="center")
ax2.text(2.3, 5.0, r"$-1, \quad \Delta p_i < 0 \quad (\mathrm{Satici \: Agresor \: / \: Bid'e \: Vuran})$", fontsize=13.5, color="#DC2626", va="center")
ax2.text(2.3, 2.5, r"$b_{i-1}, \; \Delta p_i = 0 \quad (\mathrm{Yon \: Degismedi, \: Onceki \: Yonu \: Koru})$", fontsize=13.5, color="#475569", va="center")
fig2.savefig(docs_dir / "math_eq2_lee_ready.png", bbox_inches="tight", transparent=True, pad_inches=0.1)
plt.close(fig2)
print("Generated: math_eq2_lee_ready.png")

# 3. EASLEY, LOPEZ DE PRADO & O'HARA (2012) VPIN
fig3 = plt.figure(figsize=(9, 1.2), dpi=300)
fig3.patch.set_alpha(0.0)
ax3 = fig3.add_subplot(111)
ax3.axis("off")
ax3.text(0.5, 0.5, r"$\mathrm{VPIN} = \frac{\sum_{\tau = k - N + 1}^k |V_\tau^B - V_\tau^S|}{N \times V} \quad \in \quad [0.0, \; 1.0]$", 
         fontsize=16, ha="center", va="center", color="#0F172A")
fig3.savefig(docs_dir / "math_eq3_vpin.png", bbox_inches="tight", transparent=True, pad_inches=0.1)
plt.close(fig3)
print("Generated: math_eq3_vpin.png")

# 4. ALBERT S. KYLE (1985) PRICE IMPACT LAMBDA
fig4 = plt.figure(figsize=(10.5, 1.2), dpi=300)
fig4.patch.set_alpha(0.0)
ax4 = fig4.add_subplot(111)
ax4.axis("off")
ax4.text(0.5, 0.5, r"$\Delta p_t = \lambda \cdot (V_t^B - V_t^S) + \varepsilon_t \qquad \left( \lambda = \frac{\mathrm{Cov}(\Delta p_t, \; \Delta V_t)}{\mathrm{Var}(\Delta V_t)} \right)$", 
         fontsize=15, ha="center", va="center", color="#0F172A")
fig4.savefig(docs_dir / "math_eq4_kyle_lambda.png", bbox_inches="tight", transparent=True, pad_inches=0.1)
plt.close(fig4)
print("Generated: math_eq4_kyle_lambda.png")

# 5. JARQUE-BERA NORMALITY TEST
fig5 = plt.figure(figsize=(8.5, 1.2), dpi=300)
fig5.patch.set_alpha(0.0)
ax5 = fig5.add_subplot(111)
ax5.axis("off")
ax5.text(0.5, 0.5, r"$JB = \frac{n}{6} \left( S^2 + \frac{(K - 3)^2}{4} \right) \quad \sim \quad \chi^2(2)$", 
         fontsize=16, ha="center", va="center", color="#0F172A")
fig5.savefig(docs_dir / "math_eq5_jarque_bera.png", bbox_inches="tight", transparent=True, pad_inches=0.1)
plt.close(fig5)
print("Generated: math_eq5_jarque_bera.png")

print("ALL 5 FORMULAS SUCCESSFULLY GENERATED!")
