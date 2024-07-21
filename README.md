용도
- Json 확장자 File 대상으로 File 내의 특정 문자를 정규식 패턴으로 찾기 위함임

설명
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
- file_version_info.txt
  - File 속성 정보

etc
- '.exe' 생성 명령어
  - pyinstaller --onefile --windowed main_ui.py --version-file file_version_info.txt
