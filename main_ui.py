import tkinter as tk
from tkinter import ttk
from file_tab import create_file_tab # type: ignore
from count_tab import create_count_tab # type: ignore

def create_main_ui():
    app = tk.Tk()
    app.title("파일 검색 및 분석")
    app.geometry("800x600")

    notebook = ttk.Notebook(app)
    notebook.pack(fill=tk.BOTH, expand=True)

    file_tab = ttk.Frame(notebook)
    count_tab = ttk.Frame(notebook)

    notebook.add(file_tab, text="파일 검색 및 이동")
    notebook.add(count_tab, text="문자열 개수 카운트")

    create_file_tab(file_tab)
    create_count_tab(count_tab)

    app.mainloop()

if __name__ == "__main__":
    create_main_ui()
