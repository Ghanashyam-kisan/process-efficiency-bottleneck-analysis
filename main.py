"""
main.py
-------
Entry-point for the Process Efficiency & Bottleneck Analysis System.

Runs the full pipeline:
  1. Generate (or load) synthetic data
  2. Perform analysis
  3. Compute KPI metrics
  4. Export Matplotlib charts to /charts/
"""

import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── allow running from project root without installing package ──
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_generator import generate_process_data, save_data, DELAY_THRESHOLD
from analysis       import (average_stage_times, identify_bottleneck,
                             delay_summary, stage_contribution, time_trend)
from metrics        import all_metrics

# ── output dirs ──
DATA_PATH   = "data/process_data.csv"
CHARTS_DIR  = "charts"

STAGE_LABELS = {
    "Stage_1_Time": "Stage 1",
    "Stage_2_Time": "Stage 2",
    "Stage_3_Time": "Stage 3",
}

PALETTE = {
    "normal":      "#4A90D9",
    "bottleneck":  "#E74C3C",
    "highlight":   "#F39C12",
    "line":        "#2ECC71",
    "rolling":     "#9B59B6",
    "bg":          "#F8F9FA",
}


# ══════════════════════════════════════════════════
#  Helper: pretty section headers in terminal
# ══════════════════════════════════════════════════
def section(title: str) -> None:
    print(f"\n{'═' * 55}")
    print(f"  {title}")
    print(f"{'═' * 55}")


# ══════════════════════════════════════════════════
#  1. Data
# ══════════════════════════════════════════════════
def load_or_generate() -> pd.DataFrame:
    if os.path.exists(DATA_PATH):
        print(f"[main] Loading existing data from {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
    else:
        print("[main] Generating new synthetic data …")
        df = generate_process_data()
        save_data(df, DATA_PATH)
    return df


# ══════════════════════════════════════════════════
#  2. Visualisations
# ══════════════════════════════════════════════════
def chart_avg_stage_times(avg_times: pd.Series, bottleneck: str) -> None:
    """Bar chart of average time per stage, bottleneck highlighted in red."""
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    stages  = [STAGE_LABELS[s] for s in avg_times.index]
    colors  = [PALETTE["bottleneck"] if s == bottleneck else PALETTE["normal"]
               for s in avg_times.index]

    bars = ax.bar(stages, avg_times.values, color=colors, edgecolor="white",
                  linewidth=1.5, zorder=3)

    # Value labels on bars
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3,
                f"{bar.get_height():.1f} min",
                ha="center", va="bottom", fontsize=11, fontweight="bold")

    # Legend
    normal_patch = mpatches.Patch(color=PALETTE["normal"],     label="Normal Stage")
    bottle_patch = mpatches.Patch(color=PALETTE["bottleneck"], label="Bottleneck Stage")
    ax.legend(handles=[normal_patch, bottle_patch], fontsize=10)

    ax.set_title("Average Time per Stage", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Time (minutes)", fontsize=12)
    ax.set_xlabel("Process Stage", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)
    ax.set_ylim(0, avg_times.max() * 1.25)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "avg_stage_times.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[chart] Saved → {path}")


def chart_time_trend(df: pd.DataFrame) -> None:
    """Line chart: raw Total_Time + rolling average trend."""
    trend = time_trend(df, window=50)

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    x = range(len(trend))
    ax.plot(x, trend["Total_Time"], color=PALETTE["line"], alpha=0.35,
            linewidth=0.8, label="Total Time (per run)")
    ax.plot(x, trend["Rolling_Avg"], color=PALETTE["rolling"],
            linewidth=2.5, label="50-run Rolling Average")

    # Threshold line
    ax.axhline(DELAY_THRESHOLD, color=PALETTE["bottleneck"], linestyle="--",
               linewidth=1.5, label=f"Delay Threshold ({DELAY_THRESHOLD} min)")

    ax.set_title("Process Time Trend Over All Runs", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Process Run Index", fontsize=12)
    ax.set_ylabel("Total Time (minutes)", fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(linestyle="--", alpha=0.4)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "time_trend.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[chart] Saved → {path}")


def chart_stage_contribution(contribution: pd.Series, bottleneck: str) -> None:
    """Horizontal bar chart showing each stage's % share of total time."""
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    stages = [STAGE_LABELS[s] for s in contribution.index]
    colors = [PALETTE["bottleneck"] if s == bottleneck else PALETTE["normal"]
              for s in contribution.index]

    bars = ax.barh(stages, contribution.values, color=colors,
                   edgecolor="white", linewidth=1.5, zorder=3)

    for bar in bars:
        ax.text(bar.get_width() + 0.5,
                bar.get_y() + bar.get_height() / 2,
                f"{bar.get_width():.1f}%",
                va="center", fontsize=11, fontweight="bold")

    ax.set_title("Stage Contribution to Total Cycle Time (%)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Contribution (%)", fontsize=12)
    ax.set_xlim(0, contribution.max() * 1.2)
    ax.grid(axis="x", linestyle="--", alpha=0.4, zorder=0)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, "stage_contribution.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[chart] Saved → {path}")


# ══════════════════════════════════════════════════
#  3. Console report
# ══════════════════════════════════════════════════
def print_report(metrics: dict, delay_info: dict,
                 bottleneck: str, avg_times: pd.Series) -> None:
    section("PROCESS EFFICIENCY & BOTTLENECK ANALYSIS REPORT")

    print("\n📊  STAGE AVERAGE TIMES")
    for col, val in metrics["avg_stage_times"].items():
        label = STAGE_LABELS[col]
        flag  = " ← BOTTLENECK" if col == bottleneck else ""
        print(f"    {label}: {val:.2f} min{flag}")

    print("\n⚙️   KEY PERFORMANCE METRICS")
    print(f"    Avg Total Cycle Time  : {metrics['avg_total_time']:.2f} min")
    print(f"    Median Cycle Time     : {metrics['median_total_time']:.2f} min")
    print(f"    Max Cycle Time        : {metrics['max_total_time']:.2f} min")
    print(f"    Ideal Cycle Time      : {metrics['ideal_cycle_time']:.2f} min")
    print(f"    Throughput            : {metrics['throughput_per_hour']:.2f} processes/hour")
    print(f"    Idle / Waste Time     : {metrics['idle_time_min']:.2f} min per process")
    print(f"    Process Efficiency    : {metrics['efficiency_pct']:.1f}%")

    print("\n🚨  DELAY ANALYSIS")
    print(f"    Total Processes       : {delay_info['total_processes']:,}")
    print(f"    On-Time               : {delay_info['on_time_count']:,}")
    print(f"    Delayed               : {delay_info['delayed_count']:,}")
    print(f"    Delay Rate            : {delay_info['delay_rate_pct']:.1f}%")
    print(f"    Avg On-Time Duration  : {delay_info['avg_on_time_time']:.2f} min")
    print(f"    Avg Delayed Duration  : {delay_info['avg_delayed_time']:.2f} min")
    print(f"    Delay Threshold       : {DELAY_THRESHOLD} min")

    print(f"\n🔴  IDENTIFIED BOTTLENECK : {STAGE_LABELS[bottleneck]}")
    print(f"    (This stage contributes the most to delayed processes)")
    print()


# ══════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════
def main() -> None:
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # --- Data ---
    df = load_or_generate()

    # --- Analysis ---
    avg_times    = average_stage_times(df)
    bottleneck   = identify_bottleneck(df)
    delay_info   = delay_summary(df)
    contribution = stage_contribution(df)
    metrics      = all_metrics(df)

    # --- Report ---
    print_report(metrics, delay_info, bottleneck, avg_times)

    # --- Charts ---
    section("GENERATING CHARTS")
    chart_avg_stage_times(avg_times, bottleneck)
    chart_time_trend(df)
    chart_stage_contribution(contribution, bottleneck)

    section("DONE")
    print(f"  Charts saved to: ./{CHARTS_DIR}/")
    print(f"  Data file:       ./{DATA_PATH}")
    print("  Run the Streamlit dashboard: streamlit run app/streamlit_app.py\n")


if __name__ == "__main__":
    main()
