
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"

INVENTORY_FILE = DATA_DIR / "automobile_spare_parts.csv"
SALES_FILE = DATA_DIR / "daily_sales_history.csv"
OUTPUT_FILE = DATA_DIR / "abc_xyz_results.csv"


# --------------------------------------------------
# 2. LOAD AND VALIDATE DATA
# --------------------------------------------------

print("=" * 65)
print("AUTOSTOCK AI - ABC-XYZ INVENTORY ANALYSIS")
print("=" * 65)

if not INVENTORY_FILE.exists():
    raise FileNotFoundError(f"Inventory file not found: {INVENTORY_FILE}")

if not SALES_FILE.exists():
    raise FileNotFoundError(f"Sales history file not found: {SALES_FILE}")

inventory = pd.read_csv(INVENTORY_FILE)
sales = pd.read_csv(SALES_FILE)

required_inventory = {
    "part_id",
    "part_name",
    "stock",
    "daily_demand",
    "unit_cost",
}

required_sales = {
    "part_id",
    "date",
    "units_sold",
}

missing_inventory = required_inventory - set(inventory.columns)
missing_sales = required_sales - set(sales.columns)

if missing_inventory:
    raise ValueError(
        f"Missing inventory columns: {sorted(missing_inventory)}"
    )

if missing_sales:
    raise ValueError(
        f"Missing sales columns: {sorted(missing_sales)}"
    )

if inventory["part_id"].duplicated().any():
    raise ValueError("Inventory contains duplicate part IDs.")

inventory["stock"] = pd.to_numeric(inventory["stock"], errors="raise")
inventory["daily_demand"] = pd.to_numeric(
    inventory["daily_demand"], errors="raise"
)
inventory["unit_cost"] = pd.to_numeric(
    inventory["unit_cost"], errors="raise"
)

sales["date"] = pd.to_datetime(sales["date"], errors="raise")
sales["units_sold"] = pd.to_numeric(
    sales["units_sold"], errors="raise"
)

if (inventory["stock"] < 0).any():
    raise ValueError("Stock cannot be negative.")

if (inventory["unit_cost"] < 0).any():
    raise ValueError("Unit cost cannot be negative.")

if (sales["units_sold"] < 0).any():
    raise ValueError("Sales cannot be negative.")

if not sales["part_id"].isin(inventory["part_id"]).all():
    raise ValueError("Sales history contains unknown part IDs.")

if sales.duplicated(["part_id", "date"]).any():
    raise ValueError("Duplicate sales records exist for a part and date.")


# --------------------------------------------------
# 3. ABC ANALYSIS
# --------------------------------------------------
# ABC classification uses annual consumption value:
# Average daily demand x 365 x unit cost.
#
# This is an estimate based on the inventory dataset,
# not a measured accounting value.

inventory["annual_demand_units"] = (
    inventory["daily_demand"] * 365
)

inventory["annual_consumption_value"] = (
    inventory["annual_demand_units"] * inventory["unit_cost"]
)

inventory = inventory.sort_values(
    "annual_consumption_value",
    ascending=False,
).copy()

total_value = inventory["annual_consumption_value"].sum()

if total_value <= 0:
    raise ValueError(
        "Total annual consumption value must be greater than zero."
    )

inventory["cumulative_value_share"] = (
    inventory["annual_consumption_value"].cumsum() / total_value
)

inventory["ABC_class"] = np.select(
    [
        inventory["cumulative_value_share"] <= 0.80,
        inventory["cumulative_value_share"] <= 0.95,
    ],
    ["A", "B"],
    default="C",
)

# --------------------------------------------------
# 4. XYZ ANALYSIS
# --------------------------------------------------
# X: relatively stable demand
# Y: moderate variability
# Z: high variability
#
# Calculate the coefficient of variation (CV):
# standard deviation / mean demand.
#
# These thresholds are configurable business rules.

daily_part_sales = (
    sales.groupby(["part_id", "date"], as_index=False)["units_sold"]
    .sum()
)

sales_start = sales["date"].min()
sales_end = sales["date"].max()

date_count = (sales_end - sales_start).days + 1

if date_count < 2:
    raise ValueError("At least two days of sales history are required.")

all_dates = pd.date_range(
    start=sales_start,
    end=sales_end,
    freq="D",
)

# Build a complete daily series for every part.
# Missing dates are treated as zero sales only within
# the observed overall sales-history date range.

part_ids = inventory["part_id"].tolist()

full_index = pd.MultiIndex.from_product(
    [part_ids, all_dates],
    names=["part_id", "date"],
)

complete_sales = (
    daily_part_sales.set_index(["part_id", "date"])["units_sold"]
    .reindex(full_index, fill_value=0)
    .rename("units_sold")
    .reset_index()
)

demand_stats = (
    complete_sales.groupby("part_id")["units_sold"]
    .agg(
        mean_daily_sales="mean",
        std_daily_sales="std",
        total_sales="sum",
        observed_days="count",
    )
    .reset_index()
)

demand_stats["demand_cv"] = (
    demand_stats["std_daily_sales"]
    / demand_stats["mean_daily_sales"].replace(0, np.nan)
)

# No observed sales or zero average demand is classified
# as Z because variability cannot be reliably estimated.
demand_stats["XYZ_class"] = np.select(
    [
        demand_stats["mean_daily_sales"].eq(0),
        demand_stats["demand_cv"].le(0.50),
        demand_stats["demand_cv"].le(1.00),
    ],
    ["Z", "X", "Y"],
    default="Z",
)

# --------------------------------------------------
# 5. COMBINE ABC AND XYZ RESULTS
# --------------------------------------------------

result = inventory.merge(
    demand_stats,
    on="part_id",
    how="left",
    validate="one_to_one",
)

result["ABC_XYZ_class"] = (
    result["ABC_class"] + result["XYZ_class"]
)

# Estimated days remaining based on current stock and
# historical average daily sales.
result["estimated_days_remaining"] = np.where(
    result["mean_daily_sales"] > 0,
    result["stock"] / result["mean_daily_sales"],
    np.inf,
)

# --------------------------------------------------
# 6. SAVE RESULTS
# --------------------------------------------------

result.to_csv(OUTPUT_FILE, index=False)

# --------------------------------------------------
# 7. PRINT REPORT
# --------------------------------------------------

print(f"\nInventory parts analysed: {len(result)}")
print(f"Sales history date range: {sales_start.date()} to {sales_end.date()}")
print(f"Days in analysis: {len(all_dates)}")
print(f"Total daily sales records loaded: {len(sales)}")

print("\nABC CLASS COUNTS")
print(result["ABC_class"].value_counts().sort_index())

print("\nXYZ CLASS COUNTS")
print(result["XYZ_class"].value_counts().sort_index())

print("\nCOMBINED ABC-XYZ GROUPS")
print(result["ABC_XYZ_class"].value_counts().sort_index())

print("\nTOP 10 PARTS BY ANNUAL CONSUMPTION VALUE")
print(
    result[
        [
            "part_id",
            "part_name",
            "annual_consumption_value",
            "ABC_class",
            "XYZ_class",
            "ABC_XYZ_class",
        ]
    ]
    .sort_values("annual_consumption_value", ascending=False)
    .head(10)
    .to_string(index=False)
)

print("\nDEMAND VARIABILITY SUMMARY")
print(
    result[
        ["mean_daily_sales", "demand_cv"]
    ].describe().round(3).to_string()
)

print(f"\nResults saved to: {OUTPUT_FILE}")
print("\nABC-XYZ analysis completed successfully.")
print("=" * 65)
