
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_DIR / "data" / "automobile_spare_parts.csv"

df = pd.read_csv(DATA_FILE)

required_columns = {"part_id", "part_name", "stock", "daily_demand"}

missing = required_columns - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

# ABC analysis: classify parts by estimated annual demand value.
# Since actual unit prices are not available yet, use daily demand
# as a temporary proxy. We will improve this when price data is added.
df["annual_demand_proxy"] = df["daily_demand"] * 365

df = df.sort_values("annual_demand_proxy", ascending=False).copy()

total = df["annual_demand_proxy"].sum()
if total <= 0:
    raise ValueError("Total demand must be greater than zero.")

df["cumulative_share"] = (
    df["annual_demand_proxy"].cumsum() / total
)

df["ABC_class"] = np.select(
    [
        df["cumulative_share"] <= 0.80,
        df["cumulative_share"] <= 0.95,
    ],
    ["A", "B"],
    default="C",
)

# XYZ analysis: a provisional classification.
# This uses the current daily-demand column, not historical variability.
df["XYZ_class"] = np.select(
    [
        df["daily_demand"] <= df["daily_demand"].quantile(1 / 3),
        df["daily_demand"] <= df["daily_demand"].quantile(2 / 3),
    ],
    ["X", "Y"],
    default="Z",
)

df["ABC_XYZ_class"] = df["ABC_class"] + df["XYZ_class"]

output_file = PROJECT_DIR / "data" / "abc_xyz_results.csv"
df.to_csv(output_file, index=False)

print("=" * 60)
print("AUTOSTOCK AI - ABC-XYZ ANALYSIS")
print("=" * 60)

print("\nABC class counts:")
print(df["ABC_class"].value_counts().sort_index())

print("\nXYZ class counts:")
print(df["XYZ_class"].value_counts().sort_index())

print("\nCombined ABC-XYZ groups:")
print(df["ABC_XYZ_class"].value_counts().sort_index())

print("\nTop 10 parts:")
print(
    df[
        ["part_id", "part_name", "daily_demand", "ABC_class",
         "XYZ_class", "ABC_XYZ_class"]
    ].head(10).to_string(index=False)
)

print(f"\nResults saved to: {output_file}")
print("\nABC-XYZ analysis completed.")
