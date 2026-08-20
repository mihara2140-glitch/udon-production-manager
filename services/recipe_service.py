from services.database_service import get_connection, initialize_database


def get_recipe(recipe_no):
    initialize_database()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT weak_no, medium_no, strong_no,
                   weak, medium, strong, hydration, salt_percent
            FROM recipes
            WHERE id = ?
            """,
            (int(recipe_no),),
        ).fetchone()

    if row is None:
        raise ValueError(f"配合番号 {recipe_no} は見つかりません。")

    return list(row)


def get_flour_name(kind, number):
    initialize_database()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT name FROM flours WHERE kind = ? AND number = ?",
            (kind, int(number)),
        ).fetchone()

    return row["name"] if row else "未登録"


def show_recipe_list():
    initialize_database()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, weak_no, medium_no, strong_no,
                   weak, medium, strong, hydration, salt_percent
            FROM recipes
            ORDER BY id
            """
        ).fetchall()

    text = "=== 配合一覧 ===\n\n"

    if not rows:
        return text + "配合がまだ登録されていません。\n"

    for row in rows:
        weak_name = get_flour_name("薄力粉", row["weak_no"])
        medium_name = get_flour_name("中力粉", row["medium_no"])
        strong_name = get_flour_name("強力粉", row["strong_no"])

        text += f"【{row['id']}】\n"
        text += f"薄力粉：{row['weak']}g ({weak_name})\n"
        text += f"中力粉：{row['medium']}g ({medium_name})\n"
        text += f"強力粉：{row['strong']}g ({strong_name})\n"
        text += f"加水率：{row['hydration']}%\n"
        text += f"塩分濃度：{row['salt_percent']}%\n"
        text += "-------------\n"

    return text


def get_flour_list(kind):
    initialize_database()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT number, name FROM flours WHERE kind = ? ORDER BY number",
            (kind,),
        ).fetchall()

    return [(row["number"], row["name"]) for row in rows]


def calc_water(flour, hydration):
    return flour * hydration / 100


def calc_salt(water, salt_percent):
    return water * salt_percent / 100


def get_last_recipe():
    initialize_database()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT weak_no, medium_no, strong_no,
                   weak, medium, strong, hydration, salt_percent
            FROM recipes
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

    return list(row) if row else None


def save_recipe(
    weak_no, medium_no, strong_no, weak, medium, strong, hydration, salt_percent
):
    initialize_database()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO recipes(
                weak_no, medium_no, strong_no,
                weak, medium, strong, hydration, salt_percent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(weak_no),
                int(medium_no),
                int(strong_no),
                float(weak),
                float(medium),
                float(strong),
                float(hydration),
                float(salt_percent),
            ),
        )


def show_recipe_history():
    initialize_database()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, weak_no, medium_no, strong_no,
                   weak, medium, strong, hydration, salt_percent
            FROM recipes
            ORDER BY id
            """
        ).fetchall()

    text = "=== 配合履歴 ===\n\n"

    for row in rows:
        weak_name = get_flour_name("薄力粉", row["weak_no"])
        medium_name = get_flour_name("中力粉", row["medium_no"])
        strong_name = get_flour_name("強力粉", row["strong_no"])

        flour = row["weak"] + row["medium"] + row["strong"]
        water = calc_water(flour, row["hydration"])
        salt = calc_salt(water, row["salt_percent"])

        text += "======================\n"
        text += f"【配合 {row['id']}】\n"
        text += f"薄力粉：{row['weak']}g ({weak_name})\n"
        text += f"中力粉：{row['medium']}g ({medium_name})\n"
        text += f"強力粉：{row['strong']}g ({strong_name})\n"
        text += f"加水率：{row['hydration']}%\n"
        text += f"必要な水：{water:.2f}g\n"
        text += f"塩分濃度：{row['salt_percent']}%\n"
        text += f"必要な塩：{salt:.2f}g\n"
        text += "----------------------\n\n"

    return text


def show_flour_list():
    initialize_database()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT kind, number, name, feature FROM flours ORDER BY kind, number"
        ).fetchall()

    text = "=== 粉銘柄一覧 ===\n\n"

    for row in rows:
        text += "====================\n"
        text += f"種類：{row['kind']}\n"
        text += f"番号：{row['number']}\n"
        text += f"銘柄：{row['name']}\n"
        text += f"特徴：{row['feature'] or '-'}\n"
        text += "--------------------\n"

    return text


def save_flour(kind, number, name, feature):
    initialize_database()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO flours(kind, number, name, feature)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(kind, number)
            DO UPDATE SET name = excluded.name, feature = excluded.feature
            """,
            (kind, int(number), name, feature),
        )


def search_recipe(recipe_no):
    initialize_database()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, record_date, temperature, humidity,
                   room_maturation, cold_maturation, boil_time,
                   total_score, memo, state
            FROM seimen_records
            WHERE recipe_id = ?
            ORDER BY id DESC
            """,
            (int(recipe_no),),
        ).fetchall()

    text = f"=== 配合{recipe_no}を使った製麺記録 ===\n\n"

    if not rows:
        return text + "該当する製麺記録がありません。\n"

    for row in rows:
        text += "=====================\n"
        text += f"製麺番号：{row['id']}\n"
        text += f"日付：{row['record_date'] or '-'}\n"
        text += f"気温：{row['temperature'] if row['temperature'] is not None else '-'}℃\n"
        text += f"湿度：{row['humidity'] if row['humidity'] is not None else '-'}%\n"
        text += f"常温熟成：{row['room_maturation'] or '-'}\n"
        text += f"冷蔵熟成：{row['cold_maturation'] or '-'}\n"
        text += f"茹で時間：{row['boil_time'] or '-'}\n"
        text += f"総合評価：{row['total_score'] if row['total_score'] is not None else '-'}\n"
        text += f"感想：{row['memo'] or '-'}\n"
        text += f"状態：{row['state']}\n"
        text += "---------------------\n"

    return text
