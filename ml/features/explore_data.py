
from pathlib import Path

import pandas as pd

# Find the main project folder automatically
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"

inventory_file = DATA_DIR / "automobile_spare_parts.csv"
sales_file = DATA_DIR / "daily_sales_history.csv"

# Load both datasets
inventory = pd.read_csv(inventory_file)
sales = pd.read_csv(sales_file)

print("=" * 60)
print("AUTOSTOCK AI - DATA EXPLORATION REPORT")
print("=" * 60)

# 1. Dataset sizes
print("\n1. DATASET SIZES")
print(f"Inventory records: {len(inventory)}")
print(f"Daily sales records: {len(sales)}")

# 2. Column names and missing values
print("\n2. INVENTORY COLUMNS")
print(inventory.columns.tolist())

print("\nMissing inventory values:")
print(inventory.isnull().sum())

print("\nMissing sales values:")
print(sales.isnull().sum())

# 3. Stockout risk distribution
if "stockout_risk" in inventory.columns:
    print("\n3. STOCKOUT RISK DISTRIBUTION")
    print(inventory["stockout_risk"].value_counts())

# 4. Highest-demand parts
if {"part_name", "daily_demand"}.issubset(inventory.columns):
    print("\n4. TOP 10 PARTS BY DAILY DEMAND")
    print(
        inventory.nlargest(10, "daily_demand")[
            ["part_name", "daily_demand", "stock"]
        ].to_string(index=False)
    )

# 5. Warehouse summary
if "warehouse" in inventory.columns:
    print("\n5. WAREHOUSE SUMMARY")
    print(
        inventory.groupby("warehouse")
        .agg(
            part_count=("part_id", "nunique"),
            total_stock=("stock", "sum"),
            average_demand=("daily_demand", "mean"),
        )
        .round(2)
        .to_string()
    )

# 6. Sales history summary
if {"date", "units_sold"}.issubset(sales.columns):
    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")

    print("\n6. DAILY SALES SUMMARY")
    print(f"Date range: {sales['date'].min()} to {sales['date'].max()}")
    print(f"Total units sold: {sales['units_sold'].sum()}")
    print(f"Average units per sales record: {sales['units_sold'].mean():.2f}")

print("\n" + "=" * 60)
print("DATA EXPLORATION COMPLETED")
print("=" * 60)
