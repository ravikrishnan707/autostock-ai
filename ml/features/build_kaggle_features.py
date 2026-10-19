
from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/analysis/kaggle_inventory_clean.csv")
OUTPUT_FILE = Path("data/analysis/kaggle_features_dataset.csv")

df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])
df = df.sort_values(["SKU_ID", "Warehouse_ID", "Date"]).copy()

group_columns = ["SKU_ID", "Warehouse_ID"]
grouped_sales = df.groupby(group_columns)["Units_Sold"]

# Previous day's sales: avoids using today's sales as an input
df["Previous_Day_Sales"] = grouped_sales.shift(1)

# Rolling statistics use only earlier days
df["Demand_Mean_7_Days"] = (
    df.groupby(group_columns)["Units_Sold"]
    .transform(lambda s: s.shift(1).rolling(7, min_periods=7).mean())
)

df["Demand_Mean_30_Days"] = (
    df.groupby(group_columns)["Units_Sold"]
    .transform(lambda s: s.shift(1).rolling(30, min_periods=30).mean())
)

df["Demand_Std_7_Days"] = (
    df.groupby(group_columns)["Units_Sold"]
    .transform(lambda s: s.shift(1).rolling(7, min_periods=7).std())
)

# Calendar features
df["Day_Of_Week"] = df["Date"].dt.dayofweek
df["Month"] = df["Date"].dt.month

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print("KAGGLE FEATURE ENGINEERING COMPLETED")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Saved to:", OUTPUT_FILE)
print("\nMissing values in new features:")
print(
    df[
        [
            "Previous_Day_Sales",
            "Demand_Mean_7_Days",
            "Demand_Mean_30_Days",
            "Demand_Std_7_Days",
        ]
    ].isna().sum()
)
