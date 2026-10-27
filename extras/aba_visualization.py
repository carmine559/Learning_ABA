"""
aba_visualization.py
Publication-quality figures for the thesis.
All functions return matplotlib Figure objects (no side effects).
"""
from __future__ import annotations
import math
from typing import List, Dict, Optional, Tuple, Any

import matplotlib
matplotlib.use("Agg")           # headless — safe in notebooks too
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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

ERROR_COLORS = {
    "none":               PALETTE["green"],
    "parse_error":        PALETTE["orange"],
    "completeness_error": PALETTE["blue"],
    "soundness_error":    PALETTE["red"],
    "stability_error":    PALETTE["purple"],
    "overgeneralisation": PALETTE["brown"],
    "unknown_error":      PALETTE["grey"],
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
    title: str = "Generalisation by prompting mode",
    figsize: Tuple = (7, 4),
) -> plt.Figure:
    """
    Grouped bar chart: parse rate + validity rate per mode.
    """
    _apply_thesis_style()
    modes   = [m for m in MODE_ORDER if m in results_by_mode]
    labels  = [MODE_LABELS.get(m, m) for m in modes]
    fit_v  = [aggregate_results(results_by_mode[m])["fit_at_1"]  for m in modes]
    gen_v  = [aggregate_results(results_by_mode[m])["gen_at_1"]  for m in modes]
    genk_v = [aggregate_results(results_by_mode[m])["gen_at_k"]  for m in modes]

    x   = np.arange(len(modes))
    w   = 0.25
    fig, ax = plt.subplots(figsize=figsize)

    b1 = ax.bar(x - w,  fit_v,  w, label="Fit@1 (train)",     color=PALETTE["grey"],   alpha=0.85)
    b2 = ax.bar(x,       gen_v,  w, label="Gen@1 (held-out)",   color=PALETTE["green"],  alpha=0.85)
    b3 = ax.bar(x + w,   genk_v, w, label="Gen@k (any of k)",   color=PALETTE["blue"],   alpha=0.85)

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
    Stacked bar chart showing distribution of error types per mode.
    """
    _apply_thesis_style()
    modes       = [m for m in MODE_ORDER if m in results_by_mode]
    labels      = [MODE_LABELS.get(m, m) for m in modes]
    error_types = list(ERROR_COLORS.keys())

    # Build matrix [modes × error_types]
    data = np.zeros((len(modes), len(error_types)))
    for i, mode in enumerate(modes):
        agg = aggregate_results(results_by_mode[mode])
        bd  = agg.get("error_breakdown", {})
        n   = max(agg["n_problems"], 1)
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
    ax.set_ylabel("Fraction of problems")
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
    title: str = "Validity rate vs. problem complexity",
    figsize: Tuple = (6, 4),
) -> plt.Figure:
    """
    Scatter plot: each point = one problem, colour = valid/invalid.
    An optional regression curve is overlaid if there are enough points.
    """
    _apply_thesis_style()
    xs_v, ys_v = [], []
    xs_i, ys_i = [], []
    jitter = np.random.default_rng(42)

    for row in complexity_rows:
        x = row[x_key] + jitter.uniform(-0.15, 0.15)
        y = 1 if row["valid"] else 0
        y += jitter.uniform(-0.03, 0.03)
        if row["valid"]:
            xs_v.append(x); ys_v.append(y)
        else:
            xs_i.append(x); ys_i.append(y)

    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(xs_v, ys_v, c=PALETTE["green"],  alpha=0.6, s=30, label="Valid",   zorder=3)
    ax.scatter(xs_i, ys_i, c=PALETTE["red"],    alpha=0.6, s=30, label="Invalid", zorder=3)

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
    ax.set_ylabel("Valid (jittered)")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Invalid", "Valid"])
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
    `summary` maps config_name → aggregated metrics dict.
    """
    _apply_thesis_style()
    if metrics is None:
        metrics = ["gen_at_1", "gen_at_k", "fit_at_1",
                   "intensional_rate", "degenerate_rate",
                   "mean_overfit_gap", "parse_rate"]

    col_labels = [m.replace("_", "\n") for m in metrics]
    row_labels  = list(summary.keys())
    cell_data   = []
    for name in row_labels:
        agg  = summary[name]
        row  = []
        for m in metrics:
            v = agg.get(m, "—")
            if isinstance(v, float):
                row.append(f"{v:.1%}" if "rate" in m else f"{v:.2f}")
            else:
                row.append(str(v))
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
                      if "rate" in m and m in metrics}
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


# ── 5. SFT training curves ────────────────────────────────────────────────────

def plot_training_curves(
    log_history: List[Dict],
    title: str = "SFT training curve",
    figsize: Tuple = (8, 4),
) -> plt.Figure:
    """
    Plot train loss and eval loss from HuggingFace Trainer log_history.
    """
    _apply_thesis_style()
    train_steps, train_loss = [], []
    eval_steps,  eval_loss  = [], []

    for entry in log_history:
        if "loss" in entry:
            train_steps.append(entry.get("step", len(train_steps)))
            train_loss.append(entry["loss"])
        if "eval_loss" in entry:
            eval_steps.append(entry.get("step", len(eval_steps)))
            eval_loss.append(entry["eval_loss"])

    fig, ax = plt.subplots(figsize=figsize)
    if train_steps:
        ax.plot(train_steps, train_loss, color=PALETTE["blue"],
                label="Train loss", linewidth=1.5)
    if eval_steps:
        ax.plot(eval_steps, eval_loss, color=PALETTE["orange"],
                label="Eval loss", linewidth=1.5, linestyle="--")

    ax.set_xlabel("Training step")
    ax.set_ylabel("Loss")
    ax.set_title(title)
    ax.legend(framealpha=0.8)
    fig.tight_layout()
    return fig


# ── 6. QBAF graph (for a single problem / solution) ──────────────────────────

def plot_qbaf(
    rules: List,           # List[Rule]
    assumptions: List[str],
    contraries: Dict[str, str],
    title: str = "Learned ABA framework",
    figsize: Tuple = (9, 5),
) -> plt.Figure:
    """
    Visualise the rule dependency graph of an ABA framework.
    Nodes = predicates, edges = rule dependencies.
    Assumptions shown in a different colour.
    Requires networkx.
    """
    _apply_thesis_style()
    try:
        import networkx as nx
    except ImportError:
        fig, ax = plt.subplots(figsize=(4, 1))
        ax.text(0.5, 0.5, "pip install networkx for QBAF visualisation",
                ha="center", va="center", transform=ax.transAxes)
        ax.axis("off")
        return fig

    G = nx.DiGraph()
    asm_preds = {re.match(r'^([a-z]\w*)', a).group(1)
                 for a in assumptions if re.match(r'^([a-z]\w*)', a)}
    contrary_preds = {re.match(r'^([a-z]\w*)', c).group(1)
                      for c in contraries.values()
                      if re.match(r'^([a-z]\w*)', c)}

    import re as _re
    def _pred(atom: str) -> str:
        m = _re.match(r'^([a-z]\w*)', atom)
        return m.group(1) if m else atom

    for rule in rules:
        head_pred = _pred(rule.head)
        G.add_node(head_pred)
        for body_atom in rule.body:
            bp = _pred(body_atom)
            if bp not in ("dom", "not"):
                G.add_edge(bp, head_pred)

    node_colors = []
    for node in G.nodes():
        if node in asm_preds:
            node_colors.append(PALETTE["orange"])
        elif node in contrary_preds:
            node_colors.append(PALETTE["red"])
        else:
            node_colors.append(PALETTE["blue"])

    fig, ax = plt.subplots(figsize=figsize)
    try:
        pos = nx.drawing.nx_pydot.graphviz_layout(G, prog="dot")
    except Exception:
        pos = nx.spring_layout(G, seed=42)

    nx.draw_networkx(
        G, pos, ax=ax,
        node_color=node_colors, node_size=1400,
        font_size=9, font_color="white", font_weight="bold",
        edge_color=PALETTE["grey"], arrows=True,
        arrowstyle="->", arrowsize=15,
        connectionstyle="arc3,rad=0.1",
    )

    legend_handles = [
        mpatches.Patch(color=PALETTE["blue"],   label="Derived predicate"),
        mpatches.Patch(color=PALETTE["orange"], label="Assumption"),
        mpatches.Patch(color=PALETTE["red"],    label="Contrary"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=8)
    ax.set_title(title)
    ax.axis("off")
    fig.tight_layout()
    return fig


# ── 7. Per-problem heatmap ───────────────────────────────────────────────────

def plot_results_heatmap(
    results_by_mode: Dict[str, List[ProblemResult]],
    title: str = "Generalisation (gen@k) per problem × mode",
    figsize: Tuple = (10, 5),
) -> plt.Figure:
    """
    Heatmap: rows = problems, columns = modes, cell = valid (green) / invalid (red).
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
                mat[i, j] = 1.0 if rid_map[pid].gen_at_k else 0.0

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
        Patch(facecolor="#5cb85c", label="Valid"),
        Patch(facecolor="#d9534f", label="Invalid"),
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