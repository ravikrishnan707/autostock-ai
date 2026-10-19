
from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/supply_chain_dataset1.csv")
OUTPUT_FILE = Path("data/analysis/kaggle_inventory_clean.csv")

df = pd.read_csv(INPUT_FILE)

# Convert dates and sort records
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])
df = df.sort_values(["SKU_ID", "Warehouse_ID", "Date"])

# Remove exact duplicate rows, if any
df = df.drop_duplicates()

# Create calendar features
df["Day_Of_Week"] = df["Date"].dt.dayofweek
df["Month"] = df["Date"].dt.month

# Create a descriptive inventory status
df["Inventory_Status"] = "Normal"
df.loc[
    df["Inventory_Level"] <= df["Reorder_Point"],
    "Inventory_Status"
] = "Reorder Needed"

# Save processed copy
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print("KAGGLE DATA PREPARATION COMPLETED")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Saved to:", OUTPUT_FILE)
print("\nInventory status counts:")
print(df["Inventory_Status"].value_counts())
print("\nOriginal stockout labels:")
print(df["Stockout_Flag"].value_counts(dropna=False))
