"""
aba_visualization.py
Publication-quality figures for the thesis.
All functions return matplotlib Figure objects (no side effects).
"""
from __future__ import annotations
from typing import List, Dict, Optional, Tuple

import matplotlib
matplotlib.use("Agg")           # headless — safe in notebooks too
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from src.aba_evaluation import ProblemResult, aggregate_results

# ── Style ──────────────────────────────────────────────────────────────────

PALETTE = {
    "blue":   "#1f77b4",
    "orange": "#ff7f0e",
    "green":  "#2ca02c",
    "red":    "#d62728",
    "purple": "#9467bd",
    "grey":   "#7f7f7f",
    "teal":   "#17becf",
    "brown":  "#8c564b",
}

# The score card's labels (src/aba_score.py), plus the generation failures.
ERROR_COLORS = {
    "ok":                     PALETTE["green"],
    "parse_error":            PALETTE["orange"],
    "illformed":              PALETTE["purple"],
    "not_a_solution":         PALETTE["red"],
    "valid_but_degenerate":   PALETTE["brown"],
    "self_defeating":         PALETTE["blue"],
    "illegal_transformation": PALETTE["teal"],
    "llm_error":              PALETTE["grey"],
    "unscorable":             PALETTE["grey"],
}

MODE_ORDER   = ["direct", "cot", "guided", "algorithm"]
MODE_LABELS  = {
    "direct":    "Zero-shot\n(direct)",
    "cot":       "Chain-of-\nthought",
    "guided":    "Guided\n(RoLe hint)",
    "algorithm": "Algorithm\n(execute)",
}

def _apply_thesis_style() -> None:
    plt.rcParams.update({
        "font.family":       "serif",
        "font.size":         11,
        "axes.titlesize":    12,
        "axes.labelsize":    11,
        "xtick.labelsize":   9,
        "ytick.labelsize":   9,
        "legend.fontsize":   9,
        "figure.dpi":        150,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.grid":         True,
        "grid.alpha":        0.3,
        "grid.linestyle":    "--",
    })


# ── 1. Validity by prompt mode ──────────────────────────────────────────────

def plot_validity_by_mode(
    results_by_mode: Dict[str, List[ProblemResult]],
    title: str = "Valid, clean and exact by prompting mode",
    figsize: Tuple = (7, 4),
) -> plt.Figure:
    """
    Grouped bar chart per mode: valid@1, clean@k, exact@k.
    """
    _apply_thesis_style()
    modes   = [m for m in MODE_ORDER if m in results_by_mode]
    labels  = [MODE_LABELS.get(m, m) for m in modes]
    aggs    = [aggregate_results(results_by_mode[m]) for m in modes]
    valid_v = [a["valid_at_1"] for a in aggs]
    clean_v = [a["clean_at_k"] for a in aggs]
    exact_v = [a["exact_at_k"] for a in aggs]

    x   = np.arange(len(modes))
    w   = 0.25
    fig, ax = plt.subplots(figsize=figsize)

    b1 = ax.bar(x - w, valid_v, w, label="Valid@1 (Definition 1)", color=PALETTE["grey"],  alpha=0.85)
    b2 = ax.bar(x,     clean_v, w, label="Clean@k (any of k)",     color=PALETTE["green"], alpha=0.85)
    b3 = ax.bar(x + w, exact_v, w, label="Exact@k (the algorithm's answer)", color=PALETTE["blue"], alpha=0.85)

    for bars in (b1, b2, b3):
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.01,
                        f"{h:.0%}", ha="center", va="bottom", fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.12)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.set_ylabel("Rate")
    ax.set_title(title)
    ax.legend(loc="upper right", framealpha=0.8)
    fig.tight_layout()
    return fig


# ── 2. Error breakdown ───────────────────────────────────────────────────────

def plot_error_breakdown(
    results_by_mode: Dict[str, List[ProblemResult]],
    title: str = "Error breakdown by prompting mode",
    figsize: Tuple = (8, 4),
) -> plt.Figure:
    """
    Stacked bar chart: the share of samples under each score-card label, per mode.
    """
    _apply_thesis_style()
    modes       = [m for m in MODE_ORDER if m in results_by_mode]
    labels      = [MODE_LABELS.get(m, m) for m in modes]
    error_types = list(ERROR_COLORS.keys())

    # Build matrix [modes × error_types]
    data = np.zeros((len(modes), len(error_types)))
    for i, mode in enumerate(modes):
        agg = aggregate_results(results_by_mode[mode])
        bd: Dict[str, int] = {}
        for label, c in agg.get("errors", {}).items():
            key = label.split(":")[0]               # unscorable:<type>
            bd[key] = bd.get(key, 0) + c
        n   = max(agg["n_samples"], 1)
        for j, et in enumerate(error_types):
            data[i, j] = bd.get(et, 0) / n

    fig, ax = plt.subplots(figsize=figsize)
    x       = np.arange(len(modes))
    bottoms = np.zeros(len(modes))

    for j, et in enumerate(error_types):
        vals = data[:, j]
        if vals.sum() == 0:
            continue
        ax.bar(x, vals, bottom=bottoms,
               color=ERROR_COLORS[et], label=et.replace("_", " "), alpha=0.9)
        bottoms += vals

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction of samples")
    ax.set_title(title)
    handles, labels_ = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc="upper right", fontsize=8, framealpha=0.8)
    fig.tight_layout()
    return fig


# ── 3. Complexity vs. validity ────────────────────────────────────────────────

def plot_complexity_vs_validity(
    complexity_rows: List[Dict],
    x_key: str = "n_background_rules",
    y_key: str = "clean_at_k",
    title: str = "Clean@k vs. problem complexity",
    figsize: Tuple = (6, 4),
) -> plt.Figure:
    """
    Scatter plot: each point = one problem, colour = `y_key` true/false.
    An optional regression curve is overlaid if there are enough points.
    """
    _apply_thesis_style()
    xs_v, ys_v = [], []
    xs_i, ys_i = [], []
    jitter = np.random.default_rng(42)

    for row in complexity_rows:
        x = row[x_key] + jitter.uniform(-0.15, 0.15)
        y = 1 if row[y_key] else 0
        y += jitter.uniform(-0.03, 0.03)
        if row[y_key]:
            xs_v.append(x); ys_v.append(y)
        else:
            xs_i.append(x); ys_i.append(y)

    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(xs_v, ys_v, c=PALETTE["green"],  alpha=0.6, s=30, label="Clean",     zorder=3)
    ax.scatter(xs_i, ys_i, c=PALETTE["red"],    alpha=0.6, s=30, label="Not clean", zorder=3)

    # Logistic regression overlay if sklearn available
    try:
        from sklearn.linear_model import LogisticRegression
        all_x = np.array(xs_v + xs_i).reshape(-1, 1)
        all_y = np.array([1] * len(xs_v) + [0] * len(xs_i))
        if len(set(all_y)) == 2 and len(all_y) >= 10:
            lr = LogisticRegression().fit(all_x, all_y)
            xr = np.linspace(all_x.min(), all_x.max(), 200).reshape(-1, 1)
            yr = lr.predict_proba(xr)[:, 1]
            ax.plot(xr, yr, "--", color=PALETTE["grey"],
                    linewidth=1.5, label="Logistic fit", zorder=2)
    except ImportError:
        pass

    x_label = x_key.replace("_", " ").title()
    ax.set_xlabel(x_label)
    ax.set_ylabel(f"{y_key} (jittered)")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["no", "yes"])
    ax.set_title(title)
    ax.legend(framealpha=0.8)
    fig.tight_layout()
    return fig


# ── 4. Model comparison table ────────────────────────────────────────────────

def plot_comparison_table(
    summary: Dict[str, Dict],
    metrics: Optional[List[str]] = None,
    title: str = "Results summary",
    figsize: Tuple = (9, 0.5),
) -> plt.Figure:
    """
    Render a formatted table as a matplotlib figure.
    `summary` is summary.json: mode -> aggregated metrics, plus `run` and `by_tier`.
    """
    _apply_thesis_style()
    if metrics is None:
        metrics = ["valid_at_1", "clean_at_k", "exact_at_k", "agreement",
                   "r3_balanced", "parse_rate", "truncated_rate"]

    col_labels = [m.replace("_", "\n") for m in metrics]
    row_labels  = [k for k in summary if k not in ("run", "by_tier")]
    cell_data   = []
    for name in row_labels:
        agg  = summary[name]
        row  = []
        for m in metrics:
            v = agg.get(m)
            if isinstance(v, float):
                row.append(f"{v:.1%}" if ("rate" in m or "_at_" in m) else f"{v:.2f}")
            else:
                row.append("—" if v is None else str(v))
        cell_data.append(row)

    n_rows = len(row_labels)
    height = max(1.0, 0.4 * (n_rows + 2))
    fig, ax = plt.subplots(figsize=(figsize[0], height))
    ax.axis("off")

    tbl = ax.table(
        cellText=cell_data,
        rowLabels=row_labels,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.auto_set_column_width(col=list(range(len(metrics))))

    # Highlight best per column (validity, intensionality)
    highlight_cols = {metrics.index(m) for m in metrics
                      if "_at_" in m and m in metrics}
    for col_idx in highlight_cols:
        values = []
        for row_idx, row in enumerate(cell_data):
            try:
                values.append((float(row[col_idx].replace("%", "")) / 100, row_idx))
            except ValueError:
                pass
        if values:
            best_row = max(values)[1]
            cell = tbl[best_row + 1, col_idx]  # +1 because of header row
            cell.set_facecolor("#d4edda")

    ax.set_title(title, fontsize=12, pad=10)
    fig.tight_layout()
    return fig


# ── 5. Per-problem heatmap ───────────────────────────────────────────────────

def plot_results_heatmap(
    results_by_mode: Dict[str, List[ProblemResult]],
    title: str = "Clean@k per problem × mode",
    figsize: Tuple = (10, 5),
) -> plt.Figure:
    """
    Heatmap: rows = problems, columns = modes, cell = clean@k (green) or not (red).
    """
    _apply_thesis_style()
    modes    = [m for m in MODE_ORDER if m in results_by_mode]
    all_pids = list(dict.fromkeys(
        r.problem_id
        for mode in modes
        for r in results_by_mode[mode]
    ))

    mat = np.full((len(all_pids), len(modes)), fill_value=np.nan)
    for j, mode in enumerate(modes):
        rid_map = {r.problem_id: r for r in results_by_mode[mode]}
        for i, pid in enumerate(all_pids):
            if pid in rid_map:
                mat[i, j] = 1.0 if rid_map[pid].at_k("clean") else 0.0

    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(["#d9534f", "#5cb85c"])

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(mat, cmap=cmap, vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(len(modes)))
    ax.set_xticklabels([MODE_LABELS.get(m, m) for m in modes], fontsize=9)
    ax.set_yticks(range(len(all_pids)))
    ax.set_yticklabels(all_pids, fontsize=8)
    ax.set_title(title)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#5cb85c", label="Clean"),
        Patch(facecolor="#d9534f", label="Not clean"),
    ]
    ax.legend(handles=legend_elements, loc="upper right",
              bbox_to_anchor=(1.12, 1), fontsize=8)
    fig.tight_layout()
    return fig


# ── Convenience: save all plots ───────────────────────────────────────────────

def save_all_plots(
    results_by_mode: Dict[str, List[ProblemResult]],
    complexity_rows: List[Dict],
    summary: Dict[str, Dict],
    output_dir: str = "./figures",
    fmt: str = "pdf",
) -> None:
    import os
    os.makedirs(output_dir, exist_ok=True)

    figs = {
        "validity_by_mode":    plot_validity_by_mode(results_by_mode),
        "error_breakdown":     plot_error_breakdown(results_by_mode),
        "heatmap":             plot_results_heatmap(results_by_mode),
        "comparison_table":    plot_comparison_table(summary),
    }
    if complexity_rows:
        figs["complexity_vs_validity"] = plot_complexity_vs_validity(complexity_rows)

    for name, fig in figs.items():
        path = os.path.join(output_dir, f"{name}.{fmt}")
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved {path}")