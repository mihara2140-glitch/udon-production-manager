import csv


def get_recipe(recipe_no):
    with open("data/recipe.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    # recipe_noの行を取得
    line = lines[recipe_no]

    data = line.strip().split(",")

    return data


def get_flour_name(kind, number):
    with open("data/flour_master.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines[1:]:
        data = line.strip().split(",")

        if kind == data[0] and number == int(data[1]):
            return data[2]

    return "未登録"


def show_recipe_list():

    with open("data/recipe.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    text = "===配合一覧===\n\n"

    for i, line in enumerate(lines[1:], start=1):
        text += f"【{i}】\n"

        data = line.strip().split(",")

        # 銘柄取得
        weak_name = get_flour_name("薄力粉", int(data[0]))
        medium_name = get_flour_name("中力粉", int(data[1]))
        strong_name = get_flour_name("強力粉", int(data[2]))

        # 配合データ取得
        weak = float(data[3])
        medium = float(data[4])
        strong = float(data[5])
        hydration = float(data[6])
        salt_percent = float(data[7])

        # 配合データ表示
        text += f"薄力粉：{weak}g({weak_name})\n"
        text += f"中力粉：{medium}g({medium_name})\n"
        text += f"強力粉：{strong}g({strong_name})\n"
        text += f"加水率：{hydration}%\n"
        text += f"塩分濃度：{salt_percent}%\n"
        text += "-------------\n"

    return text


def get_flour_list(kind):
    with open("data/flour_master.csv", "r", encoding="utf=8") as file:
        lines = file.readlines()

    flour_list = []

    for line in lines[1:]:
        data = line.strip().split(",")

        if data[0] == kind:
            flour_list.append((int(data[1]), data[2]))

    return flour_list


def calc_water(flour, hydration):
    return flour * hydration / 100


def calc_salt(water, salt_percent):
    return water * salt_percent / 100


def get_last_recipe():

    with open("data/recipe.csv", "r", encoding="utf=8") as file:
        lines = file.readlines()

    last_line = lines[-1]
    data = last_line.strip().split(",")

    return data


def save_recipe(
    weak_no, medium_no, strong_no, weak, medium, strong, hydration, salt_percent
):

    with open("data/recipe.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                weak_no,
                medium_no,
                strong_no,
                weak,
                medium,
                strong,
                hydration,
                salt_percent,
            ]
        )


def show_recipe_history():

    with open("data/recipe.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    text = "===配合履歴===\n\n"

    for line in lines[1:]:
        data = line.strip().split(",")

        weak_name = get_flour_name("薄力粉", int(data[0]))
        medium_name = get_flour_name("中力粉", int(data[1]))
        strong_name = get_flour_name("強力粉", int(data[2]))

        weak = float(data[3])
        medium = float(data[4])
        strong = float(data[5])

        hydration = float(data[6])
        salt_percent = float(data[7])

        flour = weak + medium + strong

        water = calc_water(flour, hydration)
        salt = calc_salt(water, salt_percent)

        text += "======================\n"
        text += "【配合】\n"
        text += f"薄力粉：{data[3]}g({weak_name})\n"
        text += f"中力粉：{data[4]}g({medium_name})\n"
        text += f"強力粉：{data[5]}g({strong_name})\n"
        text += f"加水率：{data[6]}%\n"
        text += f"必要な水：{water:.2f}g\n"
        text += f"塩分濃度：{data[7]}%\n"
        text += f"必要な塩：{salt:.2f}g\n"
        text += "----------------------\n\n"

    return text


def show_flour_list():

    with open("data/flour_master.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    text = "===粉銘柄一覧===\n\n"

    for line in lines[1:]:
        data = line.strip().split(",")

        if len(data) < 4:
            continue

        text += "====================\n"
        text += f"種類：{data[0]}\n"
        text += f"番号：{int(data[1])}\n"
        text += f"銘柄：{data[2]}\n"
        text += f"特徴：{data[3]}\n"
        text += "--------------------\n"

    return text


def save_flour(kind, number, name, feature):

    with open("data/flour_master.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([kind, number, name, feature])


def search_recipe(recipe_no):
    with open("data/udon_note.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()

    text = f"===配合{recipe_no}を使った製麺記録===\n\n"

    found = False

    for line in lines[1:]:
        data = line.strip().split(",")

        if int(data[1]) == recipe_no:
            found = True

            text += "=====================\n"
            text += f"製麺番号：{data[0]}\n"
            text += f"日付：{data[2]}\n"
            text += f"気温：{data[3]}℃\n"
            text += f"湿度：{data[4]}%\n"
            text += f"茹で時間：{data[5]}\n"
            text += f"感想：{data[6]}\n"
            text += f"状態：{data[7]}\n"
            text += "---------------------\n"

    if not found:
        text += "該当する製麺記録がありません。\n"

    return text
