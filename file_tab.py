import os
import shutil
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # 추가

# 폴더 경로와 UI 요소를 저장하는 전역 변수
file_source_dir = None
file_target_dir = None
listbox = None

def select_file_source_folder():
    global file_source_dir
    file_source_dir = filedialog.askdirectory(title="원본 폴더 선택")
    if file_source_dir:
        label_file_source.config(text=file_source_dir)

def select_file_target_folder():
    global file_target_dir
    file_target_dir = filedialog.askdirectory(title="대상 폴더 선택")
    if file_target_dir:
        label_file_target.config(text=file_target_dir)

def search_and_move_files():
    search_pattern = entry_file_search.get()

    if not search_pattern:
        messagebox.showwarning("경고", "정규식 패턴을 입력하세요.")
        return
    if not file_source_dir:
        messagebox.showwarning("경고", "원본 폴더를 선택하세요.")
        return
    if not file_target_dir:
        messagebox.showwarning("경고", "대상 폴더를 선택하세요.")
        return

    try:
        regex = re.compile(search_pattern)
    except re.error:
        messagebox.showerror("오류", "올바르지 않은 정규식 패턴입니다.")
        return

    total_files = 0
    moved_files = 0
    failed_files = 0

    if listbox:
        listbox.delete(0, tk.END)

    for file in os.listdir(file_source_dir):
        if file.endswith('.json'):
            file_path = os.path.join(file_source_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if regex.search(content):
                        total_files += 1
                        f.close()  # 파일 닫기
                        shutil.move(file_path, file_target_dir)
                        moved_files += 1
                        if listbox:
                            listbox.insert(tk.END, f"Moved: {file_path}")
            except Exception as e:
                failed_files += 1
                if listbox:
                    listbox.insert(tk.END, f"Failed to move: {file_path} - {e}")

    messagebox.showinfo("작업 완료", f"총 파일 수: {total_files}\n이동 성공: {moved_files}\n이동 실패: {failed_files}")

def clear_listbox():
    global listbox
    if listbox:
        listbox.delete(0, tk.END)

def create_file_tab(tab):
    global entry_file_search, label_file_source, label_file_target
    global button_file_search, button_clear_file, button_file_source, button_file_target
    global listbox  # listbox를 전역 변수로 선언

    frame = tk.Frame(tab)
    frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    label_file_search = tk.Label(frame, text="찾을 정규식 패턴:")
    label_file_search.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    entry_file_search = tk.Entry(frame, width=30)
    entry_file_search.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    button_file_search = tk.Button(frame, text="검색 및 이동", command=search_and_move_files)
    button_file_search.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    button_file_source = tk.Button(frame, text="원본 폴더 선택", command=select_file_source_folder)
    button_file_source.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    label_file_source = tk.Label(frame, text="원본 폴더: 선택되지 않음")
    label_file_source.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

    button_file_target = tk.Button(frame, text="대상 폴더 선택", command=select_file_target_folder)
    button_file_target.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

    label_file_target = tk.Label(frame, text="대상 폴더: 선택되지 않음")
    label_file_target.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

    button_clear_file = tk.Button(frame, text="결과 초기화", command=clear_listbox)
    button_clear_file.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

    scrollbar_y = tk.Scrollbar(tab, orient=tk.VERTICAL)
    scrollbar_y.grid(row=1, column=1, sticky="ns")

    scrollbar_x = tk.Scrollbar(tab, orient=tk.HORIZONTAL)
    scrollbar_x.grid(row=2, column=0, sticky="ew")

    listbox = tk.Listbox(tab, width=80, height=20, yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    scrollbar_y.config(command=listbox.yview)
    scrollbar_x.config(command=listbox.xview)

    tab.grid_rowconfigure(1, weight=1)
    tab.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("파일 검색 및 분석")

    tab_control = ttk.Notebook(root)
    tab1 = ttk.Frame(tab_control)

    tab_control.add(tab1, text='파일 검색 및 이동')
    tab_control.pack(expand=1, fill='both')

    create_file_tab(tab1)

    root.mainloop()
