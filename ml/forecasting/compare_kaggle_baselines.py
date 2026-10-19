
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

INPUT_FILE = Path("data/analysis/kaggle_features_dataset.csv")
OUTPUT_FILE = Path("data/analysis/kaggle_baseline_comparison.csv")

df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])
df = df.sort_values(["SKU_ID", "Warehouse_ID", "Date"]).copy()

# Check required columns
required_columns = [
    "Date",
    "SKU_ID",
    "Warehouse_ID",
    "Units_Sold",
    "Previous_Day_Sales",
    "Demand_Mean_7_Days",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# Split by calendar date: first 80% for training,
# final 20% for testing.
unique_dates = sorted(df["Date"].dropna().unique())
split_index = int(len(unique_dates) * 0.8)

if split_index >= len(unique_dates):
    raise ValueError("Not enough dates for a train/test split.")

split_date = pd.Timestamp(unique_dates[split_index])

test = df[df["Date"] >= split_date].copy()

# Use exactly the same eligible rows for both methods.
test = test.dropna(
    subset=[
        "Units_Sold",
        "Previous_Day_Sales",
        "Demand_Mean_7_Days",
    ]
)

if test.empty:
    raise ValueError("No eligible test rows remain after removing missing values.")

actual = test["Units_Sold"]
pred_previous = test["Previous_Day_Sales"]
pred_7day = test["Demand_Mean_7_Days"]

results = []

for name, prediction in [
    ("Previous day sales", pred_previous),
    ("Previous 7-day average", pred_7day),
]:
    results.append({
        "Method": name,
        "Test_Rows": len(test),
        "MAE": mean_absolute_error(actual, prediction),
        "RMSE": mean_squared_error(actual, prediction) ** 0.5,
    })

results_df = pd.DataFrame(results).round(3)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(OUTPUT_FILE, index=False)

print("=" * 55)
print("KAGGLE BASELINE COMPARISON")
print("=" * 55)
print("Test starts:", split_date.date())
print("Test ends:", test["Date"].max().date())
print("Eligible test rows:", len(test))
print("\nResults:")
print(results_df.to_string(index=False))
print("\nSaved to:", OUTPUT_FILE)
print("\nEVALUATION COMPLETED")

