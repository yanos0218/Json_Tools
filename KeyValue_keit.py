import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
from collections import defaultdict

def search_in_json_files(directory, selected_type):
    results = defaultdict(list)
    fields_travel = ['신청일', '문서번호', '출장자 성명', '출장사 소속', '출장사 직위', '출장기간', '출장목적지', '출장목적', '출장내용', '출장결과']
    fields_meeting = ['회의날짜', '회의장소', '참여자 성명', '참여자 소속', '회의주제', '항목']
    subfields_meeting = ['참여자소속', '참석자소속', '회의주제']
    
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            pdf_path = os.path.join(directory, os.path.splitext(filename)[0] + '.pdf')
            has_pdf = os.path.exists(pdf_path)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = json.load(file)
                    for document in content.get('document', []):
                        docu_type = document.get('docu_type')
                        if selected_type == '전체' and docu_type not in ['출장신청서', '회의록']:
                            continue
                        if (selected_type == '전체' or docu_type == selected_type):
                            doc_result = {
                                '파일명': filename,
                                '페이지 번호': document.get('page_num'),
                                '문서 유형': docu_type,
                                'PDF 경로': pdf_path if has_pdf else None
                            }
                            if docu_type == '출장신청서':
                                for field in fields_travel:
                                    field_content = document.get('contents', {}).get(field, {}).get('content', 'empty')
                                    if field_content == '':
                                        field_content = 'null'
                                    doc_result[field] = field_content
                            elif docu_type == '회의록':
                                for field in fields_meeting:
                                    field_content = document.get('contents', {}).get(field, 'empty')
                                    if isinstance(field_content, dict):
                                        field_content = field_content.get('content', 'empty')
                                        if field_content == '':
                                            field_content = 'null'
                                        doc_result[field] = field_content
                                    elif field == '항목' and isinstance(field_content, list):
                                        items_content = []
                                        for item in field_content:
                                            item_result = {}
                                            for subfield in subfields_meeting:
                                                subfield_content = item.get(subfield, {}).get('content', 'empty')
                                                if subfield_content == '':
                                                    subfield_content = 'null'
                                                item_result[subfield] = subfield_content
                                            items_content.append(item_result)
                                        doc_result[field] = items_content
                                    else:
                                        doc_result[field] = 'empty'
                            results[filename].append(doc_result)
            except Exception as e:
                messagebox.showerror("오류", f"{filename} 파일을 처리하는 중 오류가 발생했습니다: {e}")
    
    return results

def select_directory(entry_directory):
    directory = filedialog.askdirectory()
    entry_directory.delete(0, tk.END)
    entry_directory.insert(0, directory)

def display_results(result_list, text_results):
    text_results.delete(1.0, tk.END)
    if not result_list:
        text_results.insert(tk.END, "검색 결과가 없습니다.", "content")
        return
    for result in result_list:
        text_results.insert(tk.END, f"파일명: {result['파일명']}\n", "filename")
        text_results.insert(tk.END, f"문서 유형: {result['문서 유형']}\n", "doctype")
        text_results.insert(tk.END, f"페이지 번호: {result['페이지 번호']}\n", "pagenum")
        for key, value in result.items():
            if key not in ['파일명', '문서 유형', '페이지 번호', 'PDF 경로']:
                if key == '항목' and isinstance(value, list):
                    text_results.insert(tk.END, f"  {key}:\n", "content")
                    for item in value:
                        text_results.insert(tk.END, "    - 항목:\n", "content")
                        for subkey, subvalue in item.items():
                            text_results.insert(tk.END, f"      {subkey}: {subvalue}\n", "content")
                else:
                    text_results.insert(tk.END, f"  {key}: {value}\n", "content")
        text_results.insert(tk.END, "\n")

def on_file_select(event, results, text_results):
    selected_index = event.widget.curselection()
    if selected_index:
        selected_file = event.widget.get(selected_index[0])
        display_results(results[selected_file], text_results)

def search_pattern(entry_directory, combo_doc_type, text_results, file_listbox):
    directory = entry_directory.get()
    selected_type = combo_doc_type.get()
    
    if not directory:
        messagebox.showerror("오류", "폴더 경로를 입력해주세요.")
        return
    
    results = search_in_json_files(directory, selected_type)
    
    file_listbox.delete(0, tk.END)
    unique_files = {os.path.splitext(filename)[0]: res_list for filename, res_list in results.items()}
    
    for filename in unique_files.keys():
        file_listbox.insert(tk.END, filename)
    file_listbox.bind("<<ListboxSelect>>", lambda e: on_file_select(e, unique_files, text_results))
    
    if not unique_files:
        display_results([], text_results)
    else:
        first_file = next(iter(unique_files))
        display_results(unique_files[first_file], text_results)

def open_pdf(event, path):
    webbrowser.open(path)

def create_search_tab(tab):
    label_directory = tk.Label(tab, text="폴더 선택:")
    label_directory.grid(row=0, column=0, padx=10, pady=5, sticky='w')

    entry_directory = tk.Entry(tab, width=50)
    entry_directory.grid(row=0, column=1, padx=10, pady=5, sticky='w')

    button_browse_directory = tk.Button(tab, text="탐색", command=lambda: select_directory(entry_directory))
    button_browse_directory.grid(row=0, column=2, padx=10, pady=5, sticky='w')

    label_doc_type = tk.Label(tab, text="문서 유형 선택:")
    label_doc_type.grid(row=1, column=0, padx=10, pady=5, sticky='w')

    combo_doc_type = ttk.Combobox(tab, values=['전체', '출장신청서', '회의록'], state='readonly')
    combo_doc_type.current(0)
    combo_doc_type.grid(row=1, column=1, padx=10, pady=5, sticky='w')

    button_search = tk.Button(tab, text="검색", command=lambda: search_pattern(entry_directory, combo_doc_type, text_results, file_listbox), width=20, bg='blue', fg='white')
    button_search.grid(row=1, column=2, padx=10, pady=5, sticky='w')

    frame_results = tk.Frame(tab)
    frame_results.grid(row=2, column=0, columnspan=3, rowspan=2, padx=10, pady=10, sticky="nsew")

    text_results = tk.Text(frame_results, height=20, width=80)
    text_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame_results, command=text_results.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_results.config(yscrollcommand=scrollbar.set)

    frame_file_list = tk.Frame(tab)
    frame_file_list.grid(row=0, column=3, rowspan=4, padx=10, pady=10, sticky="nsew")

    file_listbox = tk.Listbox(frame_file_list, height=40, width=30)
    file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar_file_list = tk.Scrollbar(frame_file_list, command=file_listbox.yview)
    scrollbar_file_list.pack(side=tk.RIGHT, fill=tk.Y)

    file_listbox.config(yscrollcommand=scrollbar_file_list.set)

    text_results.tag_config("filename", font=("Helvetica", 12, "bold"))
    text_results.tag_config("hyperlink", foreground="blue", underline=True)
    text_results.tag_config("doctype", font=("Helvetica", 10, "bold"), foreground="purple")
    text_results.tag_config("pagenum", font=("Helvetica", 10, "italic"), foreground="green")
    text_results.tag_config("content", font=("Helvetica", 10), foreground="black")

    tab.grid_rowconfigure(2, weight=1)
    tab.grid_columnconfigure(3, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("JSON 파일 검색")

    tab_control = ttk.Notebook(root)
    tab = ttk.Frame(tab_control)
    tab_control.add(tab, text='JSON 파일 검색')
    tab_control.pack(expand=1, fill='both')

    create_search_tab(tab)

    root.mainloop()
