
from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/analysis/kaggle_inventory_clean.csv")
OUTPUT_DIR = Path("data/analysis")

df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])

print("=" * 55)
print("AUTOSTOCK AI - KAGGLE DEMAND ANALYSIS")
print("=" * 55)

print("\n1. Overall demand statistics")
print(df["Units_Sold"].describe().round(2))

print("\n2. Daily demand by product")
product_demand = (
    df.groupby("SKU_ID")["Units_Sold"]
    .agg(["mean", "std", "min", "max", "sum"])
    .round(2)
)
print(product_demand.head(10))

print("\n3. Monthly demand")
df["Year_Month"] = df["Date"].dt.to_period("M").astype(str)
monthly_demand = (
    df.groupby("Year_Month")["Units_Sold"]
    .sum()
    .reset_index(name="Total_Units_Sold")
)
print(monthly_demand.to_string(index=False))

print("\n4. Inventory status by warehouse")
warehouse_summary = (
    df.groupby(["Warehouse_ID", "Inventory_Status"])
    .size()
    .unstack(fill_value=0)
)
print(warehouse_summary)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
product_demand.to_csv(OUTPUT_DIR / "kaggle_product_demand_summary.csv")
monthly_demand.to_csv(OUTPUT_DIR / "kaggle_monthly_demand_summary.csv")
warehouse_summary.to_csv(OUTPUT_DIR / "kaggle_warehouse_inventory_summary.csv")

print("\nSaved three analysis reports in:", OUTPUT_DIR)
print("DEMAND ANALYSIS COMPLETED")
