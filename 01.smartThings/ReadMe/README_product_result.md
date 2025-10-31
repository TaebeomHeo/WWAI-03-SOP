# Product Result Module

## 개요
`product_result.py`는 삼성 제품 데이터를 처리하고 우선순위에 따라 정렬하는 모듈입니다. 이 모듈은 제품 메타데이터와 사용자의 제품 데이터를 받아서 등록 채널과 등록 상태에 따른 우선순위를 계산하고, 정렬된 제품 목록에서 상위 2개 제품명을 반환합니다.

## 주요 기능

### 1. 제품 데이터 처리
- API 응답에서 받은 제품 정보를 구조화된 형태로 변환
- 제품 코드, 등록 상태, 등록 채널, 생성 날짜 정보 추출

### 2. 우선순위 계산
- 등록 채널과 등록 상태에 따른 제품 우선순위 결정
- 3단계 우선순위 시스템 (1: 최고, 2: 중간, 3: 최저)

### 3. 정렬 및 필터링
- 우선순위, 생성 날짜, 원본 순서를 고려한 제품 정렬
- 상위 2개 제품 선택 및 제품명 반환

### 4. 메타데이터 매핑
- 제품 코드를 실제 제품명으로 변환
- `nameCis` 필드를 통한 사용자 친화적 제품명 제공

## 클래스 구조

### product 클래스

삼성 제품 데이터를 처리하고 우선순위에 따라 정렬하는 메인 클래스입니다.

#### 초기화 매개변수
```python
def __init__(self, meta_data, product_data):
```

**매개변수 설명:**
- `meta_data`: 제품 메타데이터 딕셔너리 (modelCode를 키로 사용)
- `product_data`: 제품 데이터 리스트 (API 응답에서 받은 제품 정보들)

#### 내부 변수
```python
self.meta_data = meta_data  # 제품 메타데이터 (modelCode -> 제품 정보 매핑)
self.product_data = product_data  # 원본 제품 데이터 리스트
self.target_columns = [    
    'modelCode',      # 제품 모델 코드
    'registration',    # 등록 상태 (REGISTRATION, UNREGISTRATION 등)
    'channel',        # 등록 채널 (SAMSUNG_ACCOUNT, SMARTTHINGS 등)
    'createdDateTime' # 생성 날짜/시간
]
```

## 메서드 상세 설명

### 1. get_priority(row) - 정적 메서드

```python
@staticmethod
def get_priority(row):
```

**기능:**
- 제품의 우선순위를 결정하는 정적 메서드
- 등록 채널과 등록 상태에 따른 우선순위 계산

**매개변수:**
- `row`: 제품 데이터 행 (DataFrame의 한 행)

**반환값:**
- `int`: 우선순위 (1: 최고, 2: 중간, 3: 최저)

**우선순위 규칙:**
1. **최고 우선순위 (1)**: SAMSUNG_ACCOUNT 채널 + REGISTRATION 상태
2. **중간 우선순위 (2)**: REGISTRATION 상태 (채널 무관)
3. **최저 우선순위 (3)**: 기타 모든 경우

**코드 예시:**
```python
if row['channel'] == 'SAMSUNG_ACCOUNT' and row['registration'] == 'REGISTRATION':
    return 1  # 최고 우선순위: 삼성 계정으로 등록된 제품
elif row['registration'] == 'REGISTRATION':
    return 2  # 중간 우선순위: 등록된 제품 (채널 무관)
else:
    return 3  # 최저 우선순위: 미등록 제품
```

### 2. get_result()

```python
def get_result(self):
```

**기능:**
- 제품 데이터를 처리하고 우선순위에 따라 정렬하여 상위 2개 제품명을 반환

**반환값:**
- `tuple`: (product1, product2) - 상위 2개 제품명

**처리 과정:**

#### 1단계: 데이터 구조화
```python
# 결과를 저장할 DataFrame 초기화
df_product = pd.DataFrame(columns=self.target_columns)
rows = []

# 제품 데이터를 DataFrame 형태로 변환
for value in self.product_data:
    rows.append({
        'modelCode': value.get('modelCode', '없음'),  # 모델 코드 (없으면 '없음')
        'registration': value.get('records', [{}])[0].get('type', '없음'),  # 등록 상태
        'channel': value.get('records', [{}])[0].get('channel', '없음'),    # 등록 채널
        'createdDateTime': str(value.get('records', [{}])[0].get('createdDateTime', '없음')).split('T')[0],  # 생성 날짜
    })
```

#### 2단계: DataFrame 생성 및 우선순위 계산
```python
# DataFrame 생성
df_product = pd.DataFrame(rows, columns=self.target_columns)
df_product['insertion_order'] = df_product.index  # 원본 순서 보존

# 우선순위 계산
df_product['priority'] = df_product.apply(product.get_priority, axis=1)
```

#### 3단계: 날짜 변환 및 정렬
```python
# 날짜 변환 - 문자열을 datetime 객체로 변환
df_product['createdDateTime'] = pd.to_datetime(df_product['createdDateTime'])

# 정렬: priority → createdDateTime → insertion_order
df_sorted = df_product.sort_values(
    by=['priority', 'createdDateTime', 'insertion_order'],
    ascending=[True, False, True]
).reset_index(drop=True)
```

#### 4단계: 상위 2개 제품명 추출
```python
# 상위 2개 제품의 메타데이터에서 제품명 추출
for compare_code in self.meta_data:
    # 첫 번째 제품 (최고 우선순위)
    if df_sorted.at[0,'modelCode'] == compare_code:
        product1 = self.meta_data[compare_code]['nameCis']

    # 두 번째 제품 (두 번째 우선순위)
    elif df_sorted.at[1,'modelCode'] == compare_code:
        product2 = self.meta_data[compare_code]['nameCis']

return product1, product2
```

## 데이터 처리 로직

### 1. 우선순위 계산 로직

**우선순위 1 (최고)**: 삼성 계정으로 등록된 제품
- `channel == 'SAMSUNG_ACCOUNT'` AND `registration == 'REGISTRATION'`

**우선순위 2 (중간)**: 등록된 제품 (채널 무관)
- `registration == 'REGISTRATION'` (채널 조건 제외)

**우선순위 3 (최저)**: 기타 모든 경우
- 미등록 제품 또는 기타 상태

### 2. 정렬 기준

1. **우선순위 (priority)**: 오름차순 (1이 가장 높음)
2. **생성 날짜 (createdDateTime)**: 내림차순 (최신 날짜가 먼저)
3. **원본 순서 (insertion_order)**: 오름차순 (원본 순서 유지)

### 3. 데이터 구조

**입력 데이터 구조:**
```python
# meta_data 예시
{
    'SM-A546B': {
        'nameCis': 'Galaxy A54 5G',
        'modelCode': 'SM-A546B',
        # 기타 메타데이터...
    },
    'SM-G998B': {
        'nameCis': 'Galaxy S21 Ultra 5G',
        'modelCode': 'SM-G998B',
        # 기타 메타데이터...
    }
}

# product_data 예시
[
    {
        'modelCode': 'SM-A546B',
        'records': [
            {
                'type': 'REGISTRATION',
                'channel': 'SAMSUNG_ACCOUNT',
                'createdDateTime': '2024-01-15T10:30:00Z'
            }
        ]
    },
    {
        'modelCode': 'SM-G998B',
        'records': [
            {
                'type': 'REGISTRATION',
                'channel': 'SMARTTHINGS',
                'createdDateTime': '2024-01-10T14:20:00Z'
            }
        ]
    }
]
```

## 사용 예시

```python
import pandas as pd
from smartThings_module.product_result import product

# 제품 메타데이터 (API 응답에서 받은 데이터)
meta_data = {
    'SM-A546B': {
        'nameCis': 'Galaxy A54 5G',
        'modelCode': 'SM-A546B'
    },
    'SM-G998B': {
        'nameCis': 'Galaxy S21 Ultra 5G',
        'modelCode': 'SM-G998B'
    },
    'SM-F946B': {
        'nameCis': 'Galaxy Z Fold5',
        'modelCode': 'SM-F946B'
    }
}

# 사용자 제품 데이터 (API 응답에서 받은 데이터)
product_data = [
    {
        'modelCode': 'SM-A546B',
        'records': [
            {
                'type': 'REGISTRATION',
                'channel': 'SAMSUNG_ACCOUNT',
                'createdDateTime': '2024-01-15T10:30:00Z'
            }
        ]
    },
    {
        'modelCode': 'SM-G998B',
        'records': [
            {
                'type': 'REGISTRATION',
                'channel': 'SMARTTHINGS',
                'createdDateTime': '2024-01-10T14:20:00Z'
            }
        ]
    },
    {
        'modelCode': 'SM-F946B',
        'records': [
            {
                'type': 'UNREGISTRATION',
                'channel': 'SAMSUNG_ACCOUNT',
                'createdDateTime': '2024-01-05T09:15:00Z'
            }
        ]
    }
]

# product 클래스 인스턴스 생성
product_processor = product(meta_data, product_data)

# 상위 2개 제품명 가져오기
device1, device2 = product_processor.get_result()

print(f"Device 1: {device1}")  # Galaxy A54 5G (SAMSUNG_ACCOUNT + REGISTRATION)
print(f"Device 2: {device2}")  # Galaxy S21 Ultra 5G (REGISTRATION)
```

## 의존성

- `pandas`: 데이터 처리 및 DataFrame 조작
- `datetime`: 날짜/시간 처리 (pandas 내장)

## 주의사항

1. **데이터 구조**: `product_data`의 각 항목은 `records` 배열을 포함해야 함
2. **메타데이터 매핑**: `meta_data`의 키는 `modelCode`와 일치해야 함
3. **날짜 형식**: `createdDateTime`은 ISO 8601 형식이어야 함
4. **최소 데이터**: 최소 2개의 제품 데이터가 필요함
5. **에러 처리**: 데이터가 없는 경우 기본값 '없음' 사용
6. **정적 메서드**: `get_priority`는 정적 메서드이므로 클래스 인스턴스 없이 호출 가능

## 에러 처리

### 일반적인 문제들
1. **데이터 누락**: `value.get()` 메서드로 안전한 데이터 추출
2. **빈 records 배열**: `[{}]` 기본값으로 인덱스 오류 방지
3. **날짜 형식 오류**: 문자열 분할로 ISO 8601 날짜 처리
4. **메타데이터 불일치**: modelCode가 일치하지 않는 경우 처리

### 디버깅 팁
- `df_product` DataFrame을 출력하여 데이터 변환 과정 확인
- `df_sorted` DataFrame을 출력하여 정렬 결과 확인
- 각 단계별 중간 결과 출력으로 문제 지점 파악

## 성능 최적화

1. **DataFrame 인덱싱**: `.at[]` 사용으로 빠른 데이터 접근
2. **정렬 최적화**: 필요한 컬럼만 정렬에 사용
3. **메모리 효율성**: 불필요한 데이터 복사 방지
4. **조건부 처리**: 우선순위 계산을 한 번만 수행

## 확장 가능성

### 1. 새로운 우선순위 규칙 추가
```python
@staticmethod
def get_priority(row):
    # 기존 로직
    if row['channel'] == 'SAMSUNG_ACCOUNT' and row['registration'] == 'REGISTRATION':
        return 1
    elif row['registration'] == 'REGISTRATION':
        return 2
    # 새로운 규칙 추가
    elif row['channel'] == 'NEW_CHANNEL':
        return 1.5  # 중간 우선순위와 최고 우선순위 사이
    else:
        return 3
```

### 2. 새로운 정렬 기준 추가
```python
# 정렬 기준에 새로운 컬럼 추가
df_sorted = df_product.sort_values(
    by=['priority', 'new_criteria', 'createdDateTime', 'insertion_order'],
    ascending=[True, False, False, True]
).reset_index(drop=True)
```

### 3. 상위 N개 제품 반환
```python
def get_result(self, top_n=2):
    # 상위 N개 제품명 반환하도록 수정
    products = []
    for i in range(min(top_n, len(df_sorted))):
        for compare_code in self.meta_data:
            if df_sorted.at[i,'modelCode'] == compare_code:
                products.append(self.meta_data[compare_code]['nameCis'])
                break
    return tuple(products)
```

## 테스트 케이스

### 1. 기본 케이스
- 3개 제품 중 상위 2개 선택
- 우선순위에 따른 정확한 정렬

### 2. 경계 케이스
- 2개 제품만 있는 경우
- 모든 제품이 같은 우선순위인 경우
- 제품 데이터가 없는 경우

### 3. 특수 케이스
- 날짜가 동일한 경우
- 메타데이터에 없는 제품 코드
- 잘못된 데이터 형식

## 관련 모듈

- `response_handler.py`: API 응답에서 제품 데이터 추출
- `smartThings_main.py`: 메인 실행 파일에서 제품 정보 처리 