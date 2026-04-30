"""
analysis.py
-----------
Core analysis functions for the Process Efficiency &
Bottleneck Analysis System.
"""

import pandas as pd
import numpy as np

# The three stages we care about
STAGE_COLS = ["Stage_1_Time", "Stage_2_Time", "Stage_3_Time"]
DELAY_THRESHOLD = 62   # minutes – processes above this are flagged as delayed


# ──────────────────────────────────────────────
#  Stage-level analysis
# ──────────────────────────────────────────────

def average_stage_times(df: pd.DataFrame) -> pd.Series:
    """Return the mean time (minutes) for each process stage."""
    return df[STAGE_COLS].mean().round(2)


def identify_bottleneck(df: pd.DataFrame) -> str:
    """
    Identify which stage causes the most delays.

    Strategy: find the stage whose average time is highest
    among delayed processes only. If no delays exist,
    fall back to the overall stage with the highest mean.
    """
    delayed = df[df["Delay_Flag"] == 1]

    if delayed.empty:
        # No delays – use overall averages
        return df[STAGE_COLS].mean().idxmax()

    return delayed[STAGE_COLS].mean().idxmax()


def delay_summary(df: pd.DataFrame) -> dict:
    """
    Summarise delay statistics.

    Returns
    -------
    dict with keys:
        total_processes, delayed_count, on_time_count,
        delay_rate_pct, avg_delayed_time, avg_on_time_time
    """
    total    = len(df)
    delayed  = df["Delay_Flag"].sum()
    on_time  = total - delayed

    avg_delayed  = df.loc[df["Delay_Flag"] == 1, "Total_Time"].mean()
    avg_on_time  = df.loc[df["Delay_Flag"] == 0, "Total_Time"].mean()

    return {
        "total_processes": total,
        "delayed_count":   int(delayed),
        "on_time_count":   int(on_time),
        "delay_rate_pct":  round(delayed / total * 100, 2),
        "avg_delayed_time":  round(avg_delayed, 2) if not np.isnan(avg_delayed) else 0,
        "avg_on_time_time":  round(avg_on_time, 2)  if not np.isnan(avg_on_time) else 0,
    }


def stage_contribution(df: pd.DataFrame) -> pd.Series:
    """Return each stage's percentage contribution to average total time."""
    avg_stages = df[STAGE_COLS].mean()
    return (avg_stages / avg_stages.sum() * 100).round(2)


def time_trend(df: pd.DataFrame, window: int = 50) -> pd.DataFrame:
    """
    Compute a rolling average of Total_Time to show trends over process runs.

    Parameters
    ----------
    window : int
        Rolling window size (number of process runs).
    """
    trend = df[["Process_ID", "Total_Time"]].copy()
    trend["Rolling_Avg"] = trend["Total_Time"].rolling(window=window, min_periods=1).mean().round(2)
    return trend
