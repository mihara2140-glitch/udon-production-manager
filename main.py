import tkinter as tk

from screens.data import open_data_window
from screens.finish import open_finish_window
from screens.flour import open_flour_window
from screens.flour_registeer import open_flour_register_window
from screens.humidity import open_humidity_window
from screens.recipe_calc import open_recipe_calc_window
from screens.recipe_history import open_recipe_history_window
from screens.recipe_search import open_recipe_search_window
from screens.start import open_start_window

# -------------------------
# ウィンドウ
# -------------------------
window = tk.Tk()
window.title("製麺管理アプリ Ver.20")
window.geometry("400x450")


# タイトル
title = tk.Label(window, text="製麺管理アプリ", font=("Meiryo", 18))
title.pack(pady=15)


# ボタン
tk.Button(
    window, text="データを見る", width=20, command=lambda: open_data_window(window)
).pack(pady=5)

tk.Button(
    window, text="製麺開始", width=20, command=lambda: open_start_window(window)
).pack(pady=5)

tk.Button(
    window, text="製麺終了", width=20, command=lambda: open_finish_window(window)
).pack(pady=5)

tk.Button(
    window,
    text="湿度70%以上検索",
    width=20,
    command=lambda: open_humidity_window(window),
).pack(pady=5)

tk.Button(
    window, text="配合計算", width=20, command=lambda: open_recipe_calc_window(window)
).pack(pady=5)

tk.Button(
    window,
    text="配合履歴を見る",
    width=20,
    command=lambda: open_recipe_history_window(window),
).pack(pady=5)

tk.Button(
    window, text="粉銘柄一覧を見る", width=20, command=lambda: open_flour_window(window)
).pack(pady=5)

tk.Button(
    window,
    text="粉銘柄を登録する",
    width=20,
    command=lambda: open_flour_register_window(window),
).pack(pady=5)

tk.Button(
    window, text="配合検索", width=20, command=lambda: open_recipe_search_window(window)
).pack(pady=5)

tk.Button(window, text="終了", width=20, command=window.destroy).pack(pady=20)


window.mainloop()
