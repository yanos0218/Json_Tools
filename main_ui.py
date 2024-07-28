import tkinter as tk
from tkinter import ttk
from file_tab import create_file_tab
from count_tab import create_count_tab
from FileInfo_tab import create_info_tab
from deletedormove_tab import create_deleteormove_tab
from KeyValue_keit_tab import create_KeyValue_keit_tab

def main():
    root = tk.Tk()
    root.title("파일 검색 및 분석")

    tab_control = ttk.Notebook(root)
    tab1 = ttk.Frame(tab_control)
    tab2 = ttk.Frame(tab_control)
    tab3 = ttk.Frame(tab_control)
    tab4 = ttk.Frame(tab_control)
    tab5 = ttk.Frame(tab_control)

    tab_control.add(tab1, text='파일 검색 및 이동')
    tab_control.add(tab2, text='문자열 개수 카운트')
    tab_control.add(tab3, text='파일 정보 검색')
    tab_control.add(tab4, text='파일 삭제 또는 이동')
    tab_control.add(tab5, text='파일 검색_keit')
    tab_control.pack(expand=1, fill='both')

    create_file_tab(tab1)
    create_count_tab(tab2)
    create_info_tab(tab3)
    create_deleteormove_tab(tab4)
    create_KeyValue_keit_tab(tab5)

    root.mainloop()

if __name__ == "__main__":
    main()
