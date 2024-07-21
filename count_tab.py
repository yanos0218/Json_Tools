import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import re
import csv

def create_count_tab(tab):
    global entry_count_search, label_count_source
    global button_count_search, button_clear_count, button_count_source
    global treeview, button_save_csv, button_delete_selected

    count_source_dir = None
    search_results = []

    def select_count_source_folder():
        nonlocal count_source_dir
        count_source_dir = filedialog.askdirectory(title="검색 폴더 선택")
        if count_source_dir:
            label_count_source.config(text=count_source_dir)

    def count_occurrences():
        search_pattern = entry_count_search.get()

        if not search_pattern:
            messagebox.showwarning("경고", "정규식 패턴을 입력하세요.")
            return
        if not count_source_dir:
            messagebox.showwarning("경고", "검색 폴더를 선택하세요.")
            return

        try:
            regex = re.compile(search_pattern)
        except re.error:
            messagebox.showerror("오류", "올바르지 않은 정규식 패턴입니다.")
            return

        for i in treeview.get_children():
            treeview.delete(i)

        search_results.clear()
        total_files = 0

        for file in os.listdir(count_source_dir):
            if file.endswith('.json'):
                file_path = os.path.join(count_source_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        matches = regex.findall(content)
                        if matches:
                            count = len(matches)
                            search_results.append((file_path, count))
                            treeview.insert("", "end", values=(0, file_path, count))
                            total_files += 1
                except Exception as e:
                    treeview.insert("", "end", values=(0, file_path, f"Failed to read: {e}"))

        messagebox.showinfo("작업 완료", f"총 파일 수: {total_files}")

    def clear_treeview():
        for i in treeview.get_children():
            treeview.delete(i)
        search_results.clear()

    def save_results_to_csv():
        if not count_source_dir:
            messagebox.showwarning("경고", "검색 폴더를 선택하세요.")
            return
        if not search_results:
            messagebox.showwarning("경고", "저장할 결과가 없습니다.")
            return

        csv_file_path = os.path.join(count_source_dir, "search_results.csv")

        try:
            with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(["File Path", "Count", "PDF Link"])
                for file_path, count in search_results:
                    pdf_path = file_path.replace(".json", ".pdf")
                    writer.writerow([f'=HYPERLINK("{file_path}", "{file_path}")', count, f'=HYPERLINK("{pdf_path}", "{pdf_path}")'])
            messagebox.showinfo("저장 완료", f"결과가 {csv_file_path}에 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"CSV 파일 저장 중 오류가 발생했습니다: {e}")

    def delete_selected_files():
        selected_items = [item for item in treeview.get_children() if treeview.set(item, "Check") == "1"]
        if not selected_items:
            messagebox.showwarning("경고", "삭제할 파일을 선택하세요.")
            return

        confirm = messagebox.askokcancel("삭제 확인", "선택한 파일을 삭제하시겠습니까?")
        if confirm:
            for item in selected_items:
                file_path = treeview.item(item, "values")[1]  # 파일 경로를 정확하게 가져오기
                try:
                    os.remove(file_path)  # 파일을 삭제
                    treeview.item(item, tags=('deleted',))
                    treeview.tag_configure('deleted', foreground='grey')
                    treeview.set(item, "Check", "Deleted")
                except Exception as e:
                    messagebox.showerror("오류", f"{file_path} 파일 삭제 중 오류가 발생했습니다: {e}")

    frame = tk.Frame(tab)
    frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    label_count_search = tk.Label(frame, text="찾을 정규식 패턴:")
    label_count_search.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    entry_count_search = tk.Entry(frame, width=30)
    entry_count_search.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    button_count_search = tk.Button(frame, text="검색", command=count_occurrences)
    button_count_search.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    button_count_source = tk.Button(frame, text="검색 폴더 선택", command=select_count_source_folder)
    button_count_source.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    label_count_source = tk.Label(frame, text="검색 폴더: 선택되지 않음")
    label_count_source.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

    button_clear_count = tk.Button(frame, text="결과 초기화", command=clear_treeview)
    button_clear_count.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

    button_save_csv = tk.Button(frame, text="CSV로 저장", command=save_results_to_csv)
    button_save_csv.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

    columns = ("Check", "FileName", "Count")
    treeview = ttk.Treeview(tab, columns=columns, show="headings")
    treeview.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    treeview.heading("Check", text="Check")
    treeview.heading("FileName", text="FileName")
    treeview.heading("Count", text="Count")

    treeview.column("Check", anchor="center", width=50)
    treeview.column("FileName", anchor="w")
    treeview.column("Count", anchor="center", width=100)

    treeview.tag_configure('deleted', foreground='grey')

    def check_all():
        for item in treeview.get_children():
            if "deleted" not in treeview.item(item, "tags"):
                treeview.set(item, "Check", "1")

    def uncheck_all():
        for item in treeview.get_children():
            if treeview.set(item, "Check") != "Deleted":
                treeview.set(item, "Check", "0")

    frame_buttons = tk.Frame(tab)
    frame_buttons.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

    button_check_all = tk.Button(frame_buttons, text="전체 선택", command=check_all)
    button_check_all.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    button_uncheck_all = tk.Button(frame_buttons, text="전체 해제", command=uncheck_all)
    button_uncheck_all.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    button_delete_selected = tk.Button(frame_buttons, text="선택 삭제", command=delete_selected_files)
    button_delete_selected.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    tab.grid_rowconfigure(3, weight=1)
    tab.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    for col in columns:
        treeview.heading(col, text=col, command=lambda c=col: sort_column(treeview, c, False))

    treeview.bind('<ButtonRelease-1>', lambda event: treeview_update(event))

def sort_column(treeview, col, reverse):
    data = [(treeview.set(child, col), child) for child in treeview.get_children('')]
    data.sort(reverse=reverse)
    for index, (value, child) in enumerate(data):
        treeview.move(child, '', index)
    treeview.heading(col, command=lambda: sort_column(treeview, col, not reverse))

def treeview_update(event):
    treeview = event.widget
    if treeview.identify_region(event.x, event.y) == "cell":
        row_id = treeview.identify_row(event.y)
        col = treeview.identify_column(event.x)
        if col == '#1':  # Checkbox column
            current_value = treeview.set(row_id, "Check")
            if current_value != "Deleted":
                new_value = "1" if current_value == "0" else "0"
                treeview.set(row_id, "Check", new_value)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("파일 검색 및 분석")

    tab_control = ttk.Notebook(root)
    tab1 = ttk.Frame(tab_control)
    tab2 = ttk.Frame(tab_control)

    tab_control.add(tab1, text='파일 검색 및 이동')
    tab_control.add(tab2, text='문자열 개수 카운트')
    tab_control.pack(expand=1, fill='both')

    create_count_tab(tab2)

    root.mainloop()
