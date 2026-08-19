import tkinter as tk
from tkinter import ttk

from services.recipe_service import (
    calc_salt,
    calc_water,
    get_flour_list,
    get_last_recipe,
    save_recipe,
)


def open_recipe_calc_window(parent):
    data = get_last_recipe()

    new_window = tk.Toplevel(parent)
    new_window.title("配合計算")
    new_window.geometry("800x600")

    weak_list = get_flour_list("薄力粉")
    weak_combo = ttk.Combobox(
        new_window,
        values=[f"{number}: {name}" for number, name in weak_list],
        state="readonly",
    )
    weak_combo.grid(row=0, column=1, padx=10, pady=10)

    last_weak_no = int(data[0])

    for i, (number, name) in enumerate(weak_list):
        if number == last_weak_no:
            weak_combo.current(i)
            break

    medium_list = get_flour_list("中力粉")
    medium_combo = ttk.Combobox(
        new_window,
        values=[f"{number}:{name}" for number, name in medium_list],
        state="readonly",
    )
    medium_combo.grid(row=1, column=1, padx=10, pady=10)

    last_medium_no = int(data[1])

    for i, (number, name) in enumerate(medium_list):
        if number == last_medium_no:
            medium_combo.current(i)
            break

    strong_list = get_flour_list("強力粉")
    strong_combo = ttk.Combobox(
        new_window,
        values=[f"{number}:{name}" for number, name in strong_list],
        state="readonly",
    )
    strong_combo.grid(row=2, column=1, padx=10, pady=10)

    last_strong_no = int(data[2])

    for i, (number, name) in enumerate(strong_list):
        if number == last_strong_no:
            strong_combo.current(i)
            break

    weak_entry = tk.Entry(new_window)
    weak_entry.insert(0, data[3])
    weak_entry.grid(row=0, column=2, padx=10, pady=10)

    medium_entry = tk.Entry(new_window)
    medium_entry.insert(0, data[4])
    medium_entry.grid(row=1, column=2, padx=10, pady=10)

    strong_entry = tk.Entry(new_window)
    strong_entry.insert(0, data[5])
    strong_entry.grid(row=2, column=2, padx=10, pady=10)

    tk.Label(new_window, text="加水率").grid(row=3, column=1, padx=10, pady=10)
    hydration_entry = tk.Entry(new_window)
    hydration_entry.insert(0, data[6])
    hydration_entry.grid(row=3, column=2, padx=10, pady=10)

    tk.Label(new_window, text="塩分濃度").grid(row=4, column=1, padx=10, pady=10)
    salt_entry = tk.Entry(new_window)
    salt_entry.insert(0, data[7])
    salt_entry.grid(row=4, column=2, padx=10, pady=10)

    def calculate():
        weak = float(weak_entry.get())
        medium = float(medium_entry.get())
        strong = float(strong_entry.get())

        flour = weak + medium + strong

        hydration = float(hydration_entry.get())
        salt_percent = float(salt_entry.get())

        water = calc_water(flour, hydration)
        salt = calc_salt(water, salt_percent)

        result_label.config(
            text=(
                f"総粉量：{flour:.1f}g\n必要な水：{water:.2f}g\n必要な塩：{salt:.2f}g"
            )
        )

    def save():
        weak_no = int(weak_combo.get().split(":")[0])
        medium_no = int(medium_combo.get().split(":")[0])
        strong_no = int(strong_combo.get().split(":")[0])

        weak = float(weak_entry.get())
        medium = float(medium_entry.get())
        strong = float(strong_entry.get())

        hydration = float(hydration_entry.get())
        salt_percent = float(salt_entry.get())

        save_recipe(
            weak_no, medium_no, strong_no, weak, medium, strong, hydration, salt_percent
        )

    result_label = tk.Label(new_window, text="")
    result_label.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    tk.Button(new_window, text="計算", command=calculate).grid(
        row=7, column=0, padx=10, pady=10
    )

    tk.Button(new_window, text="保存", command=save).grid(
        row=8, column=0, padx=10, pady=10
    )
