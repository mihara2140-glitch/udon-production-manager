from services.database_service import get_connection, initialize_database
from services.recipe_service import get_flour_name


def get_record_list():
    """製麺記録一覧画面で使う、要点だけの記録データを返す。"""
    initialize_database()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                s.id,
                s.record_date,
                s.recipe_id,
                s.temperature,
                s.humidity,
                s.room_maturation_hours,
                s.cold_maturation_hours,
                s.boil_minutes,
                s.total_score,
                s.state,
                r.hydration,
                r.salt_percent
            FROM seimen_records AS s
            JOIN recipes AS r ON r.id = s.recipe_id
            ORDER BY s.id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_record_detail(record_id):
    """選択した製麺記録の詳細データを返す。"""
    initialize_database()

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                s.*,
                r.weak_no,
                r.medium_no,
                r.strong_no,
                r.weak,
                r.medium,
                r.strong,
                r.hydration,
                r.salt_percent
            FROM seimen_records AS s
            JOIN recipes AS r ON r.id = s.recipe_id
            WHERE s.id = ?
            """,
            (int(record_id),),
        ).fetchone()

    if row is None:
        raise ValueError(f"製麺番号 {record_id} は見つかりません。")

    data = dict(row)
    data["weak_name"] = get_flour_name("薄力粉", data["weak_no"])
    data["medium_name"] = get_flour_name("中力粉", data["medium_no"])
    data["strong_name"] = get_flour_name("強力粉", data["strong_no"])
    return data
