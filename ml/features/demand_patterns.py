
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"

SALES_FILE = DATA_DIR / "daily_sales_history.csv"
OUTPUT_DIR = DATA_DIR / "analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD SALES DATA
# --------------------------------------------------

print("=" * 65)
print("AUTOSTOCK AI - DEMAND PATTERN ANALYSIS")
print("=" * 65)

if not SALES_FILE.exists():
    raise FileNotFoundError(f"Sales file not found: {SALES_FILE}")

sales = pd.read_csv(SALES_FILE)

required_columns = {"date", "part_id", "units_sold"}
missing = required_columns - set(sales.columns)

if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

sales["date"] = pd.to_datetime(sales["date"], errors="raise")
sales["units_sold"] = pd.to_numeric(
    sales["units_sold"], errors="raise"
)

if (sales["units_sold"] < 0).any():
    raise ValueError("Sales data contains negative units_sold values.")

# Combine duplicate part/date records safely, if any exist.
sales = (
    sales.groupby(["date", "part_id"], as_index=False)["units_sold"]
    .sum()
)

sales["month"] = sales["date"].dt.to_period("M").astype(str)
sales["day_of_week"] = sales["date"].dt.day_name()

# --------------------------------------------------
# 3. OVERALL SUMMARY
# --------------------------------------------------

print("\n1. OVERALL SALES SUMMARY")
print("-" * 45)

print(f"Number of parts: {sales['part_id'].nunique()}")
print(f"Date range: {sales['date'].min().date()} to {sales['date'].max().date()}")
print(f"Sales records: {len(sales)}")
print(f"Total units sold: {sales['units_sold'].sum():,.0f}")

daily_total = sales.groupby("date")["units_sold"].sum()

print(f"Average total units sold per day: {daily_total.mean():.2f}")
print(f"Highest total sales in one day: {daily_total.max():.0f}")
print(f"Lowest total sales in one day: {daily_total.min():.0f}")

# --------------------------------------------------
# 4. MONTHLY DEMAND TREND
# --------------------------------------------------

print("\n2. MONTHLY DEMAND SUMMARY")
print("-" * 45)

monthly_sales = (
    sales.groupby("month")["units_sold"]
    .sum()
    .sort_index()
)

print(monthly_sales.to_string())

plt.figure(figsize=(12, 5))
monthly_sales.plot(marker="o")
plt.title("Monthly Automobile Spare Parts Demand")
plt.xlabel("Month")
plt.ylabel("Units Sold")
plt.xticks(rotation=45)
plt.tight_layout()

monthly_chart = OUTPUT_DIR / "monthly_demand.png"
plt.savefig(monthly_chart, dpi=150)
plt.close()

# --------------------------------------------------
# 5. WEEKLY DEMAND PATTERN
# --------------------------------------------------

print("\n3. DAY-OF-WEEK DEMAND")
print("-" * 45)

weekday_order = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

weekday_sales = (
    sales.groupby("day_of_week")["units_sold"]
    .mean()
    .reindex(weekday_order)
)

print(weekday_sales.round(2).to_string())

plt.figure(figsize=(10, 5))
weekday_sales.plot(kind="bar")
plt.title("Average Sales by Day of Week")
plt.xlabel("Day")
plt.ylabel("Average Units Sold per Part Record")
plt.xticks(rotation=30)
plt.tight_layout()

weekday_chart = OUTPUT_DIR / "weekday_demand.png"
plt.savefig(weekday_chart, dpi=150)
plt.close()

# --------------------------------------------------
# 6. TOP 10 PARTS BY TOTAL SALES
# --------------------------------------------------

print("\n4. TOP 10 PARTS BY TOTAL SALES")
print("-" * 45)

part_totals = (
    sales.groupby("part_id")["units_sold"]
    .sum()
    .sort_values(ascending=False)
)

print(part_totals.head(10).to_string())

top_parts = part_totals.head(10).index

top_part_daily = (
    sales[sales["part_id"].isin(top_parts)]
    .pivot(index="date", columns="part_id", values="units_sold")
    .fillna(0)
    .sort_index()
)

plt.figure(figsize=(12, 6))
top_part_daily.plot(ax=plt.gca(), linewidth=1)
plt.title("Daily Demand for Top 10 Parts")
plt.xlabel("Date")
plt.ylabel("Units Sold")
plt.tight_layout()

top_parts_chart = OUTPUT_DIR / "top_parts_daily_demand.png"
plt.savefig(top_parts_chart, dpi=150)
plt.close()

# --------------------------------------------------
# 7. DEMAND SPIKES
# --------------------------------------------------

print("\n5. UNUSUAL DEMAND SPIKES")
print("-" * 45)

# Flag daily observations above each part's mean plus
# three standard deviations. This is a simple baseline,
# not a definitive anomaly detector.

part_stats = (
    sales.groupby("part_id")["units_sold"]
    .agg(["mean", "std"])
    .rename(columns={"mean": "part_mean", "std": "part_std"})
)

sales = sales.join(part_stats, on="part_id")

sales["spike_threshold"] = (
    sales["part_mean"] + 3 * sales["part_std"].fillna(0)
)

spikes = sales[
    (sales["units_sold"] > sales["spike_threshold"])
    & (sales["units_sold"] > 0)
].copy()

print(f"Potential demand spikes found: {len(spikes)}")

if not spikes.empty:
    print(
        spikes[
            ["date", "part_id", "units_sold", "spike_threshold"]
        ]
        .sort_values("units_sold", ascending=False)
        .head(10)
        .to_string(index=False)
    )
else:
    print("No observations crossed the spike threshold.")

spikes_file = OUTPUT_DIR / "demand_spikes.csv"
spikes.to_csv(spikes_file, index=False)

# --------------------------------------------------
# 8. SAVE SUMMARY FILES
# --------------------------------------------------

monthly_file = OUTPUT_DIR / "monthly_demand_summary.csv"
weekday_file = OUTPUT_DIR / "weekday_demand_summary.csv"
part_file = OUTPUT_DIR / "part_demand_summary.csv"

monthly_sales.rename("total_units_sold").to_csv(monthly_file)
weekday_sales.rename("average_units_sold").to_csv(weekday_file)
part_totals.rename("total_units_sold").to_csv(part_file)

# --------------------------------------------------
# 9. FINAL REPORT
# --------------------------------------------------

print("\n6. OUTPUT FILES")
print("-" * 45)

for output_file in [
    monthly_chart,
    weekday_chart,
    top_parts_chart,
    monthly_file,
    weekday_file,
    part_file,
    spikes_file,
]:
    print(output_file)

print("\nDEMAND PATTERN ANALYSIS COMPLETED")
print("=" * 65)
