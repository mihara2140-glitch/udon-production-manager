import tkinter as tk

from services.recipe_service import search_recipe


def open_recipe_search_window(parent):
    new_window = tk.Toplevel(parent)

    new_window.title("配合検索")
    new_window.geometry("700x600")

    tk.Label(new_window, text="配合番号").grid(row=0, column=0, padx=10, pady=10)

    recipe_entry = tk.Entry(new_window)

    recipe_entry.grid(row=0, column=1, padx=10, pady=10)

    result_text = tk.Text(new_window, width=70, height=30)

    result_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def search():

        recipe_no = int(recipe_entry.get())

        result = search_recipe(recipe_no)

        result_text.config(state="normal")

        result_text.delete("1.0", "end")

        result_text.insert("1.0", result)

        result_text.config(state="disabled")

    tk.Button(new_window, text="検索", command=search).grid(
        row=0, column=2, padx=10, pady=10
    )
