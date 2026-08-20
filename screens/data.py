import tkinter as tk
from tkinter import ttk

from services.record_service import get_record_detail, get_record_list


def _display(value, suffix=""):
    if value is None or value == "":
        return "-"
    return f"{value}{suffix}"


def open_data_window(parent):
    new_window = tk.Toplevel(parent)
    new_window.title("製麺記録 - Ver.23")
    new_window.geometry("1180x760")
    new_window.minsize(980, 650)

    style = ttk.Style(new_window)
    style.configure("RecordTitle.TLabel", font=("Meiryo", 18, "bold"))
    style.configure("RecordSub.TLabel", font=("Meiryo", 10))
    style.configure("Treeview", rowheight=28, font=("Meiryo", 9))
    style.configure("Treeview.Heading", font=("Meiryo", 9, "bold"))

    outer = ttk.Frame(new_window, padding=18)
    outer.pack(fill="both", expand=True)

    header = ttk.Frame(outer)
    header.pack(fill="x", pady=(0, 12))

    title_area = ttk.Frame(header)
    title_area.pack(side="left", fill="x", expand=True)
    ttk.Label(title_area, text="製麺記録", style="RecordTitle.TLabel").pack(anchor="w")
    ttk.Label(
        title_area,
        text="一覧から記録を選ぶと、下に配合・熟成・評価・メモの詳細を表示します。",
        style="RecordSub.TLabel",
    ).pack(anchor="w", pady=(3, 0))

    ttk.Button(header, text="閉じる", command=new_window.destroy).pack(side="right")

    filter_frame = ttk.LabelFrame(outer, text=" 検索・絞り込み ", padding=10)
    filter_frame.pack(fill="x", pady=(0, 12))
    filter_frame.columnconfigure(1, weight=1)

    ttk.Label(filter_frame, text="検索").grid(row=0, column=0, sticky="w", padx=(0, 8))
    search_var = tk.StringVar()
    search_entry = ttk.Entry(filter_frame, textvariable=search_var)
    search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 16))

    ttk.Label(filter_frame, text="状態").grid(row=0, column=2, sticky="w", padx=(0, 8))
    state_var = tk.StringVar(value="すべて")
    state_combo = ttk.Combobox(
        filter_frame,
        textvariable=state_var,
        values=["すべて", "完了", "作業中"],
        state="readonly",
        width=10,
    )
    state_combo.grid(row=0, column=3, sticky="w", padx=(0, 10))

    ttk.Button(filter_frame, text="検索をクリア", command=lambda: search_var.set("")).grid(
        row=0, column=4, sticky="e"
    )

    table_frame = ttk.LabelFrame(outer, text=" 記録一覧 ", padding=8)
    table_frame.pack(fill="both", expand=True, pady=(0, 12))
    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    columns = (
        "id",
        "date",
        "recipe",
        "hydration",
        "environment",
        "maturation",
        "boil",
        "score",
        "state",
    )

    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
    tree.grid(row=0, column=0, sticky="nsew")

    headings = {
        "id": "No.",
        "date": "日付",
        "recipe": "配合",
        "hydration": "加水率",
        "environment": "気温 / 湿度",
        "maturation": "常温 / 冷蔵",
        "boil": "茹で",
        "score": "総合",
        "state": "状態",
    }

    widths = {
        "id": 55,
        "date": 105,
        "recipe": 65,
        "hydration": 75,
        "environment": 125,
        "maturation": 130,
        "boil": 75,
        "score": 75,
        "state": 70,
    }

    for column in columns:
        tree.heading(column, text=headings[column])
        tree.column(column, width=widths[column], minwidth=50, anchor="center")

    tree.column("date", anchor="w")
    tree.column("environment", anchor="w")
    tree.column("maturation", anchor="w")

    y_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    y_scrollbar.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=y_scrollbar.set)

    detail_frame = ttk.LabelFrame(outer, text=" 選択した記録の詳細 ", padding=10)
    detail_frame.pack(fill="x")
    detail_frame.columnconfigure(0, weight=1)

    detail_text = tk.Text(
        detail_frame,
        height=10,
        wrap="word",
        font=("Meiryo", 10),
        padx=10,
        pady=8,
        relief="flat",
    )
    detail_text.grid(row=0, column=0, sticky="ew")
    detail_text.insert("1.0", "一覧から記録を1件選んでください。")
    detail_text.config(state="disabled")

    all_records = []

    def set_detail(text):
        detail_text.config(state="normal")
        detail_text.delete("1.0", "end")
        detail_text.insert("1.0", text)
        detail_text.config(state="disabled")

    def build_detail(record_id):
        data = get_record_detail(record_id)
        total = f"{data['total_score']}/60" if data["total_score"] is not None else "-"

        return (
            f"製麺No.{data['id']}　｜　{_display(data['record_date'])}　｜　状態：{data['state']}\n"
            f"環境：気温 {_display(data['temperature'], '℃')}　湿度 {_display(data['humidity'], '%')}\n"
            f"配合No.{data['recipe_id']}："
            f"薄力 {data['weak']}g（{data['weak_name']}） / "
            f"中力 {data['medium']}g（{data['medium_name']}） / "
            f"強力 {data['strong']}g（{data['strong_name']}）\n"
            f"加水率 {data['hydration']}%　塩分濃度 {data['salt_percent']}%\n"
            f"熟成：常温 {_display(data['room_maturation_hours'], 'h')}　"
            f"冷蔵 {_display(data['cold_maturation_hours'], 'h')}　"
            f"茹で {_display(data['boil_minutes'], '分')}\n"
            f"評価：総合 {total}　"
            f"ツル {_display(data['smooth_score'])} / "
            f"モチ {_display(data['chewy_score'])} / "
            f"コシ {_display(data['firmness_score'])} / "
            f"のど越し {_display(data['throat_score'])} / "
            f"くっつき {_display(data['sticking_score'])} / "
            f"タレ {_display(data['sauce_score'])}\n"
            f"メモ：{_display(data['memo'])}"
        )

    def refresh_table(*_):
        keyword = search_var.get().strip().lower()
        selected_state = state_var.get()

        for item in tree.get_children():
            tree.delete(item)

        visible_count = 0
        for record in all_records:
            if selected_state != "すべて" and record["state"] != selected_state:
                continue

            searchable = " ".join(
                [
                    str(record["id"]),
                    str(record["record_date"] or ""),
                    str(record["recipe_id"]),
                ]
            ).lower()
            if keyword and keyword not in searchable:
                continue

            room = _display(record["room_maturation_hours"], "h")
            cold = _display(record["cold_maturation_hours"], "h")
            temp = _display(record["temperature"], "℃")
            humidity = _display(record["humidity"], "%")
            boil = _display(record["boil_minutes"], "分")
            score = f"{record['total_score']}/60" if record["total_score"] is not None else "-"

            tree.insert(
                "",
                "end",
                iid=str(record["id"]),
                values=(
                    record["id"],
                    record["record_date"] or "-",
                    record["recipe_id"],
                    f"{record['hydration']}%",
                    f"{temp} / {humidity}",
                    f"{room} / {cold}",
                    boil,
                    score,
                    record["state"],
                ),
            )
            visible_count += 1

        table_frame.configure(text=f" 記録一覧（{visible_count}件） ")
        if visible_count == 0:
            set_detail("条件に合う製麺記録がありません。")

    def reload_records():
        nonlocal all_records
        all_records = get_record_list()
        refresh_table()

    def on_select(_event=None):
        selected = tree.selection()
        if not selected:
            return
        set_detail(build_detail(selected[0]))

    ttk.Button(filter_frame, text="最新の状態に更新", command=reload_records).grid(
        row=0, column=5, sticky="e", padx=(10, 0)
    )

    search_var.trace_add("write", refresh_table)
    state_combo.bind("<<ComboboxSelected>>", refresh_table)
    tree.bind("<<TreeviewSelect>>", on_select)
    tree.bind("<Double-1>", on_select)
    new_window.bind("<Escape>", lambda _event: new_window.destroy())

    reload_records()
    search_entry.focus_set()
