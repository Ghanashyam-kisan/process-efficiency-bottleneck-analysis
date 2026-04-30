"""
streamlit_app.py
----------------
Interactive dashboard for the Process Efficiency &
Bottleneck Analysis System — Light / Bright Theme.

Run with:
    streamlit run app/streamlit_app.py
"""

import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import streamlit as st

from data_generator import generate_process_data, save_data, DELAY_THRESHOLD
from analysis       import (average_stage_times, identify_bottleneck,
                             delay_summary, stage_contribution, time_trend)
from metrics        import all_metrics

# ══════════════════════════════════════════════════
#  Page config
# ══════════════════════════════════════════════════
st.set_page_config(
    page_title="Process Efficiency & Bottleneck Analysis",
    page_icon="⚙️",
    layout="wide",
)

# ══════════════════════════════════════════════════
#  Custom CSS — bright, clean theme
# ══════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp { background-color: #F0F4FF; color: #1A1D2E; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A8A 0%, #1D4ED8 100%);
    }
    [data-testid="stSidebar"] * { color: #E0E7FF !important; }
    [data-testid="stSidebar"] .stButton button {
        background: #FFFFFF; color: #1E3A8A !important;
        font-weight: 700; border-radius: 8px; border: none;
    }
    [data-testid="stSidebar"] .stButton button:hover { background: #DBEAFE; }

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #BFDBFE;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 2px 8px rgba(30,58,138,0.08);
    }
    [data-testid="stMetricLabel"] { color: #4B5563 !important; font-size: 0.82rem !important; font-weight: 600 !important; }
    [data-testid="stMetricValue"] { color: #1E3A8A !important; font-size: 1.7rem !important; font-weight: 800 !important; }

    .section-header {
        font-size: 0.78rem; font-weight: 800; color: #1D4ED8;
        letter-spacing: 0.12em; text-transform: uppercase;
        margin: 1.6rem 0 0.6rem 0;
        padding-bottom: 8px; border-bottom: 2px solid #BFDBFE;
    }

    .bottleneck-badge {
        display: inline-block;
        background: linear-gradient(135deg, #DC2626, #B91C1C);
        color: white; padding: 7px 22px; border-radius: 24px;
        font-weight: 800; font-size: 1rem; letter-spacing: 0.04em;
        box-shadow: 0 3px 10px rgba(220,38,38,0.3);
    }

    .summary-card {
        background: #FFFFFF; border: 1px solid #BFDBFE;
        border-radius: 12px; padding: 18px 22px;
        box-shadow: 0 2px 8px rgba(30,58,138,0.07);
    }

    .page-title { color: #1E3A8A; font-size: 2rem; font-weight: 900; margin-bottom: 0; }
    .page-subtitle { color: #6B7280; margin-top: 4px; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  Chart colour palette
# ══════════════════════════════════════════════════
PALETTE = {
    "normal":     "#3B82F6",
    "bottleneck": "#EF4444",
    "line":       "#10B981",
    "rolling":    "#8B5CF6",
    "delayed":    "#F97316",
    "bg":         "#FFFFFF",
    "text":       "#1A1D2E",
    "grid":       "#E5E7EB",
    "threshold":  "#EF4444",
}

STAGE_LABELS = {
    "Stage_1_Time": "Stage 1",
    "Stage_2_Time": "Stage 2",
    "Stage_3_Time": "Stage 3",
}

# ══════════════════════════════════════════════════
#  Data loading
# ══════════════════════════════════════════════════
DATA_PATH = os.path.join(ROOT, "data", "process_data.csv")

@st.cache_data
def load_data() -> pd.DataFrame:
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    df = generate_process_data()
    save_data(df, DATA_PATH)
    return df


# ══════════════════════════════════════════════════
#  Chart helpers
# ══════════════════════════════════════════════════
def _apply_light_theme(fig, axes):
    fig.patch.set_facecolor(PALETTE["bg"])
    for ax in (axes if isinstance(axes, list) else [axes]):
        ax.set_facecolor(PALETTE["bg"])
        ax.tick_params(colors=PALETTE["text"], labelsize=10)
        ax.xaxis.label.set_color(PALETTE["text"])
        ax.yaxis.label.set_color(PALETTE["text"])
        ax.title.set_color(PALETTE["text"])
        for spine in ax.spines.values():
            spine.set_edgecolor("#D1D5DB")
        ax.grid(color=PALETTE["grid"], linestyle="--", alpha=0.8)


def make_bar_chart(avg_times: pd.Series, bottleneck: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4.2))
    _apply_light_theme(fig, ax)
    stages = [STAGE_LABELS[s] for s in avg_times.index]
    colors = [PALETTE["bottleneck"] if s == bottleneck else PALETTE["normal"]
              for s in avg_times.index]
    bars = ax.bar(stages, avg_times.values, color=colors,
                  edgecolor="white", linewidth=2, zorder=3, width=0.55)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3,
                f"{bar.get_height():.1f} min",
                ha="center", va="bottom",
                fontsize=11, fontweight="bold", color=PALETTE["text"])
    normal_p = mpatches.Patch(color=PALETTE["normal"],     label="Normal Stage")
    bottle_p = mpatches.Patch(color=PALETTE["bottleneck"], label="Bottleneck Stage")
    ax.legend(handles=[normal_p, bottle_p], fontsize=9,
              facecolor="white", edgecolor="#D1D5DB")
    ax.set_title("Average Time per Stage (minutes)", fontsize=13,
                 fontweight="bold", pad=14, color=PALETTE["text"])
    ax.set_ylabel("Minutes", fontsize=11)
    ax.set_ylim(0, avg_times.max() * 1.3)
    ax.grid(axis="y", zorder=0)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def make_trend_chart(df: pd.DataFrame, threshold: int) -> plt.Figure:
    trend = time_trend(df, window=50)
    fig, ax = plt.subplots(figsize=(12, 4))
    _apply_light_theme(fig, ax)
    x = range(len(trend))
    ax.fill_between(x, trend["Total_Time"], alpha=0.1, color=PALETTE["line"])
    ax.plot(x, trend["Total_Time"], color=PALETTE["line"],
            alpha=0.4, linewidth=0.8, label="Total Time per Run")
    ax.plot(x, trend["Rolling_Avg"], color=PALETTE["rolling"],
            linewidth=2.5, label="50-run Rolling Avg")
    ax.axhline(threshold, color=PALETTE["threshold"], linestyle="--",
               linewidth=2, label=f"Delay Threshold ({threshold} min)")
    ax.set_title("Process Time Trend", fontsize=13, fontweight="bold", pad=14)
    ax.set_xlabel("Process Run Index", fontsize=11)
    ax.set_ylabel("Total Time (min)", fontsize=11)
    ax.legend(fontsize=9, facecolor="white", edgecolor="#D1D5DB")
    fig.tight_layout()
    return fig


def make_contrib_chart(contribution: pd.Series, bottleneck: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 3.8))
    _apply_light_theme(fig, ax)
    stages = [STAGE_LABELS[s] for s in contribution.index]
    colors = [PALETTE["bottleneck"] if s == bottleneck else PALETTE["normal"]
              for s in contribution.index]
    bars = ax.barh(stages, contribution.values, color=colors,
                   edgecolor="white", linewidth=2, zorder=3, height=0.5)
    for bar in bars:
        ax.text(bar.get_width() + 0.5,
                bar.get_y() + bar.get_height() / 2,
                f"{bar.get_width():.1f}%",
                va="center", fontsize=11, fontweight="bold", color=PALETTE["text"])
    ax.set_title("Stage Contribution to Total Cycle Time", fontsize=13,
                 fontweight="bold", pad=14)
    ax.set_xlabel("Contribution (%)", fontsize=11)
    ax.set_xlim(0, contribution.max() * 1.22)
    ax.grid(axis="x", zorder=0)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    return fig


def make_histogram(df: pd.DataFrame, threshold: int) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 4))
    _apply_light_theme(fig, ax)
    on_time = df.loc[df["Delay_Flag"] == 0, "Total_Time"]
    delayed = df.loc[df["Delay_Flag"] == 1, "Total_Time"]
    bins = np.linspace(df["Total_Time"].min(), df["Total_Time"].max(), 30)
    ax.hist(on_time, bins=bins, color=PALETTE["line"],    alpha=0.75, label="On-Time",  zorder=3)
    ax.hist(delayed, bins=bins, color=PALETTE["delayed"], alpha=0.75, label="Delayed",  zorder=3)
    ax.axvline(threshold, color=PALETTE["bottleneck"], linestyle="--",
               linewidth=2, label=f"Threshold ({threshold} min)")
    ax.set_title("Distribution of Total Cycle Times", fontsize=13,
                 fontweight="bold", pad=14)
    ax.set_xlabel("Total Time (min)", fontsize=11)
    ax.set_ylabel("Frequency", fontsize=11)
    ax.legend(fontsize=9, facecolor="white", edgecolor="#D1D5DB")
    fig.tight_layout()
    return fig


# ══════════════════════════════════════════════════
#  Main app
# ══════════════════════════════════════════════════
def main():
    # Sidebar
    st.sidebar.markdown("## ⚙️ Control Panel")
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Regenerate Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    n_display = st.sidebar.slider("Rows to preview", 5, 50, 10)
    threshold = st.sidebar.slider(
        "Delay Threshold (min)", 20, 80, int(DELAY_THRESHOLD),
        help="Processes with Total_Time above this are flagged as delayed."
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Process Efficiency & Bottleneck Analysis System v1.0")

    # Load & compute
    df = load_data().copy()
    df["Delay_Flag"] = (df["Total_Time"] > threshold).astype(int)
    avg_times    = average_stage_times(df)
    bottleneck   = identify_bottleneck(df)
    delay_info   = delay_summary(df)
    contribution = stage_contribution(df)
    metrics      = all_metrics(df)

    # Header
    st.markdown("""
        <p class='page-title'>⚙️ Process Efficiency & Bottleneck Analysis</p>
        <p class='page-subtitle'>Real-time manufacturing process performance dashboard</p>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Bottleneck + delay summary
    col_b1, col_b2 = st.columns([1, 2.5])
    with col_b1:
        st.markdown("<div class='section-header'>🔴 Bottleneck Stage</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<span class='bottleneck-badge'>{STAGE_LABELS[bottleneck]}</span>",
                    unsafe_allow_html=True)
        st.caption(f"Avg: **{avg_times[bottleneck]:.2f} min** — highest contributor to delays")

    with col_b2:
        delay_color = ("#16A34A" if delay_info["delay_rate_pct"] < 20
                       else "#D97706" if delay_info["delay_rate_pct"] < 40
                       else "#DC2626")
        st.markdown(f"""
        <div class='summary-card'>
            <b style='color:#1E3A8A; font-size:0.9rem'>📋 Delay Analysis Summary</b><br><br>
            <span style='font-size:0.95rem'>
                Total Runs: <b>{delay_info['total_processes']:,}</b>
                &nbsp;|&nbsp;
                On-Time: <b style='color:#16A34A'>{delay_info['on_time_count']:,}</b>
                &nbsp;|&nbsp;
                Delayed: <b style='color:#DC2626'>{delay_info['delayed_count']:,}</b>
            </span><br><br>
            <span style='font-size:0.95rem'>
                Delay Rate: <b style='color:{delay_color}'>{delay_info['delay_rate_pct']:.1f}%</b>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                Threshold: <b>{threshold} min</b>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                Avg Delayed: <b>{delay_info['avg_delayed_time']:.1f} min</b>
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # KPI metrics
    st.markdown("<div class='section-header'>📊 Key Performance Indicators</div>",
                unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Avg Cycle Time",    f"{metrics['avg_total_time']:.1f} min")
    m2.metric("Ideal Cycle Time",  f"{metrics['ideal_cycle_time']:.1f} min")
    m3.metric("Throughput",        f"{metrics['throughput_per_hour']:.2f} /hr")
    m4.metric("Idle / Waste Time", f"{metrics['idle_time_min']:.1f} min")
    m5.metric("Efficiency",        f"{metrics['efficiency_pct']:.1f}%",
              delta=f"{metrics['efficiency_pct'] - 100:.1f}% vs ideal")

    st.markdown("<br>", unsafe_allow_html=True)

    # Stage charts
    st.markdown("<div class='section-header'>📈 Stage Analysis</div>",
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.pyplot(make_bar_chart(avg_times, bottleneck), use_container_width=True)
    with c2:
        st.pyplot(make_contrib_chart(contribution, bottleneck), use_container_width=True)

    # Trend + histogram
    st.markdown("<div class='section-header'>📉 Time Trend & Distribution</div>",
                unsafe_allow_html=True)
    st.pyplot(make_trend_chart(df, threshold), use_container_width=True)
    st.pyplot(make_histogram(df, threshold), use_container_width=True)

    # Data table
    st.markdown("<div class='section-header'>🗂️ Raw Data Preview</div>",
                unsafe_allow_html=True)
    styler = df.head(n_display).style
    style_fn = lambda v: ("background-color:#FEE2E2; color:#DC2626; font-weight:700"
                          if v == 1 else
                          "background-color:#DCFCE7; color:#16A34A; font-weight:700")
    apply_method = getattr(styler, "map", None) or getattr(styler, "applymap")
    styled = apply_method(style_fn, subset=["Delay_Flag"])
    st.dataframe(styled, use_container_width=True)

    csv = df.to_csv(index=False).encode()
    st.download_button("⬇️ Download Full Dataset (CSV)", csv,
                       "process_data.csv", "text/csv", type="primary")


if __name__ == "__main__":
    main()