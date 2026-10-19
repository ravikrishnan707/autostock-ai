
from pathlib import Path

import numpy as np
import pandas as pd

# Project paths
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"
SALES_FILE = DATA_DIR / "daily_sales_history.csv"

OUTPUT_FILE = DATA_DIR / "features_dataset.csv"

print("=" * 60)
print("AUTOSTOCK AI - FEATURE ENGINEERING")
print("=" * 60)

# 1. Load sales history
sales = pd.read_csv(SALES_FILE)
sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
sales["units_sold"] = pd.to_numeric(
    sales["units_sold"], errors="coerce"
)

# 2. Validate required columns
required = {"date", "part_id", "units_sold"}
missing = required - set(sales.columns)

if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")

if sales["date"].isna().any():
    raise ValueError("Sales data contains invalid dates.")

if sales["part_id"].isna().any():
    raise ValueError("Sales data contains missing part IDs.")

if sales["units_sold"].isna().any():
    raise ValueError("Sales data contains invalid sales values.")

if (sales["units_sold"] < 0).any():
    raise ValueError("Sales data contains negative sales.")

# 3. Sort sales chronologically
sales = sales.sort_values(["part_id", "date"]).copy()

# 4. Create demand features for each part
grouped = sales.groupby("part_id")["units_sold"]

sales["previous_day_sales"] = grouped.shift(1)
sales["sales_7_days_ago"] = grouped.shift(7)
sales["sales_30_days_ago"] = grouped.shift(30)

sales["rolling_mean_7"] = grouped.transform(
    lambda values: values.shift(1).rolling(7, min_periods=7).mean()
)

sales["rolling_mean_30"] = grouped.transform(
    lambda values: values.shift(1).rolling(30, min_periods=30).mean()
)

sales["rolling_std_7"] = grouped.transform(
    lambda values: values.shift(1).rolling(7, min_periods=7).std()
)

# 5. Calendar features
sales["day_of_week"] = sales["date"].dt.dayofweek
sales["month"] = sales["date"].dt.month
sales["day_of_month"] = sales["date"].dt.day
sales["is_weekend"] = (
    sales["day_of_week"] >= 5
).astype(int)

# 6. Save the feature dataset
sales.to_csv(OUTPUT_FILE, index=False)

# 7. Print validation summary
feature_columns = [
    "previous_day_sales",
    "sales_7_days_ago",
    "sales_30_days_ago",
    "rolling_mean_7",
    "rolling_mean_30",
    "rolling_std_7",
]

print(f"\nInput records: {len(sales)}")
print(f"Unique parts: {sales['part_id'].nunique()}")
print(f"Feature columns created: {len(feature_columns) + 4}")

print("\nMissing values in generated features:")
print(sales[feature_columns].isna().sum())

print(f"\nSaved feature dataset to: {OUTPUT_FILE}")
print("\nFEATURE ENGINEERING COMPLETED")
print("=" * 60)
