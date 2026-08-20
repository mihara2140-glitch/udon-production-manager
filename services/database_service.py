import csv
import sqlite3
from pathlib import Path

DATA_DIR = Path("data")
DB_FILE = DATA_DIR / "udon_manager.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Ver.21用DBを作成し、既存CSVがあれば初回だけ取り込む。"""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS app_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS flours (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                number INTEGER NOT NULL,
                name TEXT NOT NULL,
                feature TEXT DEFAULT '',
                UNIQUE(kind, number)
            );

            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weak_no INTEGER NOT NULL,
                medium_no INTEGER NOT NULL,
                strong_no INTEGER NOT NULL,
                weak REAL NOT NULL,
                medium REAL NOT NULL,
                strong REAL NOT NULL,
                hydration REAL NOT NULL,
                salt_percent REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS seimen_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                record_date TEXT,
                temperature REAL,
                humidity REAL,
                room_maturation TEXT DEFAULT '',
                cold_maturation TEXT DEFAULT '',
                boil_time TEXT DEFAULT '',
                total_score INTEGER,
                smooth_score INTEGER,
                chewy_score INTEGER,
                firmness_score INTEGER,
                throat_score INTEGER,
                sticking_score INTEGER,
                sauce_score INTEGER,
                memo TEXT DEFAULT '',
                state TEXT NOT NULL DEFAULT '作業中',
                FOREIGN KEY(recipe_id) REFERENCES recipes(id)
            );
            """
        )

        migrated = conn.execute(
            "SELECT value FROM app_meta WHERE key = 'csv_migrated'"
        ).fetchone()

        if migrated is None:
            _migrate_csv_files(conn)
            conn.execute(
                "INSERT OR REPLACE INTO app_meta(key, value) VALUES('csv_migrated', '1')"
            )


def _migrate_csv_files(conn):
    _migrate_flours(conn)
    _migrate_recipes(conn)
    _migrate_seimen(conn)


def _migrate_flours(conn):
    path = DATA_DIR / "flour_master.csv"
    if not path.exists():
        return

    with path.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    for row in rows[1:]:
        if len(row) < 3 or not row[0] or not row[1]:
            continue
        feature = row[3] if len(row) > 3 else ""
        conn.execute(
            """
            INSERT OR IGNORE INTO flours(kind, number, name, feature)
            VALUES (?, ?, ?, ?)
            """,
            (row[0], int(row[1]), row[2], feature),
        )


def _migrate_recipes(conn):
    path = DATA_DIR / "recipe.csv"
    if not path.exists():
        return

    with path.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    for row in rows[1:]:
        if len(row) < 8 or not row[0]:
            continue
        conn.execute(
            """
            INSERT INTO recipes(
                weak_no, medium_no, strong_no,
                weak, medium, strong, hydration, salt_percent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(row[0]),
                int(row[1]),
                int(row[2]),
                float(row[3]),
                float(row[4]),
                float(row[5]),
                float(row[6]),
                float(row[7]),
            ),
        )


def _normalize_seimen_row(row):
    """旧8列 / Ver.20 17列を共通の17列へ変換する。"""
    if len(row) >= 17:
        return row[:17]

    if len(row) >= 8:
        return [
            row[0], row[1], row[2], row[3], row[4],
            "", "", row[5],
            "", "", "", "", "", "", "",
            row[6], row[7],
        ]

    return row + [""] * (17 - len(row))


def _to_float(value):
    value = str(value).strip()
    return float(value) if value else None


def _to_int(value):
    value = str(value).strip()
    return int(value) if value else None


def _migrate_seimen(conn):
    path = DATA_DIR / "udon_note.csv"
    if not path.exists():
        return

    with path.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    for raw in rows[1:]:
        if not raw:
            continue

        row = _normalize_seimen_row(raw)
        if not row[0] or not row[1]:
            continue

        conn.execute(
            """
            INSERT OR IGNORE INTO seimen_records(
                id, recipe_id, record_date, temperature, humidity,
                room_maturation, cold_maturation, boil_time,
                total_score, smooth_score, chewy_score, firmness_score,
                throat_score, sticking_score, sauce_score, memo, state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(row[0]),
                int(row[1]),
                row[2],
                _to_float(row[3]),
                _to_float(row[4]),
                row[5],
                row[6],
                row[7],
                _to_int(row[8]),
                _to_int(row[9]),
                _to_int(row[10]),
                _to_int(row[11]),
                _to_int(row[12]),
                _to_int(row[13]),
                _to_int(row[14]),
                row[15],
                row[16] or "完了",
            ),
        )
