from flask import Flask, render_template

from services.database_service import get_connection, initialize_database


app = Flask(
    __name__,
    template_folder="web",
    static_folder="web",
    static_url_path="/static",
)


def load_dashboard_data():
    """Webダッシュボードに必要な情報をSQLiteから読み込む。"""
    initialize_database()

    with get_connection() as conn:
        working_count = conn.execute(
            "SELECT COUNT(*) FROM seimen_records WHERE state = '作業中'"
        ).fetchone()[0]

        completed_count = conn.execute(
            "SELECT COUNT(*) FROM seimen_records WHERE state = '完了'"
        ).fetchone()[0]

        latest = conn.execute(
            """
            SELECT
                s.id,
                s.record_date,
                s.recipe_id,
                s.temperature,
                s.humidity,
                s.total_score,
                r.hydration
            FROM seimen_records AS s
            JOIN recipes AS r ON r.id = s.recipe_id
            ORDER BY s.id DESC
            LIMIT 1
            """
        ).fetchone()

        recent_records = conn.execute(
            """
            SELECT
                s.id,
                s.record_date,
                s.recipe_id,
                s.temperature,
                s.humidity,
                s.total_score,
                s.state,
                r.hydration
            FROM seimen_records AS s
            JOIN recipes AS r ON r.id = s.recipe_id
            ORDER BY s.id DESC
            LIMIT 6
            """
        ).fetchall()

    return {
        "working_count": working_count,
        "completed_count": completed_count,
        "latest_score": latest["total_score"] if latest else None,
        "latest_hydration": latest["hydration"] if latest else None,
        "recent_records": recent_records,
    }


@app.route("/")
def dashboard():
    return render_template("dashboard.html", **load_dashboard_data())


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
