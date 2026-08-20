import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from services.recipe_service import show_recipe_list
from services.seimen_service import save_start_data


def open_start_window(parent):
    recipe_text = show_recipe_list()

    new_window = tk.Toplevel(parent)
    new_window.title("製麺開始 - Ver.22")
    new_window.geometry("900x560")
    new_window.minsize(820, 520)

    style = ttk.Style(new_window)
    style.configure("Title.TLabel", font=("Meiryo", 18, "bold"))
    style.configure("Primary.TButton", font=("Meiryo", 11, "bold"), padding=8)

    outer = ttk.Frame(new_window, padding=18)
    outer.pack(fill="both", expand=True)

    ttk.Label(outer, text="今日の製麺を開始", style="Title.TLabel").pack(anchor="w")
    ttk.Label(
        outer,
        text="開始時点で分かる環境と配合を記録します。熟成時間は製麺終了時に実績を入力します。",
    ).pack(anchor="w", pady=(4, 14))

    body = ttk.Frame(outer)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)
    body.rowconfigure(0, weight=1)

    input_card = ttk.LabelFrame(body, text=" 製麺条件 ", padding=16)
    input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    input_card.columnconfigure(1, weight=1)

    recipe_card = ttk.LabelFrame(body, text=" 配合一覧 ", padding=12)
    recipe_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    recipe_card.rowconfigure(0, weight=1)
    recipe_card.columnconfigure(0, weight=1)

    fields = [
        ("日付", date.today().strftime("%Y-%m-%d")),
        ("気温（℃）", ""),
        ("湿度（%）", ""),
        ("配合番号", ""),
    ]

    entries = {}
    for row, (label, default) in enumerate(fields):
        ttk.Label(input_card, text=label).grid(
            row=row, column=0, sticky="w", padx=(0, 12), pady=10
        )
        entry = ttk.Entry(input_card, width=24)
        entry.grid(row=row, column=1, sticky="ew", pady=10)
        if default:
            entry.insert(0, default)
        entries[label] = entry

    ttk.Separator(input_card).grid(
        row=len(fields), column=0, columnspan=2, sticky="ew", pady=18
    )

    ttk.Label(
        input_card,
        text="熟成時間は、実際に終了したタイミングで記録します。",
        foreground="#555555",
        wraplength=320,
    ).grid(row=len(fields) + 1, column=0, columnspan=2, sticky="w")

    recipe_box = tk.Text(
        recipe_card,
        width=48,
        height=22,
        wrap="word",
        font=("Meiryo", 10),
        relief="flat",
        padx=8,
        pady=8,
    )
    recipe_box.grid(row=0, column=0, sticky="nsew")
    recipe_box.insert("1.0", recipe_text)
    recipe_box.config(state="disabled")

    scrollbar = ttk.Scrollbar(recipe_card, command=recipe_box.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    recipe_box.config(yscrollcommand=scrollbar.set)

    buttons = ttk.Frame(outer)
    buttons.pack(fill="x", pady=(16, 0))

    def save():
        try:
            save_start_data(
                entries["配合番号"],
                entries["日付"],
                entries["気温（℃）"],
                entries["湿度（%）"],
                new_window,
            )
            messagebox.showinfo("保存完了", "製麺を開始しました。", parent=parent)
        except (ValueError, IndexError) as error:
            messagebox.showerror("入力エラー", str(error), parent=new_window)

    ttk.Button(buttons, text="製麺を開始", command=save, style="Primary.TButton").pack(
        side="left"
    )
    ttk.Button(buttons, text="閉じる", command=new_window.destroy).pack(side="right")
