#!/usr/bin/env python3
"""
make_figures.py — publication-ready figures for the HexStrike evaluation.

Every number is hardcoded from docs/results_analysis.md (baseline §1-§10, post-fix §11, stats §12):
no recomputation, no new data. Outputs PNG (200 dpi) + PDF into ./figures/.

Run:  python make_figures.py        (needs matplotlib + numpy)
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 120,
})
C_BASE, C_POST = "#9aa0a6", "#1a73e8"   # baseline grey, post-fix blue
# In-image titles OFF for the report (the figure CAPTION carries the description, and a baked-in
# title would clash with section headings like "Where capability ran out"). Flip to True for slides.
SHOW_TITLES = False


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote figures/{name}.png + .pdf")


# ── Fig 1: before/after solve rate by configuration, with 95% Wilson CIs (§12.1) ──
def fig_config():
    labels = ["Claude /\nSonnet 4.6", "DeepSeek /\nRooCode", "DeepSeek /\n5ire", "Overall"]
    base = [78.7, 59.7, 27.9, 55.4]
    post = [89.9, 76.4, 49.6, 72.0]
    base_ci = [(73.3, 83.2), (53.6, 65.5), (22.8, 33.7), (51.9, 58.9)]
    post_ci = [(85.6, 93.0), (70.8, 81.1), (43.6, 55.7), (68.7, 75.0)]

    def err(vals, cis):
        lo = [v - c[0] for v, c in zip(vals, cis)]
        hi = [c[1] - v for v, c in zip(vals, cis)]
        return [lo, hi]

    x = np.arange(len(labels)); w = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.bar(x - w/2, base, w, yerr=err(base, base_ci), capsize=4, color=C_BASE, label="Baseline")
    ax.bar(x + w/2, post, w, yerr=err(post, post_ci), capsize=4, color=C_POST, label="Post-fix")
    for i, (b, p) in enumerate(zip(base, post)):
        ax.text(i + w/2, post_ci[i][1] + 2.0, f"+{p-b:.1f}", ha="center", va="bottom",
                fontsize=9, fontweight="bold", color=C_POST)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("Solve rate (%)"); ax.set_ylim(0, 100)
    if SHOW_TITLES: ax.set_title("Solve rate before vs. after the fixes (95% Wilson CIs)")
    ax.legend(frameon=False, loc="upper right")
    save(fig, "fig1_config_before_after")


# ── Fig 2: difficulty gradient, pre vs post (§11.3b) ──
def fig_difficulty():
    labels = ["Easy", "Medium", "Hard"]
    pre = [75.7, 60.2, 30.6]; post = [94.2, 81.7, 39.7]
    x = np.arange(len(labels)); w = 0.38
    fig, ax = plt.subplots(figsize=(7, 4.6))
    ax.bar(x - w/2, pre, w, color=C_BASE, label="Baseline")
    ax.bar(x + w/2, post, w, color=C_POST, label="Post-fix")
    for i, (a, b) in enumerate(zip(pre, post)):
        ax.text(i - w/2, a + 1.5, f"{a:.1f}", ha="center", va="bottom", fontsize=9, color="#555")
        ax.text(i + w/2, b + 1.5, f"{b:.1f}", ha="center", va="bottom", fontsize=9, color=C_POST)
        ax.text(i, max(a, b) + 8, f"+{b-a:.1f}pp", ha="center", va="bottom",
                fontsize=9, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("Solve rate (%)"); ax.set_ylim(0, 105)
    if SHOW_TITLES: ax.set_title("Solve rate by difficulty (all experiments)")
    ax.legend(frameon=False, loc="upper right")
    save(fig, "fig2_difficulty_gradient")


# ── Fig 3: category × difficulty baseline heatmap (§5) ──
def fig_heatmap():
    cats = ["Crypto", "Web", "Reversing", "Binary", "General", "Forensics", "Blockchain"]
    diffs = ["Easy", "Medium", "Hard"]
    data = np.array([
        [93.3, 66.7, 20.0],
        [82.2, 33.3, 13.3],
        [81.5, 69.4, 47.2],
        [75.0, 60.0, 20.0],
        [71.1, 62.2, 11.1],
        [53.3, 62.2, 48.9],
        [np.nan, 83.3, 66.7],   # Blockchain has no Easy challenges
    ])
    masked = np.ma.masked_invalid(data)
    cmap = plt.cm.RdYlGn.copy(); cmap.set_bad("#e8e8e8")
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    im = ax.imshow(masked, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(diffs))); ax.set_xticklabels(diffs)
    ax.set_yticks(range(len(cats))); ax.set_yticklabels(cats)
    for i in range(len(cats)):
        for j in range(len(diffs)):
            v = data[i, j]
            if np.isnan(v):
                ax.text(j, i, "—", ha="center", va="center", color="#999")
            else:
                ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                        color="black" if 30 <= v <= 75 else "white", fontsize=9)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("Baseline solve rate (%)")
    if SHOW_TITLES: ax.set_title("Where capability ran out (baseline)")
    save(fig, "fig3_category_difficulty_heatmap")


# ── Fig 4: attribution of the 128 recovered trials (§11.5) ──
def fig_attribution():
    segs = [("Tools we built", 24, "#1a73e8"),
            ("Re-pointed existing tool (pwntools)", 25, "#34a853"),
            ("Behavioral / default fixes", 79, "#fbbc04")]
    total = sum(s[1] for s in segs)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    left = 0
    for name, val, color in segs:
        ax.barh(0, val, left=left, color=color, edgecolor="white",
                label=f"{name} — {val} ({val/total*100:.1f}%)")
        ax.text(left + val/2, 0, str(val), ha="center", va="center", fontsize=12,
                fontweight="bold", color="white" if color != "#fbbc04" else "black")
        left += val
    ax.set_xlim(0, total); ax.set_ylim(-0.5, 0.5)
    ax.set_yticks([]); ax.set_xlabel(f"Recovered (flipped) trials  (n = {total})")
    if SHOW_TITLES: ax.set_title("What recovered the 128 previously-unsuccessful")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.30), ncol=1, fontsize=9.5)
    save(fig, "fig4_flip_attribution")


# ── Fig 5: solve rate by tool-access regime, pre vs post, per configuration (§11.4) ──
def fig_regime():
    regimes = ["Exp 1\nFree", "Exp 2\nRanked", "Exp 3\nStrict"]
    data = {  # config -> (baseline[3], post-fix[3]) for Exp 1 / 2 / 3
        "Claude / Sonnet 4.6": ([76.7, 76.7, 82.6], [89.5, 90.7, 89.5]),
        "DeepSeek / RooCode":  ([59.3, 59.3, 60.5], [76.7, 75.6, 76.7]),
        "DeepSeek / 5ire":     ([30.2, 19.8, 33.7], [43.0, 40.7, 65.1]),
    }
    x = np.arange(3); w = 0.38
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.2), sharey=True)
    for ax, (cfg, (pre, post)) in zip(axes, data.items()):
        ax.bar(x - w/2, pre, w, color=C_BASE, label="Baseline")
        ax.bar(x + w/2, post, w, color=C_POST, label="Post-fix")
        for i, (a, b) in enumerate(zip(pre, post)):
            ax.text(i + w/2, b + 1.5, f"+{b-a:.0f}", ha="center", va="bottom",
                    fontsize=8.5, fontweight="bold", color=C_POST)
        ax.set_xticks(x); ax.set_xticklabels(regimes)
        ax.set_title(cfg, fontsize=11)
        ax.set_ylim(0, 100)
    axes[0].set_ylabel("Solve rate (%)")
    axes[2].legend(frameon=False, loc="upper left", fontsize=9)
    if SHOW_TITLES:
        fig.suptitle("Solve rate by tool-access regime, before vs. after", y=1.02)
    save(fig, "fig5_regime_before_after")


if __name__ == "__main__":
    print("Generating figures ->", OUT)
    fig_config(); fig_difficulty(); fig_heatmap(); fig_attribution(); fig_regime()
    print("Done.")
