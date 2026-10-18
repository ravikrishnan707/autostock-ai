
import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "autostock.db"

INVENTORY_CSV = DATA_DIR / "automobile_spare_parts.csv"
SALES_CSV = DATA_DIR / "daily_sales_history.csv"


def load_data():
    # Check that both CSV files exist
    for file_path in [INVENTORY_CSV, SALES_CSV]:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    inventory_df = pd.read_csv(INVENTORY_CSV)
    sales_df = pd.read_csv(SALES_CSV)

    required_inventory = {
        "part_id", "part_name", "warehouse", "supplier",
        "stock", "daily_demand", "unit_cost", "lead_time_days"
    }
    required_sales = {
        "part_id", "warehouse", "date", "units_sold"
    }

    if not required_inventory.issubset(inventory_df.columns):
        raise ValueError(
            f"Inventory CSV must contain: {sorted(required_inventory)}"
        )

    if not required_sales.issubset(sales_df.columns):
        raise ValueError(
            f"Sales CSV must contain: {sorted(required_sales)}"
        )

    # Prepare the database connection
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        with connection:
            # Insert unique parts
            parts_df = inventory_df[
                ["part_id", "part_name", "unit_cost"]
            ].drop_duplicates(subset=["part_id"])

            connection.executemany(
                """
                INSERT INTO parts (part_id, part_name, unit_cost)
                VALUES (?, ?, ?)
                ON CONFLICT(part_id) DO UPDATE SET
                    part_name = excluded.part_name,
                    unit_cost = excluded.unit_cost
                """,
                parts_df.itertuples(index=False, name=None)
            )

            # Insert unique warehouses
            warehouses = sorted(inventory_df["warehouse"].dropna().unique())

            connection.executemany(
                """
                INSERT INTO warehouses (warehouse_name)
                VALUES (?)
                ON CONFLICT(warehouse_name) DO NOTHING
                """,
                [(name,) for name in warehouses]
            )

            # Insert unique suppliers and their lead times
            suppliers_df = (
                inventory_df[["supplier", "lead_time_days"]]
                .dropna()
                .drop_duplicates(subset=["supplier"])
            )

            connection.executemany(
                """
                INSERT INTO suppliers (supplier_name, lead_time_days)
                VALUES (?, ?)
                ON CONFLICT(supplier_name) DO UPDATE SET
                    lead_time_days = excluded.lead_time_days
                """,
                suppliers_df.itertuples(index=False, name=None)
            )

            # Build lookup dictionaries
            warehouse_ids = dict(
                connection.execute(
                    "SELECT warehouse_name, warehouse_id FROM warehouses"
                ).fetchall()
            )

            supplier_ids = dict(
                connection.execute(
                    "SELECT supplier_name, supplier_id FROM suppliers"
                ).fetchall()
            )

            # Insert current inventory
            inventory_records = []

            for row in inventory_df.itertuples(index=False):
                inventory_records.append((
                    row.part_id,
                    warehouse_ids[row.warehouse],
                    supplier_ids[row.supplier],
                    int(row.stock),
                    float(row.daily_demand)
                ))

            connection.executemany(
                """
                INSERT INTO inventory
                    (part_id, warehouse_id, supplier_id, stock, daily_demand)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(part_id, warehouse_id) DO UPDATE SET
                    supplier_id = excluded.supplier_id,
                    stock = excluded.stock,
                    daily_demand = excluded.daily_demand,
                    last_updated = CURRENT_TIMESTAMP
                """,
                inventory_records
            )

            # Convert sales dates to ISO format (YYYY-MM-DD)
            sales_df["date"] = pd.to_datetime(
                sales_df["date"], errors="raise"
            ).dt.strftime("%Y-%m-%d")

            sales_records = []

            for row in sales_df.itertuples(index=False):
                if row.warehouse not in warehouse_ids:
                    raise ValueError(
                        f"Unknown warehouse in sales data: {row.warehouse}"
                    )

                sales_records.append((
                    row.part_id,
                    warehouse_ids[row.warehouse],
                    row.date,
                    int(row.units_sold)
                ))

            connection.executemany(
                """
                INSERT INTO sales_history
                    (part_id, warehouse_id, sale_date, units_sold)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(part_id, warehouse_id, sale_date) DO UPDATE SET
                    units_sold = excluded.units_sold
                """,
                sales_records
            )

        print("CSV data loaded successfully!")

        for table in [
            "parts", "warehouses", "suppliers",
            "inventory", "sales_history", "purchase_orders"
        ]:
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            print(f"{table}: {count} records")

    finally:
        connection.close()


if __name__ == "__main__":
    load_data()
