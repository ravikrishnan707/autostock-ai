
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

INPUT_FILE = Path("data/analysis/kaggle_features_dataset.csv")

df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])
df = df.sort_values(["SKU_ID", "Warehouse_ID", "Date"]).copy()

# Keep rows where the previous day's sales are available
df = df.dropna(subset=["Previous_Day_Sales"])

# Use the first 80% of dates for training and the final 20% for testing
unique_dates = sorted(df["Date"].unique())
split_index = int(len(unique_dates) * 0.8)
split_date = unique_dates[split_index]

train = df[df["Date"] < split_date]
test = df[df["Date"] >= split_date].copy()

# Baseline prediction: tomorrow's demand equals yesterday's sales
test["Predicted_Sales"] = test["Previous_Day_Sales"]

mae = mean_absolute_error(test["Units_Sold"], test["Predicted_Sales"])
rmse = mean_squared_error(
    test["Units_Sold"], test["Predicted_Sales"]
) ** 0.5

print("=" * 50)
print("KAGGLE DEMAND FORECAST BASELINE")
print("=" * 50)
print("Training rows:", len(train))
print("Testing rows:", len(test))
print("Test starts:", split_date)
print("MAE:", round(mae, 3))
print("RMSE:", round(rmse, 3))

output_file = Path("data/analysis/kaggle_forecast_baseline_results.csv")
test.to_csv(output_file, index=False)

print("\nSaved test predictions to:", output_file)
print("BASELINE EVALUATION COMPLETED")
