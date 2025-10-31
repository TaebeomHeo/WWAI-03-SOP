# Law Agree Result Module Documentation

## 개요 (Overview)

`law_agree_result.py`는 국가별 마케팅 동의 요건을 처리하는 모듈입니다. 이 모듈은 Excel 파일에서 국가별 동의 요건 데이터를 로드하고, API 응답의 동의 타입을 분석하여 매핑한 후, 해당 국가의 동의 요건 결과를 반환합니다.

## 주요 기능 (Key Features)

- **Excel 데이터 로드**: 국가별 마케팅 동의 요건 Excel 파일에서 데이터 로드
- **동의 타입 매핑**: API 응답의 동의 타입을 Excel 데이터와 매핑
- **국가별 처리**: 각 국가 코드에 따른 동의 요건 분석
- **조건부 처리**: 동의 데이터 유무에 따른 다른 처리 로직
- **결과 반환**: 동의 필요 여부를 'X' 또는 'O'로 표시

## 클래스 구조 (Class Structure)

### law_agree

국가별 마케팅 동의 요건을 처리하는 메인 클래스입니다.

#### 초기화 (Initialization)

```python
def __init__(self, law_format_file, law_agree_data, country_code):
```

**매개변수 (Parameters):**
- `law_format_file`: 국가별 마케팅 동의 요건 Excel 파일 경로
- `law_agree_data`: API 응답에서 받은 동의 데이터 (딕셔너리 또는 리스트)
- `country_code`: 처리할 국가 코드 (예: 'DE', 'FR', 'ES', 'IT')

**인스턴스 변수 (Instance Variables):**
- `law_format_file`: 동의 요건 Excel 파일 경로
- `law_agree_data`: API 응답의 동의 데이터
- `country_code`: 국가 코드
- `df_rowdata`: Excel 파일에서 로드한 DataFrame (두 번째 행을 헤더로 사용)

## 메서드 상세 설명 (Method Details)

### 1. get_no_data_result()

```python
def get_no_data_result(self):
```

**기능:**
- 동의 데이터가 없는 경우 (204 No Content)의 결과를 반환
- 모든 동의 타입이 '-'인 경우를 찾아서 해당 국가의 결과 반환

**반환값:**
- `pandas.Series`: 해당 국가의 동의 요건 결과 ('X' 또는 'O')

**처리 과정:**
1. Excel 데이터에서 모든 동의 타입이 '-'인 행을 검색
2. 해당 행에서 지정된 국가 코드의 결과 추출
3. 디버깅을 위한 결과 출력

**코드 예시:**
```python
# 모든 동의 타입이 '-'인 행을 찾아서 해당 국가의 결과 추출
result = self.df_rowdata.query(f"MKT == '-' and CZSVC == '-' and CZADV == '-'")[self.country_code]
print("데이터 없을경우 : ", result)  # 디버깅용 출력
return result
```

### 2. get_data_result()

```python
def get_data_result(self):
```

**기능:**
- 동의 데이터가 있는 경우 (200 OK)의 결과를 반환
- API 응답의 동의 타입을 분석하여 Excel 데이터와 매핑

**반환값:**
- `pandas.Series`: 해당 국가의 동의 요건 결과 ('X' 또는 'O')

**처리 과정:**

#### 1단계: 동의 타입 정의
```python
# 처리할 동의 타입 리스트
law_list = ['MKT', 'CZSVC', 'CZADV']  # 마케팅, 서비스, 광고 동의 타입
```

#### 2단계: API 응답에서 동의 타입 추출
```python
# API 응답에서 동의 타입들만 추출
types = [item['type'] for item in self.law_agree_data]  # API 응답의 type 필드들
```

#### 3단계: 동의 타입 매핑
```python
# 결과 딕셔너리 초기화 - 각 동의 타입에 대해 매핑 결과 저장
mapped_result = {}

# 각 동의 타입에 대해 API 응답에 포함되어 있는지 확인
for law in law_list:
    if law in types:  # API 응답에 해당 동의 타입이 있으면
        mapped_result[law] = law  # 실제 값으로 매핑
    else:  # API 응답에 해당 동의 타입이 없으면
        mapped_result[law] = '-'  # '-'로 매핑 (동의 불필요)
```

#### 4단계: 조건에 맞는 행 검색
```python
# 매핑된 조건에 맞는 행을 찾아서 해당 국가의 결과 추출
result = self.df_rowdata.query(f"MKT == '{mapped_result['MKT']}' and CZSVC == '{mapped_result['CZSVC']}' and CZADV == '{mapped_result['CZADV']}'")[self.country_code]
print("데이터 있을경우 : ", result)  # 디버깅용 출력
return result
```

## 데이터 처리 로직 (Data Processing Logic)

### 1. 동의 타입 시스템

**주요 동의 타입:**
- `MKT`: 마케팅 동의 (Marketing Consent)
- `CZSVC`: 서비스 동의 (Service Consent)
- `CZADV`: 광고 동의 (Advertisement Consent)

### 2. 매핑 규칙

**API 응답에 동의 타입이 있는 경우:**
- 해당 동의 타입을 그대로 사용 (예: 'MKT', 'CZSVC', 'CZADV')

**API 응답에 동의 타입이 없는 경우:**
- '-'로 매핑 (동의 불필요를 의미)

### 3. Excel 데이터 구조

**예상되는 Excel 파일 구조:**
```
| 국가코드 | MKT | CZSVC | CZADV | DE | FR | ES | IT | ... |
|---------|-----|-------|-------|----|----|----|----|-----|
| 조건1   | MKT | CZSVC | CZADV | X  | O  | X  | O  | ... |
| 조건2   | MKT | CZSVC | -     | O  | X  | O  | X  | ... |
| 조건3   | -   | -     | -     | O  | O  | O  | O  | ... |
```

### 4. 결과 해석

**결과 값:**
- `'X'`: 동의 필요 (Consent Required)
- `'O'`: 동의 불필요 (No Consent Required)

## 사용 예시 (Usage Example)

### 1. 동의 데이터가 없는 경우 (204 No Content)

```python
import pandas as pd
from module.law_agree_result import law_agree

# Excel 파일 경로
law_format_file = "consent_rules.xlsx"

# 동의 데이터가 없는 경우 (204 응답)
law_agree_data = None  # 또는 빈 리스트 []
country_code = "DE"

# law_agree 클래스 인스턴스 생성
law_processor = law_agree(law_format_file, law_agree_data, country_code)

# 동의 불필요 결과 가져오기
result = law_processor.get_no_data_result()
print(f"독일 동의 요건: {result.iloc[0]}")  # 'O' (동의 불필요)
```

### 2. 동의 데이터가 있는 경우 (200 OK)

```python
# 동의 데이터가 있는 경우 (200 응답)
law_agree_data = [
    {'type': 'MKT'},      # 마케팅 동의 있음
    {'type': 'CZSVC'},    # 서비스 동의 있음
    # CZADV는 없음 (광고 동의 없음)
]
country_code = "FR"

# law_agree 클래스 인스턴스 생성
law_processor = law_agree(law_format_file, law_agree_data, country_code)

# 동의 필요 결과 가져오기
result = law_processor.get_data_result()
print(f"프랑스 동의 요건: {result.iloc[0]}")  # 'X' (동의 필요)
```

### 3. 다양한 동의 타입 조합

```python
# 모든 동의 타입이 있는 경우
law_agree_data = [
    {'type': 'MKT'},
    {'type': 'CZSVC'},
    {'type': 'CZADV'}
]
country_code = "ES"

law_processor = law_agree(law_format_file, law_agree_data, country_code)
result = law_processor.get_data_result()
print(f"스페인 동의 요건: {result.iloc[0]}")

# 일부 동의 타입만 있는 경우
law_agree_data = [
    {'type': 'MKT'},      # 마케팅 동의만 있음
    # CZSVC, CZADV는 없음
]
country_code = "IT"

law_processor = law_agree(law_format_file, law_agree_data, country_code)
result = law_processor.get_data_result()
print(f"이탈리아 동의 요건: {result.iloc[0]}")
```

## Excel 파일 구조 (Excel File Structure)

### 예상되는 Excel 파일 형식

| 국가코드 | MKT | CZSVC | CZADV | DE | FR | ES | IT | UK | US |
|---------|-----|-------|-------|----|----|----|----|----|----|
| 조건1   | MKT | CZSVC | CZADV | X  | X  | X  | X  | X  | X  |
| 조건2   | MKT | CZSVC | -     | X  | X  | O  | X  | X  | O  |
| 조건3   | MKT | -     | CZADV | X  | O  | X  | O  | X  | X  |
| 조건4   | MKT | -     | -     | X  | O  | O  | O  | X  | O  |
| 조건5   | -   | CZSVC | CZADV | O  | X  | X  | X  | O  | X  |
| 조건6   | -   | CZSVC | -     | O  | X  | O  | O  | O  | O  |
| 조건7   | -   | -     | CZADV | O  | O  | X  | O  | O  | X  |
| 조건8   | -   | -     | -     | O  | O  | O  | O  | O  | O  |

**설명:**
- **MKT, CZSVC, CZADV**: 동의 타입 조건
- **DE, FR, ES, IT, UK, US**: 국가별 결과 ('X' 또는 'O')
- **'-'**: 해당 동의 타입이 없음을 의미

## 의존성 (Dependencies)

- `pandas`: Excel 파일 읽기 및 데이터 처리
- `openpyxl` 또는 `xlrd`: Excel 파일 지원 (pandas 내장)

## 주의사항 (Important Notes)

1. **Excel 파일 구조**: 두 번째 행을 헤더로 사용 (`header=1`)
2. **국가 코드**: 정확한 국가 코드 사용 필요 (대소문자 구분)
3. **동의 타입**: API 응답의 'type' 필드와 Excel의 컬럼명 일치 필요
4. **데이터 형식**: API 응답은 리스트 형태의 딕셔너리 배열
5. **결과 해석**: 'X'는 동의 필요, 'O'는 동의 불필요

## 확장 가능성 (Extensibility)

### 1. 새로운 동의 타입 추가

```python
def get_data_result(self):
    # 새로운 동의 타입 추가
    law_list = ['MKT', 'CZSVC', 'CZADV', 'NEW_TYPE']
    
    # 기존 로직...
    for law in law_list:
        if law in types:
            mapped_result[law] = law
        else:
            mapped_result[law] = '-'
    
    # 쿼리 조건에 새로운 타입 추가
    result = self.df_rowdata.query(
        f"MKT == '{mapped_result['MKT']}' and "
        f"CZSVC == '{mapped_result['CZSVC']}' and "
        f"CZADV == '{mapped_result['CZADV']}' and "
        f"NEW_TYPE == '{mapped_result['NEW_TYPE']}'"
    )[self.country_code]
    
    return result
```

### 2. 새로운 국가 코드 추가

```python
def __init__(self, law_format_file, law_agree_data, country_code):
    # 기존 초기화...
    
    # 국가 코드 유효성 검사 추가
    valid_countries = ['DE', 'FR', 'ES', 'IT', 'UK', 'US', 'NEW_COUNTRY']
    if country_code not in valid_countries:
        raise ValueError(f"지원하지 않는 국가 코드: {country_code}")
```

### 3. 결과 캐싱 추가

```python
def __init__(self, law_format_file, law_agree_data, country_code):
    # 기존 초기화...
    self._cache = {}  # 결과 캐싱을 위한 딕셔너리

def get_data_result(self):
    # 캐시 키 생성
    cache_key = f"{self.country_code}_{str(self.law_agree_data)}"
    
    if cache_key in self._cache:
        return self._cache[cache_key]
    
    # 기존 로직...
    result = # 기존 처리 로직
    
    # 결과 캐싱
    self._cache[cache_key] = result
    return result
```

## 성능 최적화 (Performance Optimization)

1. **Excel 파일 캐싱**: DataFrame을 메모리에 로드하여 반복 읽기 방지
2. **쿼리 최적화**: pandas query 사용으로 빠른 필터링
3. **결과 캐싱**: 동일한 조건의 결과를 캐싱하여 중복 계산 방지
4. **메모리 효율성**: 필요한 컬럼만 로드

## 디버깅 및 로깅 (Debugging and Logging)

```python
def get_data_result(self):
    # 디버깅을 위한 상세 로깅 추가
    print(f"처리 중인 국가 코드: {self.country_code}")
    print(f"API 응답 데이터: {self.law_agree_data}")
    
    # 동의 타입 추출
    types = [item['type'] for item in self.law_agree_data]
    print(f"추출된 동의 타입: {types}")
    
    # 매핑 결과 출력
    mapped_result = {}
    law_list = ['MKT', 'CZSVC', 'CZADV']
    for law in law_list:
        if law in types:
            mapped_result[law] = law
        else:
            mapped_result[law] = '-'
    print(f"매핑 결과: {mapped_result}")
    
    # 기존 로직...
    result = self.df_rowdata.query(f"MKT == '{mapped_result['MKT']}' and CZSVC == '{mapped_result['CZSVC']}' and CZADV == '{mapped_result['CZADV']}'")[self.country_code]
    print(f"최종 결과: {result}")
    
    return result
```

## 테스트 케이스 (Test Cases)

### 1. 기본 케이스
- 모든 동의 타입이 있는 경우
- 일부 동의 타입만 있는 경우
- 동의 타입이 없는 경우

### 2. 경계 케이스
- Excel 파일이 없는 경우
- 국가 코드가 Excel에 없는 경우
- API 응답이 빈 배열인 경우

### 3. 특수 케이스
- 잘못된 Excel 파일 형식
- API 응답에 예상하지 못한 동의 타입
- 중복된 동의 타입

## 에러 처리 (Error Handling)

```python
def get_data_result(self):
    try:
        # 기존 로직...
        result = self.df_rowdata.query(...)[self.country_code]
        
        if result.empty:
            raise ValueError(f"조건에 맞는 데이터를 찾을 수 없습니다: {self.country_code}")
        
        return result
    except KeyError as e:
        print(f"국가 코드를 찾을 수 없습니다: {self.country_code}")
        raise
    except Exception as e:
        print(f"데이터 처리 중 오류 발생: {e}")
        raise
``` 