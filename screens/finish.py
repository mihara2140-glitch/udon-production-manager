import tkinter as tk
from tkinter import messagebox, ttk

from services.seimen_service import save_finish_data, show_working_list


def open_finish_window(parent):
    working_text = show_working_list()

    new_window = tk.Toplevel(parent)
    new_window.title("製麺終了 - Ver.20")
    new_window.geometry("980x680")
    new_window.minsize(900, 620)

    style = ttk.Style(new_window)
    style.configure("Title.TLabel", font=("Meiryo", 18, "bold"))
    style.configure("Section.TLabel", font=("Meiryo", 11, "bold"))
    style.configure("Primary.TButton", font=("Meiryo", 11, "bold"), padding=8)

    outer = ttk.Frame(new_window, padding=18)
    outer.pack(fill="both", expand=True)

    ttk.Label(outer, text="製麺を終了して評価を記録", style="Title.TLabel").pack(anchor="w")
    ttk.Label(
        outer,
        text="食感や扱いやすさを1〜10で記録すると、今後の分析に使えます。",
    ).pack(anchor="w", pady=(4, 14))

    body = ttk.Frame(outer)
    body.pack(fill="both", expand=True)
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)
    body.rowconfigure(0, weight=1)

    input_card = ttk.LabelFrame(body, text=" 終了記録 ", padding=16)
    input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    input_card.columnconfigure(1, weight=1)

    working_card = ttk.LabelFrame(body, text=" 作業中の製麺 ", padding=12)
    working_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    working_card.rowconfigure(0, weight=1)
    working_card.columnconfigure(0, weight=1)

    ttk.Label(input_card, text="製麺番号").grid(row=0, column=0, sticky="w", pady=6)
    seimen_entry = ttk.Entry(input_card, width=16)
    seimen_entry.grid(row=0, column=1, sticky="ew", pady=6)

    ttk.Label(input_card, text="茹で時間").grid(row=1, column=0, sticky="w", pady=6)
    boil_entry = ttk.Entry(input_card, width=16)
    boil_entry.grid(row=1, column=1, sticky="ew", pady=6)

    ttk.Separator(input_card).grid(row=2, column=0, columnspan=2, sticky="ew", pady=12)
    ttk.Label(input_card, text="評価（1〜10）", style="Section.TLabel").grid(
        row=3, column=0, columnspan=2, sticky="w", pady=(0, 6)
    )

    evaluation_labels = [
        "総合評価",
        "ツル感",
        "モチ感",
        "コシ",
        "のど越し",
        "くっつき",
        "タレとの相性",
    ]

    evaluation_entries = {}
    for index, label in enumerate(evaluation_labels, start=4):
        ttk.Label(input_card, text=label).grid(row=index, column=0, sticky="w", pady=4)
        spinbox = ttk.Spinbox(input_card, from_=1, to=10, width=8)
        spinbox.grid(row=index, column=1, sticky="w", pady=4)
        evaluation_entries[label] = spinbox

    memo_row = 4 + len(evaluation_labels)
    ttk.Label(input_card, text="感想・メモ", style="Section.TLabel").grid(
        row=memo_row, column=0, columnspan=2, sticky="w", pady=(14, 6)
    )

    comment = tk.Text(
        input_card,
        width=44,
        height=7,
        wrap="word",
        font=("Meiryo", 10),
        padx=8,
        pady=8,
    )
    comment.grid(row=memo_row + 1, column=0, columnspan=2, sticky="nsew")

    working_box = tk.Text(
        working_card,
        width=50,
        height=30,
        wrap="word",
        font=("Meiryo", 10),
        relief="flat",
        padx=8,
        pady=8,
    )
    working_box.grid(row=0, column=0, sticky="nsew")
    working_box.insert("1.0", working_text)
    working_box.config(state="disabled")

    scrollbar = ttk.Scrollbar(working_card, command=working_box.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    working_box.config(yscrollcommand=scrollbar.set)

    buttons = ttk.Frame(outer)
    buttons.pack(fill="x", pady=(16, 0))

    def save():
        try:
            save_finish_data(
                seimen_entry,
                boil_entry,
                evaluation_entries,
                comment,
                new_window,
            )
            messagebox.showinfo("保存完了", "製麺記録を完了しました。", parent=parent)
        except (ValueError, IndexError) as error:
            messagebox.showerror("入力エラー", str(error), parent=new_window)

    ttk.Button(buttons, text="保存して完了", command=save, style="Primary.TButton").pack(
        side="left"
    )
    ttk.Button(buttons, text="キャンセル", command=new_window.destroy).pack(
        side="right"
    )
