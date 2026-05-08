"""
Egyszerű SQLite séma migráció – új mezők hozzáadása ALTER TABLE-lel.
Automatikusan meghívódik az alkalmazás indításakor.
"""
from sqlalchemy import text
from app.database import engine


def _col_exists(conn, table: str, column: str) -> bool:
    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == column for r in rows)


def run_migrations():
    migrations = [
        # WorkStation – aktuális munka mezők
        ("workstations", "current_work_description", "TEXT"),
        ("workstations", "current_work_article",     "VARCHAR(100)"),
        ("workstations", "current_work_started_at",  "DATETIME"),
        ("workstations", "current_work_operator",    "VARCHAR(100)"),
        ("workstations", "canvas_w",                 "INTEGER DEFAULT 1200"),
        ("workstations", "canvas_h",                 "INTEGER DEFAULT 700"),
        # RFIDReader – térkép pozíció
        ("rfid_readers", "hall_id",  "INTEGER"),
        ("rfid_readers", "svg_x",    "INTEGER DEFAULT 100"),
        ("rfid_readers", "svg_y",    "INTEGER DEFAULT 100"),
    ]

    with engine.connect() as conn:
        for table, column, col_type in migrations:
            if not _col_exists(conn, table, column):
                try:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                    conn.commit()
                    print(f"  [migrate] {table}.{column} hozzáadva")
                except Exception as e:
                    print(f"  [migrate] HIBA: {table}.{column}: {e}")
