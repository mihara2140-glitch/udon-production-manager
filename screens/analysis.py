import tkinter as tk
from tkinter import messagebox, ttk

from services.analysis_service import get_analysis_summary, load_analysis_dataframe


CHARTS = {
    "humidity_sticking": {
        "title": "湿度 × くっつき評価",
        "x": "humidity",
        "y": "sticking_score",
        "xlabel": "湿度（%）",
        "ylabel": "くっつき評価（10=くっつきにくい）",
    },
    "room_firmness": {
        "title": "常温熟成時間 × コシ",
        "x": "room_maturation_hours",
        "y": "firmness_score",
        "xlabel": "常温熟成時間（h）",
        "ylabel": "コシ評価（1〜10）",
    },
    "hydration_total": {
        "title": "加水率 × 総合評価",
        "x": "hydration",
        "y": "total_score",
        "xlabel": "加水率（%）",
        "ylabel": "総合評価（6項目合計 / 60）",
    },
}


def open_analysis_window(parent):
    summary = get_analysis_summary()

    new_window = tk.Toplevel(parent)
    new_window.title("製麺分析 - Ver.22")
    new_window.geometry("1050x720")
    new_window.minsize(900, 620)

    style = ttk.Style(new_window)
    style.configure("AnalysisTitle.TLabel", font=("Meiryo", 18, "bold"))
    style.configure("Summary.TLabel", font=("Meiryo", 11, "bold"))
    style.configure("Chart.TButton", font=("Meiryo", 10), padding=8)

    outer = ttk.Frame(new_window, padding=18)
    outer.pack(fill="both", expand=True)

    header = ttk.Frame(outer)
    header.pack(fill="x", pady=(0, 14))

    title_area = ttk.Frame(header)
    title_area.pack(side="left", fill="x", expand=True)

    ttk.Label(title_area, text="製麺データ分析", style="AnalysisTitle.TLabel").pack(anchor="w")
    ttk.Label(
        title_area,
        text="過去記録の傾向をグラフで確認します。記録数が少ない間は因果関係ではなく参考傾向として見ます。",
        wraplength=760,
    ).pack(anchor="w", pady=(4, 0))

    ttk.Button(header, text="閉じる", command=new_window.destroy).pack(side="right")

    summary_frame = ttk.LabelFrame(outer, text=" 記録状況 ", padding=12)
    summary_frame.pack(fill="x", pady=(0, 12))

    completed = summary["completed_count"]
    evaluated = summary["evaluated_count"]
    average = summary["average_total"]
    average_text = f"{average:.1f} / 60" if average is not None else "-"

    ttk.Label(
        summary_frame,
        text=f"完了記録：{completed}件　　評価済み：{evaluated}件　　平均総合評価：{average_text}",
        style="Summary.TLabel",
    ).pack(anchor="w")

    controls = ttk.Frame(outer)
    controls.pack(fill="x", pady=(0, 12))

    chart_area = ttk.LabelFrame(outer, text=" グラフ ", padding=10)
    chart_area.pack(fill="both", expand=True)

    placeholder = ttk.Label(
        chart_area,
        text="上のボタンから見たいグラフを選んでください。",
        font=("Meiryo", 11),
    )
    placeholder.pack(expand=True)

    def show_chart(chart_key):
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure

            dataframe = load_analysis_dataframe()
        except ModuleNotFoundError as error:
            messagebox.showerror("分析機能の準備", str(error), parent=new_window)
            return

        chart = CHARTS[chart_key]
        data = dataframe[["id", chart["x"], chart["y"]]].dropna()

        if len(data) < 2:
            messagebox.showinfo(
                "データ不足",
                "このグラフを作るには、該当する記録が2件以上必要です。\n記録が増えると自動的に使えるようになります。",
                parent=new_window,
            )
            return

        for widget in chart_area.winfo_children():
            widget.destroy()

        figure = Figure(figsize=(8, 4.8), dpi=100)
        axis = figure.add_subplot(111)
        axis.scatter(data[chart["x"]], data[chart["y"]])
        axis.set_title(chart["title"])
        axis.set_xlabel(chart["xlabel"])
        axis.set_ylabel(chart["ylabel"])
        axis.grid(True, alpha=0.25)

        for _, record in data.iterrows():
            axis.annotate(
                f"No.{int(record['id'])}",
                (record[chart["x"]], record[chart["y"]]),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=8,
            )

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        ttk.Label(
            chart_area,
            text=f"表示中：{len(data)}件　※ 点が近いほど条件と評価が似ています。",
        ).pack(anchor="w", pady=(6, 0))

    buttons = [
        ("湿度 × くっつき", "humidity_sticking"),
        ("常温熟成 × コシ", "room_firmness"),
        ("加水率 × 総合評価", "hydration_total"),
    ]

    for label, key in buttons:
        ttk.Button(
            controls,
            text=label,
            style="Chart.TButton",
            command=lambda selected=key: show_chart(selected),
        ).pack(side="left", padx=(0, 8))
