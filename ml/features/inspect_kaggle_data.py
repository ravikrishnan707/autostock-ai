
from pathlib import Path

import pandas as pd

DATA_FILE = Path("data/supply_chain_dataset1.csv")

df = pd.read_csv(DATA_FILE)

print("=" * 50)
print("AUTOSTOCK AI - KAGGLE DATA QUALITY CHECK")
print("=" * 50)

print("\n1. Dataset shape:")
print(df.shape)

print("\n2. Missing values per column:")
print(df.isnull().sum())

print("\n3. Duplicate rows:")
print(df.duplicated().sum())

print("\n4. Unique products:")
print(df["SKU_ID"].nunique())

print("\n5. Unique warehouses:")
print(df["Warehouse_ID"].nunique())

print("\n6. Stockout flag distribution:")
print(df["Stockout_Flag"].value_counts(dropna=False))

print("\n7. Numeric column summary:")
print(df.describe().round(2).to_string())

print("\n8. Date range:")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
print("Start:", df["Date"].min())
print("End:", df["Date"].max())
print("Invalid dates:", df["Date"].isna().sum())

print("\n9. Negative values in numeric columns:")
numeric_df = df.select_dtypes(include="number")
print((numeric_df < 0).sum())

print("\nDATA QUALITY CHECK COMPLETED")
