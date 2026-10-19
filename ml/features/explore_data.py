
from pathlib import Path

import pandas as pd

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"

inventory_file = DATA_DIR / "automobile_spare_parts.csv"
sales_file = DATA_DIR / "daily_sales_history.csv"


# --------------------------------------------------
# 2. CHECK FILES AND LOAD DATA
# --------------------------------------------------

print("=" * 60)
print("AUTOSTOCK AI - DATA EXPLORATION REPORT")
print("=" * 60)

if not inventory_file.exists():
    raise FileNotFoundError(
        f"Inventory file not found: {inventory_file}"
    )

if not sales_file.exists():
    raise FileNotFoundError(
        f"Sales history file not found: {sales_file}"
    )

inventory = pd.read_csv(inventory_file)
sales = pd.read_csv(sales_file)

print("\nDATASETS LOADED SUCCESSFULLY")

# --------------------------------------------------
# 3. DATASET SIZES
# --------------------------------------------------

print("\n1. DATASET SIZES")
print("-" * 40)

print(f"Inventory records: {len(inventory)}")
print(f"Daily sales records: {len(sales)}")

print(f"Inventory columns: {len(inventory.columns)}")
print(f"Sales columns: {len(sales.columns)}")


# --------------------------------------------------
# 4. COLUMN NAMES AND MISSING VALUES
# --------------------------------------------------

print("\n2. INVENTORY COLUMNS")
print("-" * 40)

print(inventory.columns.tolist())

print("\nMissing inventory values:")
print(inventory.isnull().sum())

print("\nMissing sales values:")
print(sales.isnull().sum())


# --------------------------------------------------
# 5. STOCKOUT RISK DISTRIBUTION
# --------------------------------------------------

print("\n3. STOCKOUT RISK DISTRIBUTION")
print("-" * 40)

if "stockout_risk" in inventory.columns:
    print(inventory["stockout_risk"].value_counts(dropna=False))
else:
    print("The stockout_risk column is not available.")


# --------------------------------------------------
# 6. HIGHEST-DEMAND PARTS
# --------------------------------------------------

print("\n4. TOP 10 PARTS BY DAILY DEMAND")
print("-" * 40)

required_columns = {"part_name", "daily_demand", "stock"}

if required_columns.issubset(inventory.columns):
    print(
        inventory.nlargest(10, "daily_demand")[
            ["part_name", "daily_demand", "stock"]
        ].to_string(index=False)
    )
else:
    print("Required columns are missing.")


# --------------------------------------------------
# 7. WAREHOUSE SUMMARY
# --------------------------------------------------

print("\n5. WAREHOUSE SUMMARY")
print("-" * 40)

warehouse_columns = {
    "warehouse",
    "part_id",
    "stock",
    "daily_demand",
}

if warehouse_columns.issubset(inventory.columns):
    warehouse_summary = (
        inventory.groupby("warehouse")
        .agg(
            part_count=("part_id", "nunique"),
            total_stock=("stock", "sum"),
            average_demand=("daily_demand", "mean"),
        )
        .round(2)
    )

    print(warehouse_summary.to_string())
else:
    print("Required warehouse columns are missing.")


# --------------------------------------------------
# 8. SALES HISTORY SUMMARY
# --------------------------------------------------

print("\n6. DAILY SALES SUMMARY")
print("-" * 40)

if {"date", "units_sold"}.issubset(sales.columns):
    sales["date"] = pd.to_datetime(
        sales["date"], errors="coerce"
    )

    print(f"Date range: {sales['date'].min()} to {sales['date'].max()}")
    print(f"Total units sold: {sales['units_sold'].sum()}")
    print(
        "Average units per sales record: "
        f"{sales['units_sold'].mean():.2f}"
    )
else:
    print("Required sales columns are missing.")


# --------------------------------------------------
# 9. DATA-QUALITY CHECKS
# --------------------------------------------------

print("\n7. DATA QUALITY CHECKS")
print("-" * 40)

# Check duplicate inventory rows
print(
    "Duplicate inventory rows:",
    inventory.duplicated().sum()
)

# Check duplicate part IDs in inventory
if "part_id" in inventory.columns:
    print(
        "Duplicate inventory part IDs:",
        inventory["part_id"].duplicated().sum()
    )

# Check duplicate sales records for the same part and date
if {"date", "part_id"}.issubset(sales.columns):
    print(
        "Duplicate sales records (same date and part):",
        sales.duplicated(subset=["date", "part_id"]).sum()
    )

# Check negative stock
if "stock" in inventory.columns:
    print(
        "Negative stock values:",
        (inventory["stock"] < 0).sum()
    )

# Check non-positive demand
if "daily_demand" in inventory.columns:
    print(
        "Non-positive daily demand:",
        (inventory["daily_demand"] <= 0).sum()
    )

# Check negative unit cost
if "unit_cost" in inventory.columns:
    print(
        "Negative unit cost values:",
        (inventory["unit_cost"] < 0).sum()
    )

# Check negative sales
if "units_sold" in sales.columns:
    print(
        "Negative sales values:",
        (sales["units_sold"] < 0).sum()
    )

# Check sales records with unknown part IDs
if {"part_id"}.issubset(inventory.columns) and "part_id" in sales.columns:
    unknown_parts = ~sales["part_id"].isin(inventory["part_id"])

    print(
        "Sales records with unknown part IDs:",
        unknown_parts.sum()
    )

# Check invalid dates
if "date" in sales.columns:
    print(
        "Invalid sales dates:",
        sales["date"].isna().sum()
    )


# --------------------------------------------------
# 10. FINAL REPORT
# --------------------------------------------------

print("\n" + "=" * 60)
print("DATA EXPLORATION COMPLETED")
print("=" * 60)
