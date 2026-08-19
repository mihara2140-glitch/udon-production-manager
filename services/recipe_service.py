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
