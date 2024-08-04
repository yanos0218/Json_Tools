**용도**
- Json 확장자 File 대상으로 File 내의 특정 문자를 정규식 패턴으로 찾기 위함임

**설명**
- main_ui.py
  - main UI로 각 Tab에 대한 정보를 가져다가 활용한다
  - 각 Tab의 기능의 Code를 개별적 관리하기 위함
- file_tab.py
  - 검색 대상 폴더 내의 Json File 중 특정 문자를 찾아서 지정한 폴더로 이동할 수 있도록한 기능
- count_tab.py
  - 검색 대상 폴더 내의 Json File 중 특정 문자가 파일 별로 몇 개가 있는지 보여주는 기능
  - 검색된 결과물을 '.csv' 확장자로 저장하며, 저장된 내용 중 File에 대한 각 경로는 하이퍼링크되어 있음
    - 동일한 폴더 내에 '.pdf' 확장자가 있다면 하이퍼링크를 이용해서 열어볼 수 있음
  - 검색된 결과물 중 삭제하고 싶은 대상만 선택해서 삭제하는 기능
- FileInfo_tab.py
  - 검색 대상 폴더 내 Json File 중 전체 Page 정보("total_page": "##")를 제공
  - 분류 항목("docu_type": "###",)과 분류 항목이 몇 개 있는지 제공
    - 상단 Column Name은 검색된 분류 항목으로 제공함('FileName', 'Total Page' 제외)
    - 분류 항목("docu_type": "###",) 중 '미분류'라는 문자가 있는 경우 'Total Page' 오른쪽 Column에 위치함
  - 검색된 결과물을 '.csv' 확장자로 저장하며, 저장된 내용 중 File에 대한 각 경로는 하이퍼링크되어 있음
- file_version_info.txt
  - File 속성 정보
  - 제품 전체 중 일부 File의 Code가 변경된 경우 버전은 수정됨
- KeyValue_keit_tab
  - KEIT 전용 Tab 생성
  - 기능
   > 문서 유형 별 검색
   >> 출장신청서, 회의록, 카드매출전표, 출장결과보고서, 출입국확인서류, 초과근무확인내역서류, 중앙장비심의위원회공문, 연구참여확약서, 수입세금계산서, 국가연구시설장비등록증&산업기술개발장비등록증, 교육수료증, 과제참여계약서, 건강보험자격득실확인서, 전자세금계산서, 수입신고내역서
   > PDF 및 원본 보기 기능
   > 삭제 기능
   >> 삭제 시 json 파일만 있는 경우 json만 삭제하고 pdf가 같이 있음 pdf와 함께 삭제

**etc**
- '.exe' 생성 명령어
  - pyinstaller --onefile --windowed main_ui.py --version-file file_version_info.txt

**release**
- v1.0.0.2
# KeyValue_keit_tab 기능 추가

- v1.0.0.1
# file_tab, count_tab, FileInfo_tab 기능 추가
# File Version 관리