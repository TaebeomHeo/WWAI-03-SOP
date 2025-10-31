# SmartThings 프로젝트 동작 프로세스 상세 가이드

## 📋 프로젝트 개요
이 프로젝트는 삼성 SmartThings 웹페이지의 자동화 테스트를 수행하여 다양한 계정과 국가별로 데이터를 수집하고 비교하는 시스템입니다.

## 🏗️ 전체 아키텍처

```
smartThings_main.py (메인 실행 파일)
    ↓
smartThings_module/ (모듈 폴더)
    ├── rowdata_excel.py      # Excel 데이터 처리
    ├── response_handler.py   # API 응답 수집
    ├── html_result.py        # HTML 데이터 추출
    ├── product_result.py     # 제품 데이터 처리
    ├── law_agree_result.py   # 동의 요건 처리
    └── compare_result.py     # 결과 비교 및 분석
```

## 🔄 메인 실행 프로세스

### 1. 초기화 및 설정 단계

#### 1.1 모듈 경로 설정
```python
# smartThings_main.py (라인 15-21)
current_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(current_dir, 'smartThings_module')

# sys.path에 모듈 폴더 추가 (없을 경우만)
if module_path not in sys.path:
    sys.path.append(module_path)
    print(f"Added module path: {module_path}")
```
- **파일**: `smartThings_main.py`
- **역할**: Python 모듈 검색 경로에 smartThings_module 폴더 추가
- **목적**: 모듈 import를 위한 경로 설정

#### 1.2 데이터 컬럼 정의
```python
# smartThings_main.py (라인 35-47)
target_columns = [    
    'Account',    # 계정 정보
    'main_headline', 'main_description', 'main_description1', 'main_description2',  # 메인 정보
    'storyIdRank1', 'storyIdRank2', 'storyIdRank3',  # 스토리 ID들
    'storyIdRank1_title', 'storyIdRank1_desc',  # 스토리 1 제목/설명
    'storyIdRank1_rec1','storyIdRank1_rec2','storyIdRank1_rec3','storyIdRank1_rec4','storyIdRank1_rec5',  # 스토리 1 추천 제품들
    'storyIdRank2_title', 'storyIdRank2_desc',  # 스토리 2 제목/설명
    'storyIdRank2_rec1','storyIdRank2_rec2','storyIdRank2_rec3','storyIdRank2_rec4','storyIdRank2_rec5',  # 스토리 2 추천 제품들
    'storyIdRank3_title', 'storyIdRank3_desc',  # 스토리 3 제목/설명
    'storyIdRank3_rec1','storyIdRank3_rec2','storyIdRank3_rec3','storyIdRank3_rec4','storyIdRank3_rec5',  # 스토리 3 추천 제품들
    'lifeStyleIdRank1','lifeStyleIdRank2','Scenariokeyword1','Scenariokeyword2',  # 라이프스타일 및 시나리오 키워드
    'country_code','Device1','Device2','banner_text', 'banner_link_text','banner_hyperlink'  # 국가, 디바이스, 배너 정보
]
```
- **파일**: `smartThings_main.py`
- **역할**: 수집할 데이터의 구조 정의
- **목적**: 최종 결과 DataFrame의 컬럼 구조 설정

#### 1.3 파일 경로 설정
```python
# smartThings_main.py (라인 52-63)
samsung_project_path = r'C:\Users\WW\Desktop\삼성 프로젝트 관련 파일'
now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')  # 현재 시간을 파일명에 포함
result_full_path = samsung_project_path+r'\result_'+now  # 결과 저장 디렉토리
result_file_path = result_full_path+r'테스트결과_result.xlsx'  # 최종 결과 파일 경로

format_data_path = samsung_project_path + r'\Test data matrix (Umbrella merge).xlsx'
contents_data_path = samsung_project_path + r'\contents'
umbrella_file_path = samsung_project_path+r'\umbrella'
consent_file_path = samsung_project_path + r'\국가별 마케팅 동의 요건.xlsx'
compare_item_path = samsung_project_path + r'\계정별비교항목.xlsx'
```
- **파일**: `smartThings_main.py`
- **역할**: 프로젝트에 필요한 모든 파일 경로 설정
- **목적**: Excel 파일, 콘텐츠, 우산 파일 등의 경로 정의

#### 1.4 Excel 파일 설정
```python
# smartThings_main.py (라인 66-67)
usecols = 'C,U,V,X,Y,Z'  # 사용할 Excel 컬럼
tc_sheet_name = "Test data matrix"  # Excel 시트명
```
- **파일**: `smartThings_main.py`
- **역할**: Excel 파일에서 사용할 컬럼과 시트명 설정
- **목적**: 테스트 데이터 추출을 위한 Excel 설정

### 2. Excel 데이터 처리 단계

#### 2.1 RowDataExcel 객체 생성 및 초기화
```python
# smartThings_main.py (라인 92-93)
rowdata_excel = RowDataExcel(
    format_data_path, contents_data_path, umbrella_file_path,
    country_codes, tc_sheet_name, usecols,
    format_banner_text, format_banner_link_text, format_banner_hyperlink
)
```
- **파일**: `smartThings_main.py` → `smartThings_module/rowdata_excel.py`
- **역할**: Excel 데이터 처리 객체 생성
- **목적**: 테스트 데이터, 콘텐츠 매핑, 우산 파일 처리

#### 2.2 Excel 데이터 로드 및 처리
```python
# smartThings_main.py (라인 94-96)
rowdata_excel.load_excel()           # Excel 파일 로드
rowdata_excel.process_rows(6)        # 행 데이터 처리 (6행까지)
rowdata_excel.copy_format_data()     # 국가별 데이터 복사

format_result = rowdata_excel.get_result()  # 포맷 결과 가져오기
```
- **파일**: `smartThings_main.py` → `smartThings_module/rowdata_excel.py`
- **역할**: Excel 파일에서 테스트 데이터 추출 및 가공
- **목적**: 각 계정별 테스트 케이스 데이터 준비

**세부 동작 과정:**
1. **`load_excel()`**: Excel 파일 읽기 및 컬럼명 리네이밍
2. **`process_rows(6)`**: 6행까지의 데이터를 storyIdRank1, storyIdRank2, storyIdRank3로 매핑
3. **`copy_format_data()`**: 국가별 데이터 복사 (DE, FR, ES, IT)

### 3. 웹 자동화 실행 단계

#### 3.1 메인 실행 함수 정의
```python
# smartThings_main.py (라인 104-112)
async def smartThings_main(playwright: Playwright) -> None:
    """
    메인 실행 함수 - 각 계정별로 웹 자동화 및 데이터 수집을 수행
    
    - Playwright를 사용하여 브라우저 자동화
    - 각 계정별로 로그인 및 데이터 수집
    - API 응답 모니터링 및 HTML 데이터 추출
    - 스크린샷 캡처 및 결과 저장
    """
```
- **파일**: `smartThings_main.py`
- **역할**: 메인 실행 함수 정의
- **목적**: 각 계정별 웹 자동화 및 데이터 수집 프로세스 실행

#### 3.2 Playwright 브라우저 설정
```python
# smartThings_main.py (라인 123-134)
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

browser = await playwright.chromium.launch(
    headless=False,  # 브라우저 창 표시
    executable_path=CHROME_PATH,  # Chrome 실행 파일 경로
    args=[
        "--user-agent=D2CEST-AUTO-70a4cf16 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36.D2CEST-AUTO-70a4cf16",
        "--incognito",  # 시크릿 모드
        "--start-maximized",  # 최대화된 창으로 시작
        "--remote-allow-origins=*"  # 원격 연결 허용
    ]
)
```
- **파일**: `smartThings_main.py`
- **역할**: Chrome 브라우저 인스턴스 생성 및 설정
- **목적**: 웹 자동화를 위한 브라우저 환경 구성

#### 3.3 API 엔드포인트 설정
```python
# smartThings_main.py (라인 137-140)
target_url_main = f"https://hshopfront.samsung.com/aemapi/v6/mysamsung/{row['country_code'].lower()}/scv/user/recommend/st/story"
target_url_meta = f"https://hshopfront.samsung.com/aemapi/v6/mysamsung/{row['country_code'].lower()}/scv/product/meta"
target_url_product = f"https://hshopfront.samsung.com/aemapi/v6/mysamsung/{row['country_code'].lower()}/scv/newproducts"
target_url_consent = f"https://account.samsung.com/api/v1/consent/required"

# 모든 API URL을 딕셔너리로 구성
taget_url_total = {"main" : target_url_main, "meta" : target_url_meta, "product" : target_url_product, "consent" : target_url_consent}
```
- **파일**: `smartThings_main.py`
- **역할**: 모니터링할 API 엔드포인트 URL 설정
- **목적**: 각 국가별 API 응답 데이터 수집

#### 3.4 로그인 및 인증 과정
```python
# smartThings_main.py (라인 154-170)
# SmartThings 페이지로 이동
response = await page.goto(f"https://hshopfront.samsung.com/{row['country_code'].lower()}/mypage/mysmartthings")

# 응답 상태 확인 - 로그인 과정 전에 먼저 확인
if response:
    if response.status == 200:
        print("200 ok")    # 성공
        # 로그인 과정 실행
        await page.get_by_role("textbox", name="사용자 이름").click()
        await page.wait_for_timeout(1000)
        await page.get_by_role("textbox", name="사용자 이름").fill("qauser")
        await page.wait_for_timeout(1000)
        await page.get_by_role("textbox", name="암호").click()
        await page.wait_for_timeout(1000)
        await page.get_by_role("textbox", name="암호").fill("qauser1!")
        await page.wait_for_timeout(1000)
        await page.get_by_role("button", name="로그인").click()
        await page.wait_for_timeout(1000)
        
        # 계정 정보 입력
        await page.locator("input[name='account']").click()
        await page.wait_for_timeout(1000)
        await page.locator("input[name='account']").fill(format_result['Account'].values[idx])
        await page.wait_for_timeout(1000)
        await page.locator("button[type='button']").nth(0).click()
        await page.wait_for_timeout(1000)
        await page.locator("input[type='password']").fill('mypage1!')
        await page.wait_for_timeout(1000)
        await page.locator("button[type='button']").nth(2).click()
```
- **파일**: `smartThings_main.py`
- **역할**: SmartThings 웹페이지 로그인 및 계정 인증
- **목적**: 테스트 계정으로 로그인하여 데이터 수집 권한 획득

### 4. 데이터 수집 단계

#### 4.1 AccountDataCollector 객체 생성 및 설정
```python
# smartThings_main.py (라인 180-182)
data_collect = AccountDataCollector(
    page, context, taget_url_total, target_columns,
    banner_tag, banner_link_tag, consent_file_path
)
await data_collect.setup_response_handler()
await page.wait_for_timeout(4000)  # 4초 대기
```
- **파일**: `smartThings_main.py` → `smartThings_module/response_handler.py`
- **역할**: API 응답 모니터링 및 데이터 수집 객체 생성
- **목적**: 웹페이지에서 발생하는 모든 API 응답을 실시간으로 수집

**세부 동작 과정:**
1. **`setup_response_handler()`**: 브라우저 컨텍스트에 응답 이벤트 리스너 등록
2. **`wait_for_responses(timeout=60)`**: 4개 API(main, product, meta, consent) 응답 대기
3. **`process_responses(row)`**: 수집된 응답 데이터를 구조화된 형태로 변환

#### 4.2 인증 팝업 처리
```python
# smartThings_main.py (라인 184-189)
try:
    # 인증 관련 버튼 클릭 (필요한 경우)
    await page.locator("button[type='button']").nth(1).click(timeout=5000)
except:
    pass  # 인증이 필요하지 않은 경우 무시
```
- **파일**: `smartThings_main.py`
- **역할**: 추가 인증 팝업 처리
- **목적**: 필요시 추가 인증 과정 완료

#### 4.3 API 응답 데이터 처리
```python
# smartThings_main.py (라인 191-200)
# API 응답 대기
try:
    await data_collect.wait_for_responses(timeout=60)
except asyncio.TimeoutError:
    print("타임아웃 발생")
    for key, received in data_collect.called.items():
        if not received:
            print(f" - {key} 응답 없음")

# API 응답 데이터 처리
row_data = await data_collect.process_responses(row)
```
- **파일**: `smartThings_main.py` → `smartThings_module/response_handler.py`
- **역할**: API 응답 데이터를 처리하여 row_data 딕셔너리로 변환
- **목적**: 각 API에서 받은 데이터를 통합하여 하나의 데이터 구조로 정리

**처리되는 데이터 타입:**
- **Main API**: 스토리 추천 정보
- **Product API**: 제품 목록 및 메타데이터
- **Meta API**: 제품 상세 정보
- **Consent API**: 마케팅 동의 요건

### 5. HTML 데이터 추출 단계

#### 5.1 HTML 요소 대기
```python
# smartThings_main.py (라인 202-210)
# 해당 함수는 실제 데이터가 바인딩이 완료될 때까지 대기하는 함수
# 즉 selector안 요소를 변수로 받고 해당 변수값에 '{{' 텍스트가 없다는 것은 바인딩이 완료되었다는 뜻 이후 데이터 반환
await page.wait_for_function(
    """selector => {
        const el = document.querySelector(selector);
        return el && !el.innerText.includes("{{");
    }""",
    arg=[main_headline_tag],  # Python 변수 전달
    timeout=80000  # 80초 타임아웃
)
```
- **파일**: `smartThings_main.py`
- **역할**: HTML 요소의 데이터 바인딩 완료 대기
- **목적**: `{{` 텍스트가 사라질 때까지 대기하여 실제 데이터 로딩 완료 확인

#### 5.2 HTML 데이터 추출
```python
# smartThings_main.py (라인 212-216)
# HTML 데이터 추출
html_parse_data = htmlExtractor(
    page, main_headline_tag, main_desc_tag, story_data_tag,
    row_data, target_columns
)
await html_parse_data.html_main_headline_ext()    # 메인 헤드라인 추출
await html_parse_data.html_main_description_ext() # 메인 설명 추출
await html_parse_data.html_story_data_ext()      # 스토리 데이터 추출
```
- **파일**: `smartThings_main.py` → `smartThings_module/html_result.py`
- **역할**: 웹페이지의 HTML 요소에서 텍스트 데이터 추출
- **목적**: API 응답과 별도로 화면에 표시되는 실제 텍스트 데이터 수집

**추출되는 데이터:**
- **메인 헤드라인**: 페이지 상단의 주요 제목
- **메인 설명**: 페이지 설명 텍스트
- **스토리 데이터**: 각 스토리별 제목, 설명, 추천 제품 정보

### 6. 결과 데이터 통합 단계

#### 6.1 결과 DataFrame에 데이터 추가
```python
# smartThings_main.py (라인 218-219)
# 결과 데이터를 DataFrame에 추가
main_result.loc[len(main_result)] = row_data
```
- **파일**: `smartThings_main.py`
- **역할**: 수집된 모든 데이터를 main_result DataFrame에 추가
- **목적**: 각 계정별 테스트 결과를 하나의 DataFrame에 누적

#### 6.2 스크린샷 캡처
```python
# smartThings_main.py (라인 221-222)
await page.wait_for_timeout(2000)  # 2초 대기
# 해당 페이지 캡처
await page.screenshot(
    path=result_full_path+'\\'+str(row['Account'])+'.png',
    full_page=True
)
```
- **파일**: `smartThings_main.py`
- **역할**: 각 계정별 테스트 결과 페이지의 전체 스크린샷 저장
- **목적**: 시각적 검증을 위한 증거 자료 생성

#### 6.3 리소스 정리
```python
# smartThings_main.py (라인 224-227)
# 정상 종료 및 리소스 정리
await page.wait_for_timeout(2000)  # 2초 대기
await page.close()  # 페이지 닫기
await context.close()  # 컨텍스트 닫기
await browser.close()  # 브라우저 닫기
```
- **파일**: `smartThings_main.py`
- **역할**: 브라우저 리소스 정리
- **목적**: 메모리 누수 방지 및 안정적인 실행

### 7. 오류 처리 및 재시도

#### 7.1 재시도 로직
```python
# smartThings_main.py (라인 117-121)
# 같은 row에 대해 최대 3회 재시도
for attempt in range(1, 4):
    page = None
    context = None
    browser = None
    try:
        # 브라우저 실행 및 데이터 수집 로직
        # ... 생략 ...
        break  # 성공했으므로 재시도 루프 종료
    except Exception as e:
        print(f"일반 예외 발생 (시도 {attempt}/3) :", e)
        # 리소스 정리 (있을 경우에만)
        try:
            if page: await page.close()
        except: pass
        try:
            if context: await context.close()
        except: pass
        try:
            if browser: await browser.close()
        except: pass

        # 마지막(3회차) 실패 시 에러 행 기록
        if attempt == 3:
            error_row = {col: '없음' for col in main_result.columns}
            error_row['Account'] = row['Account']
            error_row['country_code'] = row['country_code']
            main_result.loc[len(main_result)] = error_row
        else:
            # 다음 재시도 전 잠시 대기
            await asyncio.sleep(2)
```
- **파일**: `smartThings_main.py`
- **역할**: 실패 시 최대 3회 재시도 및 에러 처리
- **목적**: 안정적인 데이터 수집 및 오류 상황 대응

### 8. 우산 매핑 및 최종 결과 생성 단계

#### 8.1 콘텐츠 매핑
```python
# smartThings_main.py (라인 291)
rowdata_excel.contents_mapping()  # 콘텐츠 매핑
```
- **파일**: `smartThings_main.py` → `smartThings_module/rowdata_excel.py`
- **역할**: 콘텐츠 파일과 매핑하여 완성된 테스트 데이터 생성
- **목적**: 예상 데이터와 실제 데이터를 비교하기 위한 포맷 데이터 생성

#### 8.2 우산 파일 매핑
```python
# smartThings_main.py (라인 293-294)
# 우산 매핑 및 최종 결과 생성
rowdata_excel.umbrella_main_mapping(main_result, country_codes)
final_format_result = rowdata_excel.get_result()  # 최종 포맷 결과 가져오기
```
- **파일**: `smartThings_main.py` → `smartThings_module/rowdata_excel.py`
- **역할**: 우산 파일을 사용하여 메인 데이터와 매핑
- **목적**: 예상 데이터와 실제 데이터를 비교하기 위한 포맷 데이터 생성

### 9. 데이터 비교 및 분석 단계

#### 9.1 결과 파일 저장
```python
# smartThings_main.py (라인 297-298)
# 결과 파일 저장
final_format_result.to_excel(r'C:\Users\WW\Desktop\테스트_결과_format.xlsx', index=False, sheet_name='테스트결과')
main_result.to_excel(r'C:\Users\WW\Desktop\테스트_결과_main.xlsx', index=False, sheet_name='테스트결과')
```
- **파일**: `smartThings_main.py`
- **역할**: 중간 결과 파일 저장
- **목적**: 디버깅 및 중간 검증을 위한 데이터 저장

#### 9.2 CompareProcess 객체 생성 및 실행
```python
# smartThings_main.py (라인 301-305)
# 비교 프로세스 실행
compare_process = CompareProcess(
    final_format_result, main_result, compare_item_path,
    result_file_path, country_codes
)
compare_process.compare_data()      # 데이터 비교
compare_process.item_abs_data()    # 항목별 데이터 처리
compare_process.abs_rec_data()     # 추천 제품 데이터 처리
compare_process.get_result()       # 최종 결과 생성
```
- **파일**: `smartThings_main.py` → `smartThings_module/compare_result.py`
- **역할**: 예상 데이터와 실제 데이터를 비교하여 차이점 분석
- **목적**: 테스트 결과의 정확성 검증 및 불일치 항목 식별

**세부 동작 과정:**
1. **`compare_data()`**: 각 컬럼별로 일치/불일치 여부 확인
2. **`item_abs_data()`**: 비교 항목 파일을 기반으로 데이터 필터링
3. **`abs_rec_data()`**: 추천 제품 데이터의 우선순위 처리
4. **`get_result()`**: 최종 비교 결과를 Excel 파일로 저장

## 🔧 주요 모듈별 상세 기능

### 1. RowDataExcel (`smartThings_module/rowdata_excel.py`)

**주요 메서드:**
- **`load_excel()`**: Excel 파일 로드 및 컬럼명 리네이밍
- **`process_rows(max_rows)`**: 행 데이터를 storyIdRank로 매핑
- **`copy_format_data()`**: 국가별 데이터 복사
- **`contents_mapping()`**: 콘텐츠 파일과 매핑
- **`umbrella_main_mapping()`**: 우산 파일을 사용한 최종 매핑

**데이터 처리 흐름:**
```
Excel 파일 → 컬럼 리네이밍 → 행 데이터 처리 → 국가별 복사 → 콘텐츠 매핑 → 우산 매핑 → 최종 결과
```

### 2. AccountDataCollector (`smartThings_module/response_handler.py`)

**주요 메서드:**
- **`setup_response_handler()`**: API 응답 모니터링 설정
- **`wait_for_responses(timeout)`**: 모든 API 응답 대기
- **`process_responses(row)`**: 응답 데이터를 구조화된 형태로 변환

**API 모니터링 대상:**
- **Main API**: 스토리 추천 정보
- **Product API**: 제품 목록
- **Meta API**: 제품 메타데이터
- **Consent API**: 마케팅 동의 요건

### 3. HtmlExtractor (`smartThings_module/html_result.py`)

**주요 메서드:**
- **`html_main_headline_ext()`**: 메인 헤드라인 추출
- **`html_main_description_ext()`**: 메인 설명 추출
- **`html_story_data_ext()`**: 스토리 데이터 추출

**데이터 추출 방식:**
- CSS 선택자를 사용한 요소 검색
- 텍스트 내용 추출 및 정리
- 결과를 row_data 딕셔너리에 저장

### 4. Product (`smartThings_module/product_result.py`)

**주요 메서드:**
- **`get_priority(row)`**: 제품 우선순위 계산
- **`get_result()`**: 우선순위별 정렬된 제품 목록 반환

**우선순위 규칙:**
1. **최고 우선순위**: SAMSUNG_ACCOUNT 채널 + REGISTRATION 상태
2. **중간 우선순위**: REGISTRATION 상태 (채널 무관)
3. **최저 우선순위**: 기타 모든 경우

### 5. LawAgree (`smartThings_module/law_agree_result.py`)

**주요 메서드:**
- **`get_no_data_result()`**: 동의 데이터가 없는 경우 처리
- **`get_data_result()`**: 동의 데이터가 있는 경우 처리

**동의 타입:**
- **MKT**: 마케팅 동의
- **CZSVC**: 서비스 동의
- **CZADV**: 광고 동의

### 6. CompareProcess (`smartThings_module/compare_result.py`)

**주요 메서드:**
- **`compare_data()`**: 포맷 데이터와 실제 데이터 비교
- **`item_abs_data()`**: 비교 항목별 데이터 필터링
- **`abs_rec_data()`**: 추천 제품 데이터 처리
- **`get_result()`**: 최종 비교 결과 생성

**비교 결과:**
- **일치**: 예상 데이터와 실제 데이터가 동일
- **불일치**: 차이점이 있는 경우 상세 정보 제공
- **NA**: 비교 대상이 아닌 항목

## 📊 데이터 흐름도

```
Excel 테스트 데이터
        ↓
RowDataExcel 처리
        ↓
국가별 데이터 복사
        ↓
Playwright 웹 자동화
        ↓
API 응답 수집
        ↓
HTML 데이터 추출
        ↓
결과 데이터 통합
        ↓
콘텐츠 매핑
        ↓
우산 파일 매핑
        ↓
데이터 비교 분석
        ↓
최종 결과 Excel 파일
```

## 🚀 실행 순서 요약

1. **초기화**: 모듈 경로 설정, 컬럼 정의, 파일 경로 설정
2. **Excel 처리**: 테스트 데이터 로드, 국가별 복사
3. **웹 자동화**: 브라우저 실행, 로그인, 페이지 이동
4. **데이터 수집**: API 응답 모니터링, HTML 데이터 추출
5. **결과 통합**: 수집된 데이터를 DataFrame에 저장
6. **콘텐츠 매핑**: 콘텐츠 파일과 매핑
7. **우산 매핑**: 예상 데이터와 실제 데이터 매핑
8. **비교 분석**: 일치/불일치 여부 확인 및 결과 생성
9. **파일 저장**: 최종 결과를 Excel 파일로 저장

## ⚠️ 주의사항

1. **파일 경로**: 모든 파일 경로가 올바르게 설정되어야 함
2. **로그인 정보**: 테스트 계정 정보가 유효해야 함
3. **네트워크**: API 응답을 받기 위한 안정적인 네트워크 연결 필요
4. **타임아웃**: 각 단계별 적절한 타임아웃 설정 필요
5. **에러 처리**: 재시도 로직과 예외 처리가 구현되어 있음
6. **리소스 관리**: 브라우저, 페이지, 컨텍스트의 적절한 정리 필요

## 🔍 디버깅 팁

1. **브라우저 모드**: `headless=False`로 설정하여 실행 과정 모니터링
2. **로그 출력**: 각 단계별 진행 상황을 콘솔에 출력
3. **스크린샷**: 각 계정별 결과 페이지 캡처로 시각적 검증
4. **중간 결과**: 포맷 데이터와 메인 결과를 별도 파일로 저장하여 중간 검증
5. **재시도 로직**: 실패 시 최대 3회 재시도하여 안정성 확보
6. **타임아웃 설정**: HTML 바인딩 대기 시간을 80초로 설정하여 안정성 확보
7. **에러 행 기록**: 3회 실패 시 에러 행을 결과에 추가하여 추적 가능
