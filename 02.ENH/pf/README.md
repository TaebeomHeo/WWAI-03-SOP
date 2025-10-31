# 삼성 PF 페이지 검증 도구

## 1. 개요

이 프로그램은 **삼성전자 PF 페이지의 구조와 기능을 자동으로 분석하고 검증**하는 도구입니다.


## 2. 환경 설정

### 2.1 파이썬 설치
Python 3.11.9 버전을 설치합니다.

**다운로드 URL**: https://www.python.org/downloads/release/python-3119/

**설치 방법**:
- Windows용 Python 3.11.9 설치 파일 다운로드
- 설치 시 "Add Python to PATH" 옵션 체크
- 설치 완료 후 명령 프롬프트에서 `python --version` 명령으로 버전 확인

### 2.2 git clone
프로젝트 저장소를 클론합니다.

```bash
git clone https://git.swclick.com/Orange/Pf.git
cd Pf
```

### 2.3 가상환경 생성
프로젝트 루트 디렉토리에서 가상환경을 생성합니다.

```bash
python -m venv .venv
```

### 2.4 가상환경 활성화
Windows 환경에서 가상환경을 활성화합니다.

```bash
.venv\Scripts\activate
```

**활성화 확인**: 명령 프롬프트 앞에 `(.venv)`가 표시되면 정상적으로 활성화됨

### 2.5 requirements 설치
필요한 Python 패키지들을 설치합니다.

```bash
pip install -r requirements.txt
```

### 2.6 WDS 로그인 설정
프로그램 실행 전 `env.user` 파일에서 다음 3가지 WDS 로그인 관련 설정을 조정할 수 있습니다:

1. **WDS 로그인 사용 여부** (`WDS_LOGIN`)
   - `true`: WDS SSO 로그인 사용 (권장)
   - `false`: 로그인 없는 URL 테스트시 이용(라이브 등)

2. **WDS 로그인 정보** (`WDS_USERNAME`, `WDS_PASSWORD`)
   - 삼성 내부 WDS 계정 정보 설정
   - p6 시스템 접근에 필수

3. **WDS 우회계정 모드** (`WDS_EMPLOYEE_MODE`)
   - `true`: Samsung Employee 모드 (팝업 사용)
   - `false`: Business Partner 모드 (팝업 없음)

### 2.7 실행 명령
프로그램을 실행합니다.

#### 2.7.1 개발 모드 (기본)
내장된 DEFAULT_TARGETS 배열의 URL들을 순차적으로 처리합니다.

```bash
python main.py
```

#### 2.7.2 실 테스트 모드
Zest API에서 URL을 예약받아 처리합니다.

```bash
python main.py --ssi <SSI_ID>
```

**파라미터 설명**:
- `--ssi <SSI_ID>`: 스냅샷 인덱스 ID (Zest API에서 URL 예약 시 사용)
- 예시: `python main.py --ssi 1234`

## 3. 테스트 항목

### 3.1 Broken Link 검증
- **검증 요소**: 
  1. **대상**: nv19 메인 카테고리 URL, nv20 서브 카테고리 URL (`.ot02-error-page`)
  2. **검증 내용**: HTTP 응답 상태 코드 200번대 여부, 에러 페이지 감지
- **검증 방식**:
  1. **nv19 메인 카테고리 URL 접근**:
     - 메인 탭 클릭 시 HTTP 응답 코드 확인하여 200번대 응답인지 검증
  2. **nv20 서브 카테고리 URL 접근**:
     - 새 탭에서 서브 카테고리 접근 시 HTTP 응답 코드 확인하여 200번대 응답인지 검증
  3. **현재 탭 URL 상태**:
     - 현재 페이지는 기본적으로 200으로 처리하여 정상 상태로 간주
  4. **에러 페이지 감지**:
     - HTTP 200이어도 .ot02-error-page 요소 존재 시 에러 페이지로 판단하여 검증 실패 처리
  5. **최종 판정**:
     - **성공**: 모든 URL이 200번대 응답이고 에러 페이지가 없음
     - **실패**: 하나라도 실패

### 3.2 Navigation Visible 검증
- **검증 요소**: 
  1. **대상**: nv19 메인 네비게이션 요소, nv20 서브 네비게이션 요소 (`.nv19-pd-category-main`, `.nv20-pd-category-sub`)
  2. **검증 내용**: nv19 요소의 존재 여부 및 가시성 (nv20은 서브 네비게이션이 없는 단일 페이지, PF 요소가 없는 특수 nv20, 숨겨진 탭이 있는 경우 선택적)
- **검증 방식**: 
  1. **nv19 요소 존재 확인**:
     - .nv19-pd-category-main 클래스를 가진 요소가 DOM에 존재하는지 확인
  2. **nv20 요소 존재 확인**:
     - .nv20-pd-category-sub 클래스를 가진 요소가 DOM에 존재하는지 확인 (서브 네비게이션이 없는 단일 페이지, PF 요소가 없는 특수 nv20, 숨겨진 탭이 있는 경우 제외)
  3. **nv19 가시성 검증**:
     - nv19 요소의 is_visible() 메서드를 호출하여 실제로 사용자에게 보이는지 확인
  4. **검증 조건 확인**:
     - 링크 상태가 200이고 에러 페이지가 아닌 경우에만 검증 수행
  5. **최종 판정**:
     - **성공**: nv19 요소가 존재하고 가시적
     - **실패**: 그렇지 않음

### 3.3 nv17 검증
- **검증 요소**: 
  1. **대상**: nv17-breadcrumb 요소 (`.nv17-breadcrumb`)
  2. **검증 내용**: 요소 부적절한 노출 방지 (존재하지 않거나 숨겨져야 함)
- **검증 방식**: 
  1. **요소 존재 확인**:
     - .nv17-breadcrumb 클래스를 가진 모든 요소를 찾아 개수 확인
  2. **가시성 상태 검증**:
     - 존재하는 각 요소에 대해 is_visible() 메서드로 실제 표시 여부 확인
  3. **검증 결과 판단**:
     - 요소가 존재하지 않거나 모든 요소가 visible하지 않으면 검증 통과, visible한 요소가 있으면 검증 실패
  4. **최종 판정**:
     - **성공**: nv17 요소가 존재하지 않거나 모든 요소가 숨겨져 있음
     - **실패**: visible한 요소가 있음

### 3.4 헤드라인 검증
- **검증 요소**: 
  1. **대상**: 헤드라인 요소 (`.co77-text-block-home__headline`)
  2. **검증 내용**: DOM 존재 여부 및 가시성
- **검증 방식**:
  1. **DOM 요소 존재 확인**:
     - .co77-text-block-home__headline 클래스를 가진 요소가 DOM에 존재하는지 확인
  2. **가시성 상태 검증**:
     - 요소가 존재하는 경우 is_visible() 메서드로 실제로 사용자에게 보이는지 확인
  3. **텍스트 추출**:
     - visible한 경우 inner_text() 메서드로 헤드라인 텍스트 추출
  4. **검증 결과 판단**:
     - DOM에 존재하고 visible하며 텍스트가 있으면 검증 통과, 그렇지 않으면 검증 실패
  5. **최종 판정**:
     - **성공**: 헤드라인 요소가 존재하고 가시적이며 텍스트가 있음
     - **실패**: 그렇지 않음

### 3.5 결과 수 검증
- **검증 요소**: 
  1. **대상**: 결과 수 표시 텍스트, 제품 카드 (`.pd21-top__result-count`, `.pd21-product-card__item`, `.pd21-product-card__banner`, `.pd21-product-finder__no-result`)
  2. **검증 내용**: 실제 카드 수가 표시된 결과 수보다 작거나 같은지 확인
- **검증 방식**:
  1. **no-result 상태 확인**:
     - .pd21-product-finder__no-result 요소가 있으면 제품이 없는 정상 상태로 처리
  2. **결과 수 텍스트 추출**:
     - .pd21-top__result-count 요소에서 텍스트를 추출하고 정규식으로 숫자만 파싱
  3. **제품 카드 개수 계산**:
     - .pd21-product-card__item 클래스를 가진 모든 요소를 찾아 개수 계산
  4. **배너 카드 제외**:
     - .pd21-product-card__banner 클래스를 가진 요소는 제품 카드에서 제외
  5. **조건 검증**:
     - actual_card_count <= displayed_result_count 조건을 확인하여 검증 결과 판단
  6. **최종 판정**:
     - **성공**: 실제 카드 수가 표시된 결과 수보다 작거나 같음
     - **실패**: 그렇지 않음

### 3.6 정렬 검증
- **검증 요소**: 
  1. **대상**: 정렬 버튼 텍스트, 정렬 옵션 리스트, 선택된 옵션 (`.pd21-sort__opener-name`, `.pd21-sort__opener`, `.js-pfv2-sortby-wrap`, `.pd21-sort__item`)
  2. **검증 내용**: 정렬 버튼 텍스트, 기본 정렬값, 선택된 옵션 텍스트 간 일치성
- **검증 방식**:
  1. **정렬 버튼 텍스트 추출**:
     - .pd21-sort__opener-name 요소에서 현재 표시된 정렬 옵션 텍스트 추출
  2. **정렬 드롭다운 열기**:
     - .pd21-sort__opener 버튼을 클릭하여 정렬 옵션 드롭다운 메뉴 열기
  3. **기본 정렬값 확인**:
     - .js-pfv2-sortby-wrap 요소의 data-default-sort 속성값으로 기본 정렬값 확인
  4. **선택된 옵션 확인**:
     - 선택된 라디오 버튼의 data-sort-text 속성값으로 현재 선택된 정렬 옵션 텍스트 확인
  5. **일치성 검증**:
     - 세 값(opener_text, default_sort, selected_text)이 모두 일치하는지 확인하여 검증 결과 판단
  6. **최종 판정**:
     - **성공**: 세 값이 모두 일치
     - **실패**: 하나라도 다름

### 3.7 구매 가능성 검증
- **검증 요소**: 
  1. **대상**: 제품 CTA 버튼 an-la 속성, 제품 카드 (`.pd21-product-card__item`, `an-la` 속성, `.pd21-product-finder__no-result`)
  2. **검증 내용**: 모든 제품의 CTA an-la 속성이 "pf product card:buy"인지 확인
- **검증 방식**:
  1. **no-result 상태 확인**:
     - .pd21-product-finder__no-result 요소가 있으면 제품이 없는 정상 상태로 처리
  2. **제품 리스트 검사**:
     - 전달받은 모든 제품을 순차적으로 검사 (상위 4개 제한 없음)
  3. **CTA 속성 확인**:
     - 각 제품의 CTA 버튼 an-la 속성 값을 확인
  4. **구매 가능성 판단**:
     - an-la="pf product card:buy"인 경우 구매 가능으로 판단
  5. **통합 검증**:
     - 모든 제품이 구매 가능해야 검증 통과, 1개라도 구매 불가능이면 검증 실패
  6. **최종 판정**:
     - **성공**: 모든 제품이 구매 가능
     - **실패**: 1개라도 구매 불가능

### 3.8 필터 기능 검증
- **검증 요소**: 
  1. **대상**: 필터 컨테이너, 필터 옵션, 체크박스, 제품 카드 (`.pd21-filter`, `.pd21-filter__selector-item-cta`, `.pd21-filter--hide`, `.pd21-product-card__item`)
  2. **검증 내용**: 필터 적용/해제 기능 정상 동작, 체크된 필터 텍스트 일치성, 구매 가능성
- **검증 방식**:
  1. **필터 구조 추출**:
     - .pd21-filter 컨테이너에서 모든 필터 정보를 추출하고 단일/다중 체크박스 필터로 분류
  2. **테스트 조합 생성**:
     - 개별 테스트 조합 생성: 두 번째 필터(index=1)의 모든 체크박스를 개별적으로 테스트할 조합으로 생성
     - 랜덤 조합 테스트 생성: 나머지 필터들에서 최대 3개 조합을 랜덤으로 생성하여 테스트할 조합으로 생성
  3. **필터 적용**:
     - 각 조합에 대해 체크박스를 선택하고 필터 적용
  4. **검증 수행**:
     - 텍스트 일치성 확인: 필터 적용 후 체크된 필터 텍스트가 실제 적용된 필터와 일치하는지 확인
     - 구매 가능성 확인: 필터 적용 후 현재 페이지의 모든 제품이 구매 가능한지 확인
  5. **필터 해제**:
     - 테스트 완료 후 모든 필터를 해제하여 원래 상태로 복구
  6. **최종 판정**:
     - **성공**: 모든 필터 조합에서 텍스트 일치성과 구매 가능성이 확인됨
     - **실패**: 하나라도 실패

### 3.9 BreadCrumb 검증
- **검증 요소**: 
  1. **대상**: BreadCrumb 네비게이션 경로 (`.breadcrumb__path`, `.breadcrumb__text-desktop`)
  2. **검증 내용**: 테스트-라이브 환경 간 BreadCrumb 경로 일치성
- **검증 방식**:
  1. **테스트 페이지 BreadCrumb 추출**:
     - 테스트 페이지에서 .breadcrumb__path .breadcrumb__text-desktop 요소들을 찾아 텍스트 추출
  2. **라이브 페이지 BreadCrumb 추출**:
     - 테스트 URL을 라이브 URL로 변환하여 동일한 방식으로 BreadCrumb 데이터 추출
  3. **경로 비교**:
     - 경로 길이 비교: 테스트와 라이브 페이지의 BreadCrumb 경로 길이가 동일한지 확인
     - 경로 순서 비교: 각 BreadCrumb 요소를 순서대로 비교하여 텍스트 일치성 확인
  4. **최종 판정**:
     - **성공**: 테스트와 라이브의 BreadCrumb 경로가 모두 일치
     - **실패**: 차이점이 있음

### 3.10 FAQ 검증
- **검증 요소**: 
  1. **대상**: FAQ 섹션 DOM 구조 (`.su12-accordion-faqs`)
  2. **검증 내용**: 테스트-라이브 환경 간 FAQ DOM 구조 일치성
- **검증 방식**:
  1. **테스트 페이지 FAQ 추출**:
     - 테스트 페이지에서 .su12-accordion-faqs 요소의 DOM 구조를 추출하여 계층적 구조로 변환
  2. **라이브 페이지 FAQ 추출**:
     - 테스트 URL을 라이브 URL로 변환하여 동일한 방식으로 FAQ DOM 구조 추출
  3. **DOM 구조 비교**:
     - FAQ 섹션의 DOM 구조를 재귀적으로 비교하여 HTML 태그, 속성, 텍스트 일치성 확인
     - 빈 상태 처리: 테스트와 라이브 모두 FAQ가 없는 경우 정상으로 처리
  4. **최종 판정**:
     - **성공**: 테스트와 라이브의 FAQ DOM 구조가 동일
     - **실패**: 차이점이 있음

### 3.11 Disclaimer 검증
- **검증 요소**: 
  1. **대상**: Disclaimer 섹션 DOM 구조 (`#disclaimer .text-editor__column.description-text-size--small`)
  2. **검증 내용**: 테스트-라이브 환경 간 Disclaimer DOM 구조 일치성
- **검증 방식**:
  1. **테스트 페이지 Disclaimer 추출**:
     - 테스트 페이지에서 #disclaimer .text-editor__column.description-text-size--small 요소의 DOM 구조를 추출하여 계층적 구조로 변환
  2. **라이브 페이지 Disclaimer 추출**:
     - 테스트 URL을 라이브 URL로 변환하여 동일한 방식으로 Disclaimer DOM 구조 추출
  3. **DOM 구조 비교**:
     - Disclaimer 섹션의 DOM 구조를 재귀적으로 비교하여 HTML 태그, 속성, 텍스트 일치성 확인
     - 빈 상태 처리: 테스트와 라이브 모두 Disclaimer가 없는 경우 정상으로 처리
  4. **최종 판정**:
     - **성공**: 테스트와 라이브의 Disclaimer DOM 구조가 동일
     - **실패**: 차이점이 있음

## 4. 테스트 결과

### 4.1 JSON 결과 파일
프로그램 실행 후 `crawlstore/` 디렉토리에 JSON 결과 파일이 생성됩니다.

#### 4.1.1 파일명 형식
```
{사이트코드}_pf_{날짜시간}_{도메인}_{카테고리}.json
```

**예시**:
- `BR_pf_251020-085501_p6-pre-qa3.samsung.com_br_monitors_all-monitors_.json`
- `ZA_pf_250929-094122_p6-pre-qa3.samsung.com_za_smartphones_all-smartphones_.json`

#### 4.1.2 JSON 구조
```json
{
  "extracted_at": "241213-143022",
  "extracted_url": "https://p6-pre-qa3.samsung.com/br/monitors/all-monitors/",
  "site_code": "BR",
  "tree": [
    {
      "node_type": "Main_Category",
      "name": "Monitors",
      "url": "https://p6-pre-qa3.samsung.com/br/monitors/all-monitors/",
      "children": [
        {
          "node_type": "Sub_Category",
          "name": "All Monitors",
          "url": "https://p6-pre-qa3.samsung.com/br/monitors/all-monitors/",
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

#### 4.1.3 주요 필드 설명
- **extracted_at**: 추출 시간 (YYMMDD-HHMMSS 형식)
- **extracted_url**: 분석 대상 URL
- **site_code**: 사이트 코드 (BR, ZA 등)
- **tree**: PF 구조 트리
  - **node_type**: 노드 타입 (Main_Category, Sub_Category)
  - **name**: 카테고리명
  - **url**: 카테고리 URL
  - **link_status**: HTTP 응답 상태 코드
  - **{검증항목}_validate**: 각 검증 결과 (true/false)
  - **{검증항목}_validate_desc**: 검증 실패 시 상세 설명
  - **children**: 하위 노드들 (제품 정보 포함)