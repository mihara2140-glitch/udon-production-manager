import tkinter as tk
from tkinter import ttk

from services.database_service import initialize_database

# Ver.21では起動時にSQLite DBを準備し、初回だけ既存CSVを取り込む。
initialize_database()

from screens.data import open_data_window
from screens.finish import open_finish_window
from screens.flour import open_flour_window
from screens.flour_registeer import open_flour_register_window
from screens.humidity import open_humidity_window
from screens.recipe_calc import open_recipe_calc_window
from screens.recipe_history import open_recipe_history_window
from screens.recipe_search import open_recipe_search_window
from screens.start import open_start_window


window = tk.Tk()
window.title("製麺管理アプリ Ver.21")
window.geometry("760x640")
window.minsize(700, 580)

style = ttk.Style(window)
style.configure("AppTitle.TLabel", font=("Meiryo", 22, "bold"))
style.configure("Subtitle.TLabel", font=("Meiryo", 10))
style.configure("Section.TLabelframe.Label", font=("Meiryo", 12, "bold"))
style.configure("Main.TButton", font=("Meiryo", 11, "bold"), padding=12)
style.configure("Sub.TButton", font=("Meiryo", 10), padding=9)

root = ttk.Frame(window, padding=22)
root.pack(fill="both", expand=True)

header = ttk.Frame(root)
header.pack(fill="x", pady=(0, 18))

text_area = ttk.Frame(header)
text_area.pack(side="left", fill="x", expand=True)

ttk.Label(text_area, text="製麺管理アプリ", style="AppTitle.TLabel").pack(anchor="w")
ttk.Label(
    text_area,
    text="記録・配合・評価をSQLiteで管理し、製麺の再現性を高める。",
    style="Subtitle.TLabel",
).pack(anchor="w", pady=(3, 0))

ttk.Label(header, text="Ver.21 / SQLite", font=("Meiryo", 10, "bold")).pack(
    side="right", anchor="n", pady=7
)

# 今日の製麺
seimen_frame = ttk.LabelFrame(root, text=" 今日の製麺 ", padding=14, style="Section.TLabelframe")
seimen_frame.pack(fill="x", pady=(0, 14))
for column in range(2):
    seimen_frame.columnconfigure(column, weight=1)

ttk.Button(
    seimen_frame,
    text="▶  製麺を開始",
    style="Main.TButton",
    command=lambda: open_start_window(window),
).grid(row=0, column=0, sticky="ew", padx=(0, 7), pady=4)

ttk.Button(
    seimen_frame,
    text="✓  製麺を終了・評価",
    style="Main.TButton",
    command=lambda: open_finish_window(window),
).grid(row=0, column=1, sticky="ew", padx=(7, 0), pady=4)

# 記録
record_frame = ttk.LabelFrame(root, text=" 記録を見る ", padding=14, style="Section.TLabelframe")
record_frame.pack(fill="x", pady=(0, 14))
for column in range(3):
    record_frame.columnconfigure(column, weight=1)

ttk.Button(
    record_frame,
    text="製麺記録",
    style="Sub.TButton",
    command=lambda: open_data_window(window),
).grid(row=0, column=0, sticky="ew", padx=5, pady=4)

ttk.Button(
    record_frame,
    text="湿度70%以上",
    style="Sub.TButton",
    command=lambda: open_humidity_window(window),
).grid(row=0, column=1, sticky="ew", padx=5, pady=4)

ttk.Button(
    record_frame,
    text="配合から検索",
    style="Sub.TButton",
    command=lambda: open_recipe_search_window(window),
).grid(row=0, column=2, sticky="ew", padx=5, pady=4)

# 配合・粉
recipe_frame = ttk.LabelFrame(root, text=" 配合・粉の管理 ", padding=14, style="Section.TLabelframe")
recipe_frame.pack(fill="x", pady=(0, 14))
for column in range(2):
    recipe_frame.columnconfigure(column, weight=1)

buttons = [
    ("配合計算", lambda: open_recipe_calc_window(window)),
    ("配合履歴", lambda: open_recipe_history_window(window)),
    ("粉銘柄一覧", lambda: open_flour_window(window)),
    ("粉銘柄を登録", lambda: open_flour_register_window(window)),
]

for index, (label, command) in enumerate(buttons):
    row = index // 2
    column = index % 2
    ttk.Button(recipe_frame, text=label, style="Sub.TButton", command=command).grid(
        row=row,
        column=column,
        sticky="ew",
        padx=5,
        pady=5,
    )

analysis_frame = ttk.LabelFrame(root, text=" データ基盤 ", padding=14, style="Section.TLabelframe")
analysis_frame.pack(fill="x", pady=(0, 14))

ttk.Label(
    analysis_frame,
    text=(
        "✓ SQLite移行済み　　次は pandas / matplotlib を使って、"
        "加水率・湿度・熟成時間・評価の関係を分析します。"
    ),
    wraplength=650,
).pack(anchor="w")

footer = ttk.Frame(root)
footer.pack(fill="x", pady=(6, 0))

ttk.Label(footer, text="保存先：data/udon_manager.db").pack(side="left")
ttk.Button(footer, text="終了", command=window.destroy).pack(side="right")

window.mainloop()
