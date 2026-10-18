
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

PROJECT_DIR = Path(__file__).resolve().parents[2]
SALES_FILE = PROJECT_DIR / "data" / "daily_sales_history.csv"

df = pd.read_csv(SALES_FILE)

required_columns = {"part_id", "date", "units_sold"}
missing = required_columns - set(df.columns)

if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
df = df.dropna(subset=["part_id", "date", "units_sold"])

if (df["units_sold"] < 0).any():
    raise ValueError("Sales data contains negative units_sold values.")

df["units_sold"] = df["units_sold"].astype(float)
df = df.sort_values(["part_id", "date"])

# Aggregate records in case there are multiple rows per part per day.
daily = (
    df.groupby(["part_id", "date"], as_index=False)["units_sold"]
    .sum()
)

# Evaluate the latest 30 days for each part.
# Forecasts use only observations before the evaluation period.
results = []

for part_id, group in daily.groupby("part_id"):
    group = group.sort_values("date").set_index("date")

    # Reindex to daily frequency. Missing dates are treated as zero sales.
    # This is appropriate only if missing dates mean no sales.
    series = group["units_sold"].asfreq("D", fill_value=0)

    if len(series) < 60:
        continue

    test_size = min(30, max(1, len(series) // 5))
    train = series.iloc[:-test_size]
    actual = series.iloc[-test_size:]

    # Baseline 1: forecast the training-period average.
    average_forecast = np.full(len(actual), train.mean())

    # Baseline 2: repeat the average sales for the most recent 7 days.
    recent_forecast = np.full(
        len(actual),
        train.tail(7).mean()
    )

    for method, predictions in [
        ("historical_average", average_forecast),
        ("last_7_day_average", recent_forecast),
    ]:
        mae = mean_absolute_error(actual, predictions)
        rmse = np.sqrt(mean_squared_error(actual, predictions))

        results.append({
            "part_id": part_id,
            "method": method,
            "training_days": len(train),
            "test_days": len(actual),
            "MAE": round(float(mae), 3),
            "RMSE": round(float(rmse), 3),
        })

if not results:
    raise ValueError(
        "No parts had enough daily history. Check the dates and dataset."
    )

results_df = pd.DataFrame(results)

output_file = PROJECT_DIR / "data" / "forecast_baseline_results.csv"
results_df.to_csv(output_file, index=False)

print("=" * 60)
print("AUTOSTOCK AI - DEMAND FORECAST BASELINES")
print("=" * 60)

print("\nAverage error by forecasting method:")
print(
    results_df.groupby("method")[["MAE", "RMSE"]]
    .mean()
    .round(3)
    .to_string()
)

print("\nSample results:")
print(results_df.head(10).to_string(index=False))

print(f"\nResults saved to: {output_file}")
print("\nBaseline forecasting evaluation completed.")
