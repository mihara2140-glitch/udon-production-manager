import tkinter as tk
from tkinter import messagebox, ttk

from services.seimen_service import save_finish_data, show_working_list


def open_finish_window(parent):
    working_text = show_working_list()

    new_window = tk.Toplevel(parent)
    new_window.title("製麺終了 - Ver.21")
    new_window.geometry("1000x720")
    new_window.minsize(900, 640)

    style = ttk.Style(new_window)
    style.configure("Title.TLabel", font=("Meiryo", 18, "bold"))
    style.configure("Section.TLabel", font=("Meiryo", 11, "bold"))
    style.configure("Primary.TButton", font=("Meiryo", 11, "bold"), padding=8)

    outer = ttk.Frame(new_window, padding=18)
    outer.pack(fill="both", expand=True)

    header = ttk.Frame(outer)
    header.pack(fill="x", pady=(0, 12))

    title_area = ttk.Frame(header)
    title_area.pack(side="left", fill="x", expand=True)
    ttk.Label(title_area, text="製麺を終了して評価を記録", style="Title.TLabel").pack(anchor="w")
    ttk.Label(
        title_area,
        text="熟成時間・茹で時間・食感評価を、実績としてまとめて記録します。",
    ).pack(anchor="w", pady=(4, 0))

    action_area = ttk.Frame(header)
    action_area.pack(side="right", padx=(16, 0))

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

    row = 0
    ttk.Label(input_card, text="製麺番号").grid(row=row, column=0, sticky="w", pady=5)
    seimen_entry = ttk.Entry(input_card, width=16)
    seimen_entry.grid(row=row, column=1, sticky="ew", pady=5)

    row += 1
    ttk.Label(input_card, text="常温熟成時間").grid(row=row, column=0, sticky="w", pady=5)
    room_maturation_entry = ttk.Entry(input_card, width=16)
    room_maturation_entry.grid(row=row, column=1, sticky="ew", pady=5)

    row += 1
    ttk.Label(input_card, text="冷蔵熟成時間").grid(row=row, column=0, sticky="w", pady=5)
    cold_maturation_entry = ttk.Entry(input_card, width=16)
    cold_maturation_entry.grid(row=row, column=1, sticky="ew", pady=5)

    row += 1
    ttk.Label(input_card, text="茹で時間").grid(row=row, column=0, sticky="w", pady=5)
    boil_entry = ttk.Entry(input_card, width=16)
    boil_entry.grid(row=row, column=1, sticky="ew", pady=5)

    row += 1
    ttk.Separator(input_card).grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)

    row += 1
    ttk.Label(input_card, text="評価（1〜10）", style="Section.TLabel").grid(
        row=row, column=0, columnspan=2, sticky="w", pady=(0, 5)
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
    for label in evaluation_labels:
        row += 1
        ttk.Label(input_card, text=label).grid(row=row, column=0, sticky="w", pady=3)
        spinbox = ttk.Spinbox(input_card, from_=1, to=10, width=8)
        spinbox.grid(row=row, column=1, sticky="w", pady=3)
        evaluation_entries[label] = spinbox

    row += 1
    ttk.Label(input_card, text="感想・メモ", style="Section.TLabel").grid(
        row=row, column=0, columnspan=2, sticky="w", pady=(10, 5)
    )

    row += 1
    comment = tk.Text(
        input_card,
        width=44,
        height=5,
        wrap="word",
        font=("Meiryo", 10),
        padx=8,
        pady=8,
    )
    comment.grid(row=row, column=0, columnspan=2, sticky="nsew")
    input_card.rowconfigure(row, weight=1)

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

    def save():
        try:
            save_finish_data(
                seimen_entry,
                room_maturation_entry,
                cold_maturation_entry,
                boil_entry,
                evaluation_entries,
                comment,
                new_window,
            )
            messagebox.showinfo("保存完了", "製麺記録を完了しました。", parent=parent)
        except (ValueError, IndexError) as error:
            messagebox.showerror("入力エラー", str(error), parent=new_window)

    ttk.Button(
        action_area,
        text="保存して完了",
        command=save,
        style="Primary.TButton",
    ).pack(side="left", padx=(0, 8))
    ttk.Button(action_area, text="閉じる", command=new_window.destroy).pack(side="left")
