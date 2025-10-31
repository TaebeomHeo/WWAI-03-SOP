# L0-HANDOFF-CHECKLIST.md

**Version**: 1.0
**Last Updated**: 2024-01-31
**Status**: Active
**Owner**: Process Owner

---

## 개요

이 문서는 개발자가 프로젝트를 완료하고 비개발자에게 인수인계할 때 확인해야 할 체크리스트입니다.

**목표**:
- 비개발자가 독립적으로 유지보수 가능하도록 준비
- 모든 필요한 문서와 도구 제공
- AI-Assisted Maintenance 시스템 적용

**예상 소요 시간**: 6-8시간 (1-2일)

---

## Phase 1: 문서 작성 (4-6시간)

### 1.1 L1-CLAUDE.md 작성 ⭐⭐⭐

**소요 시간**: 1-2시간
**우선순위**: 최고 (가장 중요)

**템플릿**: `.ai-maintenance/templates/TEMPLATE-CLAUDE.md`

#### 작성 가이드

**필수 포함 사항**:
```markdown
# L1-CLAUDE.md

## Metadata
- Version: 1.0
- Last Updated: YYYY-MM-DD
- Owner: [개발자 이름]
- Status: Active

## 1. Project Overview
- 프로젝트 목적 (한 문장)
- 핵심 기능 (3-5개 bullet points)
- 주요 기술 스택 (Python 버전, 주요 라이브러리)

## 2. Quick Start
### 2.1 환경 설정
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2.2 기본 실행
```bash
python main.py
```

## 3. File Structure
```
프로젝트/
├── main.py              # 메인 실행 파일
├── module/              # 핵심 모듈
│   ├── __init__.py
│   ├── handler.py       # API 응답 처리
│   └── extractor.py     # 데이터 추출
└── data/                # 데이터 파일
```

## 4. Architecture
### 4.1 Data Flow
[입력] → [처리] → [출력]

### 4.2 Key Components
- **Component 1**: 역할 설명
- **Component 2**: 역할 설명

### 4.3 External Dependencies
- API: [어떤 API 사용]
- Database: [사용 여부]
- Browser: [Playwright 등]

## 5. Important Concepts
### 5.1 Async/Await
[이 프로젝트에서 비동기 사용하는 부분]

### 5.2 Data Processing
[데이터 처리 파이프라인]

## 6. Common Patterns
### 6.1 Error Handling
[에러 처리 패턴]

### 6.2 Logging
[로그 출력 방식]

## 7. Troubleshooting
| 문제 | 원인 | 해결 |
|------|------|------|
| [자주 발생하는 문제 1] | ... | ... |
| [자주 발생하는 문제 2] | ... | ... |

## 8. References
- README.md
- L1-COMPLEXITY-MATRIX.md
- L1-TESTING.md
```

**체크포인트**:
- [ ] 비개발자가 이 문서만 보고 프로젝트 이해 가능한가?
- [ ] 주요 실행 명령어가 모두 포함되었는가?
- [ ] 파일 구조 설명이 명확한가?
- [ ] 비동기, API 등 복잡한 부분 설명했는가?
- [ ] 자주 발생하는 문제와 해결책 포함했는가?

**검증**:
```bash
# 비개발자에게 L1-CLAUDE.md만 주고 실행 가능한지 확인
```

---

### 1.2 L1-COMPLEXITY-MATRIX.md 작성 ⭐⭐⭐

**소요 시간**: 1시간
**우선순위**: 최고

**템플릿**: `.ai-maintenance/templates/TEMPLATE-COMPLEXITY-MATRIX.md`

#### 작성 가이드

**🟢 LOW 섹션** (필수: 5개 이상 예시):
```markdown
## 🟢 LOW - 비개발자 단독 수정 가능

### 타임아웃 변경
**예시**:
- ✅ `timeout=60` → `timeout=90`

**위치**:
- `main.py`: line 145

**AI 프롬프트 예시**:
```
@L1-CLAUDE.md
@main.py

타임아웃을 60초에서 90초로 변경해줘.
```

**성공률**: 95%
```

**프로젝트 특화 예시** (반드시 포함):
- 이 프로젝트에서 자주 바뀌는 설정값
- 실제 파일명과 라인 번호
- 웹사이트 변경 시 바뀌는 CSS 선택자
- 테스트 URL 변경
- 국가/사이트 코드 추가

**🟡 MEDIUM 섹션** (필수: 3개 이상 예시):
- 새로운 검증 항목 추가 (기존 패턴 복사)
- 조건문 추가 (특정 사이트 스킵 등)
- 에러 처리 개선

**🔴 HIGH 섹션**:
- 명확한 기준 제시
- "이런 키워드가 보이면 HIGH" 목록
- 예: async/await, API endpoint 변경, Class 구조 변경

**의사결정 플로우차트**:
```
수정 요청
    ↓
async/await 관련? → YES → 🔴 HIGH
    ↓ NO
API 변경? → YES → 🔴 HIGH
    ↓ NO
여러 파일 수정? → YES → 🟡 MEDIUM 이상
    ↓ NO
설정값/문자열? → YES → 🟢 LOW
```

**체크포인트**:
- [ ] 프로젝트별 구체적 예시 5개 이상 (LOW)
- [ ] 실제 파일명과 라인 번호 포함
- [ ] 각 예시에 성공률 또는 주의사항 명시
- [ ] 플로우차트로 빠른 판단 가능

---

### 1.3 L1-CONSTRAINTS.md 작성 ⭐⭐⭐

**소요 시간**: 1시간
**우선순위**: 최고 (안전성)

**템플릿**: `.ai-maintenance/templates/TEMPLATE-CONSTRAINTS.md`

#### 작성 가이드

**⛔ 절대 금지 섹션**:

이 프로젝트에서 **절대** 수정하면 안 되는 것들을 명확히:

```markdown
## ⛔ 절대 금지

### 1. 비동기 함수 순서 변경
**금지 코드**:
```python
# main.py line 50-55
async def process():
    await step_a()  # 이 순서를
    await step_b()  # 바꾸면 안 됨!
```

**이유**:
- 데이터 의존성: step_b는 step_a의 결과 필요
- 위험: 데드락, 잘못된 결과

**대안**:
- 타임아웃 조정은 가능
- 순서 변경은 개발자 필수

### 2. {프로젝트 특화 금지사항}
...
```

**프로젝트별 필수 포함**:
- 이 프로젝트의 핵심 로직 (절대 건드리면 안 되는 부분)
- 데이터 파일 구조 (Excel/CSV 컬럼 순서)
- 외부 API 계약
- 보안 관련 (하드코딩 금지, env.user 커밋 금지)

**⚠️ 주의 필요 섹션**:
- CSS 선택자 변경 (검증 필수)
- 조건문 수정 (모든 분기 테스트)
- 타임아웃 변경 (적정 범위)

**✅ 안전 섹션**:
- 설정값 변경
- 로그 메시지
- 데이터 값 (구조 유지)

**체크포인트**:
- [ ] 이 프로젝트의 위험한 부분 명확히 명시
- [ ] 각 금지 사항마다 이유 설명
- [ ] 실제 코드 예시 포함
- [ ] 대안 제시 (이렇게 하면 안 되고, 이렇게 해야 함)

---

### 1.4 L1-TESTING.md 작성 ⭐⭐⭐

**소요 시간**: 1-2시간
**우선순위**: 최고 (검증)

**템플릿**: `.ai-maintenance/templates/TEMPLATE-TESTING.md`

#### 작성 가이드

**기본 검증 섹션**:
```markdown
## 기본 검증 (모든 수정 후 필수)

### 문법 검증
```bash
python -m py_compile {파일명}
```

### 의존성 확인
```bash
pip list | grep {주요_패키지}
```
```

**프로젝트별 최소 테스트** (매우 중요):
```markdown
## {프로젝트명} 최소 테스트 (5-10분)

```bash
# 1개 항목으로 빠른 테스트
python main.py --count 1
# 또는
python main.py --quick-test
```

**확인 사항**:
- [ ] 프로그램 시작되는가?
- [ ] {주요 기능 1} 작동하는가?
- [ ] {주요 기능 2} 작동하는가?
- [ ] 결과 파일 생성되는가?
- [ ] 에러 없이 완료되는가?

**성공 기준**:
- 표준 출력에 "완료" 메시지
- `result/` 폴더에 JSON 파일 생성
- 에러 로그 없음
```

**전체 테스트 섹션**:
```markdown
## 전체 테스트 (30분-1시간)

```bash
python main.py  # 전체 실행
```

**확인 사항**:
- [ ] 모든 입력 데이터 처리
- [ ] {검증 항목 1} 통과
- [ ] {검증 항목 2} 통과
- [ ] 성능 허용 범위 내 (X분 이내)
```

**엣지 케이스** (프로젝트 특화):
```markdown
## 엣지 케이스 테스트

### 빈 데이터
```bash
# 계정 0개로 테스트
```
예상 결과: 에러 없이 종료, 빈 결과 파일

### 특수 문자 포함
- 한글, 이모지, HTML 태그
예상 결과: 정상 처리 또는 명확한 에러 메시지

### {프로젝트 특화 엣지 케이스}
```

**회귀 테스트**:
```markdown
## 회귀 테스트

### 결과 비교
```bash
# 수정 전 결과
cp result/old.json backup/

# 수정 후 결과와 비교
diff backup/old.json result/new.json
```

**기대 결과**:
- 의도한 변경만 발생
- 다른 부분은 동일
```

**체크포인트**:
- [ ] 최소 테스트 명령어 명확 (복사-붙여넣기 가능)
- [ ] 성공/실패 판단 기준 명확
- [ ] 프로젝트 특화 엣지 케이스 포함
- [ ] 비개발자가 혼자 실행 가능

**검증**:
```bash
# 비개발자에게 이 문서만 주고 테스트 가능한지 확인
```

---

### 1.5 L2-EXAMPLES.md 초기 작성 ⭐⭐

**소요 시간**: 2시간
**우선순위**: 높음

**템플릿**: `.ai-maintenance/templates/TEMPLATE-EXAMPLES.md`

#### 작성 가이드

**필수**: 최소 3-5개 사례 작성

**사례 구성**:
1. **🟢 LOW 성공 사례** (2-3개)
   - 타임아웃 변경
   - URL 변경
   - CSS 선택자 변경

2. **🟡 MEDIUM 성공 사례** (1-2개)
   - 새 검증 항목 추가
   - 조건문 수정

3. **❌ 실패 사례** (1개)
   - async/await 순서 변경 시도 실패
   - 왜 실패했는지, 교훈은 무엇인지

**사례 템플릿**:
```markdown
## 사례 1: 타임아웃 60초 → 90초 변경
**날짜**: YYYY-MM-DD
**수정자**: [개발자 이름]
**프로젝트**: {프로젝트명}
**난이도**: 🟢 LOW
**성공 여부**: ✅ 성공
**소요 시간**: 5분

### 문제 상황
네트워크가 느린 환경에서 API 응답 대기 중 타임아웃 발생

### 해결 방법
wait_for_responses의 timeout 파라미터를 60에서 90으로 증가

### 수정 파일 및 라인
- `main.py`: line 145

### 수정 전 코드
```python
await data_collect.wait_for_responses(timeout=60)
```

### 수정 후 코드
```python
await data_collect.wait_for_responses(timeout=90)
```

### AI 프롬프트
```
@L1-CLAUDE.md
@main.py

API 응답 대기 시간이 60초로 설정되어 있는데,
90초로 늘리고 싶어. 어떤 부분을 수정하면 되는지 알려줘.
```

### AI 도구
Claude (claude.ai)

### 테스트 방법
```bash
# 최소 테스트
python main.py --count 1

# 타임아웃 에러 발생하지 않는지 확인
```

### 배운 점 / 주의사항
- 타임아웃을 너무 크게 설정하면 전체 실행 시간 증가
- 90초로 충분한지 여러 번 테스트 필요
- 다른 타임아웃 설정도 있으니 혼동 주의
```

**체크포인트**:
- [ ] 3-5개 사례 작성 완료
- [ ] 각 사례에 실제 코드 포함
- [ ] AI 프롬프트 정확히 기록
- [ ] 테스트 방법 명확
- [ ] 실패 사례 1개 이상 포함 (교훈)

---

### 1.6 L2-PROMPTS.md 초기 작성 ⭐

**소요 시간**: 30분
**우선순위**: 중간

**템플릿**: `.ai-maintenance/templates/TEMPLATE-AI-PROMPTS.md`

#### 작성 가이드

기본 템플릿을 복사하고, 프로젝트 이름만 수정:

```markdown
# L2-PROMPTS.md

## Metadata
- Version: 1.0
- Last Updated: YYYY-MM-DD
- Project: {프로젝트명}

## 1. 복잡도 평가 프롬프트
[템플릿 복사]
- {프로젝트명} 부분만 수정

## 2. 구현 가이드 프롬프트
[템플릿 복사]

...
```

**체크포인트**:
- [ ] 기본 프롬프트 10개 템플릿 포함
- [ ] 프로젝트명 치환 완료
- [ ] Context 파일 경로 확인

---

## Phase 2: 코드 정리 (1-2시간)

### 2.1 주석 추가 ⭐⭐

**목표**: 비개발자가 코드 읽을 수 있게

**작업 내용**:

```python
# Before (주석 없음)
def process(data):
    result = []
    for item in data:
        if item.status == 200:
            result.append(item.extract())
    return result

# After (주석 추가)
def process(data):
    """
    데이터 리스트를 처리하여 성공한 항목만 추출합니다.

    Args:
        data: 처리할 데이터 리스트

    Returns:
        성공한 항목들의 리스트
    """
    result = []

    # 각 항목 순회
    for item in data:
        # HTTP 200 (성공) 응답만 처리
        if item.status == 200:
            # 데이터 추출하여 결과에 추가
            result.append(item.extract())

    return result
```

**가이드라인**:
- 모든 함수에 docstring (목적, 파라미터, 반환값)
- 복잡한 로직에는 라인별 주석
- "왜"를 설명 (무엇을 하는지는 코드로 알 수 있음)
- 한글 또는 영어 (팀 선택)

**체크포인트**:
- [ ] 모든 public 함수에 docstring
- [ ] 복잡한 로직 (10줄 이상)에 주석
- [ ] 비동기 함수 설명 충분
- [ ] 중요한 상수에 주석

---

### 2.2 매직 넘버 제거 ⭐

**목표**: 하드코딩된 숫자를 상수로

**작업 내용**:

```python
# Before
await page.wait_for_timeout(2000)
if count > 10:
    ...

# After
# 파일 상단에 상수 정의
TIMEOUT_PAGE_LOAD = 2000  # 페이지 로딩 대기 시간 (ms)
MAX_RETRY_COUNT = 10       # 최대 재시도 횟수

# 사용
await page.wait_for_timeout(TIMEOUT_PAGE_LOAD)
if count > MAX_RETRY_COUNT:
    ...
```

**장점**:
- 비개발자가 수정하기 쉬움
- 의미 명확
- 한 곳에서 관리

**체크포인트**:
- [ ] 주요 숫자값 상수화
- [ ] 상수명이 명확
- [ ] 파일 상단에 정의

---

### 2.3 하드코딩 제거 ⭐⭐

**목표**: 설정값을 파일 또는 환경변수로

**작업 내용**:

```python
# Before
api_key = "sk-abc123def456"  # 안 됨!
path = "C:\\Users\\WW\\Desktop\\file"  # 환경 의존

# After
# env.user 파일
API_KEY=sk-abc123def456
DATA_PATH=/path/to/data

# 코드
import os
from dotenv import load_dotenv

load_dotenv('env.user')
api_key = os.getenv('API_KEY')
data_path = os.getenv('DATA_PATH')
```

**체크포인트**:
- [ ] API 키, 비밀번호 → env.user
- [ ] 파일 경로 → 설정 파일 또는 env.user
- [ ] URL → 설정 파일
- [ ] env.user.sample 제공

---

## Phase 3: 테스트 및 검증 (1-2시간)

### 3.1 Happy Path 테스트 ⭐⭐⭐

**목표**: 기본 시나리오가 완벽히 작동

**테스트**:
```bash
# 1. 최소 테스트 (1개 항목)
# L1-TESTING.md에 정확히 명시한 대로 실행

# 2. 전체 테스트
# 처음부터 끝까지 실행

# 3. 결과 확인
# 예상 결과 파일 생성되는지
```

**체크포인트**:
- [ ] 최소 테스트 통과
- [ ] 전체 테스트 통과
- [ ] 에러 없이 완료
- [ ] 결과 파일 정상

---

### 3.2 문서 검증 ⭐⭐

**목표**: 문서대로 실행 가능한지 확인

**검증 방법**:

1. **L1-CLAUDE.md 검증**:
   ```bash
   # 새로운 터미널에서 (프로젝트 지식 없이)
   # L1-CLAUDE.md만 보고 실행 가능한지 테스트
   ```

2. **L1-TESTING.md 검증**:
   ```bash
   # 문서의 명령어 그대로 복사-붙여넣기
   # 성공하는지 확인
   ```

3. **L2-EXAMPLES.md 검증**:
   ```bash
   # 사례 1의 AI 프롬프트 그대로 AI에 입력
   # 동일한 결과 나오는지 확인
   ```

**체크포인트**:
- [ ] L1-CLAUDE.md만으로 실행 가능
- [ ] L1-TESTING.md 명령어 모두 작동
- [ ] L2-EXAMPLES.md 사례 재현 가능

---

## Phase 4: 인수인계 교육 (2-3시간)

### 4.1 교육 준비 ⭐⭐

**자료**:
- [ ] L0-WORKFLOW-MASTER.md 인쇄 또는 화면 공유
- [ ] L1-CLAUDE.md 인쇄
- [ ] L2-EXAMPLES.md (사례 1-2개)
- [ ] 실습 환경 (비개발자 PC)

**일정**: 2-3시간 (중간 휴식 포함)

---

### 4.2 교육 진행 (Session 1: 시스템 이해, 1시간)

**Agenda**:

**1. 전체 시스템 소개 (15분)**
```
- AI-Assisted Maintenance란?
- 왜 필요한가?
- 어떤 것들을 수정할 수 있는가?
- 문서 체계 (L0, L1, L2)
```

**2. 문서 둘러보기 (20분)**
```
- L0-WORKFLOW-MASTER.md (프로세스)
- L1-CLAUDE.md (프로젝트 이해)
- L1-COMPLEXITY-MATRIX.md (난이도 판단)
- L2-EXAMPLES.md (사례)
```

**3. 프로젝트 실행 (15분)**
```
- 환경 설정 확인
- 최소 테스트 실행
- 결과 확인
```

**4. 질의응답 (10분)**

---

### 4.3 교육 진행 (Session 2: 실습, 1-2시간)

**Agenda**:

**1. 간단한 수정 실습 (45분)**

실습 1: 타임아웃 변경 (🟢 LOW)
```
Step 0: Git 백업
Step 1: AI로 복잡도 평가
  - 프롬프트 작성 (L2-PROMPTS 참고)
  - @L1-CLAUDE.md, @L1-COMPLEXITY-MATRIX.md
  - 결과: 🟢 LOW 확인
Step 2: AI와 구현
  - Before/After 확인
  - 파일 수정
Step 3: 테스트
  - L1-TESTING.md 참고
  - 최소 테스트 실행
Step 5: 문서화
  - L2-EXAMPLES.md에 사례 추가
  - Git commit
```

**2. AI 도구 사용법 (30분)**
```
- Claude (claude.ai) 실습
- Cursor 설치 및 설정 (선택)
- Context 파일 제공 방법 (@파일명)
- 프롬프트 작성 요령
```

**3. 질의응답 및 마무리 (15분)**
```
- 막혔을 때 어떻게 하나?
- 개발자에게 언제 연락하나?
- 다음 스스로 해볼 것 제안
```

---

### 4.4 Follow-up 계획 ⭐

**1주차**: 매일 체크인
```
- Slack/Teams 채널 생성
- 매일 오전 "오늘 할 일" 공유
- 매일 오후 "진행 상황" 공유
- 막히면 즉시 도움
```

**2주차**: 격일 체크인
```
- 월/수/금 체크인
- 스스로 해결 유도
```

**3-4주차**: 주 2회 체크인
```
- 화/목 체크인
- 독립 운영 준비
```

**1개월 후**: 주 1회 체크인
```
- 금요일 주간 회고
- 어려웠던 점 공유
- 다음 주 계획
```

---

## Phase 5: 최종 점검 (30분)

### 5.1 체크리스트 최종 확인 ✅

```markdown
## 문서 작성 완료
- [ ] L1-CLAUDE.md ⭐⭐⭐
- [ ] L1-COMPLEXITY-MATRIX.md ⭐⭐⭐
- [ ] L1-CONSTRAINTS.md ⭐⭐⭐
- [ ] L1-TESTING.md ⭐⭐⭐
- [ ] L2-EXAMPLES.md (3-5개) ⭐⭐
- [ ] L2-PROMPTS.md ⭐

## 코드 품질
- [ ] 주요 함수에 주석
- [ ] 매직 넘버 상수화
- [ ] 하드코딩 제거
- [ ] env.user.sample 제공

## 테스트
- [ ] Happy path 테스트 통과
- [ ] 문서대로 실행 가능 검증
- [ ] 최소 테스트 명령어 검증

## 인수인계
- [ ] 2-3시간 교육 완료
- [ ] 실습 1회 이상 완료
- [ ] Follow-up 계획 수립
- [ ] 긴급 연락처 공유

## Git
- [ ] .gitignore에 env.user 포함
- [ ] 민감 정보 커밋 안 함
- [ ] change-requests/ 폴더 생성
```

---

### 5.2 인수인계 완료 보고서

**템플릿**:
```markdown
# 인수인계 완료 보고서

**프로젝트**: {프로젝트명}
**개발자**: [이름]
**인수자**: [비개발자 이름]
**날짜**: YYYY-MM-DD

## 완료 항목
- ✅ L1 문서 6개 작성 완료
- ✅ L2 문서 초기 사례 5개
- ✅ 코드 주석 및 리팩토링
- ✅ 2시간 교육 완료
- ✅ 실습 완료 (타임아웃 변경)

## 비개발자 피드백
[교육 중 나온 질문, 어려웠던 점]

## 향후 지원 계획
- 1주차: 매일 체크인
- 2주차: 격일 체크인
- 1개월: 주 1회 회고

## 긴급 연락처
- Slack: #project-{name}
- Email: dev@example.com
- 개발자 직통: 010-XXXX-XXXX

## 다음 단계
1. 비개발자: 1주일 내 첫 🟢 LOW 수정 시도
2. 개발자: 1주일 내 리뷰 제공
3. 2주 내: 🟡 MEDIUM 수정 도전
4. 1개월 내: 독립 운영 평가
```

---

## 부록 A: 시간 절약 팁

### 빠른 인수인계 (최소 4시간)

**우선순위 조정**:
1. ⭐⭐⭐ (필수): L1-CLAUDE, COMPLEXITY, CONSTRAINTS, TESTING (3시간)
2. ⭐⭐ (강력 권장): L2-EXAMPLES 3개 (1시간)
3. ⭐ (권장): L2-PROMPTS (템플릿 복사만)

**생략 가능** (나중에 추가):
- 코드 주석 (핵심 부분만)
- 매직 넘버 상수화 (점진적)
- L2-EXAMPLES 5개 → 3개로 축소

---

## 부록 B: 자주 묻는 질문 (FAQ)

**Q1: 문서 작성에 8시간이 너무 길어요**

A: 우선순위에 따라 조정 가능:
- 최소 4시간 (필수 문서만)
- 권장 6시간 (사례 포함)
- 이상적 8시간 (완전한 준비)

**Q2: 비개발자가 Python을 전혀 모르는데 가능한가요?**

A: Python 기초 지식 권장하지만 필수는 아님:
- L1-CLAUDE.md에 충분한 설명
- AI가 대부분 도와줌
- 처음 1-2주는 개발자 적극 지원

**Q3: 프로젝트가 너무 복잡한데 적용 가능한가요?**

A: 복잡도에 따라 전략 조정:
- 간단한 프로젝트: 전체 적용
- 복잡한 프로젝트: 일부 기능만 (설정 변경, URL 수정 등)
- 매우 복잡: 개발자 위주, 비개발자는 테스트만

**Q4: 여러 프로젝트에 적용하려면?**

A: .ai-maintenance 폴더 재사용:
1. 첫 프로젝트: 8시간 (전체 작성)
2. 두 번째 이후: 4-5시간 (템플릿 복사 + 커스터마이징)

---

## 부록 C: 개발자 셀프 체크

인수인계 전 스스로 확인:

```
[ ] "비개발자가 L1-CLAUDE.md만 보고 프로젝트 실행 가능한가?"
    → 안 되면: 문서 보강

[ ] "내가 이 프로젝트를 처음 본다면, L1-COMPLEXITY-MATRIX.md로 난이도 판단 가능한가?"
    → 애매하면: 예시 추가

[ ] "L1-TESTING.md의 명령어만 복사-붙여넣기로 테스트 가능한가?"
    → 안 되면: 명령어 수정

[ ] "L2-EXAMPLES.md의 사례를 따라하면 성공하는가?"
    → 안 되면: 사례 재검증

[ ] "비개발자가 막혔을 때 어디를 봐야 하는지 명확한가?"
    → 불명확하면: 인덱스 강화
```

---

## Changelog

### v1.0 (2024-01-31)
- 초기 버전 작성
- 5단계 인수인계 프로세스 정의
- 문서별 작성 가이드 상세화
- 교육 커리큘럼 추가
- FAQ 및 팁 추가
