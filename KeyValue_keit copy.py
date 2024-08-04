import json
import os
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
import concurrent.futures
import gc

# 항목 정보 관리
documents_structure = {
    "documents_1": {
        "Title": "출장신청서",
        "fields": ['신청일', '문서번호', '출장자 성명', '출장자 소속', '출장자 직위', '출장기간', '출장목적지', '출장목적', '출장내용', '출장결과'],
        "subfields": {}
    },
    "documents_2": {
        "Title": "회의록",
        "fields": ['회의날짜', '회의장소', '참여자 성명', '참여자 소속', '회의주제', '항목'],
        "subfields": {
            "항목": ['참여자소속', '참석자소속', '회의주제']
        }
    },
    "documents_3": {
        "Title": "카드매출전표",
        "fields": ['카드사명', '카드번호', '카드이용일', '카드매입사', '가맹점번호', '가맹점명', '가맹점업종', '공급액', '부가세', '합계금액'],
        "subfields": {}
    },
    "documents_4": {
        "Title": "출장결과보고서",
        "fields": ['기안일', '문서번호', '출장자 성명', '출장자 소속', '출장자 직위', '출장기간', '출장목적지', '출장목적', '출장내용', '출장결과'],
        "subfields": {}
    },
    "documents_5": {
        "Title": "출입국확인서류",
        "fields": ['문서확인번호', '발급번호', '성명', '주민등록번호', '성별', '국적', '여권번호', '출입국일자', '조회기간', '신청인', '발급일', '발급기관'],
        "subfields": {
            "출입국일자": ['출국(Depature)정보1', '입국(Entry)정보1', '출국(Depature)정보2', '입국(Entry)정보2']
        }
    },
    "documents_6": {
        "Title": "초과근무확인내역서류",
        "fields": {
            "field_1": ['성명', '초과근무일자', '초과근무시간', '업무내용'],
            "field_2": ['초과근무자정보']
        },
        "subfields": {
            "초과근무자정보": ['성명', '소속', '직급', '초과근무시간', '업무내용', '초과근무일자', '퇴근시간', '초과근무시간(부터)', '초과근무시간(까지)']
        }
    },
    "documents_7": {
        "Title": "중앙장비심의위원회공문",
        "fields": {
            "field_1": ['과제정보', '장비정보', '심의결과'],
            "field_2": ['심의일자', '심의번호', '심의항목', '요청내용(백만원)', '최종결과(백만원)']
        },
        "subfields": {
            '과제정보': ['관리전담기관', '과제번호', '사업명', '과제명', '주관기관', '총괄책임자', '참여기관', '총사업기간', '당해년도사업기간'],
            '장비정보': ['심의번호', '도입예상가격', '장비명', '심의신청기관'],
            '심의결과': ['심의일자', '심의결과', '종합의견 및 검토의견'],
            '심의항목': ['순번', '심의시설장비', '시설장비명', '담당부처', '세부사업', '내역사업', '과제명', '유형', '단가', '수량', '총금액'],
            '요청내용(백만원)': ['년도', '정부예산요구액', '자체부담금(요청)', '합계(요청내용)'],
            '최종결과(백만원)': ['심의결과', '정부예산인정', '자체부담금(최종)', '합계(최종결과)', '정부예산삭감']
        }
    },
    "documents_8": {
        "Title": "연구참여확약서",
        "fields": ['학생연구자 인적사항', '연구참여자정보', '계약일', '연구책임자(성명)', '연구책임자(소속)', '연구책임자(직급)', '연구책임자(연락처)', '연구책임자(이메일)', '연구과제명', '연구지원기관명', '연구기간', '계약기관'],
        "subfields": {
            "학생연구자 인적사항": ['성명', '학번', '생년월일', '소속(학과명)', '과정', '과학기술(국가연구)인번호', '주소', '연락처', '이메일'],
            "연구참여자정보": ['참여기간', '참여과제명', '담당업무', '참여율', '학생인건비지급액', '학생인건비지급일', '지급방법', '계정책임자(성명)', '계정책임자(소속)', '계정책임자(직급)', '계정책임자(연락처)', '계정책임자(이메일)']
        }
    }
}

# 정렬 함수
def sort_items(items, key):
    return sorted(items, key=lambda x: x.get(key, ''))

# 특정 필드의 내용을 추출하는 함수
def get_field_content(field_content):
    if isinstance(field_content, dict):
        content = field_content.get('content', 'empty')
        return 'null' if not content.strip() else content
    elif isinstance(field_content, list):
        return ['null' if not item.get('content', 'empty').strip() else item.get('content', 'empty') for item in field_content]
    elif isinstance(field_content, str):
        return 'null' if not field_content.strip() else field_content
    return 'null' if field_content == '' else field_content

# 하위 필드 콘텐츠 추출 함수
def extract_subfield_content(item, subfields):
    item_result = {}
    for subfield in subfields:
        subfield_content = item.get(subfield, {}).get('content', 'empty')
        if subfield_content == '' or subfield_content.isspace():
            subfield_content = 'null'
        item_result[subfield] = subfield_content
    return item_result

# 중앙장비심의위원회공문의 field_2 항목을 처리하는 함수
def process_central_equipment_committee(document, fields, subfields):
    result = {}
    for field in fields:
        field_content = document.get('contents', {}).get(field, 'empty')
        if isinstance(field_content, dict):
            field_content = field_content.get('content', 'empty')
        elif isinstance(field_content, list):
            items_content = [extract_subfield_content(item, subfields.get(field, [])) for item in field_content]
            if field == '심의항목':
                items_content = sort_items(items_content, '순번')
            elif field == '요청내용(백만원)':
                items_content = sort_items(items_content, '년도')
            elif field == '최종결과(백만원)':
                items_content = sort_items(items_content, '심의결과')
            field_content = items_content
        result[field] = field_content
    return result

# 초과근무확인내역서류를 처리하는 함수
def process_overtime_document(document, fields, subfields):
    result = {}
    first_field = list(document.get('contents', {}).keys())[0] if document.get('contents', {}) else ''

    fields_to_process = fields["field_1"] if first_field in fields["field_1"] else fields["field_2"]

    if fields_to_process == fields["field_1"]:
        for field in fields_to_process:
            field_content = document.get('contents', {}).get(field, 'empty')
            result[field] = get_field_content(field_content)
    else:
        items_content = []
        for page in document.get('document', []):
            if 'contents' in page and '초과근무자정보' in page['contents']:
                for item in page['contents']['초과근무자정보']:
                    item_result = extract_subfield_content(item, subfields.get('초과근무자정보', []))
                    items_content.append(item_result)
        result['초과근무자정보'] = items_content if items_content else 'empty'
    
    return result

# 문서 처리 함수 수정
def process_document(document, doc_index):
    doc_info = documents_structure.get(doc_index, {})
    result = {}
    fields = doc_info.get("fields", [])
    subfields = doc_info.get("subfields", {})

    # 중앙장비심의위원회공문의 경우 첫 번째 필드로 구분
    if doc_info.get("Title") == "중앙장비심의위원회공문":
        first_field = list(document.get('contents', {}).keys())[0] if document.get('contents', {}) else ''
        fields = doc_info["fields"]["field_1"] if first_field == '과제정보' else doc_info["fields"]["field_2"]
        return process_central_equipment_committee(document, fields, subfields)
    
    elif doc_info.get("Title") == "초과근무확인내역서류":
        first_field = list(document.get('contents', {}).keys())[0] if document.get('contents', {}) else ''
        fields_to_process = fields["field_1"] if first_field in fields["field_1"] else fields["field_2"]

        for field in fields_to_process:
            field_content = document.get('contents', {}).get(field, 'empty')
            if isinstance(field_content, dict):
                field_content = field_content.get('content', 'empty')
            elif isinstance(field_content, list):
                items_content = [extract_subfield_content(item, subfields.get(field, [])) for item in field_content]
                field_content = items_content
            result[field] = field_content

    else:
        for field in fields:
            field_content = document.get('contents', {}).get(field, 'empty')
            result[field] = get_field_content(field_content)

        # 예외 처리
        if doc_info.get("Title") == "회의록":
            result['항목'] = []
            for item in document.get('contents', {}).get('항목', []):
                item_result = extract_subfield_content(item, subfields.get('항목', []))
                result['항목'].append(item_result)
            if not result['항목']:
                result['항목'] = 'empty'

        elif doc_info.get("Title") == "출입국확인서류":
            result['출입국일자'] = []
            for item in document.get('contents', {}).get('출입국일자', []):
                item_result = extract_subfield_content(item, subfields.get('출입국일자', []))
                result['출입국일자'].append(item_result)
            if not result['출입국일자']:
                result['출입국일자'] = 'empty'

    return result

# JSON 파일에서 검색하는 함수
def search_in_json_files(directory, selected_type):
    results = defaultdict(list)
    json_files = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.endswith('.json')]

    def process_file(file_path):
        filename = os.path.basename(file_path)
        pdf_path = os.path.join(directory, os.path.splitext(filename)[0] + '.pdf')
        has_pdf = os.path.exists(pdf_path)
        file_results = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = json.load(file)
                if not content:
                    messagebox.showerror("오류", f"{filename} 파일을 처리하는 중 오류가 발생했습니다: 파일이 비어 있습니다.")
                    return []

                for document in content.get('document', []):
                    docu_type = document.get('docu_type')
                    if selected_type == '전체' or docu_type == selected_type:
                        for doc_index, doc_info in documents_structure.items():
                            if docu_type == doc_info["Title"]:
                                doc_result = process_document(document, doc_index)
                                doc_result.update({
                                    '파일명': filename,
                                    '페이지 번호': document.get('page_num'),
                                    '문서 유형': docu_type,
                                    'PDF 경로': pdf_path if has_pdf else None
                                })
                                file_results.append(doc_result)
            # 처리 후 메모리 해제
            del content
            gc.collect()
        except json.JSONDecodeError as e:
            messagebox.showerror("오류", f"{filename} 파일을 처리하는 중 JSON 오류가 발생했습니다: {e}")
        except FileNotFoundError as e:
            messagebox.showerror("오류", f"{filename} 파일을 찾을 수 없습니다: {e}")
        except Exception as e:
            messagebox.showerror("오류", f"{filename} 파일을 처리하는 중 오류가 발생했습니다: {e}")
        return file_results

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(process_file, file): file for file in json_files}
        for future in concurrent.futures.as_completed(future_to_file):
            file_results = future.result()
            if file_results:
                results[os.path.basename(future_to_file[future])] = file_results

    return results

# 디렉토리 선택 함수
def select_directory(entry_directory):
    directory = filedialog.askdirectory()
    entry_directory.delete(0, tk.END)
    entry_directory.insert(0, directory)

# 결과를 텍스트 위젯에 표시하는 함수
def display_results(result_list, text_results):
    text_results.delete(1.0, tk.END)
    if not result_list:
        text_results.insert(tk.END, "검색 결과가 없습니다.", "content")
        return
    
    current_filename = None
    for result in result_list:
        if result['파일명'] != current_filename:
            current_filename = result['파일명']
            if result['PDF 경로']:
                text_results.insert(tk.END, f"파일명: {result['파일명']}\n", "pdf_filename")
            else:
                text_results.insert(tk.END, f"파일명: {result['파일명']}\n", "filename")
        
        text_results.insert(tk.END, f"문서 유형: {result['문서 유형']}\n", "doctype")
        text_results.insert(tk.END, f"페이지 번호: {result['페이지 번호']}\n", "pagenum")
        for key, value in result.items():
            if key not in ['파일명', '문서 유형', '페이지 번호', 'PDF 경로']:
                if key in ['출입국일자', '과제정보', '장비정보', '심의결과', '심의항목', '요청내용(백만원)', '최종결과(백만원)'] and isinstance(value, list):
                    text_results.insert(tk.END, f"  {key}:\n", "content")
                    for item in value:
                        for subkey, subvalue in item.items():
                            text_results.insert(tk.END, f"      {subkey}: {subvalue}\n", "subcontent")
                elif key in ['항목', '초과근무자정보', '과제정보', '장비정보', '심의결과', '심의항목', '요청내용(백만원)', '최종결과(백만원)'] and isinstance(value, list):
                    text_results.insert(tk.END, f"  {key}:\n", "content")
                    for item in value:
                        text_results.insert(tk.END, "    - 항목:\n", "content")
                        for subkey, subvalue in item.items():
                            text_results.insert(tk.END, f"      {subkey}: {subvalue}\n", "subcontent")
                else:
                    text_results.insert(tk.END, f"  {key}: {value}\n", "content")
        text_results.insert(tk.END, "\n")

# 리스트박스에서 파일 선택 이벤트 처리 함수
def on_file_select(event, results, text_results):
    selected_index = event.widget.curselection()
    if selected_index:
        selected_file = event.widget.get(selected_index[0])
        display_results(results[selected_file], text_results)

# 검색 패턴을 시작하는 함수
def search_pattern(entry_directory, combo_doc_type, text_results, file_listbox):
    directory = entry_directory.get()
    selected_type = combo_doc_type.get()
    
    if not directory:
        messagebox.showerror("오류", "폴더 경로를 입력해주세요.")
        return
    
    results = search_in_json_files(directory, selected_type)
    
    file_listbox.delete(0, tk.END)
    unique_files = {os.path.splitext(filename)[0]: res_list for filename, res_list in results.items()}
    
    sorted_files = sorted(unique_files.keys())  # 오름차순 정렬
    for filename in sorted_files:
        file_listbox.insert(tk.END, filename)
    file_listbox.bind("<<ListboxSelect>>", lambda e: on_file_select(e, unique_files, text_results))
    
    if not unique_files:
        display_results([], text_results)
    else:
        first_file = sorted_files[0]
        display_results(unique_files[first_file], text_results)  # 첫 번째 파일의 내용을 표시

# 파일 삭제 함수
def delete_selected_file(file_listbox, text_results, entry_directory):
    selected_index = file_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("경고", "삭제할 파일을 선택하세요.")
        return
    
    selected_file = file_listbox.get(selected_index[0])
    file_path = os.path.join(entry_directory.get(), selected_file + '.json')
    pdf_path = os.path.join(entry_directory.get(), selected_file + '.pdf')
    
    # 삭제 확인 메시지
    confirm = messagebox.askyesno("확인", f"{selected_file}.json 파일을 삭제하시겠습니까?")
    if confirm:
        try:
            os.remove(file_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            messagebox.showinfo("정보", f"{selected_file}.json 파일이 삭제되었습니다.")
            file_listbox.delete(selected_index)
            text_results.delete(1.0, tk.END)
        except Exception as e:
            messagebox.showerror("오류", f"파일 삭제 중 오류가 발생했습니다: {e}")

# PDF 보기 함수
def view_pdf(file_listbox, entry_directory):
    selected_index = file_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("경고", "PDF를 볼 파일을 선택하세요.")
        return
    
    selected_file = file_listbox.get(selected_index[0])
    pdf_path = os.path.join(entry_directory.get(), selected_file + '.pdf')
    
    if os.path.exists(pdf_path):
        webbrowser.open(pdf_path)
    else:
        messagebox.showerror("오류", f"{selected_file}.pdf 파일을 찾을 수 없습니다.")

# PDF 파일을 기본 웹 브라우저에서 여는 함수
def open_pdf(path):
    webbrowser.open(path)

# 검색 탭을 생성하는 함수
def create_KeyValue_keit_tab(tab):
    label_directory = tk.Label(tab, text="폴더 선택:")
    label_directory.grid(row=0, column=0, padx=10, pady=5, sticky='w')

    entry_directory = tk.Entry(tab, width=50)
    entry_directory.grid(row=0, column=1, padx=10, pady=5, sticky='w')

    button_browse_directory = tk.Button(tab, text="탐색", command=lambda: select_directory(entry_directory))
    button_browse_directory.grid(row=0, column=2, padx=10, pady=5, sticky='w')

    label_doc_type = tk.Label(tab, text="문서 유형 선택:")
    label_doc_type.grid(row=1, column=0, padx=10, pady=5, sticky='w')

    # "전체" 항목을 상위에 두고, 나머지 항목은 오름차순으로 정렬
    doc_types = ['전체'] + sorted([info['Title'] for key, info in documents_structure.items()])
    combo_doc_type = ttk.Combobox(tab, values=doc_types, state='readonly')
    combo_doc_type.current(0)
    combo_doc_type.grid(row=1, column=1, padx=10, pady=5, sticky='w')

    button_delete = tk.Button(tab, text="삭제하기", command=lambda: delete_selected_file(file_listbox, text_results, entry_directory), width=20, bg='red', fg='white')
    button_delete.grid(row=2, column=0, padx=10, pady=5, sticky='w')

    button_view_pdf = tk.Button(tab, text="PDF보기", command=lambda: view_pdf(file_listbox, entry_directory), width=20, bg='green', fg='white')
    button_view_pdf.grid(row=2, column=1, padx=10, pady=5, sticky='w')

    button_search = tk.Button(tab, text="검색", command=lambda: search_pattern(entry_directory, combo_doc_type, text_results, file_listbox), width=20, bg='blue', fg='white')
    button_search.grid(row=2, column=2, padx=10, pady=5, sticky='w')

    frame_results = tk.Frame(tab)
    frame_results.grid(row=3, column=0, columnspan=3, rowspan=2, padx=10, pady=10, sticky="nsew")

    text_results = tk.Text(frame_results, height=20, width=80)
    text_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame_results, command=text_results.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_results.config(yscrollcommand=scrollbar.set)

    frame_file_list = tk.Frame(tab)
    frame_file_list.grid(row=0, column=3, rowspan=5, padx=10, pady=10, sticky="nsew")

    file_listbox = tk.Listbox(frame_file_list, height=40, width=30)
    file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar_file_list = tk.Scrollbar(frame_file_list, command=file_listbox.yview)
    scrollbar_file_list.pack(side=tk.RIGHT, fill=tk.Y)

    file_listbox.config(yscrollcommand=scrollbar_file_list.set)

    text_results.tag_config("filename", font=("Helvetica", 12, "bold"), foreground="black")
    text_results.tag_config("pdf_filename", font=("Helvetica", 12, "bold"), foreground="blue")
    text_results.tag_config("doctype", font=("Helvetica", 10, "bold"), foreground="purple")
    text_results.tag_config("pagenum", font=("Helvetica", 10, "italic"), foreground="green")
    text_results.tag_config("content", font=("Helvetica", 10), foreground="black")
    text_results.tag_config("subcontent", font=("Helvetica", 10, "italic"), foreground="grey")

    tab.grid_rowconfigure(3, weight=1)
    tab.grid_columnconfigure(3, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("JSON 파일 검색")

    tab_control = ttk.Notebook(root)
    tab5 = ttk.Frame(tab_control)
    tab_control.add(tab5, text='JSON 파일 검색')
    tab_control.pack(expand=1, fill='both')

    create_KeyValue_keit_tab(tab5)

    root.mainloop()
