import tkinter as tk

from services.seimen_service import save_finish_data, show_working_list


def open_finish_window(parent):

    working_text = show_working_list()
    new_window = tk.Toplevel(parent)
    new_window.title("製麺終了")
    new_window.geometry("500x500")

    tk.Label(new_window, text=working_text, justify="left").grid(
        row=0, column=2, rowspan=6, padx=20, pady=10, sticky="nw"
    )

    tk.Label(new_window, text="製麺番号").grid(
        row=1, column=0, padx=10, pady=10, sticky="w"
    )

    seimen_entry = tk.Entry(new_window)

    seimen_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(new_window, text="茹で時間").grid(
        row=2, column=0, padx=10, pady=10, sticky="w"
    )

    boil_entry = tk.Entry(new_window)

    boil_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(new_window, text="感想").grid(
        row=3, column=0, padx=10, pady=10, sticky="w"
    )

    comment = tk.Text(new_window, width=45, height=8)

    comment.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    tk.Button(
        new_window,
        text="保存",
        command=lambda: save_finish_data(seimen_entry, boil_entry, comment, new_window),
    ).grid(row=5, column=0, pady=10)

    tk.Button(new_window, text="閉じる", command=new_window.destroy).grid(
        row=5, column=1, pady=10
    )
