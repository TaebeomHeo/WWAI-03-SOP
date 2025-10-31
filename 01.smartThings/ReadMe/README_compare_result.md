# Compare Result Module Documentation

## 개요 (Overview)

`compare_result.py`는 포맷 데이터와 실제 추출 데이터를 비교하여 결과를 생성하는 모듈입니다. 이 모듈은 예상 데이터와 실제 추출된 데이터의 일치 여부를 비교하고, 비교 결과를 Excel 파일로 저장하며 포맷팅을 적용합니다.

## 주요 기능 (Key Features)

- **데이터 비교**: 포맷 데이터와 실제 추출 데이터의 일치 여부 확인
- **공백 제거 비교**: 공백을 제거한 상태에서 정확한 비교 수행
- **선택적 비교**: 배너 관련 컬럼은 "없음"인 경우 제외
- **Excel 결과 생성**: 비교 결과를 Excel 파일로 저장
- **포맷팅 적용**: Excel 파일의 컬럼 너비, 셀 정렬, 테두리 설정
- **추천 제품 정보 추가**: 각 계정별 추천 제품 정보를 결과에 포함

## 클래스 구조 (Class Structure)

### CompareProcess

포맷 데이터와 실제 추출 데이터를 비교하여 결과를 생성하는 메인 클래스입니다.

#### 초기화 (Initialization)

```python
def __init__(self, df_format_data, df_abs_data, df_compare_item_path, output_path, country_code):
```

**매개변수 (Parameters):**
- `df_format_data`: 포맷 데이터 DataFrame (예상 데이터)
- `df_abs_data`: 실제 추출 데이터 DataFrame
- `df_compare_item_path`: 비교 항목 Excel 파일 경로
- `output_path`: 결과 Excel 파일 저장 경로
- `country_code`: 처리할 국가 코드 리스트

**인스턴스 변수 (Instance Variables):**
- `df_abs_data`: 실제 추출된 데이터
- `df_format_data`: 포맷 데이터 (예상 데이터)
- `df_compare_item`: 비교 항목 파일 (헤더 없음)
- `country_code`: 국가 코드 리스트
- `compare_result`: 비교 결과를 저장할 DataFrame
- `merge_compare_result`: 최종 병합된 비교 결과
- `output_path`: 출력 파일 경로
- `compare_columns`: 비교할 컬럼 리스트

## 메서드 상세 설명 (Method Details)

### 1. compare_data()

```python
def compare_data(self):
```

**기능:**
- 포맷 데이터와 실제 추출 데이터를 비교
- 각 행의 각 컬럼에 대해 일치 여부를 확인
- 공백을 제거한 상태에서 비교 수행
- 배너 관련 컬럼은 "없음"인 경우 제외

**처리 과정:**

#### 1단계: 공백 제거 처리
```python
# 공백 제거한 상태의 비교 포맷 구성
format_row = self.df_format_data.loc[idx, self.compare_columns].astype(str).apply(lambda x: ''.join(x.split()))  # 포맷데이터를 공백없는 상태로 변경
abs_row = self.df_abs_data.loc[idx, self.compare_columns].astype(str).apply(lambda x: ''.join(x.split()))  # 추출데이터를 공백없는 상태로 변경
```

#### 2단계: 배너 컬럼 제외 처리
```python
# 배너 관련 컬럼이 "없음"인 경우 건너뛰기 (배너는 선택적 표시)
if abs_row[col] == "없음" and col == 'banner_text':
    continue
elif abs_row[col] == "없음" and col == 'banner_link_text':
    continue
elif abs_row[col] == "없음" and col == 'banner_hyperlink':
    continue
```

#### 3단계: 데이터 비교 및 결과 저장
```python
if format_row[col] == abs_row[col]:  # 데이터 비교 - 일치하는 경우
    self.compare_result.loc[len(self.compare_result)] = [
        self.df_abs_data.loc[idx, 'Account'], 
        col, 
        '일치', 
        '', 
        '',
        self.df_format_data.at[idx, 'country_code']
    ]
else:  # 불일치하는 경우
    detail = f"포맷데이터: {self.df_format_data.loc[idx, col]}\n\n\n추출데이터: {self.df_abs_data.loc[idx, col]}"
    self.compare_result.loc[len(self.compare_result)] = [
        self.df_abs_data.loc[idx, 'Account'], 
        col, 
        '불일치', 
        detail, 
        '',
        self.df_format_data.at[idx, 'country_code']
    ]
```

### 2. item_abs_data()

```python
def item_abs_data(self):
```

**기능:**
- 비교 항목 파일을 기반으로 데이터를 필터링
- 계정이 비교 항목에 없는 경우는 모두 유지
- 계정이 비교 항목에 있는 경우는 해당 항목만 유지

**처리 과정:**

#### 1단계: 비교 항목 파일에서 계정-항목 쌍 추출
```python
# 비교 항목 파일에서 계정-항목 쌍을 추출
account_value_pairs = []
for i in range(len(self.df_compare_item)):
    account = self.df_compare_item.iloc[i, 0]  # 첫 번째 컬럼은 계정
    values = self.df_compare_item.iloc[i, 1:].dropna().tolist()  # 나머지 컬럼들은 항목들 (NaN 제거)
    for val in values:
        account_value_pairs.append((account, val))  # 계정-항목 쌍 생성
```

#### 2단계: 계정 기준 분리
```python
# 계정 기준 일치 여부 확인
accounts_in_value_df = set(account_value_df["계정"].unique())  # 비교 항목에 있는 계정들

# 계정이 account_value_df에 없는 경우 → 무조건 유지
df_account_not_exist = self.compare_result[~self.compare_result["계정"].isin(accounts_in_value_df)]

# 계정이 존재하는 경우만 추출
df_account_exist = self.compare_result[self.compare_result["계정"].isin(accounts_in_value_df)]
```

#### 3단계: 계정과 항목이 모두 일치하는 데이터 추출
```python
# 계정과 항목이 모두 일치하는 데이터만 추출
df_matched = pd.merge(df_account_exist, account_value_df, on=["계정", "항목"], how="inner")

# 두 결과 합치기 - 필터링된 데이터와 유지할 데이터를 병합
self.merge_compare_result = pd.concat([df_matched, df_account_not_exist], ignore_index=True)
```

### 3. abs_rec_data()

```python
def abs_rec_data(self):
```

**기능:**
- 추출 데이터에서 추천 제품 정보를 비교 결과에 추가
- rec가 포함된 컬럼들을 찾아서 추천 제품 정보 수집
- 각 계정별로 추천 제품 정보를 NA 컬럼에 추가

**처리 과정:**

#### 1단계: 추천 제품 컬럼 찾기
```python
rec_columns = [col for col in self.df_abs_data.columns if 'rec' in col]  # 추출 데이터에서 rec 포함된 컬럼 추출
```

#### 2단계: 각 계정별 추천 제품 정보 수집
```python
for idx, row in self.df_abs_data.iterrows():
    country_value = row['country_code']  # 각 계정의 국가 코드 추출
    
    rec_product = '\n'.join(f"{col}: {row[col]}" for col in rec_columns)  # 추천제품 리스트를 문자열로 결합
    match_idx = self.merge_compare_result[self.merge_compare_result['국가'] == country_value].index.min()  # 각 계정이 삽입된 최소 인덱스를 추출
    
    if pd.notna(match_idx):  # 일치하는 인덱스가 존재할 경우
        self.merge_compare_result.at[match_idx, 'NA'] = rec_product  # 해당 인덱스의 na 컬럼에 추천 제품 데이터 삽입
```

### 4. get_result()

```python
def get_result(self):
```

**기능:**
- 비교 결과를 Excel 파일로 저장하고 포맷팅
- 국가별로 시트를 분리하여 저장
- Excel 파일의 컬럼 너비와 셀 정렬 설정
- 추천 제품 컬럼을 계정별로 병합
- 각 계정의 마지막 행에 굵은 테두리 추가

**처리 과정:**

#### 1단계: Excel 파일로 저장
```python
# Excel 파일로 저장 (openpyxl 엔진 사용)
with pd.ExcelWriter(self.output_path, engine='openpyxl') as writer:
    for country in self.country_code:
        # 조건에 맞는 데이터 추출
        filtered_df = self.merge_compare_result[self.merge_compare_result['국가'] == country]
        
        # 시트 이름으로 저장
        sheet_name = f'비교결과({country})'  # Excel 시트명은 31자 제한
        filtered_df.to_excel(writer, sheet_name=sheet_name, index=False)
```

#### 2단계: Excel 파일 포맷팅
```python
wb = load_workbook(self.output_path)
for country in self.country_code:
    sheet_name = f'비교결과({country})'
    ws = wb[sheet_name]
    
    # 엑셀의 D컬럼위치와 E컬럼 위치 너비 조정
    for col_index in range(1, ws.max_column+1):
        col_letter = get_column_letter(col_index)
        if(col_letter == "D" or col_letter == "E"):  # 결과 상세와 NA 컬럼은 넓게
            ws.column_dimensions[col_letter].width = 50
        else:  # 나머지 컬럼들은 기본 너비
            ws.column_dimensions[col_letter].width = 20
```

#### 3단계: 셀 정렬 설정
```python
# 각 셀별 텍스트 위치 조정
for row in ws.iter_rows():
    for cell in row:
        cell.alignment = Alignment(vertical='center', horizontal='center')  # 기본 정렬: 가운데
        rec_col = row[3]  # 결과 상세 컬럼 (D열)
        rec_col.alignment = Alignment(vertical='center', horizontal='left', wrap_text=True)  # 왼쪽 정렬, 자동 줄바꿈
        rec_col = row[4]  # NA 컬럼 (E열)
        rec_col.alignment = Alignment(vertical='top', horizontal='left', wrap_text=True)  # 위쪽 정렬, 자동 줄바꿈
```

#### 4단계: 추천 제품 컬럼 병합 및 테두리 설정
```python
# 추천제품 컬럼을 각 계정에 맞게 병합
for num, value in self.df_abs_data.drop_duplicates(subset=['Account']).iterrows():
    target_account = value['Account']  # 대상 계정
    
    for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):  # 헤더 제외하고 행 순회
        if row[0] == target_account:  # 계정 컬럼이 첫 번째 열(A열)이라고 가정
            last_row = idx  # 해당 계정의 마지막 행 인덱스 업데이트
    
    ws.merge_cells(start_row=start_row+1, start_column=5, end_row=last_row, end_column=5)  # NA 컬럼(E열) 병합
    
    # 반복 대상 행 (예: 병합된 마지막 행) -> 마지막행마다 아래 라인을 굵게 표시
    for col in range(1, 6):  # 1~5열
        cell = ws.cell(row=last_row, column=col)
        cell.border = bottom_thick_border  # 굵은 아래 테두리 적용
    
    start_row = last_row  # 다음 병합을 위한 시작 행 업데이트
```

## 데이터 처리 로직 (Data Processing Logic)

### 1. 비교 컬럼 시스템

**주요 비교 컬럼:**
```python
self.compare_columns = [ 
    'main_headline', 'main_description',         # 메인 헤드라인, 설명
    'storyIdRank1', 'storyIdRank2', 'storyIdRank3',  # 스토리 ID들
    'storyIdRank1_title', 'storyIdRank1_desc',  # 스토리 1 제목/설명
    'storyIdRank2_title', 'storyIdRank2_desc',  # 스토리 2 제목/설명
    'storyIdRank3_title', 'storyIdRank3_desc',  # 스토리 3 제목/설명
    'banner_text', 'banner_link_text', 'banner_hyperlink'  # 배너 관련 정보
]
```

### 2. 비교 결과 구조

**결과 DataFrame 컬럼:**
- `계정`: 계정 정보
- `항목`: 비교 항목명
- `결과`: 일치/불일치 여부
- `결과 상세`: 불일치 시 상세 비교 정보
- `NA`: 추천 제품 정보
- `국가`: 국가 코드

### 3. 배너 컬럼 처리

**선택적 비교:**
- `banner_text`, `banner_link_text`, `banner_hyperlink` 컬럼
- 실제 데이터가 "없음"인 경우 비교에서 제외
- 배너는 선택적으로 표시되므로 예외 처리

## 사용 예시 (Usage Example)

### 1. 기본 사용법

```python
import pandas as pd
from module.compare_result import CompareProcess

# 포맷 데이터 (예상 데이터)
df_format_data = pd.DataFrame({
    'Account': ['user1@example.com', 'user2@example.com'],
    'main_headline': ['예상 헤드라인 1', '예상 헤드라인 2'],
    'main_description': ['예상 설명 1', '예상 설명 2'],
    'country_code': ['KR', 'US']
})

# 실제 추출 데이터
df_abs_data = pd.DataFrame({
    'Account': ['user1@example.com', 'user2@example.com'],
    'main_headline': ['실제 헤드라인 1', '실제 헤드라인 2'],
    'main_description': ['실제 설명 1', '실제 설명 2'],
    'country_code': ['KR', 'US']
})

# 비교 항목 파일 경로
df_compare_item_path = "compare_items.xlsx"

# 출력 파일 경로
output_path = "comparison_result.xlsx"

# 국가 코드 리스트
country_code = ['KR', 'US']

# CompareProcess 인스턴스 생성
comparator = CompareProcess(
    df_format_data=df_format_data,
    df_abs_data=df_abs_data,
    df_compare_item_path=df_compare_item_path,
    output_path=output_path,
    country_code=country_code
)

# 데이터 비교
comparator.compare_data()

# 비교 항목 필터링
comparator.item_abs_data()

# 추천 제품 정보 추가
comparator.abs_rec_data()

# 결과 저장 및 포맷팅
comparator.get_result()

print("비교 완료!")
```

### 2. 비교 항목 파일 예시

**Excel 파일 구조 (compare_items.xlsx):**
```
| 계정              | 항목1        | 항목2        | 항목3        |
|-------------------|--------------|--------------|--------------|
| user1@example.com | main_headline| main_description| storyIdRank1_title|
| user2@example.com | banner_text  | banner_link_text|              |
```

### 3. 결과 파일 구조

**생성되는 Excel 파일 구조:**
```
시트: 비교결과(KR)
| 계정              | 항목           | 결과   | 결과 상세                    | NA                    |
|-------------------|----------------|--------|------------------------------|------------------------|
| user1@example.com| main_headline  | 불일치 | 포맷데이터: 예상 헤드라인 1   | storyIdRank1_rec1: 제품1|
|                  |                |        | 추출데이터: 실제 헤드라인 1   | storyIdRank1_rec2: 제품2|
| user2@example.com| banner_text    | 일치   |                              | storyIdRank2_rec1: 제품3|
```

## Excel 파일 포맷팅 (Excel File Formatting)

### 1. 컬럼 너비 설정

```python
# D열과 E열은 넓게 설정 (50)
# 나머지 컬럼들은 기본 너비 (20)
for col_index in range(1, ws.max_column+1):
    col_letter = get_column_letter(col_index)
    if(col_letter == "D" or col_letter == "E"):
        ws.column_dimensions[col_letter].width = 50
    else:
        ws.column_dimensions[col_letter].width = 20
```

### 2. 셀 정렬 설정

```python
# 기본 정렬: 가운데
cell.alignment = Alignment(vertical='center', horizontal='center')

# 결과 상세 컬럼: 왼쪽 정렬, 자동 줄바꿈
rec_col.alignment = Alignment(vertical='center', horizontal='left', wrap_text=True)

# NA 컬럼: 위쪽 정렬, 자동 줄바꿈
rec_col.alignment = Alignment(vertical='top', horizontal='left', wrap_text=True)
```

### 3. 셀 병합 및 테두리

```python
# NA 컬럼(E열)을 계정별로 병합
ws.merge_cells(start_row=start_row+1, start_column=5, end_row=last_row, end_column=5)

# 마지막 행에 굵은 아래 테두리 적용
bottom_thick_border = Border(bottom=Side(border_style="thick", color="000000"))
for col in range(1, 6):
    cell = ws.cell(row=last_row, column=col)
    cell.border = bottom_thick_border
```

## 의존성 (Dependencies)

- `pandas`: 데이터 처리 및 DataFrame 조작
- `openpyxl`: Excel 파일 읽기/쓰기 및 포맷팅
- `openpyxl.styles`: Excel 스타일링 (Alignment, Border, Side)
- `openpyxl.utils`: Excel 유틸리티 (get_column_letter)

## 주의사항 (Important Notes)

1. **공백 제거 비교**: 공백을 제거한 상태에서 비교하므로 정확한 비교 가능
2. **배너 컬럼 예외**: 배너 관련 컬럼은 "없음"인 경우 비교에서 제외
3. **Excel 파일 크기**: 대용량 데이터의 경우 메모리 사용량 주의
4. **시트명 제한**: Excel 시트명은 31자 제한
5. **파일 경로**: 출력 파일 경로가 유효한지 확인 필요

## 확장 가능성 (Extensibility)

### 1. 새로운 비교 컬럼 추가

```python
def __init__(self, df_format_data, df_abs_data, df_compare_item_path, output_path, country_code):
    # 기존 초기화...
    
    # 새로운 비교 컬럼 추가
    self.compare_columns = [ 
        'main_headline', 'main_description',
        'storyIdRank1', 'storyIdRank2', 'storyIdRank3',
        'storyIdRank1_title', 'storyIdRank1_desc',
        'storyIdRank2_title', 'storyIdRank2_desc',
        'storyIdRank3_title', 'storyIdRank3_desc',
        'banner_text', 'banner_link_text', 'banner_hyperlink',
        'new_column1', 'new_column2'  # 새로운 컬럼 추가
    ]
```

### 2. 새로운 비교 로직 추가

```python
def compare_data(self):
    # 기존 로직...
    
    # 새로운 비교 로직 추가
    for col in self.compare_columns:
        # 기존 비교 로직...
        
        # 새로운 비교 조건 추가
        if col.startswith('new_'):
            # 새로운 비교 로직
            if self.custom_compare_logic(format_row[col], abs_row[col]):
                # 일치 처리
            else:
                # 불일치 처리
```

### 3. 새로운 포맷팅 옵션 추가

```python
def get_result(self):
    # 기존 포맷팅...
    
    # 새로운 포맷팅 옵션 추가
    for country in self.country_code:
        ws = wb[f'비교결과({country})']
        
        # 새로운 스타일 적용
        for row in ws.iter_rows():
            for cell in row:
                if cell.value == '불일치':
                    cell.font = Font(color="FF0000")  # 빨간색 글자
                elif cell.value == '일치':
                    cell.font = Font(color="008000")  # 초록색 글자
```

## 성능 최적화 (Performance Optimization)

1. **벡터화 연산**: pandas의 벡터화 연산 사용으로 성능 향상
2. **메모리 효율성**: 대용량 데이터 처리 시 청크 단위 처리
3. **Excel 최적화**: openpyxl 엔진 사용으로 빠른 Excel 처리
4. **병렬 처리**: 여러 국가별 처리를 병렬로 수행

## 디버깅 및 로깅 (Debugging and Logging)

```python
def compare_data(self):
    """디버깅 기능이 추가된 데이터 비교"""
    print(f"비교할 컬럼 수: {len(self.compare_columns)}")
    print(f"포맷 데이터 행 수: {len(self.df_format_data)}")
    print(f"실제 데이터 행 수: {len(self.df_abs_data)}")
    
    match_count = 0
    mismatch_count = 0
    
    for idx in range(len(self.df_abs_data)):
        print(f"처리 중인 행: {idx + 1}")
        
        # 기존 비교 로직...
        
        for col in self.compare_columns:
            if format_row[col] == abs_row[col]:
                match_count += 1
            else:
                mismatch_count += 1
                print(f"불일치 발견: {col} - 포맷: {format_row[col]}, 실제: {abs_row[col]}")
    
    print(f"일치 항목: {match_count}, 불일치 항목: {mismatch_count}")
```

## 테스트 케이스 (Test Cases)

### 1. 기본 케이스
- 모든 데이터가 일치하는 경우
- 일부 데이터만 일치하는 경우
- 모든 데이터가 불일치하는 경우

### 2. 경계 케이스
- 빈 데이터 처리
- 매우 긴 텍스트 비교
- 특수 문자가 포함된 데이터

### 3. 특수 케이스
- 배너 컬럼이 "없음"인 경우
- 비교 항목 파일이 비어있는 경우
- 국가별 데이터가 없는 경우

## 에러 처리 (Error Handling)

```python
def compare_data(self):
    """에러 처리가 추가된 데이터 비교"""
    try:
        for idx in range(len(self.df_abs_data)):
            try:
                # 기존 비교 로직...
                
            except KeyError as e:
                print(f"행 {idx}에서 컬럼을 찾을 수 없습니다: {e}")
                continue
            except Exception as e:
                print(f"행 {idx} 처리 중 오류 발생: {e}")
                continue
                
    except Exception as e:
        print(f"데이터 비교 중 오류 발생: {e}")
        raise
``` 