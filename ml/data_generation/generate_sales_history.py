
import random
from pathlib import Path

import numpy as np
import pandas as pd

# Reproducible results
random.seed(42)
np.random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

INVENTORY_FILE = DATA_DIR / "automobile_spare_parts.csv"
OUTPUT_FILE = DATA_DIR / "daily_sales_history.csv"

# Check that the inventory dataset exists
if not INVENTORY_FILE.exists():
    raise FileNotFoundError(
        f"Inventory file not found: {INVENTORY_FILE}. "
        "Run generate_data.py first."
    )

inventory = pd.read_csv(INVENTORY_FILE)

# Generate two years of daily history
dates = pd.date_range(
    end=pd.Timestamp.today().normalize(),
    periods=730,
    freq="D"
)

records = []

for _, part in inventory.iterrows():
    base_demand = float(part["daily_demand"])
    part_id = part["part_id"]
    part_name = part["part_name"]
    warehouse = part["warehouse"]

    # Each part has slightly different demand behaviour
    part_factor = np.random.uniform(0.8, 1.2)

    for date in dates:
        # Weekly pattern: demand is lower on Sundays
        weekday_factor = 0.55 if date.dayofweek == 6 else 1.0

        # Gentle yearly seasonality
        seasonal_factor = (
            1 + 0.20 * np.sin(2 * np.pi * date.dayofyear / 365.25)
        )

        # Random daily variation
        random_factor = np.random.normal(1.0, 0.18)
        random_factor = max(0.2, random_factor)

        # Occasional demand spike
        spike_factor = (
            random.uniform(1.5, 2.5)
            if random.random() < 0.025
            else 1.0
        )

        expected_demand = (
            base_demand
            * part_factor
            * weekday_factor
            * seasonal_factor
            * random_factor
            * spike_factor
        )

        units_sold = max(0, int(round(expected_demand)))

        records.append({
            "date": date,
            "part_id": part_id,
            "part_name": part_name,
            "warehouse": warehouse,
            "units_sold": units_sold
        })

sales = pd.DataFrame(records)

# Save the daily sales history
sales.to_csv(OUTPUT_FILE, index=False)

print("=" * 60)
print("AUTOSTOCK AI - DAILY SALES HISTORY")
print("=" * 60)
print(f"Inventory parts : {inventory['part_id'].nunique()}")
print(f"Warehouses      : {sales['warehouse'].nunique()}")
print(f"Start date      : {sales['date'].min().date()}")
print(f"End date        : {sales['date'].max().date()}")
print(f"Total records   : {len(sales):,}")
print(f"Output file     : {OUTPUT_FILE}")
print("\nSample records:")
print(sales.head(10).to_string(index=False))
