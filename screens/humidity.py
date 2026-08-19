import tkinter as tk

from services.seimen_service import show_high_humidity


def open_humidity_window(parent):
    humidity_text = show_high_humidity()

    new_window = tk.Toplevel(parent)

    new_window.title("湿度７０％以上")
    new_window.geometry("800x600")

    text = tk.Text(new_window, width=80, height=30)
    text.insert("1.0", humidity_text)
    text.pack(padx=10, pady=10)

    tk.Button(new_window, text="閉じる", command=new_window.destroy).pack(pady=5)
