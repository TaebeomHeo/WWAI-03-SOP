# RowDataExcel Module

## 개요
`rowdata_excel.py`는 삼성 SmartThings 프로젝트의 Excel 데이터를 처리하는 핵심 모듈입니다. 이 모듈은 Excel 파일에서 테스트 데이터를 로드하고, 국가별 데이터 매핑 및 포맷팅을 수행하여 최종 결과 데이터를 생성합니다.

## 주요 기능

### 1. Excel 데이터 로드 및 처리
- Excel 파일에서 테스트 데이터를 로드
- 컬럼명을 의미있는 이름으로 변경 (storyIdRank1, main_headline 등)
- 데이터 정리 및 전처리

### 2. 국가별 데이터 매핑
- 여러 국가(DE, FR, ES, IT)의 데이터를 처리
- 각 국가별로 데이터를 복사하여 생성
- 국가별 특화된 콘텐츠 매핑

### 3. 우산(Umbrella) 파일 처리
- HQ Suggestion과 Local 버전 간의 데이터 매핑
- 템플릿 변수 치환 ({Name}, {Device 1} 등)
- 국가별 맞춤형 콘텐츠 생성

### 4. 콘텐츠 매핑
- 스토리 데이터의 제목과 설명 추출
- 섹션별 데이터 처리 (1, 2, 3, 4 섹션 지원)
- 추천 제품 정보 매핑

## 클래스 구조

### RowDataExcel 클래스

#### 초기화 매개변수
```python
def __init__(self, row_file_path, contents_file_path, umbrella_file_path, country_code, 
             tc_sheet_name, usecols, banner_text, banner_link_text, banner_hyperlink, header_row=2)
```

**매개변수 상세 설명:**
- `row_file_path`: 메인 테스트 데이터 Excel 파일 경로 (예: "Test data matrix (Umbrella merge).xlsx")
- `contents_file_path`: 콘텐츠 매핑 파일들이 저장된 디렉토리 경로 (예: "contents/")
- `umbrella_file_path`: 우산(umbrella) 파일들이 저장된 디렉토리 경로 (예: "umbrella/")
- `country_code`: 처리할 국가 코드 리스트 (예: ['DE','FR','ES','IT'])
- `tc_sheet_name`: Excel 시트 이름 (예: "Test Cases")
- `usecols`: 사용할 Excel 컬럼 (예: 'C,U,V,X,Y,Z')
- `banner_text`: 기본 배너 텍스트 (예: "기본 배너")
- `banner_link_text`: 기본 배너 링크 텍스트 (예: "링크 텍스트")
- `banner_hyperlink`: 기본 배너 하이퍼링크 (예: "https://example.com")
- `header_row`: Excel 헤더 행 번호 (기본값: 2, 세 번째 행을 헤더로 사용)

#### 인스턴스 변수
```python
# 파일 경로 관련
self.row_file_path = row_file_path          # 메인 Excel 파일 경로
self.umbrella_file_path = umbrella_file_path # 우산 파일 디렉토리 경로
self.contents_file_path = contents_file_path # 콘텐츠 파일 디렉토리 경로

# 설정 관련
self.country_code = country_code            # 국가 코드 리스트
self.tc_sheet_name = tc_sheet_name          # Excel 시트명
self.usecols = usecols                      # 사용할 Excel 컬럼
self.header_row = header_row                # 헤더 행 번호

# 데이터 저장용
self.df_rowdata = None                      # 원본 Excel 데이터 DataFrame
self.df_result = pd.DataFrame()             # 최종 결과 DataFrame
self.df_list = []                           # 중간 처리용 DataFrame 리스트
self.new_row = pd.DataFrame()               # 새 행 데이터
self.next_row = pd.DataFrame()              # 다음 행 데이터

# 배너 관련
self.banner_text = banner_text              # 기본 배너 텍스트
self.banner_link_text = banner_link_text    # 기본 배너 링크 텍스트
self.banner_hyperlink = banner_hyperlink    # 기본 배너 하이퍼링크
```

## 메서드 상세 설명

### 1. load_excel()
Excel 파일을 로드하고 컬럼명을 리네이밍하는 함수입니다.

**동작 과정:**
1. 지정된 Excel 파일을 읽어서 DataFrame으로 저장
2. 컬럼명을 의미있는 이름으로 변경:
   - 첫 번째 컬럼 → 'Account'
   - 두 번째 컬럼 → 'storyIdRank1'
   - 세 번째 컬럼 → 'storyIdRank1N'
   - 네 번째 컬럼 → 'main_headline'
   - 다섯 번째 컬럼 → 'main_description1'
   - 여섯 번째 컬럼 → 'main_description2'

**코드 예시:**
```python
def load_excel(self):
    self.df_rowdata = pd.read_excel(
        self.row_file_path,
        sheet_name=self.tc_sheet_name,
        header=self.header_row,
        usecols=self.usecols
    )
    
    # 컬럼 이름 리네이밍 - Excel의 실제 컬럼 위치에 따라 매핑
    self.df_rowdata.rename(columns={
        self.df_rowdata.columns[0]: 'Account',           # 첫 번째 컬럼을 Account로 변경
        self.df_rowdata.columns[1]: 'storyIdRank1',      # 두 번째 컬럼을 storyIdRank1로 변경
        self.df_rowdata.columns[2]: 'storyIdRank1N',     # 세 번째 컬럼을 storyIdRank1N로 변경
        self.df_rowdata.columns[3]: 'main_headline',     # 네 번째 컬럼을 main_headline로 변경
        self.df_rowdata.columns[4]: 'main_description1', # 다섯 번째 컬럼을 main_description1로 변경
        self.df_rowdata.columns[5]: 'main_description2'  # 여섯 번째 컬럼을 main_description2로 변경
    }, inplace=True)
```

**반환값:** 없음 (self.df_rowdata에 결과 저장)

### 2. process_rows(max_rows=2)
Excel 행 데이터를 처리하여 결과 DataFrame을 생성하는 함수입니다.

**매개변수:**
- `max_rows`: 처리할 최대 행 수 (기본값: 2)

**동작 과정:**
1. 유효한 Account가 있는 행을 찾아서 기본 행으로 설정
2. 다음 행들을 storyIdRank2, storyIdRank3 등으로 매핑
3. 필요한 모든 컬럼을 생성하고 기본값 설정
4. 줄바꿈 문자를 공백으로 치환하여 데이터 정리

**코드 예시:**
```python
def process_rows(self, max_rows=2):
    story_prefix = 'storyIdRank'  # 스토리 ID 접두사
    num = 1  # 스토리 순번

    for i in range(min(max_rows, len(self.df_rowdata))):
        row = self.df_rowdata.iloc[i]  # 현재 행 데이터
       
        if pd.notna(row['Account']) and row['Account'] != "":  # 유효한 데이터 행
            # 줄바꿈 문자를 공백으로 치환하여 데이터 정리
            row = row.map(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x)
            self.new_row = pd.DataFrame([row])
        
            # 결과 DataFrame에 새 행 추가
            self.df_result = pd.concat([self.df_result, self.new_row], ignore_index=True)           
            num = 1  # 스토리 순번 초기화
            
        else:
            # Account가 비어있는 행은 이전 행의 추가 스토리 데이터로 처리
            num += 1
            next_row = row
            story_key = f"{story_prefix}{num}"  # storyIdRank2, storyIdRank3 등
            story_keyN = f"{story_prefix}{num}N"  # storyIdRank2N, storyIdRank3N 등

            if(pd.isna(next_row['storyIdRank1']) or next_row['storyIdRank1']=='-'):
                self.df_result.at[self.df_result.index[-1], story_key] = "없음"
            else:    
                self.df_result.at[self.df_result.index[-1], story_key] = next_row['storyIdRank1']

            if(pd.isna(next_row['storyIdRank1N']) or next_row['storyIdRank1N']=='-'):
                self.df_result.at[self.df_result.index[-1], story_key+'N'] = "없음"
            else:    
                self.df_result.at[self.df_result.index[-1], story_key+'N'] = next_row['storyIdRank1N']
```

**target_columns 구조:**
```python
target_columns = [
    # 스토리 ID 관련
    'storyIdRank1','storyIdRank2','storyIdRank3',
    'storyIdRank1N','storyIdRank2N','storyIdRank3N',
    
    # 스토리 제목/설명
    'storyIdRank1_title', 'storyIdRank1_desc',
    'storyIdRank1_rec1','storyIdRank1_rec2','storyIdRank1_rec3','storyIdRank1_rec4','storyIdRank1_rec5',
    'storyIdRank2_title', 'storyIdRank2_desc',
    'storyIdRank2_rec1','storyIdRank2_rec2','storyIdRank2_rec3','storyIdRank2_rec4','storyIdRank2_rec5',
    'storyIdRank3_title', 'storyIdRank3_desc',
    'storyIdRank3_rec1','storyIdRank3_rec2','storyIdRank3_rec3','storyIdRank3_rec4','storyIdRank3_rec5',
    
    # 라이프스타일 및 시나리오
    'lifeStyleIdRank1','lifeStyleIdRank2','Scenariokeyword1','Scenariokeyword2',
    
    # 국가 및 디바이스 정보
    'country_code','Device1','Device2',
    
    # 배너 관련
    'banner_text', 'banner_link_text','banner_hyperlink'
]
```

**기본값 설정 로직:**
```python
for col in target_columns:
    if col not in self.df_result.columns:
        if col == 'banner_text':
            self.df_result[col] = self.banner_text
        elif col == 'banner_link_text':
            self.df_result[col] = self.banner_link_text
        elif col == 'banner_hyperlink':  
            self.df_result[col] = self.banner_hyperlink
        else:
            self.df_result[col] = "없음"
```

**반환값:** 없음 (self.df_result에 결과 저장)

### 3. copy_format_data()
국가별 데이터 복사 함수입니다.

**동작 과정:**
1. 첫 번째 국가는 원본 데이터에 그대로 적용
2. 나머지 국가들은 데이터를 복사하여 각 국가별로 생성
3. 예: DE, FR, ES, IT 4개 국가면 각 행이 4개씩 생성됨

**코드 예시:**
```python
def copy_format_data(self):
    copy_df_result = self.df_result.copy()  # 원본 데이터 복사
    for idx, country in enumerate(self.country_code):
        
        if(idx == 0):
            self.df_result['country_code'] = country   # 첫 번째 국가는 원본에 적용
        else:
            copy_df_result['country_code'] = country   # 나머지 국가는 복사본에 적용
            self.df_result = pd.concat([self.df_result, copy_df_result], ignore_index=True)   # 결과에 추가
    print(self.df_result)
```

**반환값:** 없음 (self.df_result에 결과 저장)

### 4. umbrella_main_mapping(main_result, country_code)
우산(umbrella) 파일을 사용하여 메인 데이터를 매핑하는 함수입니다.

**매개변수:**
- `main_result`: 웹에서 수집된 실제 데이터 DataFrame
- `country_code`: 처리할 국가 코드 리스트

**동작 과정:**
1. 각 국가별로 해당하는 umbrella 파일을 찾음
2. Excel 파일에서 '11. My SmartThings' 시트의 데이터를 읽음
3. HQ Suggestion과 일치하는 데이터를 Local 버전으로 교체
4. 템플릿 변수들을 실제 데이터로 치환 ({Name}, {Device 1} 등)

**코드 예시:**
```python
def umbrella_main_mapping(self, main_result, country_code):
    umbrella_list = os.listdir(self.umbrella_file_path)  # umbrella 디렉토리의 모든 파일 목록
    for country in country_code:
        # 해당 국가의 umbrella 파일 찾기
        for filename in umbrella_list:
            if country in filename:  # 파일명에 국가 코드가 포함되어 있으면
                cgd_file = filename
                break
            
        umbrella_full_path = os.path.join(self.umbrella_file_path, cgd_file)    
        df_umbrella = pd.read_excel(
            umbrella_full_path,
            sheet_name='11. My SmartThings',  # 특정 시트에서 데이터 읽기
            header=6,  # 7번째 행을 헤더로 사용
            usecols='H,K'  # H, K 컬럼만 사용 (HQ Suggestion, To be filled by Local)
        )

        first_col = df_umbrella.columns[0]  # 첫 번째 컬럼명 가져오기
        # 공백 제거 및 정리 (데이터 매칭을 위해)
        df_umbrella[first_col] = df_umbrella[first_col].astype(str).str.replace(" ", "").str.strip()
        
        # 각 결과 행에 대해 매핑 수행
        for idx, row in self.df_result.iterrows():
            if row['country_code'] != country:  # 해당 국가가 아니면 건너뛰기
                continue
                
            # 공백 제거 및 정리 (매칭을 위해)
            row = row.map(lambda x: x.replace(" ", "").strip() if isinstance(x, str) else x)

            # umbrella 데이터와 매칭하여 교체
            for um_idx, um_row in df_umbrella.iterrows():
                # 메인 헤드라인 매핑
                if um_row["HQ Suggestion"] == row["main_headline"]:
                    self.df_result.at[idx, "main_headline"] = um_row["To be filled by Local"]
                    value = self.df_result.at[idx, "main_headline"]
                    # {Name} 템플릿을 실제 계정명으로 치환
                    self.df_result.at[idx, "main_headline"] = value.replace("{Name}", self.df_result.at[idx, "Account"].split("@")[0])

                # 메인 설명1 매핑
                if um_row["HQ Suggestion"] == row["main_description1"]:
                    self.df_result.at[idx, "main_description1"] = um_row["To be filled by Local"]
                    value = self.df_result.at[idx, "main_description1"]
                    # 템플릿 변수들을 실제 데이터로 치환
                    value = value.replace("{Device 1}", main_result.at[idx, "Device1"])
                    value = value.replace("{Device 2}", main_result.at[idx, "Device2"])
                    value = value.replace("{lifestyle1}", main_result.at[idx, "lifeStyleIdRank1"])
                    value = value.replace("{lifestyle2}", main_result.at[idx, "lifeStyleIdRank2"])
                    value = value.replace("{Scenario keyword 1}", main_result.at[idx, "Scenariokeyword1"])
                    value = value.replace("{Scenario keyword 2}", main_result.at[idx, "Scenariokeyword2"])
                    self.df_result.at[idx, "main_description1"] = value

                # 메인 설명2 매핑
                if um_row["HQ Suggestion"] == row["main_description2"]:
                    self.df_result.at[idx, "main_description2"] = um_row["To be filled by Local"]

                # 배너 관련 매핑
                if um_row["HQ Suggestion"] == row["banner_text"]:
                    self.df_result.at[idx, "banner_text"] = um_row["To be filled by Local"]
                if um_row["HQ Suggestion"] == row["banner_link_text"]:
                    self.df_result.at[idx, "banner_link_text"] = um_row["To be filled by Local"]
                if um_row["HQ Suggestion"] == row["banner_hyperlink"]:
                    self.df_result.at[idx, "banner_hyperlink"] = um_row["To be filled by Local"]

            # main_description1과 main_description2를 합쳐서 main_description 생성
            self.df_result.at[idx,"main_description"] = str(self.df_result.at[idx,"main_description1"])+' '+ str(self.df_result.at[idx,"main_description2"])
```

**지원하는 템플릿 변수:**
- `{Name}`: 계정명 (이메일 주소의 @ 앞부분)
- `{Device 1}`: 첫 번째 디바이스 정보
- `{Device 2}`: 두 번째 디바이스 정보
- `{lifestyle1}`: 첫 번째 라이프스타일 ID
- `{lifestyle2}`: 두 번째 라이프스타일 ID
- `{Scenario keyword 1}`: 첫 번째 시나리오 키워드
- `{Scenario keyword 2}`: 두 번째 시나리오 키워드

**반환값:** 없음 (self.df_result에 결과 저장)

### 5. contents_mapping()
콘텐츠 파일을 사용하여 스토리 데이터를 매핑하는 함수입니다.

**동작 과정:**
1. contents 디렉토리의 모든 파일을 검색
2. 각 스토리 ID에 해당하는 파일을 찾음
3. 국가별 시트에서 해당 섹션의 제목과 설명을 추출
4. storyIdRank1_title, storyIdRank1_desc 등에 매핑

**섹션별 행 위치 매핑:**
| 섹션 번호 | 제목 행 | 설명 행 | Excel 행 번호 |
|-----------|---------|---------|---------------|
| 1         | 8       | 9       | 9, 10         |
| 2         | 13      | 14      | 14, 15        |
| 3         | 18      | 19      | 19, 20        |
| 4         | 23      | 24      | 24, 25        |

**코드 예시:**
```python
def contents_mapping(self):
    format_list = os.listdir(self.contents_file_path)  # contents 디렉토리의 모든 파일 목록

    # 각 결과 행에 대해 콘텐츠 매핑 수행
    for idx, row in self.df_result.iterrows():
        # storyIdRank1, storyIdRank2, storyIdRank3 각각에 대해 처리
        for value in range(1, 4):
            col = 'storyIdRank'+str(value)  # storyIdRank1, storyIdRank2, storyIdRank3
            col_title = col+'_title'  # storyIdRank1_title 등
            col_desc = col+'_desc'    # storyIdRank1_desc 등
            
            if not col in row: # 해당 데이터에 col 컬럼이 없으면 스킵
                continue
            if row[col] != '없음':  # 스토리 ID가 존재하는 경우만 처리
                # 스토리 ID에서 콘텐츠 번호와 섹션 번호 추출 (예: "1-2" -> story_con_num=1, story_sec_num=2)
                story_con_num, story_sec_num = row[col].split('-')
            else:
                continue  # 스토리 ID가 없으면 건너뛰기

            # contents 디렉토리의 모든 파일을 검색하여 매칭되는 파일 찾기
            for filename in format_list:
                # 파일명에서 숫자 추출 (예: "format001.xlsx" -> 1)
                match = re.search(r'(\d+)$', os.path.splitext(filename)[0]) # 숫자추출
               
                if match:
                    file_num = int(match.group(1).lstrip("0")) # 앞의 0 제거 후 정수로 변환
                    
                    # 파일 번호와 콘텐츠 번호가 일치하는 경우
                    if file_num == int(story_con_num):
                        format_full_path = os.path.join(self.contents_file_path, filename)
                        excel_file = pd.ExcelFile(format_full_path)
                        sheet_names = excel_file.sheet_names

                        # 국가별 시트 찾기
                        for sheet in sheet_names:
                            if row["country_code"] in sheet:  # 시트명에 국가 코드가 포함되어 있으면
                                matched_sheet = sheet

                                # C 컬럼만 읽어오기
                                df_format_data = pd.read_excel(format_full_path, sheet_name=sheet, usecols='c')
                                
                                # 섹션 번호에 따라 다른 행에서 데이터 추출
                                if int(story_sec_num) == 1:  # 섹션 1
                                    sec1_title = df_format_data.iloc[8].values[0]   # 9번째 행의 제목
                                    sec1_desc = df_format_data.iloc[9].values[0]    # 10번째 행의 설명
                                    self.df_result.at[idx, col_title] = sec1_title
                                    self.df_result.at[idx, col_desc] = sec1_desc
                                    
                                elif int(story_sec_num) == 2:  # 섹션 2
                                    sec2_title = df_format_data.iloc[13].values[0]  # 14번째 행의 제목
                                    sec2_desc = df_format_data.iloc[14].values[0]   # 15번째 행의 설명
                                    self.df_result.at[idx, col_title] = sec2_title
                                    self.df_result.at[idx, col_desc] = sec2_desc
                                    
                                elif int(story_sec_num) == 3:  # 섹션 3
                                    sec3_title = df_format_data.iloc[18].values[0]  # 19번째 행의 제목
                                    sec3_desc = df_format_data.iloc[19].values[0]   # 20번째 행의 설명
                                    self.df_result.at[idx, col_title] = sec3_title
                                    self.df_result.at[idx, col_desc] = sec3_desc
                                    
                                elif int(story_sec_num) == 4:  # 섹션 4 (새로 추가)
                                    sec4_title = df_format_data.iloc[23].values[0]  # 24번째 행의 제목
                                    sec4_desc = df_format_data.iloc[24].values[0]   # 25번째 행의 설명
                                    self.df_result.at[idx, col_title] = sec4_title
                                    self.df_result.at[idx, col_desc] = sec4_desc
                                    
                                else:  # 기타 섹션 번호 (예외 처리)
                                    print(f"Warning: Unknown section number {story_sec_num} for {col}")
                                    self.df_result.at[idx, col_title] = "섹션 정보 없음"
                                    self.df_result.at[idx, col_desc] = "섹션 정보 없음"
```

**반환값:** 없음 (self.df_result에 결과 저장)

### 6. get_result()
최종 처리된 결과 DataFrame을 반환하는 함수입니다.

**코드 예시:**
```python
def get_result(self):
    return self.df_result
```

**반환값:**
- `pd.DataFrame`: 모든 처리가 완료된 최종 결과 데이터

## 데이터 구조

### 입력 데이터 구조
**Excel 파일 구조:**
- **시트명**: "Test Cases" (기본값)
- **헤더 행**: 3번째 행 (기본값)
- **사용 컬럼**: C, U, V, X, Y, Z (기본값)
- **데이터 형식**: 
  - C: Account (계정 정보)
  - U: Story ID (스토리 식별자)
  - V: Story ID N (스토리 식별자 N)
  - X: Main Headline (메인 헤드라인)
  - Y: Main Description 1 (메인 설명 1)
  - Z: Main Description 2 (메인 설명 2)

**콘텐츠 파일 구조:**
- **파일명 형식**: "format001.xlsx", "format002.xlsx" 등
- **시트명**: 국가별 시트 (예: "DE", "FR", "ES", "IT")
- **데이터 위치**: C 컬럼의 특정 행에 제목과 설명 저장
- **섹션별 행 위치**: 섹션 번호에 따라 다른 행에서 데이터 추출

**우산 파일 구조:**
- **파일명 형식**: 국가 코드가 포함된 파일명 (예: "umbrella_DE.xlsx")
- **시트명**: "11. My SmartThings"
- **헤더 행**: 7번째 행
- **사용 컬럼**: H (HQ Suggestion), K (To be filled by Local)

### 출력 데이터 구조
**기본 컬럼:**
- `Account`: 계정 정보 (이메일 주소)
- `main_headline`: 메인 헤드라인
- `main_description`: 메인 설명 (main_description1 + main_description2)
- `main_description1`: 메인 설명 1
- `main_description2`: 메인 설명 2

**스토리 관련 컬럼:**
- `storyIdRank1/2/3`: 스토리 ID (예: "1-2", "2-1")
- `storyIdRank1N/2N/3N`: 스토리 ID N
- `storyIdRank1/2/3_title`: 스토리 제목
- `storyIdRank1/2/3_desc`: 스토리 설명
- `storyIdRank1/2/3_rec1~5`: 추천 제품들 (현재 미사용)

**라이프스타일 및 시나리오:**
- `lifeStyleIdRank1/2`: 라이프스타일 ID
- `Scenariokeyword1/2`: 시나리오 키워드

**국가 및 디바이스:**
- `country_code`: 국가 코드 (DE, FR, ES, IT)
- `Device1/2`: 디바이스 정보

**배너 정보:**
- `banner_text`: 배너 텍스트
- `banner_link_text`: 배너 링크 텍스트
- `banner_hyperlink`: 배너 하이퍼링크

## 사용 예시

### 기본 사용법
```python
# RowDataExcel 객체 생성
rowdata_excel = RowDataExcel(
    format_data_path,      # Excel 파일 경로
    contents_data_path,    # 콘텐츠 디렉토리
    umbrella_file_path,    # 우산 파일 디렉토리
    country_codes,         # 국가 코드 리스트
    tc_sheet_name,         # 시트명
    usecols,              # 사용할 컬럼
    format_banner_text,   # 배너 텍스트
    format_banner_link_text,  # 배너 링크 텍스트
    format_banner_hyperlink   # 배너 하이퍼링크
)

# 데이터 처리 과정
rowdata_excel.load_excel()           # Excel 파일 로드
rowdata_excel.process_rows(2)        # 행 데이터 처리 (최대 2행)
rowdata_excel.copy_format_data()     # 국가별 데이터 복사
rowdata_excel.contents_mapping()     # 콘텐츠 매핑

# 결과 가져오기
format_result = rowdata_excel.get_result()
```

### 고급 사용법
```python
# 사용자 정의 설정으로 객체 생성
rowdata_excel = RowDataExcel(
    row_file_path="custom_test_data.xlsx",
    contents_file_path="custom_contents/",
    umbrella_file_path="custom_umbrella/",
    country_code=['US', 'CA', 'MX'],  # 다른 국가 코드 사용
    tc_sheet_name="Custom Test Cases",
    usecols='A,C,E,G,I,K',           # 다른 컬럼 사용
    banner_text="Custom Banner",
    banner_link_text="Custom Link",
    banner_hyperlink="https://custom.com",
    header_row=1                      # 첫 번째 행을 헤더로 사용
)

# 데이터 처리 및 결과 확인
rowdata_excel.load_excel()
rowdata_excel.process_rows(5)         # 최대 5행 처리
rowdata_excel.copy_format_data()
rowdata_excel.contents_mapping()

# 결과 데이터 확인
result = rowdata_excel.get_result()
print(f"총 {len(result)} 행의 데이터가 처리되었습니다.")
print(f"국가별 데이터: {result['country_code'].value_counts()}")
```

## 의존성

- `pandas`: 데이터 처리 및 DataFrame 조작
- `os`: 파일 시스템 접근
- `re`: 정규표현식 처리

## 주의사항

1. **파일 경로**: 모든 파일 경로가 올바르게 설정되어야 합니다.
2. **Excel 파일 형식**: 지정된 시트명과 컬럼 구조를 따라야 합니다.
3. **국가 코드**: 지원되는 국가 코드만 사용해야 합니다.
4. **메모리 사용량**: 대용량 데이터 처리 시 메모리 사용량을 고려해야 합니다.
5. **파일 인코딩**: Excel 파일의 인코딩이 올바르게 설정되어야 합니다.
6. **데이터 형식**: 스토리 ID는 "숫자-숫자" 형식이어야 합니다 (예: "1-2").

## 에러 처리

- **파일이 존재하지 않는 경우**: FileNotFoundError
- **Excel 파일 형식 오류**: ValueError
- **데이터 타입 불일치**: TypeError
- **섹션 번호 오류**: 알 수 없는 섹션 번호에 대한 경고 메시지 출력
- **매칭 실패**: 데이터 매칭에 실패한 경우 기본값 사용

## 성능 최적화

- **대용량 데이터 처리**: 청크 단위 처리 고려
- **불필요한 컬럼 제거**: usecols로 필요한 컬럼만 로드
- **캐싱**: 반복 처리 최소화
- **메모리 관리**: DataFrame 복사 시 메모리 사용량 고려

## 확장 가능성

- **새로운 국가 코드 추가**: country_code 리스트에 추가
- **추가 데이터 컬럼 지원**: target_columns에 새로운 컬럼 추가
- **다양한 Excel 파일 형식 지원**: load_excel 메서드 수정
- **병렬 처리 지원**: 대용량 데이터 처리 시 멀티프로세싱 적용
- **새로운 섹션 지원**: contents_mapping에 새로운 섹션 번호 추가
- **템플릿 변수 확장**: umbrella_main_mapping에 새로운 변수 추가

## 디버깅 및 로깅

### 디버깅 정보 출력
```python
# 데이터 처리 과정 확인
print(f"로드된 Excel 데이터: {len(rowdata_excel.df_rowdata)} 행")
print(f"처리된 결과 데이터: {len(rowdata_excel.df_result)} 행")
print(f"국가별 데이터 분포: {rowdata_excel.df_result['country_code'].value_counts()}")

# 특정 컬럼 데이터 확인
print(f"스토리 ID 분포: {rowdata_excel.df_result['storyIdRank1'].value_counts()}")
print(f"메인 헤드라인 샘플: {rowdata_excel.df_result['main_headline'].head()}")
```

### 에러 로깅
```python
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 에러 발생 시 로깅
try:
    rowdata_excel.load_excel()
except Exception as e:
    logger.error(f"Excel 파일 로드 실패: {e}")
    raise
```

## 테스트 및 검증

### 데이터 검증 함수 예시
```python
def validate_data_integrity(self):
    """데이터 무결성 검증"""
    errors = []
    
    # 필수 컬럼 존재 확인
    required_columns = ['Account', 'country_code', 'main_headline']
    for col in required_columns:
        if col not in self.df_result.columns:
            errors.append(f"필수 컬럼 누락: {col}")
    
    # 데이터 타입 검증
    if not self.df_result['country_code'].isin(['DE', 'FR', 'ES', 'IT']).all():
        errors.append("잘못된 국가 코드가 포함되어 있습니다.")
    
    # 빈 값 검증
    if self.df_result['Account'].isna().any():
        errors.append("Account 컬럼에 빈 값이 있습니다.")
    
    return len(errors) == 0, errors
```

이제 `rowdata_excel.py` 모듈의 모든 함수와 변수에 대한 상세한 설명을 제공하는 완전한 README가 완성되었습니다. 