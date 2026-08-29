from services.database_service import get_connection, initialize_database


def _format_amount(value):
    return f"{float(value):g}"


def get_recipe(recipe_no):
    """旧GUIとの互換用。中力粉が複数の場合、medium は中力粉合計量になる。"""
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


def get_recipe_components(recipe_no):
    """1つの配合で実際に使う粉を、登録順にすべて返す。"""
    initialize_database()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT f.kind, f.number, f.name, f.feature,
                   rf.amount, rf.sort_order
            FROM recipe_flours AS rf
            JOIN flours AS f ON f.id = rf.flour_id
            WHERE rf.recipe_id = ?
            ORDER BY rf.sort_order, rf.id
            """,
            (int(recipe_no),),
        ).fetchall()

    return [dict(row) for row in rows]


def get_flour_name(kind, number):
    """固定3粉表示との互換を保ちつつ、未使用・中力粉ブレンドも表示する。"""
    initialize_database()
    number = int(number or 0)

    if number == 0:
        return "使用しない"

    # Web版の旧表示は medium_no 1個しか持てないため、
    # 中力粉を複数使う配合では -配合ID を互換用の目印として保存する。
    if kind == "中力粉" and number < 0:
        recipe_id = abs(number)
        components = [
            item for item in get_recipe_components(recipe_id)
            if item["kind"] == "中力粉"
        ]
        if components:
            return " + ".join(
                f"{item['name']} {_format_amount(item['amount'])}g"
                for item in components
            )
        return "中力粉ブレンド"

    with get_connection() as conn:
        row = conn.execute(
            "SELECT name FROM flours WHERE kind = ? AND number = ?",
            (kind, number),
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


def _form_medium_pairs(default_no, default_amount):
    """Flask画面では同名フィールドの繰り返しから中力粉を複数受け取る。"""
    try:
        from flask import has_request_context, request
    except ImportError:
        return [(default_no, default_amount)]

    if not has_request_context():
        return [(default_no, default_amount)]

    numbers = request.form.getlist("medium_no")
    amounts = request.form.getlist("medium")
    if not numbers and not amounts:
        return [(default_no, default_amount)]

    pairs = []
    row_count = max(len(numbers), len(amounts))
    for index in range(row_count):
        number_text = numbers[index].strip() if index < len(numbers) else ""
        amount_text = amounts[index].strip() if index < len(amounts) else ""

        if not number_text and not amount_text:
            continue

        try:
            number = int(number_text or "0")
            amount = float(amount_text or "0")
        except ValueError as error:
            raise ValueError("中力粉の番号と量を正しく入力してください。") from error
        pairs.append((number, amount))

    return pairs or [(0, 0)]


def _add_component(components, kind, number, amount):
    number = int(number or 0)
    amount = float(amount or 0)

    if number == 0 and amount == 0:
        return
    if number <= 0:
        raise ValueError(f"{kind}を使用する場合は銘柄を選択してください。")
    if amount <= 0:
        raise ValueError(f"{kind}を使用する場合は粉量を0より大きくしてください。")

    components.append({"kind": kind, "number": number, "amount": amount})


def _merge_duplicate_components(components):
    """同じ銘柄を複数行で選んだ場合は量を合算する。"""
    merged = []
    positions = {}

    for item in components:
        key = (item["kind"], item["number"])
        if key in positions:
            merged[positions[key]]["amount"] += item["amount"]
            continue
        positions[key] = len(merged)
        merged.append(dict(item))

    return merged


def _validate_components(conn, components):
    for item in components:
        flour = conn.execute(
            "SELECT id, name FROM flours WHERE kind = ? AND number = ?",
            (item["kind"], item["number"]),
        ).fetchone()
        if flour is None:
            raise ValueError(
                f"{item['kind']} No.{item['number']} は粉銘柄マスターに登録されていません。"
            )
        item["flour_id"] = flour["id"]
        item["name"] = flour["name"]


def save_recipe(
    weak_no, medium_no, strong_no, weak, medium, strong, hydration, salt_percent
):
    """旧8引数を保ったまま、Web版では中力粉の複数行も保存する。"""
    initialize_database()

    hydration = float(hydration)
    salt_percent = float(salt_percent)
    if not 0 < hydration <= 100:
        raise ValueError("加水率は0より大きく100以下で入力してください。")
    if not 0 <= salt_percent <= 30:
        raise ValueError("塩分濃度は0〜30%で入力してください。")

    components = []
    _add_component(components, "薄力粉", weak_no, weak)

    for number, amount in _form_medium_pairs(medium_no, medium):
        _add_component(components, "中力粉", number, amount)

    _add_component(components, "強力粉", strong_no, strong)

    components = _merge_duplicate_components(components)
    if not components:
        raise ValueError("少なくとも1種類の小麦粉を使用してください。")

    weak_components = [item for item in components if item["kind"] == "薄力粉"]
    medium_components = [item for item in components if item["kind"] == "中力粉"]
    strong_components = [item for item in components if item["kind"] == "強力粉"]

    if len(weak_components) > 1:
        raise ValueError("薄力粉は1種類まで登録できます。")
    if len(strong_components) > 1:
        raise ValueError("強力粉は1種類まで登録できます。")

    legacy_weak_no = weak_components[0]["number"] if weak_components else 0
    legacy_weak = weak_components[0]["amount"] if weak_components else 0.0
    legacy_medium_no = medium_components[0]["number"] if medium_components else 0
    legacy_medium = sum(item["amount"] for item in medium_components)
    legacy_strong_no = strong_components[0]["number"] if strong_components else 0
    legacy_strong = strong_components[0]["amount"] if strong_components else 0.0

    with get_connection() as conn:
        _validate_components(conn, components)

        cursor = conn.execute(
            """
            INSERT INTO recipes(
                weak_no, medium_no, strong_no,
                weak, medium, strong, hydration, salt_percent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                legacy_weak_no,
                legacy_medium_no,
                legacy_strong_no,
                legacy_weak,
                legacy_medium,
                legacy_strong,
                hydration,
                salt_percent,
            ),
        )
        recipe_id = cursor.lastrowid

        # 固定列しか見ない旧画面にも「複数の中力粉」と分かるよう、
        # -配合ID を互換用マーカーとして使う。実データは recipe_flours が正。
        if len(medium_components) > 1:
            conn.execute(
                "UPDATE recipes SET medium_no = ? WHERE id = ?",
                (-recipe_id, recipe_id),
            )

        for sort_order, item in enumerate(components):
            conn.execute(
                """
                INSERT INTO recipe_flours(
                    recipe_id, flour_id, amount, sort_order
                ) VALUES (?, ?, ?, ?)
                """,
                (recipe_id, item["flour_id"], item["amount"], sort_order),
            )

    return recipe_id


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
