import csv

from services.recipe_service import get_flour_name, get_recipe


def save_start_data(recipe_entry, date_entry, temp_entry, humidity_entry, new_window):

    recipe_no = recipe_entry.get()
    date = date_entry.get()
    temp = temp_entry.get()
    humidity = humidity_entry.get()

    print(recipe_no)
    print(date)
    print(temp)
    print(humidity)

    with open("data/udon_note.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    seimen_no = len(lines)
    state = "作業中"

    with open("data/udon_note.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([seimen_no, recipe_no, date, temp, humidity, "", "", state])

    print("保存しました")

    new_window.destroy()


def show_working_list():

    with open("data/udon_note.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    text = "===作業中一覧===\n\n"

    for line in lines[1:]:
        data = line.strip().split(",")

        if data[7] == "作業中":
            recipe_no = int(data[1])

            recipe = get_recipe(recipe_no)

            # 銘柄取得
            weak_name = get_flour_name("薄力粉", int(recipe[0]))
            medium_name = get_flour_name("中力粉", int(recipe[1]))
            strong_name = get_flour_name("強力粉", int(recipe[2]))

            # 配合データ取得
            weak = float(recipe[3])
            medium = float(recipe[4])
            strong = float(recipe[5])

            # 文字列を作成
            text += "=========================\n"
            text += f"製麺番号：{data[0]}\n"
            text += f"日付：{data[2]}\n"
            text += f"配合番号：{recipe_no}\n"

            text += "【配合】\n"
            text += f"薄力粉：{weak}g({weak_name})\n"
            text += f"中力粉：{medium}g({medium_name})\n"
            text += f"強力粉：{strong}g({strong_name})\n"
            text += f"加水率：{recipe[6]}%\n"
            text += f"塩分濃度：{recipe[7]}%\n"

            text += f"状態：{data[7]}\n"
            text += "--------------------------\n\n"

    return text


def save_finish_data(seimen_entry, boil_entry, comment, new_window):
    seimen_no = int(seimen_entry.get())
    boil = boil_entry.get()
    memo = comment.get("1.0", "end").strip()
    memo = memo.replace("\n", "/")

    with open("data/udon_note.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    for i, line in enumerate(lines[1:], start=1):
        data = line.strip().split(",")

        if data[7] == "作業中" and int(data[0]) == seimen_no:
            state = "完了"

            new_line = (
                f"{data[0]},{data[1]},{data[2]},"
                f"{data[3]},{data[4]},{boil},"
                f"{memo},{state}\n"
            )

            lines[i] = new_line
            break

    with open("data/udon_note.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for line in lines:
            writer.writerow(line.strip().split(","))

    print("保存しました")

    new_window.destroy()


def show_data():

    with open("data/udon_note.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    text = "===製麺記録===\n\n"

    for line in lines[1:]:
        data = line.strip().split(",")
        recipe_no = int(data[1])
        recipe = get_recipe(recipe_no)

        weak_name = get_flour_name("薄力粉", int(recipe[0]))
        medium_name = get_flour_name("中力粉", int(recipe[1]))
        strong_name = get_flour_name("強力粉", int(recipe[2]))

        text += "=====================\n"
        text += f"製麺番号：{data[0]}\n"
        text += f"配合番号：{data[1]}\n"
        text += "【配合】\n"
        text += f"薄力粉：{recipe[3]}g（{weak_name}）\n"
        text += f"中力粉：{recipe[4]}g（{medium_name}）\n"
        text += f"強力粉：{recipe[5]}g（{strong_name}）\n"
        text += f"加水率：{recipe[6]}%\n"
        text += f"塩分濃度：{recipe[7]}%\n"
        text += f"日付：{data[2]}\n"
        text += f"気温：{data[3]}℃\n"
        text += f"湿度：{data[4]}%\n"
        text += f"茹で時間：{data[5]}\n"
        text += f"感想：{data[6]}\n"
        text += f"状態：{data[7]}\n"
        text += "--------------------\n"

    return text


def show_high_humidity():

    with open("data/udon_note.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    text = "===湿度７０％以上===\n\n"

    for line in lines[1:]:
        data = line.strip().split(",")
        humidity = int(data[4])

        recipe_no = int(data[1])
        recipe = get_recipe(recipe_no)

        weak_name = get_flour_name("薄力粉", int(recipe[0]))
        medium_name = get_flour_name("中力粉", int(recipe[1]))
        strong_name = get_flour_name("強力粉", int(recipe[2]))

        if humidity >= 70:
            text += "=====================\n"
            text += f"製麺番号：{data[0]}\n"
            text += f"配合番号：{data[1]}\n"
            text += "【配合】\n"
            text += f"薄力粉：{recipe[3]}g（{weak_name}）\n"
            text += f"中力粉：{recipe[4]}g（{medium_name}）\n"
            text += f"強力粉：{recipe[5]}g（{strong_name}）\n"
            text += f"加水率：{recipe[6]}%\n"
            text += f"塩分濃度：{recipe[7]}%\n"
            text += f"日付：{data[2]}\n"
            text += f"気温：{data[3]}℃\n"
            text += f"湿度：{data[4]}%\n"
            text += f"茹で時間：{data[5]}\n"
            text += f"感想：{data[6]}\n"
            text += f"状態：{data[7]}\n"
            text += "--------------------\n"

    return text
