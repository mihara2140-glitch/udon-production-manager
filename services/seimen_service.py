import csv
from pathlib import Path

from services.recipe_service import get_flour_name, get_recipe

DATA_FILE = Path("data/udon_note.csv")

HEADER = [
    "製麺番号",
    "配合番号",
    "日付",
    "気温",
    "湿度",
    "常温熟成時間",
    "冷蔵熟成時間",
    "茹で時間",
    "総合評価",
    "ツル感",
    "モチ感",
    "コシ",
    "のど越し",
    "くっつき",
    "タレとの相性",
    "感想",
    "状態",
]


def _normalize_row(row):
    """Ver.19以前の8列データをVer.20の17列形式に変換する。"""
    if len(row) >= len(HEADER):
        return row[: len(HEADER)]

    if len(row) >= 8:
        # 旧形式:
        # 製麺番号, 配合番号, 日付, 気温, 湿度, 茹で時間, 感想, 状態
        return [
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            "",
            "",
            row[5],
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            row[6],
            row[7],
        ]

    return row + [""] * (len(HEADER) - len(row))


def ensure_ver20_format():
    """CSVをVer.20形式へ安全に揃える。既存データは保持する。"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(HEADER)
        return

    with DATA_FILE.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    if not rows:
        rows = [HEADER]
    else:
        old_rows = rows[1:]
        rows = [HEADER] + [_normalize_row(row) for row in old_rows if row]

    with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
        csv.writer(file).writerows(rows)


def _read_rows():
    ensure_ver20_format()
    with DATA_FILE.open("r", newline="", encoding="utf-8") as file:
        return list(csv.reader(file))


def _write_rows(rows):
    with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
        csv.writer(file).writerows(rows)


def save_start_data(
    recipe_entry,
    date_entry,
    temp_entry,
    humidity_entry,
    room_maturation_entry,
    cold_maturation_entry,
    new_window,
):
    recipe_no = recipe_entry.get().strip()
    record_date = date_entry.get().strip()
    temp = temp_entry.get().strip()
    humidity = humidity_entry.get().strip()
    room_maturation = room_maturation_entry.get().strip()
    cold_maturation = cold_maturation_entry.get().strip()

    if not recipe_no:
        raise ValueError("配合番号を入力してください。")

    rows = _read_rows()
    seimen_no = len(rows)

    rows.append(
        [
            seimen_no,
            recipe_no,
            record_date,
            temp,
            humidity,
            room_maturation,
            cold_maturation,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "作業中",
        ]
    )
    _write_rows(rows)
    new_window.destroy()


def show_working_list():
    rows = _read_rows()
    text = "=== 作業中の製麺 ===\n\n"
    found = False

    for data in rows[1:]:
        if data[16] != "作業中":
            continue

        found = True
        recipe_no = int(data[1])
        recipe = get_recipe(recipe_no)

        weak_name = get_flour_name("薄力粉", int(recipe[0]))
        medium_name = get_flour_name("中力粉", int(recipe[1]))
        strong_name = get_flour_name("強力粉", int(recipe[2]))

        text += f"製麺番号：{data[0]}\n"
        text += f"日付：{data[2]}\n"
        text += f"気温 / 湿度：{data[3]}℃ / {data[4]}%\n"
        text += f"常温熟成：{data[5] or '-'}\n"
        text += f"冷蔵熟成：{data[6] or '-'}\n"
        text += f"配合番号：{recipe_no}\n"
        text += (
            f"薄力 {recipe[3]}g（{weak_name}） / "
            f"中力 {recipe[4]}g（{medium_name}） / "
            f"強力 {recipe[5]}g（{strong_name}）\n"
        )
        text += f"加水率 {recipe[6]}% / 塩分濃度 {recipe[7]}%\n"
        text += "─" * 38 + "\n\n"

    if not found:
        text += "現在、作業中の製麺はありません。\n"

    return text


def save_finish_data(
    seimen_entry,
    boil_entry,
    evaluation_entries,
    comment,
    new_window,
):
    seimen_no = int(seimen_entry.get().strip())
    boil = boil_entry.get().strip()
    memo = comment.get("1.0", "end").strip().replace("\n", " / ")

    scores = {}
    for key, entry in evaluation_entries.items():
        value = entry.get().strip()
        if value:
            score = int(value)
            if not 1 <= score <= 10:
                raise ValueError(f"{key}は1〜10で入力してください。")
            scores[key] = str(score)
        else:
            scores[key] = ""

    rows = _read_rows()
    target_found = False

    for data in rows[1:]:
        if int(data[0]) == seimen_no and data[16] == "作業中":
            data[7] = boil
            data[8] = scores["総合評価"]
            data[9] = scores["ツル感"]
            data[10] = scores["モチ感"]
            data[11] = scores["コシ"]
            data[12] = scores["のど越し"]
            data[13] = scores["くっつき"]
            data[14] = scores["タレとの相性"]
            data[15] = memo
            data[16] = "完了"
            target_found = True
            break

    if not target_found:
        raise ValueError("指定した作業中の製麺番号が見つかりません。")

    _write_rows(rows)
    new_window.destroy()


def show_data():
    rows = _read_rows()
    text = "=== 製麺記録 ===\n\n"

    for data in reversed(rows[1:]):
        recipe_no = int(data[1])
        recipe = get_recipe(recipe_no)

        weak_name = get_flour_name("薄力粉", int(recipe[0]))
        medium_name = get_flour_name("中力粉", int(recipe[1]))
        strong_name = get_flour_name("強力粉", int(recipe[2]))

        text += f"製麺番号：{data[0]}　状態：{data[16]}\n"
        text += f"日付：{data[2]}　気温：{data[3]}℃　湿度：{data[4]}%\n"
        text += f"常温熟成：{data[5] or '-'}　冷蔵熟成：{data[6] or '-'}\n"
        text += f"配合番号：{data[1]}\n"
        text += (
            f"薄力 {recipe[3]}g（{weak_name}） / "
            f"中力 {recipe[4]}g（{medium_name}） / "
            f"強力 {recipe[5]}g（{strong_name}）\n"
        )
        text += f"加水率：{recipe[6]}%　塩分濃度：{recipe[7]}%\n"
        text += f"茹で時間：{data[7] or '-'}\n"

        if data[16] == "完了":
            text += (
                f"評価：総合 {data[8] or '-'} / ツル {data[9] or '-'} / "
                f"モチ {data[10] or '-'} / コシ {data[11] or '-'} / "
                f"のど越し {data[12] or '-'} / くっつき {data[13] or '-'} / "
                f"タレ {data[14] or '-'}\n"
            )
            text += f"感想：{data[15] or '-'}\n"

        text += "─" * 48 + "\n\n"

    return text


def show_high_humidity():
    rows = _read_rows()
    text = "=== 湿度70%以上の記録 ===\n\n"
    found = False

    for data in rows[1:]:
        if not data[4]:
            continue

        try:
            humidity = float(data[4])
        except ValueError:
            continue

        if humidity < 70:
            continue

        found = True
        recipe_no = int(data[1])
        recipe = get_recipe(recipe_no)

        text += f"製麺番号：{data[0]}　日付：{data[2]}\n"
        text += f"気温：{data[3]}℃　湿度：{data[4]}%\n"
        text += f"常温熟成：{data[5] or '-'}　冷蔵熟成：{data[6] or '-'}\n"
        text += f"加水率：{recipe[6]}%　塩分濃度：{recipe[7]}%\n"
        text += f"くっつき評価：{data[13] or '-'}\n"
        text += f"感想：{data[15] or '-'}\n"
        text += "─" * 38 + "\n\n"

    if not found:
        text += "該当する記録はありません。\n"

    return text
