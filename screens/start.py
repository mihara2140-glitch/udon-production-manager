import tkinter as tk
from datetime import date

from services.recipe_service import show_recipe_list
from services.seimen_service import save_start_data


def open_start_window(parent):

    recipe_text = show_recipe_list()
    new_window = tk.Toplevel(parent)
    new_window.title("製麺開始")
    new_window.geometry("750x500")

    tk.Label(new_window, text="日付").grid(
        row=0, column=0, padx=10, pady=10, sticky="w"
    )

    today = date.today().strftime("%Y-%m-%d")  # noqa: DTZ011

    date_entry = tk.Entry(new_window)

    date_entry.insert(0, today)

    date_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(new_window, text="気温").grid(
        row=1, column=0, padx=10, pady=10, sticky="w"
    )

    temp_entry = tk.Entry(new_window)

    temp_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(new_window, text="湿度").grid(
        row=2, column=0, padx=10, pady=10, sticky="w"
    )

    humidity_entry = tk.Entry(new_window)

    humidity_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(new_window, text="配合番号").grid(
        row=3, column=0, padx=10, pady=10, sticky="w"
    )

    recipe_entry = tk.Entry(new_window)

    recipe_entry.grid(row=3, column=1, padx=10, pady=10)

    recipe_box = tk.Text(new_window, width=45, height=25)
    recipe_box.grid(row=0, column=2, rowspan=6, padx=20, pady=10)
    recipe_box.insert("1.0", recipe_text)
    recipe_box.configstate = "disabled"

    scrollbar = tk.Scrollbar(new_window, command=recipe_box.yview)
    scrollbar.grid(row=0, column=3, rowspan=6, sticky="ns")
    recipe_box.config(yscrollcommand=scrollbar.set)

    tk.Button(
        new_window,
        text="保存",
        command=lambda: save_start_data(
            recipe_entry, date_entry, temp_entry, humidity_entry, new_window
        ),
    ).grid(row=6, column=0, pady=10)

    tk.Button(new_window, text="閉じる", command=new_window.destroy).grid(
        row=6, column=1, pady=10
    )
