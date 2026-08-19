import tkinter as tk
from tkinter import ttk

from services.recipe_service import save_flour


def open_flour_register_window(parent):

    new_window = tk.Toplevel(parent)
    new_window.title("粉銘柄登録")
    new_window.geometry("500x400")

    tk.Label(new_window, text="種類").grid(
        row=0, column=0, padx=10, pady=10, sticky="w"
    )

    kind_combo = ttk.Combobox(
        new_window, values=["薄力粉", "中力粉", "強力粉"], state="rearonly"
    )

    kind_combo.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(new_window, text="番号").grid(
        row=1, column=0, padx=10, pady=10, sticky="w"
    )
    number_entry = tk.Entry(new_window)
    number_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(new_window, text="銘柄").grid(
        row=2, column=0, padx=10, pady=10, sticky="w"
    )

    name_entry = tk.Entry(new_window)
    name_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(new_window, text="特徴").grid(
        row=3, column=0, padx=10, pady=10, sticky="w"
    )

    feature_entry = tk.Entry(new_window)
    feature_entry.grid(row=3, column=1, padx=10, pady=10)

    def save():
        kind = kind_combo.get()
        number = int(number_entry.get())
        name = name_entry.get()
        feature = feature_entry.get()

        save_flour(kind, number, name, feature)

        print("保存しました")

    tk.Button(new_window, text="保存", command=save).grid(row=4, column=0, pady=10)

    tk.Button(new_window, text="閉じる", command=new_window.destroy).grid(
        row=4, column=1, pady=10
    )
