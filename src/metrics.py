"""
metrics.py
----------
Business-level KPI computations for the Process Efficiency &
Bottleneck Analysis System.

Definitions
-----------
Throughput     : Number of processes completed per hour
                 = 60 / avg_total_time  (assuming one process at a time)
Idle Time      : Time between ideal minimum cycle and actual average cycle
                 = avg_total_time - ideal_total_time
Efficiency %   : ideal_total_time / avg_total_time × 100
                 Higher is better (100 % = zero waste/idle time)
"""

import pandas as pd

STAGE_COLS = ["Stage_1_Time", "Stage_2_Time", "Stage_3_Time"]


def compute_throughput(df: pd.DataFrame) -> float:
    """
    Processes completed per hour (single-line assumption).

    Returns
    -------
    float : throughput in processes/hour
    """
    avg_cycle = df["Total_Time"].mean()          # minutes per process
    return round(60 / avg_cycle, 4)              # processes per hour


def compute_ideal_cycle(df: pd.DataFrame) -> float:
    """
    Ideal (minimum realistic) cycle time = sum of each stage's minimum.

    This represents the theoretical best-case scenario with no variability.
    """
    # Use the 5th-percentile for each stage as "ideal" (not absolute min to avoid anomalies)
    ideal = df[STAGE_COLS].quantile(0.05).sum()
    return round(ideal, 2)


def compute_idle_time(df: pd.DataFrame) -> float:
    """
    Average idle / waste time per process run (minutes).

    idle_time = avg_total_time − ideal_total_time
    """
    avg_cycle   = df["Total_Time"].mean()
    ideal_cycle = compute_ideal_cycle(df)
    return round(max(avg_cycle - ideal_cycle, 0), 2)


def compute_efficiency(df: pd.DataFrame) -> float:
    """
    Process efficiency as a percentage.

    efficiency = (ideal_cycle / avg_cycle) × 100
    """
    avg_cycle   = df["Total_Time"].mean()
    ideal_cycle = compute_ideal_cycle(df)
    if avg_cycle == 0:
        return 100.0
    return round((ideal_cycle / avg_cycle) * 100, 2)


def all_metrics(df: pd.DataFrame) -> dict:
    """
    Compute and return all KPIs in a single dictionary.

    Returns
    -------
    dict with keys:
        avg_total_time, ideal_cycle_time, throughput_per_hour,
        idle_time_min, efficiency_pct, avg_stage_times
    """
    avg_stage_times = df[STAGE_COLS].mean().round(2).to_dict()

    return {
        "avg_total_time":      round(df["Total_Time"].mean(), 2),
        "median_total_time":   round(df["Total_Time"].median(), 2),
        "max_total_time":      round(df["Total_Time"].max(), 2),
        "ideal_cycle_time":    compute_ideal_cycle(df),
        "throughput_per_hour": compute_throughput(df),
        "idle_time_min":       compute_idle_time(df),
        "efficiency_pct":      compute_efficiency(df),
        "avg_stage_times":     avg_stage_times,
    }
