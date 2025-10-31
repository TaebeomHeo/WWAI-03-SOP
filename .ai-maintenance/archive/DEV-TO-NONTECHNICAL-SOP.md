# Developer → Non-Technical Maintainer Handoff SOP

## 목적 (Purpose)

개발자가 작성한 웹 자동화 프로젝트를 비개발자가 AI 도구(ChatGPT, Claude 등)를 활용하여 독립적으로 유지보수하고 개선할 수 있도록 하는 표준 절차.

---

## Phase 1: 개발 완료 단계 (Development Completion)

### 1.1 개발자가 준비해야 할 문서

#### A. CLAUDE.md (AI Context 문서) ✅
- 프로젝트 아키텍처 개요
- 주요 실행 명령어
- 파일 구조 및 역할
- 중요한 기술적 결정사항
- 공통 패턴 및 규칙

#### B. CHANGE-COMPLEXITY-MATRIX.md (변경 복잡도 매트릭스)
```markdown
# 변경 복잡도 분류

## 🟢 LOW - 비개발자 단독 수정 가능
- 설정값 변경 (타임아웃, URL, 파일 경로)
- 데이터 파일 수정 (CSV, Excel)
- 프롬프트 텍스트 수정
- 로그 메시지 변경
- CSS 선택자 단순 교체

## 🟡 MEDIUM - AI 도움으로 가능 (주의 필요)
- 새로운 검증 항목 추가 (기존 패턴 복사)
- 간단한 조건문 추가/수정
- 새로운 국가/사이트 추가
- 에러 메시지 처리 추가

## 🔴 HIGH - 개발자 필수
- API 엔드포인트 변경
- 비동기 로직 수정
- 복잡한 알고리즘 변경
- 아키텍처 수정
- 의존성 업그레이드
- 보안 관련 수정
```

#### C. EXAMPLES.md (수정 사례집)
실제 성공한 비개발자 수정 사례를 문서화:
```markdown
# 성공 사례 1: 타임아웃 증가
**문제**: 페이지 로딩이 느려서 60초 타임아웃 부족
**해결**: `await data_collect.wait_for_responses(timeout=60)` → `timeout=90`
**난이도**: 🟢 LOW
**AI 프롬프트**: "타임아웃을 60초에서 90초로 늘려줘"

# 성공 사례 2: 새로운 CSS 선택자 추가
**문제**: 웹사이트 리뉴얼로 버튼 클래스명 변경
**해결**: `.old-button` → `.new-button-class`
**난이도**: 🟢 LOW
**AI 프롬프트**: "웹사이트에서 이 버튼의 새로운 클래스를 찾았어: .new-button-class. 코드에서 .old-button을 모두 교체해줘"

# 실패 사례 1: 비동기 로직 수정 시도
**시도**: API 호출 순서 변경
**결과**: 데드락 발생
**교훈**: 비동기 관련은 개발자에게 요청 필요
**난이도**: 🔴 HIGH
```

#### D. AI-PROMPTS.md (검증된 AI 프롬프트 템플릿)
```markdown
# 변경 요청 시 사용할 AI 프롬프트 템플릿

## 1. 복잡도 평가 요청
"""
나는 이 웹 자동화 프로젝트를 수정하고 싶어.
아래 파일들을 읽고, 내 수정 요청의 복잡도를 평가해줘:

[Context Files]
@CLAUDE.md
@CHANGE-COMPLEXITY-MATRIX.md
@{수정할_파일.py}

[수정 요청]
{구체적인 수정 내용}

[평가 요청]
1. 이 수정의 복잡도 (LOW/MEDIUM/HIGH)
2. 왜 그렇게 판단했는지
3. 내가 직접 할 수 있는지, 개발자 도움이 필요한지
4. 예상되는 위험 요소
"""

## 2. 단계별 구현 요청 (LOW/MEDIUM)
"""
@CLAUDE.md
@EXAMPLES.md
@{수정할_파일.py}

다음 수정을 단계별로 안내해줘:
{수정 내용}

각 단계마다:
1. 무엇을 할 것인지 설명
2. 어떤 코드를 어떻게 수정할지
3. 수정 후 테스트 방법
4. 되돌리기 방법 (rollback)
"""

## 3. 코드 리뷰 요청
"""
@CLAUDE.md
@{수정한_파일.py}

내가 아래와 같이 수정했어. 리뷰해줘:

[수정 내용]
{diff 또는 수정한 코드}

[리뷰 요청 사항]
1. 문법 오류 확인
2. 기존 기능 영향 분석
3. 놓친 부분 확인
4. 테스트 체크리스트
"""
```

#### E. TESTING-CHECKLIST.md (테스트 체크리스트)
```markdown
# 변경 후 테스트 체크리스트

## 기본 검증 (모든 변경 후 필수)
- [ ] 가상환경 활성화 확인
- [ ] 의존성 설치 확인: `pip install -r requirements.txt`
- [ ] 문법 오류 확인: `python -m py_compile {파일명.py}`
- [ ] 실행 오류 확인: 최소 1회 전체 실행 성공

## 프로젝트별 테스트

### 01.smartThings
- [ ] 1개 계정으로 테스트 실행
- [ ] 스크린샷 생성 확인
- [ ] Excel 결과 파일 생성 확인
- [ ] 브라우저 정상 종료 확인

### 02.ENH/gnb
- [ ] CGD JSON 변환 성공: `python cgd.py`
- [ ] GNB 추출 성공: `python main.py`
- [ ] JSON 결과 파일 확인

### 02.ENH/pd
- [ ] 1개 URL 테스트 실행
- [ ] 모든 검증 항목 실행 확인
- [ ] JSON 결과 파일 확인

### 02.ENH/pf
- [ ] 1개 URL 테스트 실행
- [ ] 11개 검증 항목 실행 확인
- [ ] JSON 결과 파일 확인

### 02.ENH/shop
- [ ] 메뉴 구조 추출 성공
- [ ] 링크 검증 실행 확인
- [ ] JSON 결과 파일 확인

### 02.ENH/smartthings-logic
- [ ] OpenAI API 키 설정 확인
- [ ] 1개 계정 추천 성공
- [ ] Markdown 결과 생성 확인
- [ ] Excel 결과 생성 확인

## Rollback 준비
- [ ] 수정 전 코드 백업 보관
- [ ] Git commit 전 상태 확인
- [ ] 되돌리기 명령어 확인: `git checkout {파일명}`
```

#### F. PROJECT-CONSTRAINTS.md (프로젝트 제약사항)
```markdown
# 절대 수정하면 안 되는 것들

## 1. 핵심 아키텍처
- ❌ 비동기 함수 (`async def`, `await`) 구조 변경
- ❌ Class 상속 구조 변경
- ❌ 모듈 import 순서 변경

## 2. 외부 의존성
- ❌ Python 버전 변경 (3.11.9 고정)
- ❌ Playwright 버전 임의 변경
- ❌ requirements.txt 임의 수정

## 3. 보안 관련
- ❌ env.user 파일을 git에 커밋
- ❌ API 키를 코드에 하드코딩
- ❌ 비밀번호를 평문으로 저장

## 4. 데이터 무결성
- ❌ Excel/CSV 파일 구조(컬럼 순서) 변경
- ❌ JSON 결과 파일 스키마 변경

## 수정 가능한 것들

## 1. 설정값 (Safe)
- ✅ 타임아웃 값 (timeout=60)
- ✅ URL 주소
- ✅ 파일 경로
- ✅ 로그 메시지
- ✅ 국가 코드 리스트

## 2. CSS 선택자 (주의)
- ✅ 선택자 문자열 교체
- ⚠️ 선택자 검증 필요 (브라우저 개발자도구)

## 3. 조건문 (주의)
- ✅ 단순 비교값 변경 (if x > 10 → if x > 20)
- ⚠️ 복잡한 조건 추가는 AI와 상의

## 4. 프롬프트 (매우 Safe)
- ✅ smartthings-logic의 .md 프롬프트 파일
- ✅ 로직 설명 텍스트 수정
```

---

## Phase 2: 변경 요청 프로세스 (Change Request Process)

### 2.1 변경 요청 템플릿

비개발자가 작성하는 표준 양식:

```markdown
# 변경 요청서 (Change Request)

## 1. 기본 정보
- **요청자**: [이름]
- **날짜**: [YYYY-MM-DD]
- **프로젝트**: [01.smartThings / 02.ENH/gnb / 02.ENH/pd / ...]
- **우선순위**: [High / Medium / Low]

## 2. 변경 이유
[왜 이 변경이 필요한가?]

예) 웹사이트가 리뉴얼되어 버튼 클래스가 변경됨

## 3. 구체적 변경 내용
[무엇을 어떻게 바꾸고 싶은가?]

예) "장바구니에 담기" 버튼의 CSS 선택자를 .old-cart-button에서 .new-cart-btn으로 변경

## 4. 예상 영향 범위
- [ ] 설정 파일만 수정
- [ ] 1개 파일 수정
- [ ] 여러 파일 수정
- [ ] 모르겠음 (AI 분석 필요)

## 5. 긴급도
- [ ] 즉시 필요 (프로덕션 오류)
- [ ] 이번 주 내
- [ ] 여유 있음

## 6. 첨부 자료
- 스크린샷
- 에러 로그
- 관련 문서
```

### 2.2 AI 복잡도 분석 프로세스

```markdown
# Step 1: AI에게 복잡도 평가 요청

[Cursor/Claude/ChatGPT에 입력]
"""
@CLAUDE.md
@CHANGE-COMPLEXITY-MATRIX.md
@PROJECT-CONSTRAINTS.md
@{변경할_파일.py}

다음 변경 요청을 평가해줘:

[변경 요청서 내용 붙여넣기]

다음 형식으로 답변해줘:
1. 복잡도 분류: 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH
2. 판단 근거: [이유]
3. 변경할 파일 목록: [파일1, 파일2, ...]
4. 예상 소요 시간: [시간]
5. 위험 요소: [있다면]
6. 권장 사항: [비개발자 진행 가능 / 개발자 리뷰 필요 / 개발자 필수]
"""

# Step 2: 결과에 따른 의사결정

## 🟢 LOW → 비개발자 진행
- AI 가이드 받아 직접 수정
- 테스트 후 완료

## 🟡 MEDIUM → AI + 개발자 리뷰
- AI 가이드로 수정
- 개발자에게 코드 리뷰 요청
- 승인 후 적용

## 🔴 HIGH → 개발자 필수
- 개발자에게 요청서 전달
- 개발자가 구현
- 비개발자는 테스트 참여
```

---

## Phase 3: 구현 프로세스 (Implementation Process)

### 3.1 비개발자 구현 절차 (LOW/MEDIUM)

```markdown
# 단계별 구현 가이드

## Step 1: 환경 준비
1. Git에서 현재 상태 커밋 (되돌리기 위해)
   ```bash
   git add .
   git commit -m "변경 전 백업"
   ```

2. 백업 브랜치 생성 (선택사항)
   ```bash
   git checkout -b backup-{날짜}
   git checkout main
   ```

## Step 2: AI와 함께 수정

[Cursor/Claude에 입력]
"""
@CLAUDE.md
@EXAMPLES.md
@{수정할_파일.py}

다음을 단계별로 구현해줘. 각 단계마다 멈춰서 내가 확인할 수 있게 해줘:

[변경 내용]

각 단계에서:
1. 어떤 파일의 어느 라인을 수정할지
2. 원래 코드 → 수정 코드
3. 왜 이렇게 수정하는지
4. 테스트 방법
"""

## Step 3: 단계별 검증

### 변경 후 즉시 검증
```bash
# 문법 오류 체크
python -m py_compile {수정한_파일.py}

# 성공하면 → OK
# 오류 나면 → AI에게 오류 메시지 보여주고 수정 요청
```

### 기능 테스트
- TESTING-CHECKLIST.md 참고하여 테스트
- 1개 항목으로 작게 테스트 먼저

## Step 4: 문제 발생 시 Rollback

```bash
# 방법 1: Git으로 되돌리기
git checkout {파일명}

# 방법 2: 전체 되돌리기
git reset --hard HEAD

# 방법 3: 백업 브랜치로 돌아가기
git checkout backup-{날짜}
```

## Step 5: 성공 시 문서화

EXAMPLES.md에 추가:
"""
# 성공 사례 X: [제목]
**날짜**: {YYYY-MM-DD}
**수정자**: {이름}
**문제**: {문제 설명}
**해결**: {해결 방법}
**수정 파일**: {파일명}:{라인}
**난이도**: 🟢 LOW / 🟡 MEDIUM
**AI 프롬프트**: "{사용한 프롬프트}"
**소요 시간**: {시간}
"""
```

### 3.2 개발자 리뷰 요청 프로세스 (MEDIUM)

```markdown
# 개발자 리뷰 요청 양식

**요청자**: [이름]
**날짜**: [YYYY-MM-DD]
**변경 파일**: [파일 목록]

## 변경 내용
[수정한 코드의 diff 또는 스크린샷]

## AI 분석 결과
- 복잡도: 🟡 MEDIUM
- 예상 위험: [AI가 제시한 위험 요소]

## 테스트 결과
- [ ] 문법 오류 없음
- [ ] 1회 실행 성공
- [ ] 결과 파일 정상 생성
- [ ] 기존 기능 영향 없음 (확인한 범위 내)

## 리뷰 요청 사항
- 코드 품질 확인
- 예상치 못한 부작용 확인
- 더 나은 방법 제안

## 첨부
- 수정 전/후 코드 비교
- 테스트 결과 파일
- 에러 로그 (있다면)
```

---

## Phase 4: 표준화된 프로젝트 구조 (Standardization)

### 4.1 모든 프로젝트에 포함되어야 할 파일

```
project-root/
├── README.md                           # 일반 사용자용 설명서
├── CLAUDE.md                          # AI Context (필수)
├── CHANGE-COMPLEXITY-MATRIX.md        # 복잡도 분류 (필수)
├── EXAMPLES.md                        # 수정 사례집 (필수)
├── AI-PROMPTS.md                      # 검증된 프롬프트 (필수)
├── TESTING-CHECKLIST.md               # 테스트 체크리스트 (필수)
├── PROJECT-CONSTRAINTS.md             # 제약사항 (필수)
├── env.user.sample                    # 설정 파일 샘플
├── requirements.txt                   # 의존성
└── .ai/                               # AI 관련 파일 폴더
    ├── complexity-analyzer-prompt.md  # 복잡도 분석 전용 프롬프트
    └── implementation-guide.md        # 구현 가이드 프롬프트
```

### 4.2 프로젝트 인수인계 체크리스트

개발자가 프로젝트 완료 시 확인할 항목:

```markdown
# 인수인계 체크리스트

## 문서 작성 완료
- [ ] CLAUDE.md 작성 (프로젝트 개요, 아키텍처, 명령어)
- [ ] CHANGE-COMPLEXITY-MATRIX.md 작성 (LOW/MEDIUM/HIGH 분류)
- [ ] EXAMPLES.md 작성 (최소 3개 이상의 예시)
- [ ] AI-PROMPTS.md 작성 (검증된 프롬프트 템플릿)
- [ ] TESTING-CHECKLIST.md 작성 (프로젝트 특화 테스트)
- [ ] PROJECT-CONSTRAINTS.md 작성 (절대 금지 사항)

## 코드 품질
- [ ] 모든 함수에 주석 (한글 또는 영어)
- [ ] 복잡한 로직은 설명 주석 추가
- [ ] 매직 넘버 제거 (상수로 변환)
- [ ] 하드코딩된 값을 설정 파일로 이동

## 환경 설정
- [ ] env.user.sample 파일 제공
- [ ] requirements.txt 정확성 확인
- [ ] Python 버전 명시 (README.md)

## 테스트
- [ ] 전체 기능 1회 이상 실행 성공
- [ ] 주요 시나리오별 테스트 케이스 문서화
- [ ] 에러 발생 시 복구 방법 문서화

## 인수인계 교육
- [ ] 비개발자에게 실행 데모 (1회)
- [ ] AI 도구 사용 방법 안내
- [ ] 변경 요청 프로세스 안내
- [ ] 긴급 연락처 공유

## 유지보수 지원
- [ ] 초기 1개월간 주 1회 체크인 계획
- [ ] Slack/Teams 채널 생성 (질문 채널)
- [ ] FAQ 문서 준비
```

---

## Phase 5: AI Agent 설계 (Complexity Analyzer Agent)

### 5.1 Agent Prompt Template

```markdown
# Complexity Analyzer Agent

You are an expert code complexity analyzer for web automation projects. Your role is to help non-technical users understand if they can safely modify code with AI assistance.

## Your Analysis Framework

### Input Documents (Always Read First)
1. CLAUDE.md - Project architecture
2. CHANGE-COMPLEXITY-MATRIX.md - Complexity classification rules
3. PROJECT-CONSTRAINTS.md - What must never be changed
4. The specific file(s) user wants to modify

### Classification Criteria

#### 🟢 LOW Complexity (Non-technical can do alone)
- Configuration value changes (timeouts, URLs, paths)
- Data file modifications (CSV, Excel, JSON data)
- Prompt text changes (.md files)
- Log message changes
- Simple CSS selector replacements (one-to-one swap)
- Comment additions

**Confidence**: User can proceed with AI guidance

#### 🟡 MEDIUM Complexity (AI + Developer Review)
- Adding new validation items (copy existing patterns)
- Simple conditional logic changes (if/else with clear conditions)
- Adding new countries/site codes to lists
- Adding error message handling
- Multiple CSS selector changes
- Loop iteration changes

**Confidence**: User can implement with AI, but needs developer review before production

#### 🔴 HIGH Complexity (Developer Required)
- Async/await logic modifications
- API endpoint changes
- Complex algorithm changes (multi-stage logic)
- Database operations
- Architecture changes
- Dependency upgrades
- Security-related changes
- Error handling strategy changes
- Class inheritance modifications

**Confidence**: Must involve developer

### Your Output Format

When user asks about a change, respond with:

"""
## 📊 Complexity Analysis

**Classification**: 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH

**Reasoning**:
[Explain why this classification in 2-3 sentences]

**Files to Modify**:
- file1.py (lines 45-47)
- file2.py (lines 120-125)

**Estimated Time**: [time estimate]

**Risk Level**: Low / Medium / High
**Risks**:
- [Risk 1 if any]
- [Risk 2 if any]

**Recommendation**:
[One of:]
- ✅ Safe for you to proceed with AI guidance
- ⚠️ You can do it, but request developer review before production
- ❌ Please request developer assistance

**Next Steps**:
[If LOW/MEDIUM: provide step-by-step plan]
[If HIGH: suggest contacting developer with specific details]
"""

### Safety Checks

Before classifying as LOW or MEDIUM, verify:
1. ❌ Does NOT modify async/await patterns → If yes, → HIGH
2. ❌ Does NOT change API contracts → If yes, → HIGH
3. ❌ Does NOT alter security logic → If yes, → HIGH
4. ❌ Does NOT change core algorithms → If yes, → HIGH
5. ❌ Does NOT modify class structures → If yes, → HIGH

If ANY check fails → Automatically HIGH

### Example Analyses

#### Example 1: Timeout Change
"""
User: "I want to change timeout from 60 to 90 seconds"

📊 Complexity Analysis
Classification: 🟢 LOW
Reasoning: Simple numeric constant change with no logic impact
Files: main.py (line 145)
Estimated Time: 2 minutes
Risk Level: Low
Recommendation: ✅ Safe to proceed
Next Steps:
1. Find: `timeout=60`
2. Replace: `timeout=90`
3. Test with 1 URL
"""

#### Example 2: Adding New Validation
"""
User: "I want to add a new check for button visibility"

📊 Complexity Analysis
Classification: 🟡 MEDIUM
Reasoning: Follows existing pattern but adds new logic flow
Files: validator.py (add ~10 lines), main.py (add 1 call)
Estimated Time: 30 minutes
Risk Level: Medium
Risks:
- May affect execution flow
- Need to handle new error cases
Recommendation: ⚠️ Proceed with AI, then request review
Next Steps:
1. Copy existing visibility check pattern
2. Modify selector
3. Add to validation sequence
4. Test thoroughly
5. Request developer review
"""

#### Example 3: Async Logic Change
"""
User: "I want to change the order of API calls"

📊 Complexity Analysis
Classification: 🔴 HIGH
Reasoning: Involves async/await execution order - can cause deadlocks or race conditions
Files: response_handler.py (async functions)
Risk Level: High
Risks:
- Deadlock potential
- Race conditions
- Data inconsistency
Recommendation: ❌ Developer assistance required
Next Steps:
Please contact developer with:
- Which API calls you want to reorder
- Why the change is needed
- Expected behavior
"""

## Special Instructions

1. **Always be conservative** - When in doubt between two levels, choose the higher complexity
2. **Consider blast radius** - If change affects multiple modules → increase complexity
3. **Think about rollback** - If difficult to rollback → increase complexity
4. **Check project constraints** - If violates PROJECT-CONSTRAINTS.md → HIGH + reject
5. **Provide learning** - Explain WHY, not just WHAT, so user learns for next time

## Confidence Scoring

Include a confidence score:
- 95-100%: Very confident in classification
- 80-94%: Confident, but user should review reasoning
- <80%: Uncertain, recommend developer consultation regardless of classification
```

### 5.2 Implementation Guide Agent Prompt

```markdown
# Implementation Guide Agent

You are a patient, step-by-step coding instructor for non-technical users modifying web automation code.

## Your Role

Help users implement changes classified as 🟢 LOW or 🟡 MEDIUM complexity. Break down changes into tiny, verifiable steps.

## Your Teaching Principles

1. **One step at a time** - Wait for user confirmation before next step
2. **Show before/after** - Always show original code and modified code
3. **Explain why** - Help user understand, not just copy-paste
4. **Test frequently** - After each significant change
5. **Safety first** - Remind about backups and rollback

## Your Output Format

"""
## 📝 Step-by-Step Implementation Guide

**Total Steps**: [number]
**Estimated Time**: [time]

---

### Step 1: Backup Current State

Before making any changes:
```bash
# Run this command in terminal
git add .
git commit -m "Before: [change description]"
```

Why: This creates a restore point if something goes wrong.

**After running, reply "Done" to continue**

---

### Step 2: Open File

Open file: `{filepath}`

Look for line {line_number}:
```python
# Original code (what you'll see):
{original_code}
```

**Reply "Found it" when you locate this code**

---

### Step 3: Make Change

**Replace** this:
```python
{original_code}
```

**With** this:
```python
{new_code}
```

**Why**: {explanation of what this does and why}

**After editing, reply "Changed" to continue**

---

### Step 4: Verify Syntax

Run this command to check for errors:
```bash
python -m py_compile {filepath}
```

**If no output** → ✅ Success, reply "OK"
**If error appears** → ❌ Copy the error and send it to me

---

### Step 5: Test Run

Run a small test:
```bash
{test_command}
```

**Expected result**:
- [Expected outcome 1]
- [Expected outcome 2]

**Reply "Test passed" if you see this**

---

### Step 6: [Continue with more steps...]

---

## 🚨 If Something Goes Wrong

### Rollback to previous state:
```bash
git checkout {filepath}
```

This will undo all changes to the file.

### Get help:
Send me:
1. Which step you're on
2. What you see vs. what you expected
3. Any error messages (full text)
"""

## Safety Reminders

Include these reminders at appropriate points:
- "💾 Remember: You can always undo with `git checkout {file}`"
- "🧪 Test with just 1 item first before running on all data"
- "📸 Take a screenshot of the working state for reference"
- "⏸️ Take a break if you're stuck - it's okay to ask for help"

## Troubleshooting Guidance

When user reports an error:

"""
## 🔍 Debugging Help

**Error Type**: {classify the error}

**What this means**: {simple explanation}

**Most likely cause**: {probable cause}

**Let's try these fixes in order**:

1. First, try: {simplest fix}
   ```bash
   {command}
   ```

2. If that doesn't work, try: {next fix}
   ```bash
   {command}
   ```

3. If still stuck: This might be beyond our scope. Let's contact the developer with these details:
   - Error message: {error}
   - What you were trying to do: {context}
   - What you changed: {changes}
"""

## Code Review Mode

After user completes changes, offer review:

"""
## ✅ Final Review Checklist

Let's verify your changes are solid:

**1. Code Correctness**
- [ ] No syntax errors: `python -m py_compile {file}`
- [ ] File still has all required functions
- [ ] Indentation looks correct

**2. Functionality**
- [ ] Test run completed successfully
- [ ] Output files generated
- [ ] No error messages in console

**3. Comparison**
- [ ] Compare output with previous run
- [ ] Verify the change had intended effect
- [ ] No unexpected side effects

**4. Documentation**
- [ ] Add your success to EXAMPLES.md
- [ ] Note any gotchas you discovered

**5. Cleanup**
- [ ] Commit your changes: `git commit -m "{description}"`
- [ ] Remove backup files if any

[If 🟡 MEDIUM] **6. Request Review**
- [ ] Create review request using template
- [ ] Send to developer with test results
"""
```

---

## Phase 6: 교육 프로그램 (Training Program)

### 6.1 비개발자를 위한 초기 교육 커리큘럼

```markdown
# 비개발자 자가 유지보수 교육 프로그램 (4주 과정)

## Week 1: 기초 다지기

### Day 1-2: 환경 설정
- [ ] Python 설치 확인
- [ ] 가상환경 개념 이해
- [ ] Git 기초 (commit, checkout)
- [ ] 프로젝트 실행해보기

### Day 3-4: 문서 읽기
- [ ] CLAUDE.md 읽고 프로젝트 구조 이해
- [ ] CHANGE-COMPLEXITY-MATRIX.md로 수정 유형 학습
- [ ] EXAMPLES.md의 성공/실패 사례 학습

### Day 5: AI 도구 사용법
- [ ] Claude/ChatGPT/Cursor 기본 사용법
- [ ] Context 파일 제공 방법 (@파일명)
- [ ] 프롬프트 작성 연습

## Week 2: 간단한 수정 실습 (🟢 LOW)

### Day 1: 설정값 변경
- **실습**: 타임아웃 60→90초 변경
- **목표**: 숫자 상수 변경 익히기
- **AI 프롬프트 연습**

### Day 2: CSS 선택자 변경
- **실습**: 버튼 선택자 변경 (.old → .new)
- **목표**: 브라우저 개발자도구로 선택자 찾기
- **검증 방법 학습**

### Day 3: URL 변경
- **실습**: 테스트 URL 변경
- **목표**: 문자열 치환 익히기

### Day 4: 로그 메시지 추가
- **실습**: print 문 추가하여 디버깅
- **목표**: 코드 흐름 이해

### Day 5: 종합 실습
- **실습**: 위 변경사항 통합 적용
- **목표**: 백업→수정→테스트→커밋 프로세스 완성

## Week 3: 중급 수정 도전 (🟡 MEDIUM)

### Day 1-2: 검증 항목 추가
- **실습**: 기존 검증 로직 복사하여 새 항목 추가
- **AI와 함께**: 패턴 분석 및 적용
- **개발자 리뷰**: 코드 리뷰 받기

### Day 3-4: 조건문 수정
- **실습**: if문 조건 변경
- **AI와 함께**: 조건 로직 이해
- **테스트**: 다양한 케이스 검증

### Day 5: 실패 경험
- **실습**: 의도적으로 잘못 수정하기
- **목표**: 에러 메시지 읽기, Rollback 연습

## Week 4: 실전 프로젝트

### Day 1-5: 실제 변경 요청 처리
- **미션**: 실제 업무에서 발생한 변경 요청 처리
- **프로세스**:
  1. 변경 요청서 작성
  2. AI 복잡도 분석
  3. 구현 (AI 가이드)
  4. 테스트
  5. 문서화 (EXAMPLES.md 추가)
  6. 개발자 리뷰 (MEDIUM인 경우)

## 수료 기준

- [ ] 🟢 LOW 난이도 3개 이상 독립적으로 완수
- [ ] 🟡 MEDIUM 난이도 1개 이상 (개발자 리뷰 포함) 완수
- [ ] Git 사용 능숙 (commit, checkout, diff)
- [ ] AI 도구로 복잡도 판단 가능
- [ ] 문제 발생 시 rollback 가능
- [ ] EXAMPLES.md에 자신의 사례 3개 이상 등록
```

---

## Phase 7: 위험 관리 및 품질 보증 (Risk Management)

### 7.1 변경 전 위험 평가 체크리스트

```markdown
# 변경 위험 평가 (Change Risk Assessment)

## 변경 범위 (Scope)
- [ ] 1개 파일만 수정 → Low Risk
- [ ] 2-3개 파일 수정 → Medium Risk
- [ ] 4개 이상 파일 수정 → High Risk → 개발자 필수

## 영향 범위 (Impact)
- [ ] 설정값만 변경 → Low Impact
- [ ] 로직 추가/수정 → Medium Impact
- [ ] 핵심 알고리즘 변경 → High Impact → 개발자 필수

## 복구 난이도 (Recovery)
- [ ] Git checkout으로 즉시 복구 가능 → Low Risk
- [ ] 데이터 파일 복구 필요 → Medium Risk
- [ ] DB/외부 시스템 영향 → High Risk → 개발자 필수

## 테스트 커버리지 (Testing)
- [ ] 자동화된 테스트 있음 → Low Risk
- [ ] 수동 테스트 가능 → Medium Risk
- [ ] 테스트 방법 불명확 → High Risk → 개발자 상담

## 긴급도 vs 복잡도 매트릭스

|              | 🟢 LOW     | 🟡 MEDIUM         | 🔴 HIGH           |
|--------------|-----------|-------------------|-------------------|
| **긴급**     | 직접 수정  | AI+빠른리뷰       | 개발자 우선 배정   |
| **보통**     | 직접 수정  | AI+정규리뷰       | 개발자 스케줄     |
| **여유**     | 직접 수정  | 학습 기회로 활용   | 개발자 계획 작업  |
```

### 7.2 품질 게이트 (Quality Gates)

```markdown
# 변경 사항 적용 전 필수 통과 기준

## Gate 1: 문법 검증 (Syntax Validation)
```bash
python -m py_compile {모든_수정된_파일.py}
```
- ✅ Pass: 에러 없음
- ❌ Fail: 에러 발생 → 수정 필요

## Gate 2: 기능 테스트 (Functional Testing)
- ✅ Pass: 1개 항목으로 전체 프로세스 성공
- ❌ Fail: 에러 발생 → 원인 분석 필요

## Gate 3: 비교 검증 (Comparison Testing)
- ✅ Pass: 수정 전/후 결과 비교하여 의도한 변경만 발생
- ❌ Fail: 예상치 못한 변경 발생 → 부작용 분석

## Gate 4: 문서화 (Documentation)
- ✅ Pass: EXAMPLES.md에 변경 사항 기록
- ❌ Fail: 문서 미작성 → 완료로 인정 안 됨

## Gate 5: 리뷰 (Review) - MEDIUM 이상
- ✅ Pass: 개발자 승인
- ❌ Fail: 개발자 수정 요청 → 재작업
```

---

## Phase 8: 지속적 개선 (Continuous Improvement)

### 8.1 월간 회고 (Monthly Retrospective)

```markdown
# 월간 자가 유지보수 회고

**날짜**: YYYY-MM

## 통계
- 총 변경 요청: {N}개
- 직접 완료 (🟢 LOW): {N}개
- AI+리뷰 (🟡 MEDIUM): {N}개
- 개발자 의뢰 (🔴 HIGH): {N}개
- 성공률: {N}%

## 잘한 점 (What Went Well)
-

## 어려웠던 점 (Challenges)
-

## 배운 점 (Learnings)
-

## 다음 달 목표 (Next Month Goals)
-

## 문서 업데이트 필요 사항
- EXAMPLES.md에 추가할 사례:
- AI-PROMPTS.md에 추가할 프롬프트:
- CHANGE-COMPLEXITY-MATRIX.md 수정 필요:
```

### 8.2 EXAMPLES.md 지속적 확장

매월 최소 2개 이상의 새로운 성공/실패 사례 추가:
- 비개발자들이 겪은 실제 문제
- AI와의 대화 로그 샘플
- 해결 과정
- 시행착오
- 최종 해결책

### 8.3 AI 프롬프트 라이브러리 확장

검증된 프롬프트를 계속 추가:
- 프로젝트 특화 프롬프트
- 자주 발생하는 오류 해결 프롬프트
- 성공률 높은 프롬프트 패턴

---

## 부록 A: 긴급 상황 대응 (Emergency Response)

### 프로덕션 오류 발생 시

```markdown
# 긴급 대응 절차 (Production Issue Response)

## Step 1: 즉시 Rollback (3분 내)
```bash
# 마지막 작동하던 버전으로 복구
git log --oneline  # 마지막 작동 커밋 찾기
git checkout {작동하던_커밋_해시}
```

## Step 2: 개발자에게 즉시 연락 (5분 내)
**연락 사항**:
- 언제부터 오류 발생
- 어떤 오류 (에러 메시지 전문)
- 마지막으로 한 변경 사항
- 현재 rollback 완료 여부

## Step 3: 로그 수집
- 에러 로그 전체 저장
- 스크린샷 캡처
- 재현 가능하면 재현 방법 기록

## Step 4: 사후 분석
- 왜 발생했는지
- 어떻게 방지할 수 있었는지
- 문서에 추가할 교훈
```

---

## 부록 B: 타 프로젝트 적용 체크리스트

### 새 프로젝트에 이 SOP 적용하기

```markdown
# 새 프로젝트 SOP 적용 체크리스트

## 1. 문서 생성 (개발자)
- [ ] CLAUDE.md 작성 (템플릿 사용)
- [ ] CHANGE-COMPLEXITY-MATRIX.md 작성 (프로젝트 맞춤)
- [ ] EXAMPLES.md 작성 (초기 3개 예시)
- [ ] AI-PROMPTS.md 작성 (기본 템플릿 복사)
- [ ] TESTING-CHECKLIST.md 작성 (프로젝트 특화)
- [ ] PROJECT-CONSTRAINTS.md 작성 (금지사항 명시)

## 2. 코드 정리 (개발자)
- [ ] 주석 추가 (비개발자가 읽을 수 있게)
- [ ] 매직 넘버 → 상수화
- [ ] 하드코딩 → 설정 파일화
- [ ] 복잡한 함수 분리 (단일 책임)

## 3. 테스트 (개발자)
- [ ] Happy path 테스트 케이스
- [ ] Edge case 테스트 케이스
- [ ] Rollback 시나리오 테스트

## 4. 인수인계 (개발자 → 비개발자)
- [ ] 1회 실행 데모
- [ ] 문서 설명 (30분)
- [ ] AI 도구 사용 실습 (30분)
- [ ] 간단한 수정 실습 (1시간)

## 5. 초기 지원 (개발자)
- [ ] 1주차: 매일 체크인
- [ ] 2주차: 격일 체크인
- [ ] 3-4주차: 주 2회 체크인
- [ ] 1개월 후: 주 1회 체크인

## 6. 독립 확인
- [ ] 비개발자가 🟢 LOW 3회 성공
- [ ] 비개발자가 🟡 MEDIUM 1회 성공 (리뷰 포함)
- [ ] 긴급 상황 대응 훈련 완료
```

---

## 부록 C: AI 도구별 활용 전략

### Cursor
- **강점**: 코드베이스 전체 컨텍스트, 멀티파일 편집
- **용도**: 복잡한 수정, 패턴 찾기, 리팩토링

### Claude (claude.ai)
- **강점**: 긴 문서 분석, 상세한 설명, 단계별 가이드
- **용도**: 복잡도 분석, 학습, 문서 작성

### ChatGPT
- **강점**: 빠른 응답, 코드 스니펫
- **용도**: 빠른 질문, 에러 메시지 해석, 간단한 수정

### 추천 워크플로우
1. **복잡도 분석**: Claude (긴 컨텍스트 분석)
2. **구현**: Cursor (코드 편집)
3. **디버깅**: ChatGPT (빠른 오류 해결)
4. **문서화**: Claude (상세한 설명)

---

## 결론

이 SOP는 **살아있는 문서(Living Document)**입니다.

- 매월 업데이트
- 새로운 사례 추가
- 비개발자 피드백 반영
- AI 도구 발전에 따른 개선

**핵심 원칙**:
1. **안전 우선** - 항상 백업, 항상 테스트
2. **작게 시작** - 한 번에 하나씩
3. **배우며 성장** - 실수는 학습 기회
4. **문서화** - 다음 사람을 위해
5. **협력** - 개발자와 비개발자의 파트너십
