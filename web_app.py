import hmac
import os
from datetime import date

from flask import Flask, redirect, render_template, request, session, url_for

from services.database_service import get_connection, initialize_database
from services.record_service import get_record_detail, get_record_list
from services.recipe_service import get_flour_list, get_flour_name, save_flour, save_recipe


app = Flask(
    __name__,
    template_folder="web",
    static_folder="web",
    static_url_path="/static",
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-development-secret-change-on-public")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
)

APP_PASSWORD = os.environ.get("APP_PASSWORD", "").strip()


@app.before_request
def require_login_when_public():
    """公開先でAPP_PASSWORDが設定されたときだけログインを必須にする。"""
    if not APP_PASSWORD:
        return None
    if request.endpoint in {"login", "static"}:
        return None
    if session.get("authenticated"):
        return None
    return redirect(url_for("login"))


def _optional_float(value, label):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError as error:
        raise ValueError(f"{label}は数値で入力してください。") from error


def _required_float(value, label):
    number = _optional_float(value, label)
    if number is None:
        raise ValueError(f"{label}を入力してください。")
    return number


def _score(value, label):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        score = int(text)
    except ValueError as error:
        raise ValueError(f"{label}は1〜10の整数で入力してください。") from error
    if not 1 <= score <= 10:
        raise ValueError(f"{label}は1〜10で入力してください。")
    return score


def load_recipes():
    initialize_database()
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, weak_no, medium_no, strong_no,
                   weak, medium, strong, hydration, salt_percent
            FROM recipes
            ORDER BY id DESC
            """
        ).fetchall()


def load_recipe_cards():
    cards = []
    for row in load_recipes():
        data = dict(row)
        data["weak_name"] = get_flour_name("薄力粉", row["weak_no"])
        data["medium_name"] = get_flour_name("中力粉", row["medium_no"])
        data["strong_name"] = get_flour_name("強力粉", row["strong_no"])
        cards.append(data)
    return cards


def load_all_flours():
    initialize_database()
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT kind, number, name, feature
            FROM flours
            ORDER BY CASE kind
                WHEN '薄力粉' THEN 1
                WHEN '中力粉' THEN 2
                WHEN '強力粉' THEN 3
                ELSE 4 END,
                number
            """
        ).fetchall()


def load_working_records():
    initialize_database()
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT s.id, s.record_date, s.recipe_id, s.temperature, s.humidity,
                   r.hydration
            FROM seimen_records AS s
            JOIN recipes AS r ON r.id = s.recipe_id
            WHERE s.state = '作業中'
            ORDER BY s.id DESC
            """
        ).fetchall()


def load_dashboard_data():
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
            SELECT s.total_score, r.hydration
            FROM seimen_records AS s
            JOIN recipes AS r ON r.id = s.recipe_id
            ORDER BY s.id DESC
            LIMIT 1
            """
        ).fetchone()
        recent_records = conn.execute(
            """
            SELECT s.id, s.record_date, s.recipe_id, s.temperature, s.humidity,
                   s.total_score, s.state, r.hydration
            FROM seimen_records AS s
            JOIN recipes AS r ON r.id = s.recipe_id
            ORDER BY s.id DESC
            LIMIT 6
            """
        ).fetchall()
        scored_records = conn.execute(
            """
            SELECT id, total_score
            FROM seimen_records
            WHERE state = '完了' AND total_score IS NOT NULL
            ORDER BY id DESC
            LIMIT 8
            """
        ).fetchall()[::-1]

    chart_points = []
    count = len(scored_records)
    for index, record in enumerate(scored_records):
        x = 50 if count == 1 else 5 + (90 * index / (count - 1))
        score = max(0, min(60, record["total_score"]))
        top = 94 - (score / 60 * 88)
        chart_points.append(
            {"id": record["id"], "score": score, "x": round(x, 2), "top": round(top, 2)}
        )

    return {
        "working_count": working_count,
        "completed_count": completed_count,
        "latest_score": latest["total_score"] if latest else None,
        "latest_hydration": latest["hydration"] if latest else None,
        "recent_records": recent_records,
        "chart_points": chart_points,
    }


def _record_matches(record, search_type, keyword):
    if not keyword:
        return True
    if search_type == "seimen_no":
        return str(record["id"]) == keyword
    if search_type == "recipe_no":
        return str(record["recipe_id"]) == keyword
    if search_type == "date":
        return keyword in str(record["record_date"] or "")
    return True


def _sort_records(records, sort_by):
    """Web一覧でよく使う並び順に並べ替える。Noneは常に最後へ送る。"""
    records = list(records)

    if sort_by == "date_asc":
        return sorted(
            records,
            key=lambda r: (not bool(r["record_date"]), r["record_date"] or "", r["id"]),
        )
    if sort_by == "score_desc":
        return sorted(
            records,
            key=lambda r: (r["total_score"] is not None, r["total_score"] or 0),
            reverse=True,
        )
    if sort_by == "score_asc":
        return sorted(
            records,
            key=lambda r: (r["total_score"] is None, r["total_score"] or 0),
        )
    if sort_by == "hydration_desc":
        return sorted(records, key=lambda r: r["hydration"], reverse=True)
    if sort_by == "hydration_asc":
        return sorted(records, key=lambda r: r["hydration"])
    if sort_by == "salt_desc":
        return sorted(records, key=lambda r: r["salt_percent"], reverse=True)
    if sort_by == "salt_asc":
        return sorted(records, key=lambda r: r["salt_percent"])

    # 標準は新しい日付順。日付がない場合は最後へ。
    return sorted(
        records,
        key=lambda r: (r["record_date"] or "", r["id"]),
        reverse=True,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if not APP_PASSWORD:
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if hmac.compare_digest(password, APP_PASSWORD):
            session["authenticated"] = True
            return redirect(url_for("dashboard"))
        error = "パスワードが違います。"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def dashboard():
    return render_template("dashboard.html", **load_dashboard_data())


@app.route("/records")
def records():
    search_type = request.args.get("search_type", "seimen_no")
    keyword = request.args.get("keyword", "").strip()
    state = request.args.get("state", "すべて")
    sort_by = request.args.get("sort", "date_desc")
    selected = request.args.get("selected", "").strip()

    visible_records = []
    for record in get_record_list():
        if state != "すべて" and record["state"] != state:
            continue
        if not _record_matches(record, search_type, keyword):
            continue
        visible_records.append(record)

    visible_records = _sort_records(visible_records, sort_by)

    detail = None
    detail_error = None
    if selected:
        try:
            detail = get_record_detail(selected)
        except (ValueError, TypeError) as exc:
            detail_error = str(exc)

    return render_template(
        "records.html",
        records=visible_records,
        detail=detail,
        detail_error=detail_error,
        search_type=search_type,
        keyword=keyword,
        state=state,
        sort_by=sort_by,
    )


@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    error = None

    if request.method == "POST":
        try:
            weak_no = int(request.form.get("weak_no", ""))
            medium_no = int(request.form.get("medium_no", ""))
            strong_no = int(request.form.get("strong_no", ""))
            weak = _required_float(request.form.get("weak"), "薄力粉量")
            medium = _required_float(request.form.get("medium"), "中力粉量")
            strong = _required_float(request.form.get("strong"), "強力粉量")
            hydration = _required_float(request.form.get("hydration"), "加水率")
            salt_percent = _required_float(request.form.get("salt_percent"), "塩分濃度")

            if min(weak, medium, strong) < 0:
                raise ValueError("粉量は0以上で入力してください。")
            if not 0 < hydration <= 100:
                raise ValueError("加水率は0より大きく100以下で入力してください。")
            if not 0 <= salt_percent <= 30:
                raise ValueError("塩分濃度は0〜30%で入力してください。")

            save_recipe(
                weak_no,
                medium_no,
                strong_no,
                weak,
                medium,
                strong,
                hydration,
                salt_percent,
            )
            return redirect(url_for("recipes"))
        except (ValueError, TypeError) as exc:
            error = str(exc)

    return render_template(
        "recipes.html",
        recipes=load_recipe_cards(),
        weak_flours=get_flour_list("薄力粉"),
        medium_flours=get_flour_list("中力粉"),
        strong_flours=get_flour_list("強力粉"),
        error=error,
    )


@app.route("/flours", methods=["GET", "POST"])
def flours():
    error = None

    if request.method == "POST":
        try:
            kind = request.form.get("kind", "").strip()
            number = int(request.form.get("number", "").strip())
            name = request.form.get("flour_name", request.form.get("name", "")).strip()
            feature = request.form.get("feature", "").strip()

            if kind not in {"薄力粉", "中力粉", "強力粉"}:
                raise ValueError("粉の種類を選択してください。")
            if number <= 0:
                raise ValueError("番号は1以上で入力してください。")
            if not name:
                raise ValueError("銘柄名を入力してください。")

            save_flour(kind, number, name, feature)
            return redirect(url_for("flours"))
        except (ValueError, TypeError) as exc:
            error = str(exc)

    return render_template("flours.html", flours=load_all_flours(), error=error)


@app.route("/start", methods=["GET", "POST"])
def start_seimen():
    error = None

    if request.method == "POST":
        try:
            recipe_id = int(request.form.get("recipe_id", "").strip())
            record_date = request.form.get("record_date", "").strip()
            temperature = _optional_float(request.form.get("temperature"), "気温")
            humidity = _optional_float(request.form.get("humidity"), "湿度")

            if humidity is not None and not 0 <= humidity <= 100:
                raise ValueError("湿度は0〜100で入力してください。")

            initialize_database()
            with get_connection() as conn:
                recipe = conn.execute(
                    "SELECT id FROM recipes WHERE id = ?", (recipe_id,)
                ).fetchone()
                if recipe is None:
                    raise ValueError("指定した配合番号が見つかりません。")
                conn.execute(
                    """
                    INSERT INTO seimen_records(recipe_id, record_date, temperature, humidity, state)
                    VALUES (?, ?, ?, ?, '作業中')
                    """,
                    (recipe_id, record_date, temperature, humidity),
                )

            return redirect(url_for("dashboard"))
        except (ValueError, TypeError) as exc:
            error = str(exc)

    return render_template(
        "start.html",
        recipes=load_recipes(),
        today=date.today().isoformat(),
        error=error,
    )


@app.route("/finish", methods=["GET", "POST"])
def finish_seimen():
    error = None

    if request.method == "POST":
        try:
            record_id = int(request.form.get("record_id", "").strip())
            room_hours = _optional_float(request.form.get("room_hours"), "常温熟成時間")
            cold_hours = _optional_float(request.form.get("cold_hours"), "冷蔵熟成時間")
            boil_minutes = _optional_float(request.form.get("boil_minutes"), "茹で時間")

            for value, label in [
                (room_hours, "常温熟成時間"),
                (cold_hours, "冷蔵熟成時間"),
                (boil_minutes, "茹で時間"),
            ]:
                if value is not None and value < 0:
                    raise ValueError(f"{label}は0以上で入力してください。")

            scores = {
                "smooth": _score(request.form.get("smooth_score"), "ツル感"),
                "chewy": _score(request.form.get("chewy_score"), "モチ感"),
                "firmness": _score(request.form.get("firmness_score"), "コシ"),
                "throat": _score(request.form.get("throat_score"), "のど越し"),
                "sticking": _score(request.form.get("sticking_score"), "くっつき"),
                "sauce": _score(request.form.get("sauce_score"), "タレとの相性"),
            }
            score_values = list(scores.values())
            total_score = sum(score_values) if all(v is not None for v in score_values) else None
            memo = request.form.get("memo", "").strip()

            room_text = f"{room_hours:g}h" if room_hours is not None else ""
            cold_text = f"{cold_hours:g}h" if cold_hours is not None else ""
            boil_text = f"{boil_minutes:g}分" if boil_minutes is not None else ""

            initialize_database()
            with get_connection() as conn:
                current = conn.execute(
                    "SELECT id FROM seimen_records WHERE id = ? AND state = '作業中'",
                    (record_id,),
                ).fetchone()
                if current is None:
                    raise ValueError("指定した作業中の製麺記録が見つかりません。")

                conn.execute(
                    """
                    UPDATE seimen_records
                    SET room_maturation = ?, cold_maturation = ?, boil_time = ?,
                        room_maturation_hours = ?, cold_maturation_hours = ?, boil_minutes = ?,
                        total_score = ?, smooth_score = ?, chewy_score = ?, firmness_score = ?,
                        throat_score = ?, sticking_score = ?, sauce_score = ?, memo = ?, state = '完了'
                    WHERE id = ?
                    """,
                    (
                        room_text,
                        cold_text,
                        boil_text,
                        room_hours,
                        cold_hours,
                        boil_minutes,
                        total_score,
                        scores["smooth"],
                        scores["chewy"],
                        scores["firmness"],
                        scores["throat"],
                        scores["sticking"],
                        scores["sauce"],
                        memo,
                        record_id,
                    ),
                )

            return redirect(url_for("dashboard"))
        except (ValueError, TypeError) as exc:
            error = str(exc)

    return render_template("finish.html", working_records=load_working_records(), error=error)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    host = os.environ.get("HOST", "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host=host, port=port)
