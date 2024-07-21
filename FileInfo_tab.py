import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import csv
import webbrowser

# 폴더 경로와 UI 요소를 저장하는 전역 변수
info_source_dir = None
treeview = None
search_results = []
column_widths = {}

def select_info_source_folder():
    global info_source_dir
    info_source_dir = filedialog.askdirectory(title="검색 폴더 선택")
    if info_source_dir:
        label_info_source.config(text=info_source_dir)

def adjust_column_widths(treeview):
    global column_widths
    # 고정된 컬럼 너비 설정
    fixed_widths = {
        "FileName": 300,
        "Total Page": 80,
        "미분류": 55,
    }

    for col in treeview["columns"]:
        if col in fixed_widths:
            max_width = fixed_widths[col]
        else:
            col_name_length = len(col)
            max_width = 15 * col_name_length
            max_width = max(max_width, 55)  # 최소 너비 55 설정
        treeview.column(col, width=max_width, minwidth=max_width, stretch=tk.NO)  # 열 너비 고정
        column_widths[col] = max_width
        treeview.update_idletasks()  # 강제로 업데이트하여 너비 반영

def sort_treeview_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    try:
        l.sort(reverse=reverse, key=lambda t: int(t[0]))
    except ValueError:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: sort_treeview_column(tv, col, not reverse))

def search_info():
    global search_results, treeview
    search_results = []

    if not info_source_dir:
        messagebox.showwarning("경고", "검색 폴더를 선택하세요.")
        return

    # 정규식 패턴 설정
    total_page_pattern = re.compile(r'\t*"total_page":[ \t]*"(.+)"\t*')
    docu_type_pattern = re.compile(r'\t*"docu_type":[ \t]*"(.+)"\t*')

    if treeview:
        for i in treeview.get_children():
            treeview.delete(i)

    # 폴더 내의 .json 파일 검색 및 정보 추출
    docu_type_columns = set()
    for file in os.listdir(info_source_dir):
        if file.endswith('.json') and os.path.isfile(os.path.join(info_source_dir, file)):
            file_path = os.path.join(info_source_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    total_page_match = total_page_pattern.search(content)
                    docu_type_matches = docu_type_pattern.findall(content)
                    if total_page_match:
                        total_page = total_page_match.group(1)
                        docu_type_count = {}
                        for docu_type in docu_type_matches:
                            docu_type_columns.add(docu_type)
                            if docu_type in docu_type_count:
                                docu_type_count[docu_type] += 1
                            else:
                                docu_type_count[docu_type] = 1
                        result = [os.path.basename(file), total_page, docu_type_count]
                        search_results.append(result)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    if not search_results:
        messagebox.showinfo("검색 완료", "조건에 맞는 파일을 찾지 못했습니다.")
        return

    # '미분류' 컬럼을 'Total Page' 다음으로 이동
    docu_type_columns = list(docu_type_columns)
    if '미분류' in docu_type_columns:
        docu_type_columns.remove('미분류')
        docu_type_columns.insert(0, '미분류')

    # Treeview 컬럼 설정
    columns = ["FileName", "Total Page"] + docu_type_columns
    treeview["columns"] = columns
    for col in columns:
        treeview.heading(col, text=col, anchor="center", command=lambda c=col: sort_treeview_column(treeview, c, False))
        if col == "FileName":
            treeview.column(col, anchor="w", width=300, stretch=tk.NO)  # 고정 너비 300
        elif col == "Total Page":
            treeview.column(col, anchor="center", width=80, stretch=tk.NO)  # 고정 너비 80
        elif col == "미분류":
            treeview.column(col, anchor="center", width=55, stretch=tk.NO)  # 고정 너비 55
        else:
            col_name_length = len(col)
            max_width = 15 * col_name_length
            max_width = max(max_width, 55)  # 최소 너비 55 설정
            treeview.column(col, anchor="center", width=max_width, stretch=tk.NO)  # 고정 너비

    # 검색 결과 표시
    for result in search_results:
        file_name, total_page, docu_type_count = result
        row = [file_name, total_page]
        for col in docu_type_columns:
            row.append(docu_type_count.get(col, 0))
        treeview.insert("", "end", values=row)

    # 컬럼 폭 조정
    treeview.update_idletasks()
    adjust_column_widths(treeview)

    for col in treeview["columns"]:
        col_width = treeview.column(col, option='width')
        print(f"Final Column Width - {col}: {col_width}")

    messagebox.showinfo("검색 완료", f"{len(search_results)}개의 파일을 찾았습니다.")

def clear_results():
    global treeview
    if treeview:
        for i in treeview.get_children():
            treeview.delete(i)
    messagebox.showinfo("초기화 완료", "검색 결과가 초기화되었습니다.")

def save_to_csv():
    if not search_results:
        messagebox.showwarning("경고", "저장할 결과가 없습니다.")
        return

    csv_file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not csv_file_path:
        return

    try:
        with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            headers = ["FileName", "Total Page"] + list(treeview["columns"][2:])
            writer.writerow(headers)
            for result in search_results:
                file_name, total_page, docu_type_count = result
                row = [f'=HYPERLINK("{os.path.join(info_source_dir, file_name)}", "{file_name}")', total_page]
                for col in treeview["columns"][2:]:
                    row.append(docu_type_count.get(col, 0))
                writer.writerow(row)
        messagebox.showinfo("저장 완료", f"결과가 {csv_file_path}에 저장되었습니다.")
    except Exception as e:
        messagebox.showerror("오류", f"결과를 저장하는 중 오류가 발생했습니다: {e}")

def create_info_tab(tab):
    global label_info_source, treeview

    frame = tk.Frame(tab)
    frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    button_info_source = tk.Button(frame, text="검색 폴더 선택", command=select_info_source_folder)
    button_info_source.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    label_info_source = tk.Label(frame, text="검색 폴더: 선택되지 않음")
    label_info_source.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

    button_search = tk.Button(frame, text="검색", command=search_info)
    button_search.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    button_clear = tk.Button(frame, text="초기화", command=clear_results)
    button_clear.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

    button_save = tk.Button(frame, text="CSV로 저장", command=save_to_csv)
    button_save.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

    treeview_frame = tk.Frame(tab)
    treeview_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    treeview = ttk.Treeview(treeview_frame, show="headings")
    treeview.grid(row=0, column=0, sticky="nsew")

    vsb = ttk.Scrollbar(treeview_frame, orient="vertical", command=treeview.yview)
    vsb.grid(row=0, column=1, sticky="ns")
    treeview.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(treeview_frame, orient="horizontal", command=treeview.xview)
    hsb.grid(row=1, column=0, sticky="ew")
    treeview.configure(xscrollcommand=hsb.set)

    treeview_frame.grid_rowconfigure(0, weight=1)
    treeview_frame.grid_columnconfigure(0, weight=1)

    tab.grid_rowconfigure(1, weight=1)
    tab.grid_columnconfigure(0, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("파일 정보 검색 및 분석")
    root.geometry("800x600")  # 기본 창 크기 설정

    tab_control = ttk.Notebook(root)
    tab3 = ttk.Frame(tab_control)

    tab_control.add(tab3, text='파일 정보 검색')
    tab_control.pack(expand=1, fill='both')

    create_info_tab(tab3)

    root.mainloop()
