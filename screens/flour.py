import tkinter as tk

from services.recipe_service import show_flour_list


def open_flour_window(parent):
    flour_text = show_flour_list()
    new_window = tk.Toplevel(parent)
    new_window.title("粉銘柄一覧")
    new_window.geometry("700x600")

    text = tk.Text(new_window, width=70, height=30)

    text.insert("1.0", flour_text)
    text.config(state="disabled")
    text.pack(padx=10, pady=10)

    tk.Button(new_window, text="閉じる", command=new_window.destroy).pack(padx=5)
