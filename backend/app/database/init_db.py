
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DB_PATH = PROJECT_ROOT / "data" / "autostock.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema)

        print("Database initialized successfully!")
        print(f"Database location: {DB_PATH}")

        cursor = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' "
            "AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )

        print("\nTables created:")
        for row in cursor.fetchall():
            print("-", row[0])

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
