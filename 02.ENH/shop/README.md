# 삼성 SHOP 네비게이션 구조 자동 추출 도구

## 1. 개요

삼성전자 SHOP 웹사이트의 네비게이션 구조를 자동으로 추출하고 분석하는 도구입니다. Playwright 기반 브라우저 자동화를 통해 실제 페이지 이동, 로그인, 스크롤, 메뉴 탐색, 링크 유효성 검사까지 수행하여 결과를 JSON 파일로 저장합니다.


## 2. 환경 설정

### 2.1 파이썬 설치
- Python 3.11.9 설치가 필요합니다.
- 다운로드 URL: https://www.python.org/downloads/release/python-3119/
- Windows 환경에서 설치 시 "Add Python to PATH" 옵션을 체크해주세요.

### 2.2 git clone
```bash
git clone https://git.swclick.com/Orange/Pf.git
```

### 2.3 가상환경 생성
```bash
python -m venv .venv
```

### 2.4 가상환경 활성화
```bash
.venv/Scripts/activate
```

### 2.5 requirements 설치
```bash
pip install -r requirements.txt
```

### 2.6 실행 명령
```bash
python main.py
```

## 3. 테스트 항목

### 3.1 SHOP 메뉴 구조 추출
- **검증 요소**: 
  1. **대상**: SHOP 메뉴 (`div.tab.pd22-shop-product-category__primary-tab > ul > li > button`)
  2. **검증 내용**: L0/L1/Product 계층 구조 추출
- **검증 방식**:
  1. **메인 메뉴(L0) 추출**:
     - 페이지에서 메인 메뉴 버튼들을 찾기
     - 각 메인 메뉴 버튼을 순서대로 클릭
     - 클릭 후 1초 대기하여 메뉴가 완전히 로드되도록 함
  2. **서브 메뉴(L1) 추출**:
     - 메인 메뉴 클릭 후 서브 메뉴 패널을 찾기
     - 서브 메뉴 패널에서 모든 서브 메뉴 버튼을 찾아 순서대로 클릭
     - 각 서브 메뉴 클릭 후 2초 대기하여 상품 목록이 로드되도록 함
  3. **상품(Product) 추출**:
     - 서브 메뉴 클릭 후 해당 메뉴의 상품 목록을 찾기
     - 각 상품의 이름과 링크를 추출
  4. **결과 저장**:
     - 계층적 트리 구조로 변환하여 저장
     - 메뉴명, URL, 메타정보 등을 포함한 완전한 구조 추출
  5. **JSON 파일 저장**:
     - `crawlstore` 폴더에 결과 저장
     - 파일명: `{sitecode}_shop_{yymmdd-hhmmss}_{url}.json`
     - **데이터 구조**:
       - 추출 시간, URL, siteCode 정보를 문자열 필드로 포함
       - 각 노드의 필드 순서는 name_verify, url_verify, link_status, link_validate, link_validate_desc로 정렬
     - **최종 저장**:
       - 완전한 트리 구조를 JSON 형태로 저장
       - 메타정보와 검증 결과를 모두 포함한 완전한 분석 결과 제공

### 3.2 링크 유효성 검사
- **검증 요소**: 
  1. **대상**: 모든 메뉴 링크
  2. **검증 내용**: 링크의 접근성 및 정상 응답 여부
- **검증 방식**:
  1. **링크 확인**:
     - 메뉴 노드에 URL이 있는지 확인
     - URL이 없는 경우 "No URL" 상태로 표시
     - L0/L1 노드의 경우 URL이 없어도 특별 처리
  2. **페이지 이동**:
     - URL이 있는 경우 새 탭에서 해당 페이지로 이동 시도
     - 페이지 이동 후 body 요소가 로드될 때까지 최대 20초 대기
     - 최대 5번까지 재시도
  3. **상태 확인**:
     - 페이지 이동이 성공한 경우 HTTP 상태 코드 확인 (200이면 성공)
     - 리다이렉트가 발생한 경우 최종 URL 기록
     - 페이지 이동이 실패한 경우 HTTP 상태 코드 확인하여 "404 Not Found" 등의 상태 표시
  4. **최종 판정**:
     - **성공**: HTTP 상태 코드 200 (페이지가 정상적으로 로드됨)
     - **실패**: HTTP 상태 코드가 200이 아님 (페이지가 로드되지 않거나 오류 페이지가 표시됨)

## 4. 테스트 결과

### 4.1 JSON 결과 데이터
추출된 SHOP 메뉴 구조는 JSON 파일로 저장되며, 다음과 같은 구조를 가집니다.

#### 4.1.1 파일 저장 위치
- **저장 폴더**: `crawlstore/`
- **파일명 형식**: `{sitecode}_shop_{yymmdd-hhmmss}_{url}.json`

#### 4.1.2 JSON 구조
```json
{
  "extracted_at": "250610-085613",
  "extracted_url": "https://p6-pre-qa3.samsung.com/au/new-shop/?co78price",
  "site_code": "AU",
  "tree": [
    {
      "node_type": "L0",
      "name": "TV",
      "url": "",
      "name_verify": false,
      "url_verify": false,
      "link_status": -1,
      "link_validate": false,
      "link_validate_desc": "L0 has no link by design",
      "desc": "",
      "meta": {...},
      "children": [...]
    }
  ]
}
```

#### 4.1.3 필드 설명
- **extracted_at**: 추출 시간 (YYMMDD-HHMMSS 형식)
- **extracted_url**: 추출 대상 URL
- **site_code**: 사이트 코드 (AU, HK, NZ 등)
- **tree**: 메뉴 트리 구조 배열
- **node_type**: 노드 타입 (L0, L1, Product)
- **name**: 메뉴명
- **url**: 메뉴 URL
- **name_verify**: 메뉴명 검증 여부
- **url_verify**: URL 검증 여부
- **link_status**: HTTP 상태 코드
- **link_validate**: 링크 유효성
- **link_validate_desc**: 링크 검증 설명
- **desc**: 메뉴 설명
- **meta**: 버튼 요소의 메타정보
- **children**: 하위 메뉴 배열
