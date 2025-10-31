# SmartThings 자동화 테스트 프로세스

## 개요
이 프로젝트는 Samsung SmartThings 웹사이트의 자동화 테스트를 위한 Python 스크립트입니다. Playwright를 사용하여 브라우저 자동화를 수행하고, 다양한 API 응답을 모니터링하며, HTML 데이터를 추출하여 Excel 파일로 결과를 저장합니다.

## 프로젝트 구조
```
git_samsung/
├── smartThings_main.py          # 메인 실행 파일
├── smartThings_module/          # 모듈 폴더
│   ├── compare_result.py        # 결과 비교 처리
│   ├── html_result.py           # HTML 데이터 추출
│   ├── law_agree_result.py      # 법적 동의 요건 처리
│   ├── product_result.py        # 제품 결과 처리
│   ├── response_handler.py      # API 응답 처리
│   └── rowdata_excel.py         # Excel 데이터 처리
└── ReadMe/                      # 결과 문서들
    ├── README_compare_result.md
    ├── README_html_result.md
    ├── README_law_agree_result.md
    ├── README_product_result.md
    ├── README_response_handler.md
    └── README_rowdata_excel.md
```

## 주요 기능

### 1. 데이터 수집 대상 컬럼
- **계정 정보**: Account
- **메인 정보**: main_headline, main_description, main_description1, main_description2
- **스토리 정보**: storyIdRank1~3, 각 스토리의 제목/설명/추천제품
- **라이프스타일**: lifeStyleIdRank1~2, Scenariokeyword1~2
- **기타**: country_code, Device1~2, banner_text, banner_link_text, banner_hyperlink

### 2. 대상 국가
- DE (독일), FR (프랑스), ES (스페인), IT (이탈리아)

### 3. 기본 배너 설정
- **배너 텍스트**: "General recommendations are shown by default. Opt in to required settings on the Privacy tab of your Samsung Account for a more personalized experience."
- **링크 텍스트**: "Go to Samung Account"
- **하이퍼링크**: "http://account.samsung.com/"

## 상세 프로세스

### 1. 초기 설정 및 데이터 로드
```python
# Excel 파일 경로 설정
samsung_project_path = r'C:\Users\WW\Desktop\삼성 프로젝트 관련 파일'
format_data_path = samsung_project_path + r'\Test data matrix (Umbrella merge).xlsx'
contents_data_path = samsung_project_path + r'\contents'
umbrella_file_path = samsung_project_path + r'\umbrella'
consent_file_path = samsung_project_path + r'\국가별 마케팅 동의 요건.xlsx'
compare_item_path = samsung_project_path + r'\계정별비교항목.xlsx'
```

### 2. Excel 데이터 처리
- `RowDataExcel` 클래스를 사용하여 테스트 데이터 로드
- 6행까지의 데이터 처리
- 국가별 데이터 복사 및 콘텐츠 매핑
- 우산 파일을 통한 메인 데이터 매핑

### 3. 브라우저 자동화 프로세스

#### 3.1 브라우저 설정
- Chrome 브라우저 사용 (headless=False)
- 시크릿 모드, 최대화된 창으로 시작
- 사용자 에이전트 설정: "D2CEST-AUTO-70a4cf16"

#### 3.2 API 엔드포인트 모니터링
- **메인 스토리 API**: `/aemapi/v6/mysamsung/{country}/scv/user/recommend/st/story`
- **제품 메타데이터 API**: `/aemapi/v6/mysamsung/{country}/scv/product/meta`
- **새 제품 API**: `/aemapi/v6/mysamsung/{country}/scv/newproducts`
- **동의 요건 API**: `https://account.samsung.com/api/v1/consent/required`

#### 3.3 로그인 프로세스
1. SmartThings 페이지 접속
2. 응답 상태 확인 (200: 성공, 400: 로그인 실패, 500: 서버 오류)
3. 사용자명/비밀번호 입력 (qauser/qauser1!)
4. 계정 정보 입력 및 인증
5. 필요시 추가 인증 과정

#### 3.4 데이터 수집 및 처리
1. **응답 핸들러 설정**: API 응답 모니터링 시작
2. **API 응답 대기**: 최대 60초 동안 모든 API 응답 대기
3. **응답 데이터 처리**: 수집된 API 응답 데이터를 행 데이터로 변환
4. **HTML 바인딩 대기**: 템플릿 변수(`{{}}`)가 실제 데이터로 바인딩될 때까지 대기
5. **HTML 데이터 추출**: 메인 헤드라인, 설명, 스토리 데이터 추출

### 4. 오류 처리 및 재시도
- 각 계정별로 최대 3회 재시도
- 예외 발생 시 리소스 정리 (페이지, 컨텍스트, 브라우저)
- 3회 실패 시 에러 행을 결과에 추가

### 5. 결과 저장
- **스크린샷**: 각 계정별 전체 페이지 캡처
- **Excel 파일**: 
  - `테스트_결과_format.xlsx`: 포맷된 결과
  - `테스트_결과_main.xlsx`: 메인 결과
  - `result_{timestamp}/테스트결과_result.xlsx`: 최종 비교 결과

### 6. 데이터 비교 및 분석
- `CompareProcess` 클래스를 사용하여 포맷 결과와 메인 결과 비교
- 항목별 데이터 처리 및 추천 제품 데이터 처리
- 최종 결과 생성 및 저장

## 주요 모듈 설명

### rowdata_excel.py
- Excel 파일 로드 및 처리
- 국가별 데이터 복사
- 콘텐츠 매핑
- 우산 파일 매핑

### response_handler.py
- API 응답 모니터링
- 응답 데이터 수집 및 처리
- 계정별 데이터 바인딩

### html_result.py
- HTML 요소에서 데이터 추출
- 메인 헤드라인, 설명, 스토리 데이터 파싱

### compare_result.py
- 데이터 비교 및 분석
- 항목별 데이터 처리
- 최종 결과 생성

## 실행 방법

```bash
python smartThings_main.py
```

## 의존성

- **Playwright**: 브라우저 자동화
- **Pandas**: 데이터 처리 및 Excel 파일 처리
- **lxml**: HTML 파싱
- **requests**: HTTP 요청 처리
- **asyncio**: 비동기 프로그래밍

## 주의사항

1. **파일 경로**: 실행 전 모든 파일 경로가 올바르게 설정되어 있는지 확인
2. **Chrome 브라우저**: Chrome 실행 파일 경로가 올바른지 확인
3. **네트워크 환경**: 안정적인 인터넷 연결 필요
4. **권한**: Excel 파일 읽기/쓰기 권한 필요
5. **타임아웃**: API 응답 대기 시간은 60초로 설정되어 있음

## 결과 파일

- **스크린샷**: 각 계정별 페이지 캡처 이미지
- **Excel 결과**: 포맷된 데이터, 메인 데이터, 비교 결과
- **로그**: 콘솔에 출력되는 진행 상황 및 오류 정보

## 문제 해결

### 일반적인 문제들
1. **로그인 실패**: 계정 정보 확인, 네트워크 상태 점검
2. **API 응답 없음**: 타임아웃 설정 조정, 네트워크 상태 확인
3. **HTML 바인딩 실패**: 페이지 로딩 시간 증가, 선택자 확인
4. **파일 저장 오류**: 경로 권한, 디스크 공간 확인

### 디버깅 팁
- `headless=False`로 설정하여 브라우저 동작 확인
- 콘솔 출력을 통한 진행 상황 모니터링
- 각 단계별 예외 처리 및 로깅
