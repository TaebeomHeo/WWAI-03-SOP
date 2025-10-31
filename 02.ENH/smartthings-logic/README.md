# SmartThings 로직 추천 시스템

SmartThings 로직 추천 시스템은 사용자의 관심사키워드와 보유제품을 기반으로 적절한 스토리를 추천하는 프롬프트 기반 AI 시스템입니다. 복잡한 5단계 로직을 통해 계정별로 최적의 스토리를 도출하며, 각 단계마다 명확한 규칙과 우선순위를 적용합니다.

## 🚀 주요 기능

- **프롬프트 기반 처리**: LLM이 구조화된 프롬프트를 통해 복잡한 5단계 로직을 처리
- **배치 처리**: 여러 계정을 효율적으로 일괄 처리
- **2단계 추천**: 스토리 추천 → 제품 추천 순차 처리
- **상세한 로깅**: 모든 처리 과정에 대한 상세한 로그 및 오류 추적
- **다양한 출력 형식**: Excel, Markdown, 요약 보고서 생성
- **이중 사용 모드**: 코드 기반 실행과 Chat 기반 대화형 사용 지원

## 📋 시스템 요구사항

### 필수 요구사항
- Python 3.8 이상
- OpenAI API 키
- 필요한 Python 패키지 (requirements.txt 참조)

### 입력 파일
- `data/account.csv`: 계정 정보 (Account, 관심사키워드, 보유제품)
- `data/story.csv`: 스토리 정보 (관심사키워드, 스토리ID, 제품 정보)
- `prompt/story_prompt.md`: 스토리 추천 프롬프트
- `prompt/product_prompt.md`: 제품 추천 프롬프트
- `prompt/story_prompt_chat.md`: Chat 기반 스토리 추천 프롬프트

## 🛠 설치 및 설정

### 1. 저장소 클론 및 가상환경 설정

```bash
git clone <repository-url>
cd SmartThings-Logic

# 가상환경 생성 및 활성화
python -m venv venv

# Windows에서 가상환경 활성화
venv\Scripts\activate

# macOS/Linux에서 가상환경 활성화
# source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 초기 설정

#### 2-1. 환경 설정 파일 생성

```bash
# env.user.sample을 복사하여 env.user 생성
cp env.user.sample env.user
```

#### 2-2. OpenAI API 키 설정

`env.user` 파일을 편집하여 OpenAI API 키를 설정합니다:

```bash
# OpenAI 설정
OPENAI_API_KEY=your_openai_api_key_here

# LLM 모델 설정
MODEL_NAME=gpt-4o-mini

# 파일 경로 설정 (새로운 폴더 구조)
ACCOUNT_CSV_PATH=data/account.csv
STORY_CSV_PATH=data/story.csv
STORY_PROMPT_PATH=prompt/story_prompt.md
PRODUCT_PROMPT_PATH=prompt/product_prompt.md

# 출력 설정
OUTPUT_DIRECTORY=output
```

### 3. 데이터 파일 확인

프로젝트의 `data/` 폴더에 다음 파일들이 있는지 확인합니다:
- `data/account.csv`: 계정 데이터 (탭 구분자)
- `data/story.csv`: 스토리 데이터 (탭 구분자)

프로젝트의 `prompt/` 폴더에 다음 파일들이 있는지 확인합니다:
- `prompt/story_prompt.md`: 스토리 추천 프롬프트
- `prompt/product_prompt.md`: 제품 추천 프롬프트
- `prompt/story_prompt_chat.md`: Chat 기반 스토리 추천 프롬프트

## 🎯 사용법

### 방법 1: 코드 기반 실행 (기본)

```bash
# 가상환경 활성화 (아직 활성화되지 않은 경우)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 전체 계정 배치 처리
python main.py
```

시스템은 자동으로 다음 단계를 수행합니다:
1. 환경 설정 로드 및 검증
2. CSV 데이터 로딩
3. 모든 계정에 대해 스토리 추천 처리
4. 성공한 스토리 추천에 대해 제품 추천 처리
5. 결과 파일 생성

### 방법 2: Chat 기반 대화형 사용

Cursor AI에서 다음 파일들을 context로 제공하고 대화형으로 사용:

**필요한 Context 파일들:**
- `data/account.csv`
- `data/story.csv`
- `prompt/story_prompt_chat.md`

**사용 예시:**
```
[계정 데이터]
@data/account.csv

[스토리 데이터]
@data/story.csv

[스토리 추천 로직]
@prompt/story_prompt_chat.md

[추가 사항]
- 현재 주어진 데이터와 로직만을 이용해서 분석
- 계정에 대한 분석을 반드시 단계별로 실행

계정 st_story1@teml.net에 맞는 스토리를 추천해주세요.
```

**전체 계정 분석 시 주의사항:**

```
⚠️ 전체 계정에 대한 분석 요청 시 채팅이 중간에 멈출 수 있습니다.
권장사항: 4개 정도의 계정으로 분할하여 실행하세요.

예시:
"계정 1-4번에 대해 스토리를 추천해주세요."
"계정 5-8번에 대해 스토리를 추천해주세요."
```

## 📊 출력 결과

### 생성되는 파일들

실행 후 `output/` 디렉토리에 다음 파일들이 생성됩니다:

- **`story_reasoning_YYYYMMDD_HHMMSS.md`**: 스토리 추천 상세 분석
- **`product_reasoning_YYYYMMDD_HHMMSS.md`**: 제품 추천 상세 분석
- **`final_results_YYYYMMDD_HHMMSS.xlsx`**: 최종 통합 Excel 보고서

### 결과 형식

시스템은 다음과 같은 형식으로 결과를 출력합니다:

1. **특례 조건**: `35-1, 35-3, 42-3, 35-2 중 랜덤`
2. **일반 추천**: `37-1, 39-1`
3. **단일 추천**: `38-1`

## 🏗 시스템 아키텍처

### 핵심 컴포넌트

1. **main.py**: 메인 실행 파일 - 설정 로드 및 검증
2. **processor.py**: 핵심 처리 로직
   - `DataLoader`: CSV 파일 로딩 및 데이터 추출
   - `SmartThingsProcessor`: 전체 워크플로우 관리
   - `call_llm()`: LLM API 호출
   - `parse_story_result()`: 결과 파싱
3. **prompts.py**: 프롬프트 관리 모듈
   - `load_system_prompts()`: 시스템 프롬프트 로드
   - `build_story_prompt()`: 스토리 추천 프롬프트 생성
   - `build_product_prompt()`: 제품 추천 프롬프트 생성
4. **reports.py**: 보고서 생성 모듈
   - `generate_story_reasoning()`: 스토리 추천 분석 보고서
   - `generate_product_reasoning()`: 제품 추천 분석 보고서
   - `generate_excel_report()`: 통합 Excel 보고서

### 처리 워크플로우

```
설정 로드 → 데이터 로딩 → 스토리 추천 → 제품 추천 → 보고서 생성
```

## 🔍 5단계 추천 로직

시스템은 다음과 같은 5단계 로직을 통해 스토리를 추천합니다:

### 1단계: 관심사키워드 매칭
- 계정의 관심사키워드와 스토리의 관심사키워드 정확 일치 확인
- 특례 조건: 관심사키워드가 '-'이고 보유제품도 '-'인 경우 → "38-2, 38-1" 반환

### 2단계: 제품 매칭 분석
- 계정 보유제품과 스토리 제품의 일치/미일치 개수 계산
- 완벽 매칭, 부분 매칭, 미일치 분류

### 3단계: 복합 정렬 로직 (5차 정렬)
1. **1차**: 일치개수 많은 순 (내림차순)
2. **2차**: 동일 관심사키워드 내 일치 제품별 스토리 개수 적은 순
3. **3차**: 일치 제품의 제품 우선순위 높은 순 (숫자 작은 순)
4. **4차**: 미일치개수 적은 순
5. **5차**: 미일치 제품의 제품 우선순위 높은 순

### 4단계: 최종 스토리 선별
- 1등과 2등까지만 선별 (동점자 포함)
- 독보적인 1위/2위 감지 시 즉시 출력

### 5단계: 결과 형식화
- 4개 스토리 특정 조합: "중 랜덤" 형식
- 2개 스토리: "1순위, 2순위" 형식
- 기타: "[검토필요]" 표시

## 🔧 특별 처리 로직

### 특례 조건
- **Ease of use + Mobile,TV**: `35-1, 35-3, 42-3, 35-2 중 랜덤`
- **관심사/제품 모두 없음**: `38-2, 38-1`

### 단일 키워드 매칭
- 해당 키워드 스토리 1개 + 전체 스토리에서 제품 매칭 최고 스토리 1개

### 혼합 키워드 전략
- 완벽 매칭 스토리 1개 + 다른 키워드에서 제품 매칭 최고 스토리 1개

## 🔧 유지보수 가이드

### 프롬프트 수정 (권장)

**같은 관심사 키워드 조건이 달라지지 않는 경우:**
- `prompt/story_prompt.md` 파일을 직접 수정
- `prompt/product_prompt.md` 파일을 직접 수정
- 코드 수정 없이 로직 변경 가능

### 코드 수정 (필요시)

**같은 관심사 키워드 조건이 달라지는 경우:**
- Cursor AI에 `prompts.py`를 context로 제공
- 변경된 조건에 따라 코드 수정 요청
- `prompts.py`의 `build_story_prompt()` 함수 수정 필요

### 수정 우선순위

1. **프롬프트 수정**: 가장 간단하고 안전한 방법
2. **코드 수정**: 조건 변경이 필요한 경우에만

## 🚨 문제 해결

### 일반적인 문제들

#### API 키 오류
```
❌ 오류: OpenAI API 키가 설정되지 않았습니다.
```
**해결방법**: `env.user` 파일에 올바른 OpenAI API 키를 설정하세요.

#### 파일 누락 오류
```
❌ 오류: 계정 CSV 파일을 찾을 수 없습니다: data/account.csv
```
**해결방법**: 
- `data/` 폴더에 `account.csv`와 `story.csv` 파일을 배치하세요
- `prompt/` 폴더에 `story_prompt.md`와 `product_prompt.md` 파일을 배치하세요

#### 환경 설정 파일 오류
```
❌ 오류: env.user 파일이 없습니다.
```
**해결방법**: 
```bash
cp env.user.sample env.user
# env.user 파일에 API 키 설정
```

#### 가상환경 관련 오류
```
❌ 오류: 모듈을 찾을 수 없습니다.
```
**해결방법**: 
```bash
# 가상환경이 활성화되어 있는지 확인
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 의존성이 설치되어 있는지 확인
pip list

# 필요시 의존성 재설치
pip install -r requirements.txt
```

#### CSV 형식 오류
**해결방법**: 
- CSV 파일이 탭 구분자(`\t`) 형식인지 확인하세요
- UTF-8 인코딩으로 저장되었는지 확인하세요

#### API 호출 실패
**해결방법**:
- 네트워크 연결을 확인하세요
- API 키의 유효성을 확인하세요
- OpenAI API 할당량을 확인하세요

## 📝 개발자 가이드

### 프로젝트 구조

```
SmartThings-Logic/
├── main.py                 # 메인 실행 스크립트
├── processor.py            # 핵심 처리 로직
├── prompts.py             # 프롬프트 관리
├── reports.py             # 보고서 생성
├── env.user.sample        # 환경 설정 샘플
├── requirements.txt       # 의존성 목록
├── venv/                  # 가상환경 (생성됨)
├── data/                  # 데이터 파일
│   ├── account.csv       # 계정 데이터
│   ├── story.csv         # 스토리 데이터
│   └── product.csv       # 제품 데이터
├── prompt/                # 프롬프트 파일
│   ├── story_prompt.md   # 스토리 추천 프롬프트
│   ├── product_prompt.md # 제품 추천 프롬프트
│   └── story_prompt_chat.md
└── output/                # 출력 결과
      ├── story_reasoning_*.md
      ├── product_reasoning_*.md
      └── final_results_*.xlsx
```

### 주요 파일 설명

- **main.py**: 시스템 진입점, 설정 로드 및 검증
- **processor.py**: 핵심 비즈니스 로직, 데이터 처리 및 LLM 호출
- **prompts.py**: 프롬프트 생성 및 관리 로직
- **reports.py**: 결과 파일 생성 (Excel, Markdown)
- **env.user**: 환경 설정 (API 키, 파일 경로 등)