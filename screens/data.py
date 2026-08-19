import tkinter as tk

from services.seimen_service import show_data


def open_data_window(parent):
    data_text = show_data()

    new_window = tk.Toplevel(parent)
    new_window.title("データを見る")
    new_window.geometry("800x600")

    text = tk.Text(new_window, width=80, height=30)
    text.insert("1.0", data_text)
    text.pack(padx=10, pady=10)

    tk.Button(new_window, text="閉じる", command=new_window.destroy).pack(pady=5)
