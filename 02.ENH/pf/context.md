# PF 검증 시스템 Context 문서

> **AI 에이전트 모드 전용 참조 문서**  
> 이 문서는 Cursor AI가 코드 수정, 업데이트, 버그 수정 시 참고하는 핵심 정보를 담고 있습니다.

## 🚀 빠른 시작 가이드

### 핵심 실행 명령어
```bash
# 개발 중 실행 (DEFAULT_TARGETS 순회)
python main.py

# 실 테스트 실행 (SSI 지정)
python main.py --ssi <SSI_ID>

# 가상환경 활성화 (Windows)
.venv\Scripts\activate
```

### 실행 모드 구분
- **개발 모드**: `python main.py` - main.py의 DEFAULT_TARGETS 배열을 순회
- **실 테스트 모드**: `python main.py --ssi <SSI_ID>` - Zest API에서 URL 예약받아 처리

### 주요 진입점
- **main.py**: 애플리케이션 진입점, nv19 추출 및 통합 관리
- **pf.py**: PF 구조 추출 및 모든 검증 모듈 통합
- **pf_modules/**: 모듈화된 검증 시스템 (8개 모듈)

### DEFAULT_TARGETS 설정
```python
# main.py의 DEFAULT_TARGETS 배열
DEFAULT_TARGETS = [
    {"url": "https://p6-pre-qa3.samsung.com/za/smartphones/all-smartphones/", "siteCode": "ZA"},
    # {"url": "https://p6-pre-qa3.samsung.com/za/tvs/all-tvs/", "siteCode": "ZA"},
    # {"url": "https://p6-pre-qa3.samsung.com/za/computers/all-computers/", "siteCode": "ZA"},
    # {"url": "https://p6-pre-qa3.samsung.com/za/refrigerators/all-refrigerators/", "siteCode": "ZA"},
]
```

## 🏗️ 시스템 아키텍처

### 전체 실행 흐름
```
main.py → nv19 추출 → pf.py → nv20 병렬 처리 → 검증 모듈들 → JSON 저장
```

### 핵심 모듈 구조
```
pf_modules/
├── filter.py          # 필터 기능 검증
├── live_validation.py  # 라이브 환경 검증
├── result_count.py    # 결과 수 검증
├── nv17.py           # nv17-breadcrumb 검증
├── purchase.py       # 구매 가능성 검증
├── sort.py           # 정렬 기능 검증
└── node.py           # 데이터 구조화
```

## 🎯 핵심 CSS 선택자

### nv19 (메인 네비게이션)
```css
.nv19-pd-category-main .nv19-pd-category-main__item
```

### nv20 (서브 네비게이션)
```css
.tab__item-title
```

### 필터
```css
.pd21-filter__selector-list
.pd21-filter__selector-item--checkbox
.checkbox-v3
```

### 제품 카드
```css
div.pd21-product-card__item[data-productidx]
.pd21-product-card__name
```

### BreadCrumb
```css
.breadcrumb__path li .breadcrumb__text-desktop
```

## 🔧 핵심 함수 참조

### main.py
- `extract_main_category()`: nv19 추출
- `extract_pf_structure()`: PF 구조 추출 (pf.py 호출)
- `verify_cgd_data()`: CGD 검증 통합 실행

### pf.py
- `extract_pf_structure()`: 메인 함수 (모든 검증 모듈 통합)
- `_extract_subtab_info()`: nv20 정보 추출
- `_process_subtab()`: nv20 처리
- `extract_product()`: 제품 정보 추출

### pf_modules 패키지

#### filter.py
- `extract_filter_structure()`: 필터 구조 추출
- `validate_filter()`: 필터 검증 실행
- `_generate_random_combinations()`: 랜덤 조합 생성
- `_test_filter_combination()`: 필터 조합 테스트

#### live_validation.py
- `validate_all_live_elements()`: 라이브 검증 통합 실행
- `extract_breadcrumb()`: BreadCrumb 추출
- `extract_faq()`: FAQ DOM 구조 추출
- `extract_disclaimer()`: Disclaimer DOM 구조 추출
- `convert_to_live_url()`: 라이브 URL 변환

#### 기타 모듈
- **result_count.py**: `extract_result_count()` - 결과 수 추출 및 검증
- **nv17.py**: `validate_nv17_breadcrumb_absence()` - nv17-breadcrumb 요소 부적절한 노출 검증
- **purchase.py**: `validate_purchase_capability()` - 구매 가능성 검증 (CTA 버튼 an-la 속성 기반)
- **sort.py**: `validate_sort()` - 정렬 기능 일치성 검증
- **node.py**: 데이터 구조 클래스들 (MainCategoryNode, SubCategoryNode, PfMenuNode)

## 📊 데이터 구조

### SubCategoryNode (핵심 필드)
```python
@dataclass
class SubCategoryNode:
    # 기본 정보
    name: str = ""
    url: str = ""
    
    # 링크 검증 필드
    link_status: int = -1  # HTTP 응답 상태 코드
    link_validate: bool = False
    link_validate_desc: str = ""
    
    # nv17 검증 필드
    nv17_validate: bool = False
    nv17_validate_desc: str = ""
    
    # 네비게이션 가시성 검증 필드
    navigation_visible_validate: bool = False
    navigation_visible_validate_desc: str = ""
    
    # 헤드라인 검증 필드
    headline: str = ""
    headline_validate: bool = False
    headline_validate_desc: str = ""
    
    # 결과 수 검증 필드
    result_count: int = 0
    result_validate: bool = False
    result_validate_desc: str = ""
    
    # 정렬 검증 필드
    sort_validate: bool = False
    sort_validate_desc: str = ""
    sort_validate_info: Dict[str, Any] = None
    
    # 구매 가능 검증 필드
    purchase_validate: bool = False
    purchase_validate_desc: str = ""
    purchase_validate_info: Dict[str, Any] = None
    
    # BreadCrumb 검증 필드
    breadcrumb: List[str] = None
    live_breadcrumb: List[str] = None
    breadcrumb_validate: bool = False
    breadcrumb_validate_desc: str = ""
    
    # FAQ 검증 필드
    faq: Dict[str, Any] = None
    live_faq: Dict[str, Any] = None
    faq_validate: bool = False
    faq_validate_desc: str = ""
    
    # Disclaimer 검증 필드
    disclaimer: Dict[str, Any] = None
    live_disclaimer: Dict[str, Any] = None
    disclaimer_validate: bool = False
    disclaimer_validate_desc: str = ""
    
    # 필터 검증 필드
    filter_validate: bool = False
    filter_validate_desc: str = ""
    filter_info: Dict[str, Any] = None
    filter_validate_info: Dict[str, Any] = None
    
    # 자식 노드
    children: List[PfMenuNode] = None
    
    # 특수 플래그
    is_special: bool = False  # 특수 nv20 여부
    is_filter_testable: bool = False  # 필터 테스트 대상 여부
```

### PfMenuNode
```python
@dataclass
class PfMenuNode:
    name: str = ""
    url: str = ""
    price: str = ""  # 레거시 필드 (기존 호환성 유지)
    cta_an_la: str = ""  # CTA 버튼의 an-la 속성 (구매 가능 여부 판단)
    desc: str = ""
    badge: str = ""
    meta: Dict[str, Any] = None
```

## 🔍 검증 프로세스

### 1. 기본 검증 순서
1. **링크 검증**: nv20 URL 접근 가능성 (HTTP 상태 코드 200 확인)
2. **Navigation Visible 검증**: nv19 메인 네비게이션 요소의 가시성 확인
3. **nv17 검증**: nv17-breadcrumb 요소의 부적절한 노출 방지
4. **헤드라인 검증**: 헤드라인 DOM 존재 및 가시성 확인
5. **결과 수 검증**: 표시된 결과 수 vs 실제 카드 수
6. **정렬 검증**: 정렬 버튼 텍스트와 실제 정렬 옵션 간 일치성
7. **구매 가능성 검증**: 상위 4개 제품의 구매 가능성 (CTA 버튼 an-la 속성 기반)
8. **필터 검증**: 필터 기능성 및 정확성 (현재 탭만)
9. **라이브 검증**: 테스트-라이브 환경 간 콘텐츠 일관성 (BreadCrumb, FAQ, Disclaimer)

### 2. 특수 nv20 처리
- **감지 방법**: 페이지 요소 존재 여부와 다른 메인 탭 이동으로 판단
- **감지 조건 1**: PF 요소가 없는 페이지 (nv19, nv20, filter 요소가 모두 없음)
  - 예시: Compare 페이지, Help Me Choose 페이지 등
- **감지 조건 2**: 다른 메인 탭(nv19)으로 이동하는 경우
  - 예시: 스마트폰 카테고리에서 TV 카테고리로 이동
- **처리 방식**: 링크 검증 후 즉시 종료 (제품 추출, 필터 검증 등 건너뜀)

### 3. 병렬 처리
- **nv20 병렬 처리**: 각 nv20을 새 탭에서 동시 처리
- **BreadCrumb 병렬 검증**: 모든 노드의 BreadCrumb 검증을 동시 실행
- **필터 테스트**: 순차 실행 (페이지 상태 의존성)

## 🐛 자주 발생하는 문제와 해결 방법

### 1. 필터 검증 실패
**문제**: "Filter validation FAILED: No filter items found"
**해결**: 
- 페이지 로딩 대기 시간 증가
- 필터 영역 스크롤 후 재시도
- 필터 컨테이너 선택자 확인

**문제**: "Failed to click checkbox"
**해결**:
- 하이브리드 클릭 방식 확인 (ID 우선, 텍스트 대체)
- 페이지 상태 확인 (필터 확장 여부)

### 2. BreadCrumb 검증 실패
**문제**: "BreadCrumb validation FAILED: Network error"
**해결**:
- 네트워크 연결 상태 확인
- 라이브 URL 변환 로직 확인
- aiohttp 타임아웃 설정 조정

### 3. 페이지 로딩 실패
**문제**: "Page navigation timeout"
**해결**:
- 타임아웃 설정 증가 (현재 60초)
- 네트워크 상태 확인
- 페이지 URL 유효성 검사

### 4. 특수 nv20 처리 오류
**문제**: "Special nv20 not detected"
**해결**:
- `_extract_subtab_info` 함수의 `an-la` 속성 값 확인
- 새로운 특수 nv20 패턴 추가

## 🛠️ 디버깅 도구

### Playwright 디버깅
```python
# 헤드리스 모드 비활성화
browser = await playwright.chromium.launch(headless=False)

# 스크린샷 저장
await page.screenshot(path="debug.png")

# 콘솔 로그 확인
page.on("console", lambda msg: print(f"Console: {msg.text}"))
```

### 선택자 테스트
```python
# 요소 존재 확인
elements = await page.query_selector_all(".pd21-filter__selector-item")
print(f"Found {len(elements)} elements")

# 텍스트 추출
text = await element.inner_text()
print(f"Text: {text}")
```

## 📝 코드 변경 시 체크리스트

### 필수 업데이트 항목
1. **함수명 변경**: 해당 함수의 docstring과 context.md 설명 동시 업데이트
2. **선택자 변경**: CSS 선택자 변경 시 context.md의 "핵심 CSS 선택자" 섹션 업데이트
3. **데이터 구조 변경**: SubCategoryNode, PfMenuNode 변경 시 "데이터 구조" 섹션 업데이트
4. **검증 로직 변경**: 검증 기준 변경 시 "검증 프로세스" 섹션 업데이트
5. **모듈 추가/제거**: pf_modules 패키지 변경 시 "핵심 모듈 구조" 섹션 업데이트

### 자주 변경되는 부분
- **CSS 선택자**: 삼성 웹사이트 업데이트로 인한 선택자 변경
- **특수 nv20 처리**: 새로운 특수 nv20 감지 로직 (`_process_subtab` 함수)
- **필터 분류 로직**: 새로운 필터 타입 추가 시 필터 분류 방식 수정
- **검증 기준**: 비즈니스 요구사항 변경에 따른 검증 로직 수정
- **구매 가능성 판단**: CTA 버튼 an-la 속성 값 기준 변경 가능

## 🔄 성능 최적화

### 병렬 처리
1. **nv20 병렬 처리**: 각 nv20을 새 탭에서 동시 처리
2. **BreadCrumb 병렬 검증**: 모든 노드의 BreadCrumb 검증을 동시 실행
3. **필터 테스트**: 순차 실행 (페이지 상태 의존성)

### 특수 nv20 최적화
1. **조기 종료**: 특수 nv20 감지 시 링크 검증 후 즉시 종료
2. **불필요한 처리 방지**: 특수 nv20에서는 제품 추출, 필터 검증 등 건너뜀
3. **리소스 절약**: 특수 nv20 처리 후 즉시 탭 종료

### Lazy Load 최적화
- **적용 범위**: 제품 카드 로딩 시에만 사용
- **필터 조작 시**: lazy_load 사용하지 않음 (불필요한 오버헤드 방지)
- **스크롤 전략**: `scroll_for_lazyload` 함수로 전체 페이지 스크롤

## 📋 로그 분석

### 로그 형식
```
[YY/MM/DD HH:MM:SS Level LoggerName] Message
```

### 주요 로그 패턴
```bash
# 에러만 필터링
grep "ERROR" logs/app.log

# 특정 함수 실행 추적
grep "_generate_random_combinations" logs/app.log

# 성능 관련 로그
grep "Generated.*combinations" logs/app.log

# 특수 nv20 감지
grep "Special nv20 detected" logs/app.log
```

## 🎯 운영 환경 시나리오

1. **정상 케이스**: 모든 검증이 성공하는 일반적인 페이지
2. **특수 nv20**: 다른 nv19로 이동하거나 nv19/nv20/필터 요소가 모두 없는 페이지
3. **에러 페이지**: HTTP 200이지만 `.ot02-error-page` 요소가 존재하는 페이지
4. **필터 없는 페이지**: 필터가 없는 카테고리 페이지
5. **네트워크 오류**: 라이브 URL 접근 실패 케이스
6. **페이지 로딩 실패**: 타임아웃이나 HTTP 오류가 발생하는 페이지
7. **라이브 환경 불일치**: 테스트-라이브 환경 간 콘텐츠 차이 발생 (BreadCrumb, FAQ, Disclaimer)

## 📊 JSON 출력 구조

### 기본 구조
```json
{
  "extracted_at": "241213-143022",
  "extracted_url": "https://p6-pre-qa3.samsung.com/za/smartphones/all-smartphones/",
  "site_code": "ZA",
  "tree": [
    {
      "node_type": "Main_Category",
      "name": "Mobile",
      "url": "https://p6-pre-qa3.samsung.com/za/smartphones/all-smartphones/",
      "children": [
        {
          "node_type": "Sub_Category",
          "name": "All Smartphones",
          "url": "https://p6-pre-qa3.samsung.com/za/smartphones/all-smartphones/",
          "link_status": 200,
          "link_validate": true,
          "nv17_validate": true,
          "navigation_visible_validate": true,
          "headline_validate": true,
          "result_validate": true,
          "sort_validate": true,
          "purchase_validate": true,
          "breadcrumb_validate": true,
          "faq_validate": true,
          "disclaimer_validate": true,
          "filter_validate": true,
          "children": [...]
        }
      ]
    }
  ]
}
```

### 특수 nv20 구조
```json
{
  "node_type": "Sub_Category",
  "name": "Compare",
  "url": "https://p6-pre-qa3.samsung.com/za/galaxy-book/galaxy-book-series/compare/",
  "link_status": 200,
  "link_validate": true,
  "link_validate_desc": ""
}
```

---

## 📚 상세 구현 정보

### 필터 검증 시스템
- **필터 컨테이너**: `.pd21-filter__selector-list`
- **필터 아이템**: `.pd21-filter__selector-item--checkbox, .pd21-filter__selector-item--menu`
- **체크박스**: `.checkbox-v3`
- **필터 확장**: `.pd21-filter__selector-item-cta` 클릭 후 500ms 대기

### 필터 분류 및 테스트 전략
1. **단일 체크박스 필터**: 직접 체크박스에서 정보 추출
2. **다중 체크박스 필터**: CTA에서 이름 추출, 펼친 후 체크박스 추출
3. **개별 테스트 필터**: an-la 속성에 "size" 포함 시 개별 테스트
4. **랜덤 조합 테스트**: 일반 필터는 랜덤 조합 생성 (최대 2개 필터 조합)

### 필터 검증 방식
- **텍스트 검증**: 필터 적용 후 체크된 필터 텍스트 일치성 확인
- **구매 검증**: 필터 적용 후 상위 4개 제품의 구매 가능성 확인 (CTA 버튼 an-la 속성 기반)

### 라이브 검증
- **BreadCrumb**: 
  - 선택자: `.breadcrumb__path li .breadcrumb__text-desktop`
  - URL 변환: `p6-pre-qa3.samsung.com` → `www.samsung.com`
  - 검증 방식: 테스트-라이브 간 텍스트 일치성 확인
- **FAQ**:
  - 선택자: `.pd25-faq`
  - 검증 방식: DOM 구조를 재귀적으로 비교하여 구조적 동일성 검증
- **Disclaimer**:
  - 선택자: `.pd22-disclaimer`
  - 검증 방식: DOM 구조를 재귀적으로 비교하여 구조적 동일성 검증

### 제품 정보 추출
- **제품 카드**: `div.pd21-product-card__item`
- **제외 대상**: `.pd21-product-card__banner` 클래스 요소, `display: none` 스타일
- **정보 추출**: 이름, URL, 가격, CTA 버튼 an-la 속성, 설명, 배지, 메타 정보

### 정렬 검증
- **정렬 버튼**: `.pd21-sort__opener-name` (현재 표시된 정렬 옵션)
- **정렬 옵션 리스트**: `.js-pfv2-sortby-wrap` (data-default-sort 속성)
- **선택된 옵션**: `.radio-v3__input[checked]` (data-sort-text 속성)
- **검증 방식**: 버튼 텍스트와 선택된 옵션의 일치성 확인

### nv17 검증
- **대상 요소**: `.nv17-breadcrumb`
- **검증 방식**: nv17-breadcrumb 요소가 존재하지 않거나 visible하지 않아야 통과
- **목적**: 부적절한 네비게이션 요소 노출 방지

### Navigation Visible 검증
- **대상 요소**: `.nv19-pd-category-main`, `.nv20-pd-category-sub`
- **검증 방식**: nv19 메인 네비게이션 요소가 visible해야 통과
- **목적**: 필수 네비게이션 요소의 가시성 확인

---

**⚠️ 중요**: 코드를 변경할 때는 반드시 이 context.md도 함께 업데이트해야 합니다. 코드와 문서의 일관성을 유지하는 것이 유지보수의 핵심입니다.