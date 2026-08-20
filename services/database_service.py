import csv
import os
import re
import sqlite3
from datetime import date as date_type
from pathlib import Path

# ローカルでは従来どおり製麺管理アプリ直下の data を使う。
# 公開先では UDON_DB_PATH を設定すると、永続ストレージ上のSQLiteへ切り替えられる。
BASE_DIR = Path(__file__).resolve().parent.parent
LEGACY_DATA_DIR = BASE_DIR / "data"
DB_FILE = Path(
    os.environ.get("UDON_DB_PATH", str(LEGACY_DATA_DIR / "udon_manager.db"))
).expanduser()
DATA_DIR = DB_FILE.parent


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def normalize_record_date(value):
    """製麺日を YYYY-MM-DD に統一する。例: 2026/8/6 -> 2026-08-06。"""
    text = str(value or "").strip()
    if not text:
        return ""

    # 2026/8/6, 2026-8-6, 2026.8.6 を受け付ける。
    match = re.fullmatch(r"(\d{4})[./-](\d{1,2})[./-](\d{1,2})", text)
    if match:
        try:
            year, month, day = (int(part) for part in match.groups())
            return date_type(year, month, day).isoformat()
        except ValueError:
            return text

    # 20260806 のような8桁表記も念のため対応。
    if re.fullmatch(r"\d{8}", text):
        try:
            return date_type(int(text[:4]), int(text[4:6]), int(text[6:8])).isoformat()
        except ValueError:
            return text

    return text


def parse_hours(value):
    """熟成時間を時間単位の数値へ変換する。例: 1.5 / 1.5h / 90分。"""
    text = str(value or "").strip().lower()
    if not text:
        return None

    text = text.replace("時間", "h").replace("hours", "h").replace("hour", "h")

    if ":" in text:
        parts = text.split(":")
        try:
            return float(parts[0]) + float(parts[1]) / 60
        except (ValueError, IndexError):
            return None

    hour_match = re.search(r"(-?\d+(?:\.\d+)?)\s*h", text)
    minute_match = re.search(r"(-?\d+(?:\.\d+)?)\s*分", text)

    if hour_match:
        hours = float(hour_match.group(1))
        if minute_match:
            hours += float(minute_match.group(1)) / 60
        return hours

    if minute_match:
        return float(minute_match.group(1)) / 60

    number_match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(number_match.group()) if number_match else None


def parse_minutes(value):
    """茹で時間を分単位の数値へ変換する。例: 12.5 / 12分30秒 / 12:30。"""
    text = str(value or "").strip().lower()
    if not text:
        return None

    if ":" in text:
        parts = text.split(":")
        try:
            return float(parts[0]) + float(parts[1]) / 60
        except (ValueError, IndexError):
            return None

    minute_match = re.search(r"(-?\d+(?:\.\d+)?)\s*分", text)
    second_match = re.search(r"(-?\d+(?:\.\d+)?)\s*秒", text)

    if minute_match:
        minutes = float(minute_match.group(1))
        if second_match:
            minutes += float(second_match.group(1)) / 60
        return minutes

    number_match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(number_match.group()) if number_match else None


def initialize_database():
    """DBを準備し、旧データを現在形式へ自動アップグレードする。"""
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
                room_maturation_hours REAL,
                cold_maturation_hours REAL,
                boil_minutes REAL,
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

        _ensure_ver22_columns(conn)

        migrated = conn.execute(
            "SELECT value FROM app_meta WHERE key = 'csv_migrated'"
        ).fetchone()

        if migrated is None:
            _migrate_csv_files(conn)
            conn.execute(
                "INSERT OR REPLACE INTO app_meta(key, value) VALUES('csv_migrated', '1')"
            )

        _backfill_ver22_values(conn)
        _normalize_record_dates(conn)
        conn.execute(
            "INSERT OR REPLACE INTO app_meta(key, value) VALUES('schema_version', '23')"
        )


def _ensure_ver22_columns(conn):
    """Ver.21 DBを削除せず、分析用の数値列だけ追加する。"""
    columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(seimen_records)").fetchall()
    }

    additions = {
        "room_maturation_hours": "REAL",
        "cold_maturation_hours": "REAL",
        "boil_minutes": "REAL",
    }

    for column, data_type in additions.items():
        if column not in columns:
            conn.execute(
                f"ALTER TABLE seimen_records ADD COLUMN {column} {data_type}"
            )


def _normalize_record_dates(conn):
    """既存の製麺日を YYYY-MM-DD へ統一する。"""
    rows = conn.execute("SELECT id, record_date FROM seimen_records").fetchall()
    for row in rows:
        normalized = normalize_record_date(row["record_date"])
        if normalized != (row["record_date"] or ""):
            conn.execute(
                "UPDATE seimen_records SET record_date = ? WHERE id = ?",
                (normalized, row["id"]),
            )


def _backfill_ver22_values(conn):
    """Ver.21までの文字データから、分析用の数値を可能な範囲で作る。"""
    rows = conn.execute(
        """
        SELECT id, room_maturation, cold_maturation, boil_time,
               room_maturation_hours, cold_maturation_hours, boil_minutes,
               smooth_score, chewy_score, firmness_score,
               throat_score, sticking_score, sauce_score
        FROM seimen_records
        """
    ).fetchall()

    for row in rows:
        room_hours = row["room_maturation_hours"]
        cold_hours = row["cold_maturation_hours"]
        boil_minutes = row["boil_minutes"]

        if room_hours is None:
            room_hours = parse_hours(row["room_maturation"])
        if cold_hours is None:
            cold_hours = parse_hours(row["cold_maturation"])
        if boil_minutes is None:
            boil_minutes = parse_minutes(row["boil_time"])

        score_values = [
            row["smooth_score"],
            row["chewy_score"],
            row["firmness_score"],
            row["throat_score"],
            row["sticking_score"],
            row["sauce_score"],
        ]
        total_score = sum(score_values) if all(v is not None for v in score_values) else None

        conn.execute(
            """
            UPDATE seimen_records
            SET room_maturation_hours = ?,
                cold_maturation_hours = ?,
                boil_minutes = ?,
                total_score = COALESCE(?, total_score)
            WHERE id = ?
            """,
            (room_hours, cold_hours, boil_minutes, total_score, row["id"]),
        )


def _migrate_csv_files(conn):
    _migrate_flours(conn)
    _migrate_recipes(conn)
    _migrate_seimen(conn)


def _migrate_flours(conn):
    path = LEGACY_DATA_DIR / "flour_master.csv"
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
    path = LEGACY_DATA_DIR / "recipe.csv"
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
    path = LEGACY_DATA_DIR / "udon_note.csv"
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

        score_values = [_to_int(row[i]) for i in range(9, 15)]
        auto_total = sum(score_values) if all(v is not None for v in score_values) else _to_int(row[8])

        conn.execute(
            """
            INSERT OR IGNORE INTO seimen_records(
                id, recipe_id, record_date, temperature, humidity,
                room_maturation, cold_maturation, boil_time,
                room_maturation_hours, cold_maturation_hours, boil_minutes,
                total_score, smooth_score, chewy_score, firmness_score,
                throat_score, sticking_score, sauce_score, memo, state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(row[0]),
                int(row[1]),
                normalize_record_date(row[2]),
                _to_float(row[3]),
                _to_float(row[4]),
                row[5],
                row[6],
                row[7],
                parse_hours(row[5]),
                parse_hours(row[6]),
                parse_minutes(row[7]),
                auto_total,
                score_values[0],
                score_values[1],
                score_values[2],
                score_values[3],
                score_values[4],
                score_values[5],
                row[15],
                row[16] or "完了",
            ),
        )
