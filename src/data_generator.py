"""
data_generator.py
-----------------
Generates synthetic manufacturing process data with realistic
stage times, delays, and variability for analysis.
"""

import numpy as np
import pandas as pd
import os

# ------------------------------------------------------------------
# Configuration – tweak these to change data characteristics
# ------------------------------------------------------------------
RANDOM_SEED    = 42          # reproducibility
N_ROWS         = 1000        # number of process runs to simulate
DELAY_THRESHOLD = 62         # minutes; runs above this are "delayed"

# Baseline mean & std for each stage (in minutes)
STAGE_CONFIG = {
    "Stage_1_Time": {"mean": 15, "std": 4},   # fastest stage
    "Stage_2_Time": {"mean": 25, "std": 8},   # bottleneck (highest mean)
    "Stage_3_Time": {"mean": 18, "std": 5},
}


def generate_process_data(n_rows: int = N_ROWS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """
    Create a DataFrame with simulated process stage times.

    Returns
    -------
    pd.DataFrame
        Columns: Process_ID, Stage_1_Time, Stage_2_Time,
                 Stage_3_Time, Total_Time, Delay_Flag
    """
    rng = np.random.default_rng(seed)

    data = {}

    # Process IDs
    data["Process_ID"] = [f"P{str(i).zfill(4)}" for i in range(1, n_rows + 1)]

    # Generate stage times – normally distributed, clipped to realistic bounds
    for stage, cfg in STAGE_CONFIG.items():
        times = rng.normal(loc=cfg["mean"], scale=cfg["std"], size=n_rows)
        times = np.clip(times, 1, cfg["mean"] * 3)   # no negatives, no extreme outliers
        data[stage] = np.round(times, 2)

    df = pd.DataFrame(data)

    # Total cycle time
    stage_cols = ["Stage_1_Time", "Stage_2_Time", "Stage_3_Time"]
    df["Total_Time"] = df[stage_cols].sum(axis=1).round(2)

    # Delay flag – 1 if total time exceeds threshold
    df["Delay_Flag"] = (df["Total_Time"] > DELAY_THRESHOLD).astype(int)

    return df


def save_data(df: pd.DataFrame, path: str = "data/process_data.csv") -> None:
    """Save the DataFrame to a CSV file, creating directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[data_generator] Saved {len(df):,} rows → {path}")


if __name__ == "__main__":
    df = generate_process_data()
    save_data(df, "data/process_data.csv")
    print(df.head())
