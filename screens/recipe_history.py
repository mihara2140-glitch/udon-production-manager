import tkinter as tk

from services.recipe_service import show_recipe_history


def open_recipe_history_window(parent):

    history_text = show_recipe_history()

    new_window = tk.Toplevel(parent)

    new_window.title("配合履歴")
    new_window.geometry("800x600")

    text = tk.Text(new_window, width=80, height=30)
    text.insert("1.0", history_text)
    text.pack(padx=10, pady=10)

    tk.Button(new_window, text="閉じる", command=new_window.destroy).pack(pady=5)
