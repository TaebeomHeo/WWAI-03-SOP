# 삼성 GNB/CGD 메뉴 검증 도구

## 1. 개요

삼성전자 글로벌 웹사이트의 메뉴(GNB) 구조와 엑셀(CGD) 메뉴 구조를 자동으로 검증하는 도구입니다. 웹사이트에 표시되는 메뉴가 회사 내부 문서와 일치하는지, 메뉴 링크가 정상적으로 작동하는지 체계적으로 검증하여 결과를 JSON 파일로 저장합니다.

## 2. 환경 설정

### 2.1 파이썬 설치
Python 3.11.9 버전을 설치합니다.
- 다운로드 URL: https://www.python.org/downloads/release/python-3119/
- Windows용 설치 파일을 다운로드하여 설치합니다.

### 2.2 git clone
프로젝트를 클론합니다.
```bash
git clone https://git.swclick.com/Orange/Pf.git
```

### 2.3 가상환경 생성
프로젝트 디렉토리에서 가상환경을 생성합니다.
```bash
python -m venv .venv
```

### 2.4 가상환경 활성화
Windows 환경에서 가상환경을 활성화합니다.
```bash
.venv/Scripts/activate
```

### 2.5 requirements 설치
필요한 의존성 패키지를 설치합니다.
```bash
pip install -r requirements.txt
```

### 2.6 CGD 데이터 변환
**CGD 데이터 준비:**
1. **엑셀 파일 배치**: CGD 엑셀 파일들을 `cgddocs/` 폴더에 넣어야 합니다
2. **데이터 변환 실행**: 다음 명령어로 엑셀 파일을 JSON으로 변환합니다
   ```bash
   python cgd.py
   ```

### 2.7 실행 명령
프로그램을 실행합니다.
```bash
python main.py
```

## 3. 테스트 항목

### 2.1 메뉴 구조 일치 검증
- **검증 요소**: 
  1. **대상**: GNB 메뉴와 CGD 엑셀 데이터의 메뉴명, URL
     - GNB 메뉴 요소: L0 (`.nv00-gnb-v4__l0-menu`), L1 (`.nv00-gnb-v4__l1-menu`), Featured (`.nv00-gnb-v4__l1-featured`)
     - CGD 엑셀 데이터: Menu label, Linked URL, Analytics, SEO 등
  2. **검증 내용**: 웹사이트에 표시되는 메뉴가 CGD 문서와 정확히 일치하는지 확인
- **검증 방식**:
  1. **CGD 데이터 추출**: 엑셀 파일에서 메뉴 데이터를 추출하여 CgdMenuNode 트리 구조로 변환
  2. **GNB 메뉴 구조 추출**: 
     - 웹페이지 접속: Playwright를 통해 대상 URL에 접속하고 AEM 로그인 자동 처리 (`#login-box` 셀렉터로 로그인 페이지 확인)
     - 페이지 로딩 완료 대기: DOMContentLoaded 이벤트까지 대기하고 지연 로딩 컨텐츠를 위해 스크롤 수행
     - HTML 파싱: BeautifulSoup으로 HTML을 파싱하여 메뉴 요소를 찾고 계층 구조 분석
     - 트리 구조 생성: GnbMenuNode 객체를 생성하여 계층적 트리 구조로 변환
  3. **메뉴 구조 비교**: 
     - 트리 순회: GNB와 CGD 트리를 재귀적으로 순회하며 각 노드 쌍을 비교
     - 메뉴명 비교: `compare_name` 함수를 사용하여 메뉴명의 일치 여부를 검증 (공백, 대소문자 무시)
     - URL 비교: `compare_url_without_domain` 함수를 사용하여 URL의 일치 여부를 검증 (도메인 제외)
  4. **최종 판정**:
     - Note에 판정 결과 표시
     - name이 일치하면 True, 일치하지 않으면 False
     - url이 일치하면 True, 일치하지 않으면 False

### 2.2 메뉴 링크 유효성 검증
- **검증 요소**: 
  1. **대상**: 추출된 모든 메뉴 링크 URL
     - 페이지 로딩 확인: `body` 셀렉터로 페이지 로딩 완료 대기
     - 에러 페이지 감지: `.ot02-error-page` 클래스 존재 여부 확인
  2. **검증 내용**: 메뉴 링크가 실제로 접근 가능하고 정상 페이지를 반환하는지 확인
- **검증 방식**:
  1. **링크 수집**: GNB 트리에서 모든 URL을 수집하여 검증 대상 리스트 생성
  2. **링크 접근 테스트**: Playwright를 사용하여 각 링크에 HTTP 요청을 전송
  3. **응답 상태 확인**: HTTP 응답 상태 코드를 확인하여 200번대 응답인지 검증
  4. **에러 페이지 감지**: HTTP 200이어도 `.ot02-error-page` 요소가 존재하면 에러 페이지로 판단
  5. **최종 판정**:
     - **성공**: HTTP 상태 코드 200이고 에러 페이지가 아님
     - **실패**: HTTP 상태 코드가 200이 아니거나 에러 페이지가 표시됨
     - link_validate: 링크가 정상이면 True, 오류면 False

## 4. 테스트 결과

### 4.1 JSON 결과 파일
검증 완료 후 결과 데이터가 JSON 파일로 저장됩니다.

#### 4.1.1 저장 위치
- **디렉토리**: `crawlstore/` 폴더
- **파일명 형식**: `{날짜시간}_{도메인}_{사이트코드}_.json`
- **예시**: `250918-135337_www.samsung.com_uk_.json`

#### 4.1.2 JSON 구조
```json
{
  "timestamp": "2025-01-09 13:53:37",
  "url": "https://www.samsung.com/uk/",
  "siteCode": "UK",
  "gnb_structure": [
    {
      "name": "Mobile",
      "url": "/mobile/",
      "children": [
        {
          "name": "Galaxy",
          "url": "/mobile/galaxy/",
          "children": [
            {
              "name": "Galaxy S24",
              "url": "/mobile/galaxy/galaxy-s24/",
              "name_verify": true,
              "url_verify": true,
              "link_validate": true,
              "link_status": 200,
              "link_validate_desc": "Link validation passed"
            }
          ]
        }
      ]
    }
  ],
  "verification_summary": {
    "total_nodes": 15,
    "name_matches": 14,
    "url_matches": 13,
    "valid_links": 12,
    "failed_links": 1
  }
}
```

#### 4.1.3 JSON 필드 설명
- **timestamp**: 검증 실행 시간
- **url**: 검증 대상 URL
- **siteCode**: 사이트 코드
- **gnb_structure**: GNB 메뉴 구조 트리
  - **name**: 메뉴명
  - **url**: 메뉴 URL
  - **children**: 하위 메뉴 목록
  - **name_verify**: 메뉴명 일치 여부 (true/false)
  - **url_verify**: URL 일치 여부 (true/false)
  - **link_validate**: 링크 유효성 검증 결과 (true/false)
  - **link_status**: HTTP 응답 상태 코드
  - **link_validate_desc**: 링크 검증 상세 설명
- **verification_summary**: 검증 결과 요약 통계