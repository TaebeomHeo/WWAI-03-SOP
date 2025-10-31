# Response Handler Module

## 개요
`response_handler.py`는 삼성 SmartThings 웹페이지의 API 응답을 수집하고 처리하는 핵심 모듈입니다. Playwright를 사용하여 웹페이지에서 발생하는 API 응답을 모니터링하고, 응답 데이터를 파싱하여 구조화된 데이터로 변환합니다.

## 주요 기능

### 1. API 응답 모니터링
- 웹페이지에서 발생하는 모든 API 응답을 실시간으로 모니터링
- 타겟 URL과 일치하는 응답을 자동으로 감지
- 각 API 응답의 완료 상태를 추적

### 2. 데이터 수집 및 처리
- 메인 API에서 추천 데이터 추출
- 메타 API와 제품 API에서 디바이스 정보 추출
- 동의 API에서 동의 요건 확인
- 동의가 필요한 경우 배너 정보 수집

### 3. 비동기 이벤트 처리
- asyncio를 사용한 비동기 응답 대기
- 각 API 응답 완료를 이벤트로 관리
- 타임아웃 설정을 통한 안정적인 처리

## 클래스 구조

### AccountDataCollector 클래스

#### 초기화 매개변수
```python
def __init__(self, page, context, target_urls, target_columns, banner_tag, banner_link_tag, consent_file_path)
```

**매개변수 설명:**
- `page`: Playwright 페이지 객체
- `context`: Playwright 컨텍스트 객체
- `target_urls`: 모니터링할 API URL 딕셔너리 (main, product, meta, consent)
- `target_columns`: 수집할 데이터 컬럼 리스트
- `banner_tag`: 배너 텍스트를 추출할 CSS 선택자
- `banner_link_tag`: 배너 링크를 추출할 CSS 선택자
- `consent_file_path`: 동의 요건 파일 경로

#### 내부 변수
```python
self.responses = {}                    # 수집된 응답 데이터 저장
self.called = {k: False for k in target_urls.keys()}  # 각 API 호출 완료 여부 추적
self.main_event = asyncio.Event()     # 메인 API 응답 완료 이벤트
self.product_event = asyncio.Event()  # 제품 API 응답 완료 이벤트
self.meta_event = asyncio.Event()     # 메타 API 응답 완료 이벤트
self.consent_event = asyncio.Event()  # 동의 API 응답 완료 이벤트
```

## 메서드 상세 설명

### 1. setup_response_handler()
웹페이지의 모든 응답을 모니터링하는 핸들러를 설정하는 함수입니다.

**동작 과정:**
1. 브라우저 컨텍스트에 응답 이벤트 리스너 등록
2. 타겟 URL과 일치하는 응답을 감지하면 해당 이벤트를 설정
3. 각 API 응답의 완료 상태를 추적

**핸들러 로직:**
```python
def handler(res):
    for key in self.target_urls:
        if res.url.startswith(self.target_urls[key]) and not self.called[key]:
            self.called[key] = True
            self.responses[key] = res
            getattr(self, f"{key}_event").set()
```

### 2. wait_for_responses(timeout=60)
모든 필요한 API 응답이 완료될 때까지 대기하는 함수입니다.

**동작 과정:**
1. main, product, meta, consent 4개 API 응답을 모두 기다림
2. 모든 응답이 완료되거나 타임아웃이 발생하면 종료
3. asyncio.gather를 사용하여 병렬 대기

**매개변수:**
- `timeout`: 대기 시간 (초, 기본값: 60초)

### 3. handle_authentication_popup()
인증 팝업을 처리하는 함수입니다.

**동작 과정:**
1. 1초 대기 후 인증 버튼 선택자 대기
2. 모든 보이는 인증 버튼을 순차적으로 클릭
3. 인증이 필요하지 않은 경우 무시

### 4. process_responses(row)
수집된 API 응답들을 처리하여 구조화된 데이터로 변환하는 함수입니다.

**동작 과정:**
1. **메인 API 응답 처리**: 추천 데이터 추출 및 모든 타겟 컬럼에 매핑
2. **메타 API 응답 처리**: 제품 메타데이터 추출
3. **제품 API 응답 처리**: 사용자 제품 목록 추출
4. **디바이스 정보 처리**: 메타데이터가 2개 이하면 첫 번째 제품을 중복 사용
5. **동의 API 응답 처리**: 상태 코드에 따라 다른 처리
6. **배너 정보 수집**: 동의가 필요한 경우에만 배너 표시

**반환값:**
- `dict`: 처리된 행 데이터 (모든 target_columns 포함)

## API 응답 처리 상세

### 1. 메인 API 응답 처리
```python
body_main = await self.responses["main"].json()
json_data_main = body_main['resultData']['result']['recommend']
row_data = {col: json_data_main.get(col, "없음") for col in self.target_columns}
```

### 2. 메타 API 응답 처리
```python
body_meta = await self.responses["meta"].json()
json_data_meta = body_meta['resultData']['result']
```

### 3. 제품 API 응답 처리
```python
body_product = await self.responses["product"].json()
json_data_product = body_product['resultData']['myProducts']['products']['productList']['items']
```

### 4. 디바이스 정보 처리
```python
if len(json_data_meta) <= 2:
    first_key = next(iter(json_data_meta))
    first_value = json_data_meta[first_key]
    Device1 = Device2 = first_value['nameCis']
else:
    product_list = product(json_data_meta, json_data_product)
    Device1, Device2 = product_list.get_result()
```

### 5. 동의 API 응답 처리
```python
if self.responses["consent"].status == 204:  # 204: No Content (동의 불필요)
    law_agree_data = law_agree(self.consent_file_path, self.responses["consent"], str(row['country_code']))
    law_agree_result = law_agree_data.get_no_data_result()
else:  # 200: OK (동의 필요)
    consent_json = await self.responses["consent"].json()
    law_agree_data = law_agree(self.consent_file_path, consent_json, str(row['country_code']))
    law_agree_result = law_agree_data.get_data_result()
```

### 6. 동의가 필요한 경우 추가 처리
```python
if law_agree_result.iloc[0] == 'X':
    # N 버전의 스토리와 라이프스타일 데이터 사용
    for n in range(1, 4):
        story_keyN = f"storyIdRank{n}N"
        story_key = f"storyIdRank{n}"
        lifestyle_keyN = f"lifeStyleIdRank{n}N"
        lifestyle_key = f"lifeStyleIdRank{n}"
        
        if story_keyN in json_data_main:
            row_data[story_key] = json_data_main[story_keyN]
        if lifestyle_keyN in json_data_main:
            row_data[lifestyle_key] = json_data_main[lifestyle_keyN]
    
    # 배너 정보 수집
    banner_locator = self.page.locator(self.banner_tag)
    banner_link_locator = self.page.locator(self.banner_link_tag)
    
    if await banner_locator.count() > 0 and await banner_locator.is_visible():
        row_data['banner_text'] = await banner_locator.inner_text()
        row_data['banner_link_text'] = await banner_link_locator.inner_text()
        row_data['banner_hyperlink'] = await banner_link_locator.get_attribute('href')
```

## 모니터링 대상 API

### 1. 메인 스토리 API
- **URL**: `/aemapi/v6/mysamsung/{country}/scv/user/recommend/st/story`
- **용도**: 추천 데이터, 스토리 정보, 라이프스타일 정보 수집
- **응답 구조**: `resultData.result.recommend`

### 2. 제품 메타데이터 API
- **URL**: `/aemapi/v6/mysamsung/{country}/scv/product/meta`
- **용도**: 제품 메타데이터, 디바이스 정보 수집
- **응답 구조**: `resultData.result`

### 3. 새 제품 API
- **URL**: `/aemapi/v6/mysamsung/{country}/scv/newproducts`
- **용도**: 사용자 제품 목록, 제품 우선순위 정보 수집
- **응답 구조**: `resultData.myProducts.products.productList.items`

### 4. 동의 요건 API
- **URL**: `https://account.samsung.com/api/v1/consent/required`
- **용도**: 마케팅 동의 요건 확인
- **응답 상태**: 200 (동의 필요), 204 (동의 불필요)

## 사용 예시

```python
# AccountDataCollector 객체 생성
data_collect = AccountDataCollector(
    page,                    # Playwright 페이지 객체
    context,                 # Playwright 컨텍스트 객체
    target_urls,            # API URL 딕셔너리
    target_columns,         # 수집할 컬럼 리스트
    banner_tag,             # 배너 텍스트 선택자
    banner_link_tag,        # 배너 링크 선택자
    consent_file_path       # 동의 요건 파일 경로
)

# 응답 핸들러 설정
await data_collect.setup_response_handler()

# API 응답 대기
await data_collect.wait_for_responses(timeout=60)

# 응답 데이터 처리
row_data = await data_collect.process_responses(row)
```

## 의존성

### 외부 모듈
- `playwright.sync_api`: 브라우저 자동화
- `playwright.async_api`: 비동기 브라우저 제어
- `asyncio`: 비동기 프로그래밍

### 내부 모듈
- `smartThings_module.product_result`: 제품 정보 처리
- `smartThings_module.law_agree_result`: 동의 요건 처리

## 주의사항

1. **비동기 처리**: 모든 메서드가 비동기로 구현되어 있어 await 키워드 사용 필요
2. **타임아웃 설정**: API 응답 대기 시간을 적절히 설정해야 함
3. **선택자 설정**: 배너 관련 CSS 선택자가 올바르게 설정되어야 함
4. **파일 경로**: 동의 요건 파일 경로가 유효해야 함
5. **API 응답 구조**: 각 API의 응답 구조가 예상과 일치해야 함

## 에러 처리

### 일반적인 문제들
1. **API 응답 없음**: 타임아웃 설정 조정, 네트워크 상태 확인
2. **선택자 오류**: CSS 선택자 유효성 확인
3. **파일 경로 오류**: 동의 요건 파일 경로 확인
4. **응답 구조 변경**: API 응답 구조 변경 시 코드 수정 필요

### 디버깅 팁
- `self.called` 딕셔너리를 통해 각 API 응답 상태 확인
- `self.responses` 딕셔너리에서 실제 응답 데이터 확인
- 콘솔 출력을 통한 진행 상황 모니터링
- 각 단계별 예외 처리 및 로깅

## 성능 최적화

- **병렬 대기**: asyncio.gather를 사용하여 여러 API 응답을 동시에 대기
- **이벤트 기반 처리**: 각 API 응답 완료를 이벤트로 관리하여 효율적인 처리
- **선택적 데이터 수집**: 필요한 경우에만 배너 정보 수집

## 확장 가능성

- 새로운 API 엔드포인트 추가
- 추가 데이터 처리 로직 구현
- 다양한 응답 형식 지원
- 캐싱을 통한 성능 향상
- 로깅 및 모니터링 기능 강화 