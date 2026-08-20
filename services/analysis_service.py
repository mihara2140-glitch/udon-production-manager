from services.database_service import get_connection, initialize_database


def get_analysis_summary():
    """分析画面上部に表示する記録件数と平均点を返す。"""
    initialize_database()

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS completed_count,
                SUM(CASE WHEN total_score IS NOT NULL THEN 1 ELSE 0 END) AS evaluated_count,
                AVG(total_score) AS average_total
            FROM seimen_records
            WHERE state = '完了'
            """
        ).fetchone()

    return {
        "completed_count": row["completed_count"] or 0,
        "evaluated_count": row["evaluated_count"] or 0,
        "average_total": row["average_total"],
    }


def load_analysis_dataframe():
    """SQLiteの製麺記録をpandasのDataFrameとして読み込む。"""
    try:
        import pandas as pd
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(
            "pandasが必要です。'python -m pip install -r requirements.txt' を実行してください。"
        ) from error

    initialize_database()
    conn = get_connection()

    try:
        return pd.read_sql_query(
            """
            SELECT
                s.id,
                s.record_date,
                s.temperature,
                s.humidity,
                s.room_maturation_hours,
                s.cold_maturation_hours,
                s.boil_minutes,
                s.total_score,
                s.smooth_score,
                s.chewy_score,
                s.firmness_score,
                s.throat_score,
                s.sticking_score,
                s.sauce_score,
                r.hydration,
                r.salt_percent
            FROM seimen_records AS s
            JOIN recipes AS r ON r.id = s.recipe_id
            WHERE s.state = '完了'
            ORDER BY s.id
            """,
            conn,
        )
    finally:
        conn.close()
