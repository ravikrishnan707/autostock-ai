
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

inventory_file = DATA_DIR / "automobile_spare_parts.csv"
sales_file = DATA_DIR / "daily_sales_history.csv"

# Check that both datasets exist
for file_path in [inventory_file, sales_file]:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing file: {file_path}\n"
            "Run the data-generation scripts first."
        )

inventory = pd.read_csv(inventory_file)
sales = pd.read_csv(sales_file)

print("=" * 60)
print("AUTOSTOCK AI - DATA VALIDATION REPORT")
print("=" * 60)

# 1. Check row counts
print("\n1. ROW COUNTS")
print(f"Inventory records: {len(inventory):,}")
print(f"Sales records:     {len(sales):,}")

# 2. Check missing values
print("\n2. MISSING VALUES")
print("Inventory missing values:")
print(inventory.isnull().sum().to_string())

print("\nSales missing values:")
print(sales.isnull().sum().to_string())

# 3. Check duplicate records
print("\n3. DUPLICATES")
print(f"Duplicate inventory part IDs: {inventory['part_id'].duplicated().sum()}")
print(
    "Duplicate part/date/warehouse records: "
    f"{sales.duplicated(['part_id', 'date', 'warehouse']).sum()}"
)

# 4. Check invalid numeric values
print("\n4. VALUE CHECKS")
print(f"Negative stock: {(inventory['stock'] < 0).sum()}")
print(f"Non-positive daily demand: {(inventory['daily_demand'] <= 0).sum()}")
print(f"Negative units sold: {(sales['units_sold'] < 0).sum()}")

# 5. Check daily history coverage
print("\n5. HISTORY COVERAGE")
days_per_part = sales.groupby("part_id")["date"].nunique()

print(f"Unique inventory parts: {inventory['part_id'].nunique()}")
print(f"Parts with sales history: {sales['part_id'].nunique()}")
print(f"Minimum days per part: {days_per_part.min()}")
print(f"Maximum days per part: {days_per_part.max()}")

# 6. Check whether sales parts exist in inventory
unknown_parts = set(sales["part_id"]) - set(inventory["part_id"])
print(f"Sales records with unknown part IDs: {len(unknown_parts)}")

# 7. Overall validation result
checks_passed = (
    inventory["part_id"].is_unique
    and not inventory.isnull().any().any()
    and not sales.isnull().any().any()
    and not sales.duplicated(["part_id", "date", "warehouse"]).any()
    and (inventory["stock"] >= 0).all()
    and (inventory["daily_demand"] > 0).all()
    and (sales["units_sold"] >= 0).all()
    and len(unknown_parts) == 0
    and len(days_per_part) == inventory["part_id"].nunique()
    and days_per_part.eq(730).all()
)

print("\n" + "=" * 60)
print("RESULT:", "ALL CHECKS PASSED" if checks_passed else "CHECKS NEED ATTENTION")
print("=" * 60)

if not checks_passed:
    raise SystemExit("Fix the validation issues before continuing.")
