from services.database_service import get_connection, initialize_database
from services.recipe_service import get_flour_name, get_recipe


def _score(entry, label):
    value = entry.get().strip()
    if not value:
        return None

    score = int(value)
    if not 1 <= score <= 10:
        raise ValueError(f"{label}は1〜10で入力してください。")
    return score


def save_start_data(recipe_entry, date_entry, temp_entry, humidity_entry, new_window):
    initialize_database()

    recipe_no = recipe_entry.get().strip()
    record_date = date_entry.get().strip()
    temp = temp_entry.get().strip()
    humidity = humidity_entry.get().strip()

    if not recipe_no:
        raise ValueError("配合番号を入力してください。")

    # 配合番号が存在するか先に確認
    get_recipe(int(recipe_no))

    temperature = float(temp) if temp else None
    humidity_value = float(humidity) if humidity else None

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO seimen_records(
                recipe_id, record_date, temperature, humidity, state
            ) VALUES (?, ?, ?, ?, '作業中')
            """,
            (int(recipe_no), record_date, temperature, humidity_value),
        )

    new_window.destroy()


def show_working_list():
    initialize_database()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, recipe_id, record_date, temperature, humidity
            FROM seimen_records
            WHERE state = '作業中'
            ORDER BY id DESC
            """
        ).fetchall()

    text = "=== 作業中の製麺 ===\n\n"

    if not rows:
        return text + "現在、作業中の製麺はありません。\n"

    for row in rows:
        recipe = get_recipe(row["recipe_id"])
        weak_name = get_flour_name("薄力粉", int(recipe[0]))
        medium_name = get_flour_name("中力粉", int(recipe[1]))
        strong_name = get_flour_name("強力粉", int(recipe[2]))

        temp = row["temperature"] if row["temperature"] is not None else "-"
        humidity = row["humidity"] if row["humidity"] is not None else "-"

        text += f"製麺番号：{row['id']}\n"
        text += f"日付：{row['record_date'] or '-'}\n"
        text += f"気温 / 湿度：{temp}℃ / {humidity}%\n"
        text += f"配合番号：{row['recipe_id']}\n"
        text += (
            f"薄力 {recipe[3]}g（{weak_name}） / "
            f"中力 {recipe[4]}g（{medium_name}） / "
            f"強力 {recipe[5]}g（{strong_name}）\n"
        )
        text += f"加水率 {recipe[6]}% / 塩分濃度 {recipe[7]}%\n"
        text += "─" * 38 + "\n\n"

    return text


def save_finish_data(
    seimen_entry,
    room_maturation_entry,
    cold_maturation_entry,
    boil_entry,
    evaluation_entries,
    comment,
    new_window,
):
    initialize_database()

    seimen_no = int(seimen_entry.get().strip())
    room_maturation = room_maturation_entry.get().strip()
    cold_maturation = cold_maturation_entry.get().strip()
    boil = boil_entry.get().strip()
    memo = comment.get("1.0", "end").strip()

    scores = {
        label: _score(entry, label)
        for label, entry in evaluation_entries.items()
    }

    with get_connection() as conn:
        current = conn.execute(
            "SELECT id FROM seimen_records WHERE id = ? AND state = '作業中'",
            (seimen_no,),
        ).fetchone()

        if current is None:
            raise ValueError("指定した作業中の製麺番号が見つかりません。")

        conn.execute(
            """
            UPDATE seimen_records
            SET room_maturation = ?,
                cold_maturation = ?,
                boil_time = ?,
                total_score = ?,
                smooth_score = ?,
                chewy_score = ?,
                firmness_score = ?,
                throat_score = ?,
                sticking_score = ?,
                sauce_score = ?,
                memo = ?,
                state = '完了'
            WHERE id = ?
            """,
            (
                room_maturation,
                cold_maturation,
                boil,
                scores["総合評価"],
                scores["ツル感"],
                scores["モチ感"],
                scores["コシ"],
                scores["のど越し"],
                scores["くっつき"],
                scores["タレとの相性"],
                memo,
                seimen_no,
            ),
        )

    new_window.destroy()


def show_data():
    initialize_database()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM seimen_records
            ORDER BY id DESC
            """
        ).fetchall()

    text = "=== 製麺記録 ===\n\n"

    if not rows:
        return text + "製麺記録はまだありません。\n"

    for row in rows:
        recipe = get_recipe(row["recipe_id"])
        weak_name = get_flour_name("薄力粉", int(recipe[0]))
        medium_name = get_flour_name("中力粉", int(recipe[1]))
        strong_name = get_flour_name("強力粉", int(recipe[2]))

        temp = row["temperature"] if row["temperature"] is not None else "-"
        humidity = row["humidity"] if row["humidity"] is not None else "-"

        text += f"製麺番号：{row['id']}　状態：{row['state']}\n"
        text += f"日付：{row['record_date'] or '-'}　気温：{temp}℃　湿度：{humidity}%\n"
        text += (
            f"常温熟成：{row['room_maturation'] or '-'}　"
            f"冷蔵熟成：{row['cold_maturation'] or '-'}\n"
        )
        text += f"配合番号：{row['recipe_id']}\n"
        text += (
            f"薄力 {recipe[3]}g（{weak_name}） / "
            f"中力 {recipe[4]}g（{medium_name}） / "
            f"強力 {recipe[5]}g（{strong_name}）\n"
        )
        text += f"加水率：{recipe[6]}%　塩分濃度：{recipe[7]}%\n"
        text += f"茹で時間：{row['boil_time'] or '-'}\n"

        if row["state"] == "完了":
            text += (
                f"評価：総合 {row['total_score'] or '-'} / "
                f"ツル {row['smooth_score'] or '-'} / "
                f"モチ {row['chewy_score'] or '-'} / "
                f"コシ {row['firmness_score'] or '-'} / "
                f"のど越し {row['throat_score'] or '-'} / "
                f"くっつき {row['sticking_score'] or '-'} / "
                f"タレ {row['sauce_score'] or '-'}\n"
            )
            text += f"感想：{row['memo'] or '-'}\n"

        text += "─" * 48 + "\n\n"

    return text


def show_high_humidity():
    initialize_database()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM seimen_records
            WHERE humidity >= 70
            ORDER BY id DESC
            """
        ).fetchall()

    text = "=== 湿度70%以上の記録 ===\n\n"

    if not rows:
        return text + "該当する記録はありません。\n"

    for row in rows:
        recipe = get_recipe(row["recipe_id"])

        text += f"製麺番号：{row['id']}　日付：{row['record_date'] or '-'}\n"
        text += f"気温：{row['temperature'] or '-'}℃　湿度：{row['humidity']}%\n"
        text += (
            f"常温熟成：{row['room_maturation'] or '-'}　"
            f"冷蔵熟成：{row['cold_maturation'] or '-'}\n"
        )
        text += f"加水率：{recipe[6]}%　塩分濃度：{recipe[7]}%\n"
        text += f"くっつき評価：{row['sticking_score'] or '-'}\n"
        text += f"感想：{row['memo'] or '-'}\n"
        text += "─" * 38 + "\n\n"

    return text
