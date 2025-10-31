# 삼성 PD 페이지 검증 도구

## 1. 개요

삼성전자 제품 페이지(PD)의 기능과 성능을 자동으로 검증하는 도구입니다. 제품 페이지의 기본 요소, Dimension 기능, 링크 유효성, 카트 기능 등을 체계적으로 검증하여 결과를 JSON 파일로 저장합니다.

## 2. 환경 설정

### 2.1 파이썬 설치

Python 3.11.9 버전을 설치합니다.
- 다운로드: https://www.python.org/downloads/release/python-3119/

### 2.2 git clone

프로젝트를 클론합니다:
```bash
git clone https://git.swclick.com/Orange/Pd.git
```

### 2.3 가상환경 생성

프로젝트 디렉토리에서 가상환경을 생성합니다:
```bash
python -m venv .venv
```

### 2.4 가상환경 활성화

가상환경을 활성화합니다:
```bash
.venv/Scripts/activate
```

### 2.5 requirements 설치

필요한 의존성 패키지들을 설치합니다:
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

프로그램을 실행합니다:

#### 2.7.1 기본 실행
```bash
python main.py
```
- `main.py`의 `DEFAULT_TARGETS` 배열에 정의된 URL들을 순차적으로 테스트
- 로컬 테스트용

#### 2.7.2 PlateAPI 연동 실행
```bash
python main.py --ssi 1234
```
- `--ssi`: 스냅샷 인덱스 (필수)
- PlateAPI에서 예약된 URL로 PD 테스트 실행
- 운영 환경용

## 3. 테스트 항목

### 3.1 평점 검증
- **검증 요소**: 
  1. **대상**: 평점 (`pdd39-anchor-nav__info-rating`)
  2. **검증 내용**: 평점의 존재 여부
- **검증 방식**:
  1. **평점 영역 확인**:
     - 페이지에서 평점이 표시되는 영역을 찾기
     - 평점 영역이 있으면 내부에 실제 별점이나 평점 숫자가 보이는지 확인
  2. **최종 판정**:
     - 평점이 표시되면 성공, 없으면 실패

### 3.2 카트 전이 검증
- **검증 요소**: 
  1. **대상**: 카트 전이 (`cta.cta--contained.cta--emphasis.cta--2line.add-special-tagging.js-buy-now.tg-add-to-cart[an-la="anchor navi:add to cart"]`)
  2. **검증 내용**: 카트 전이의 성공 여부
- **검증 방식**:
  1. **카트 버튼 확인**:
     - 페이지에서 "장바구니에 담기" 또는 "구매하기" 버튼이 보이는지 확인
     - 버튼이 비활성화되어 있지 않은지 확인
  2. **카트 버튼 클릭**:
     - **Standard PD**: "장바구니에 담기" 버튼 클릭
     - **Simple PD**: "구매하기" 버튼 클릭 → 구매 페이지 로딩 → "장바구니에 담기" 버튼 클릭 → 페이지 하단으로 스크롤 → "장바구니로 이동" 버튼 클릭
  3. **전환 성공 확인**:
     - 카트 페이지로 이동했는지 확인
     - 쿠키 동의 및 국가 선택 모달 처리 완료
     - 카트에 상품이 담겼는지 확인 (가격이 표시되는지 확인)
     - **성공 판정 기준**: 카트 페이지에서 상품 가격이 **visible한 상태**로 표시됨
     - **실패 사유**: 
       - 카트 버튼을 찾을 수 없음
       - 카트 이동은 성공했지만 가격이 보이지 않음
       - 가격 요소를 찾을 수 없음

### 3.3 Broken Link 검증
- **검증 요소**: 
  1. **대상**: 링크 (`hdd02-buying-tool a[href]`)
  2. **검증 내용**: 링크의 유효성
- **검증 방식**:
  1. **구매 도구 영역 확인**:
     - 페이지에서 구매 관련 도구들이 있는 영역을 찾기
     - 해당 영역 내의 모든 링크들을 확인
  2. **유효한 링크만 선별**:
     - 팝업으로 열리는 링크는 제외
     - 보이지 않는 링크는 제외
     - 의미없는 링크(#, javascript 등)는 제외
  3. **링크 접근 테스트**:
     - 선별된 링크들을 하나씩 클릭해서 페이지가 정상적으로 열리는지 확인
     - 모든 링크를 동시에 테스트
  4. **최종 판정**:
     - **정상**: HTTP 상태 코드 200 (페이지가 정상적으로 로드됨)
     - **오류**: HTTP 상태 코드가 200이 아님 (페이지가 로드되지 않거나 오류 페이지가 표시됨)
     - 모든 링크가 정상적으로 작동하면 성공

### 3.4 Dimension 검증
- **검증 요소**: 
  1. **대상**: Dimension (`button.cta.cta--contained.cta--black:not(.cta--disabled)[an-la*="check fit"]`)
  2. **검증 내용**: Dimension의 적합성(fit)과 부적합성(not fit) 기능 검증
- **검증 방식**:
  1. **예시 값 확인**:
     - Dimension 팝업에서 제시된 예시 크기 값들을 확인
     - 예시 값이 없으면 테스트 불가
  2. **적합한 크기 테스트**:
     - 예시 값의 1.1~1.5배 범위에서 랜덤하게 선택된 크기를 입력 (가로, 세로, 깊이)
     - 예: 예시가 1000mm이면 1100~1500mm 사이의 랜덤 값 입력
     - "맞음 확인" 버튼 클릭
     - "맞음" 결과가 표시되는지 확인
  3. **입력 필드 초기화**:
     - 각 입력 필드의 삭제 버튼을 클릭하여 내용 지우기
  4. **부적합한 크기 테스트**:
     - 예시 값의 0.8~1.0배 범위에서 랜덤하게 선택된 크기를 입력 (가로, 세로, 깊이)
     - 예: 예시가 1000mm이면 800~1000mm 사이의 랜덤 값 입력
     - "맞음 확인" 버튼 클릭
     - "맞지 않음" 결과가 표시되는지 확인
  5. **최종 판정**:
     - 두 테스트 모두 올바른 결과가 나오면 성공
     - 팝업 닫기

### 3.5 가격 일치 검증
- **검증 요소**: 
  1. **대상**: 가격 일치 (`pd-buying-price__new-price-currency`)
  2. **검증 내용**: PD 페이지의 가격과 카트 페이지 가격의 일치성
- **검증 방식**:
  1. **PD 페이지에서 가격 확인**:
     - 제품 페이지에서 표시된 가격을 확인
     - 가격이 표시되지 않으면 재시도
  2. **카트로 이동 및 가격 확인**:
     - **Standard PD**: "장바구니에 담기" 버튼 클릭
     - **Simple PD**: "구매하기" 버튼 클릭 → 구매 페이지 로딩 → "장바구니에 담기" 버튼 클릭 → 페이지 하단으로 스크롤 → "장바구니로 이동" 버튼 클릭
     - 카트 페이지에서 상품 가격이 표시되는지 확인
     - 가격이 보이지 않으면 페이지를 스크롤하여 확인
  3. **가격 일치 확인**:
     - PD 페이지의 가격과 카트 페이지의 가격이 같은지 비교
     - 공백이나 쉼표 등은 무시하고 숫자 부분만 비교
     - 가격이 일치하면 성공, 다르면 실패

## 4. 테스트 결과

### 4.1 JSON 결과 파일
테스트 실행 후 `result/` 폴더에 JSON 파일이 생성됩니다.

#### 4.1.1 파일명 형식
```
{SITECODE}_{YYYYMMDD}_{HHMMSS}.json
```
- 예: `UK_20251010_153651.json`, `TEST_20251010_094302.json`

#### 4.1.2 JSON 구조
```json
{
  "url": "테스트한 URL",
  "pd_type": "Standard|Simple|Unknown",
  "rating_validate": true/false,
  "rating_validate_desc": "평점 검증 결과 설명",
  "link_validate": true/false,
  "link_validate_desc": "링크 검증 결과 설명",
  "transition_validate": true/false,
  "transition_validate_desc": "카트 전이 검증 결과 설명",
  "price_validate": true/false,
  "price_validate_desc": "가격 일치 검증 결과 설명",
  "is_dimension": true/false,
  "dimension_validate": true/false,
  "dimension_validate_desc": "Dimension 검증 결과 설명"
}
```

#### 4.1.3 결과 해석
- **`true`**: 해당 검증 성공
- **`false`**: 해당 검증 실패
- **`*_validate_desc`**: 실패시 상세 원인, 성공시 빈 문자열 또는 상세 정보(Dimension)
- **`is_dimension`**: Dimension 영역 존재 여부 (있을 때만 dimension_validate 필드 포함)

### 4.2 로그 파일
테스트 실행 중 `logs/` 폴더에 상세 로그가 기록됩니다.
- 파일명: `{MMDD}-{HHMMSS}.log`
- 실행 과정의 모든 단계별 로그 포함
- 오류 발생시 디버깅에 활용