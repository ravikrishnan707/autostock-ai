
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "autostock.db"

EXPECTED_TABLES = {
    "parts",
    "warehouses",
    "suppliers",
    "inventory",
    "sales_history",
    "purchase_orders",
}


def verify_database():
    print("=== AutoStock AI Database Verification ===\n")

    if not DB_PATH.exists():
        print("FAIL: Database file not found:", DB_PATH)
        return

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    errors = []

    try:
        # 1. Check required tables
        tables = {
            row[0]
            for row in connection.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type = 'table'
                AND name NOT LIKE 'sqlite_%'
                """
            )
        }

        print("1. TABLE CHECK")
        for table in sorted(EXPECTED_TABLES):
            if table in tables:
                print(f"PASS: {table} exists")
            else:
                print(f"FAIL: {table} is missing")
                errors.append(f"Missing table: {table}")

        if not EXPECTED_TABLES.issubset(tables):
            print("\nVerification finished with errors.")
            return

        # 2. Display record counts
        print("\n2. RECORD COUNTS")
        for table in sorted(EXPECTED_TABLES):
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            print(f"{table}: {count}")

        # 3. Check required data
        print("\n3. REQUIRED DATA CHECK")

        required_counts = {
            "parts": 1,
            "warehouses": 1,
            "suppliers": 1,
            "inventory": 1,
            "sales_history": 1,
        }

        for table, minimum in required_counts.items():
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            if count >= minimum:
                print(f"PASS: {table} contains records")
            else:
                print(f"FAIL: {table} is empty")
                errors.append(f"{table} is empty")

        # 4. Check invalid numeric values
        print("\n4. DATA QUALITY CHECK")

        checks = {
            "Negative stock": """
                SELECT COUNT(*) FROM inventory WHERE stock < 0
            """,
            "Non-positive daily demand": """
                SELECT COUNT(*) FROM inventory WHERE daily_demand <= 0
            """,
            "Negative unit cost": """
                SELECT COUNT(*) FROM parts WHERE unit_cost < 0
            """,
            "Negative sales": """
                SELECT COUNT(*) FROM sales_history WHERE units_sold < 0
            """,
        }

        for description, query in checks.items():
            count = connection.execute(query).fetchone()[0]

            if count == 0:
                print(f"PASS: {description}")
            else:
                print(f"FAIL: {description} ({count} records)")
                errors.append(description)

        # 5. Check foreign-key relationships
        print("\n5. FOREIGN KEY CHECK")

        foreign_key_errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if not foreign_key_errors:
            print("PASS: No foreign-key violations")
        else:
            print("FAIL: Foreign-key violations found")
            for error in foreign_key_errors[:10]:
                print(error)
            errors.append("Foreign-key violations")

        # 6. Check duplicate inventory and sales records
        print("\n6. DUPLICATE CHECK")

        duplicate_checks = {
            "Duplicate part per warehouse": """
                SELECT COUNT(*) FROM (
                    SELECT part_id, warehouse_id
                    FROM inventory
                    GROUP BY part_id, warehouse_id
                    HAVING COUNT(*) > 1
                )
            """,
            "Duplicate daily sales records": """
                SELECT COUNT(*) FROM (
                    SELECT part_id, warehouse_id, sale_date
                    FROM sales_history
                    GROUP BY part_id, warehouse_id, sale_date
                    HAVING COUNT(*) > 1
                )
            """,
        }

        for description, query in duplicate_checks.items():
            count = connection.execute(query).fetchone()[0]

            if count == 0:
                print(f"PASS: {description}")
            else:
                print(f"FAIL: {description} ({count} duplicate groups)")
                errors.append(description)

        # 7. Final result
        print("\n=== FINAL RESULT ===")

        if errors:
            print(f"CHECK FAILED: {len(errors)} issue(s) found.")
            for error in errors:
                print("-", error)
        else:
            print("ALL CHECKS PASSED!")

    finally:
        connection.close()


if __name__ == "__main__":
    verify_database()
