import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # ttk 모듈을 가져옵니다

def process_files(directory, action, target_directory=None):
    if action == 'move' and not target_directory:
        messagebox.showerror("오류", "'이동' 작업에는 대상 폴더가 필요합니다.")
        return
    
    json_files = set()
    pdf_files = set()

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            json_files.add(filename[:-5])
        elif filename.endswith('.pdf'):
            pdf_files.add(filename[:-4])

    common_files = json_files.intersection(pdf_files)

    if not common_files:
        messagebox.showinfo("정보", "일치하는 .json 및 .pdf 파일을 찾을 수 없습니다.")
        return

    deleted_files_count = 0
    moved_files_count = 0

    for filename in common_files:
        json_path = os.path.join(directory, filename + '.json')
        pdf_path = os.path.join(directory, filename + '.pdf')

        try:
            if action == 'delete':
                os.remove(json_path)
                os.remove(pdf_path)
                deleted_files_count += 1
            elif action == 'move':
                shutil.move(json_path, os.path.join(target_directory, filename + '.json'))
                shutil.move(pdf_path, os.path.join(target_directory, filename + '.pdf'))
                moved_files_count += 1
        except Exception as e:
            messagebox.showerror("오류", f"{filename} 처리 실패: {e}")

    if action == 'delete':
        messagebox.showinfo("결과", f"{deleted_files_count}쌍의 파일을 삭제했습니다.")
    elif action == 'move':
        messagebox.showinfo("결과", f"{moved_files_count}쌍의 파일을 이동했습니다.")

def select_directory(entry_directory):
    directory = filedialog.askdirectory()
    entry_directory.delete(0, tk.END)
    entry_directory.insert(0, directory)

def select_target_directory(entry_target_directory):
    directory = filedialog.askdirectory()
    entry_target_directory.delete(0, tk.END)
    entry_target_directory.insert(0, directory)

def delete_files(entry_directory):
    directory = entry_directory.get()
    process_files(directory, 'delete')

def move_files(entry_directory, entry_target_directory):
    directory = entry_directory.get()
    target_directory = entry_target_directory.get()
    process_files(directory, 'move', target_directory)

def create_deleteormove_tab(tab):
    label_directory = tk.Label(tab, text="폴더 선택:")
    label_directory.grid(row=0, column=0, padx=10, pady=5)

    entry_directory = tk.Entry(tab, width=50)
    entry_directory.grid(row=0, column=1, padx=10, pady=5)

    button_browse_directory = tk.Button(tab, text="탐색", command=lambda: select_directory(entry_directory))
    button_browse_directory.grid(row=0, column=2, padx=10, pady=5)

    label_target_directory = tk.Label(tab, text="대상 폴더 (이동할 경우):")
    label_target_directory.grid(row=1, column=0, padx=10, pady=5)

    entry_target_directory = tk.Entry(tab, width=50)
    entry_target_directory.grid(row=1, column=1, padx=10, pady=5)

    button_browse_target_directory = tk.Button(tab, text="탐색", command=lambda: select_target_directory(entry_target_directory))
    button_browse_target_directory.grid(row=1, column=2, padx=10, pady=5)

    button_delete = tk.Button(tab, text="파일 삭제", command=lambda: delete_files(entry_directory), width=20, bg='red', fg='white')
    button_delete.grid(row=2, column=0, columnspan=3, pady=10)

    button_move = tk.Button(tab, text="파일 이동", command=lambda: move_files(entry_directory, entry_target_directory), width=20, bg='blue', fg='white')
    button_move.grid(row=3, column=0, columnspan=3, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("파일 삭제 또는 이동")

    tab_control = ttk.Notebook(root)
    tab = ttk.Frame(tab_control)
    tab_control.add(tab, text='파일 삭제 또는 이동')
    tab_control.pack(expand=1, fill='both')

    create_deleteormove_tab(tab)

    root.mainloop()
