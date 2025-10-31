# AI-Assisted Maintenance System

## 문서 체계 (Document Architecture)

이 시스템은 **2-Level 구조**로 구성되어 있습니다:

```
.ai-maintenance/                    # L0: 메타 문서 (범용, 모든 프로젝트 공통)
├── README.md                       # 이 파일 - 시스템 개요
├── L0-WORKFLOW-MASTER.md          # 표준 워크플로우 정의
├── L0-DOCUMENT-INDEX.md           # 모든 문서의 인덱스 및 사용법
├── L0-HANDOFF-CHECKLIST.md        # 개발자 인수인계 체크리스트
└── templates/                      # 템플릿 폴더
    ├── TEMPLATE-CLAUDE.md
    ├── TEMPLATE-COMPLEXITY-MATRIX.md
    ├── TEMPLATE-EXAMPLES.md
    ├── TEMPLATE-AI-PROMPTS.md
    ├── TEMPLATE-CONSTRAINTS.md
    └── TEMPLATE-TESTING.md

(프로젝트 루트)/                   # L1: 프로젝트별 실행 문서
├── L1-CLAUDE.md                   # 프로젝트 AI Context
├── L1-COMPLEXITY-MATRIX.md        # 프로젝트별 복잡도 기준
├── L1-CONSTRAINTS.md              # 프로젝트별 제약사항
├── L1-TESTING.md                  # 프로젝트별 테스트 절차
├── L2-EXAMPLES.md                 # 살아있는 사례집 (계속 업데이트)
└── L2-PROMPTS.md                  # 검증된 프롬프트 (계속 업데이트)
```

---

## 문서 레벨 정의

### L0: Meta Documents (메타 문서)
**특성**:
- 범용적, 프로젝트 독립적
- 프로세스, 워크플로우, 방법론 정의
- **거의 변경되지 않음**
- 모든 프로젝트에서 재사용

**역할**:
- "어떻게 할 것인가"의 정의
- 표준 절차 제공
- 체크리스트 제공

**소유자**: 프로세스 관리자 / 아키텍트

---

### L1: Project Documents (프로젝트 문서)
**특성**:
- 프로젝트별로 커스터마이징
- L0 템플릿을 복사하여 작성
- **초기 작성 후 가끔 업데이트**
- 프로젝트 특화 정보

**역할**:
- "이 프로젝트에서는 무엇인가"의 정의
- 프로젝트 특화 규칙
- AI Context 제공

**소유자**: 개발자 (초기 작성) → 비개발자 (유지보수)

---

### L2: Living Documents (살아있는 문서)
**특성**:
- 지속적으로 업데이트
- 사용하면서 계속 풍부해짐
- **매주/매월 변경됨**
- 경험과 지식의 축적

**역할**:
- 실제 사례 기록
- 검증된 방법 축적
- 팀 학습의 결과물

**소유자**: 비개발자 (주 작성자) + 개발자 (리뷰)

---

## 사용자별 문서 매핑

### 👨‍💻 개발자 (Developer)

#### 개발 완료 시 작성 필수 (L1)
| 문서 | 작업 | 소요 시간 | 템플릿 |
|------|------|----------|--------|
| L1-CLAUDE.md | 프로젝트 개요, 아키텍처, 명령어 | 1-2시간 | L0 템플릿 |
| L1-COMPLEXITY-MATRIX.md | 프로젝트별 난이도 기준 | 1시간 | L0 템플릿 |
| L1-CONSTRAINTS.md | 절대 금지/주의 사항 | 1시간 | L0 템플릿 |
| L1-TESTING.md | 테스트 절차, 체크리스트 | 1-2시간 | L0 템플릿 |
| L2-EXAMPLES.md | 초기 3-5개 예시 | 2시간 | L0 템플릿 |
| L2-PROMPTS.md | 기본 프롬프트 | 30분 | L0 템플릿 |

**총 소요 시간**: 6-8시간 (1-2일)

#### 인수인계 시 (L0 참고)
| 문서 | 용도 |
|------|------|
| L0-HANDOFF-CHECKLIST.md | 인수인계 항목 확인 |
| L0-WORKFLOW-MASTER.md | 비개발자에게 프로세스 설명 |

---

### 👤 비개발자 (Non-Technical Maintainer)

#### 수정 작업 시 참고 (L1)
| 문서 | 사용 시점 | 필수도 |
|------|----------|--------|
| L1-CLAUDE.md | 항상 (AI에 제공) | ⭐⭐⭐ |
| L1-COMPLEXITY-MATRIX.md | 난이도 판단 시 | ⭐⭐⭐ |
| L1-CONSTRAINTS.md | 수정 전 확인 | ⭐⭐⭐ |
| L1-TESTING.md | 수정 후 테스트 | ⭐⭐⭐ |
| L2-EXAMPLES.md | 유사 사례 참고 | ⭐⭐ |
| L2-PROMPTS.md | AI 사용 시 | ⭐⭐ |

#### 학습 시 참고 (L0)
| 문서 | 용도 |
|------|------|
| L0-WORKFLOW-MASTER.md | 전체 프로세스 이해 |
| L0-DOCUMENT-INDEX.md | 문서 찾기 |

#### 지속 업데이트 (L2)
| 문서 | 업데이트 시점 | 빈도 |
|------|-------------|------|
| L2-EXAMPLES.md | 작업 완료 후 | 매 작업마다 |
| L2-PROMPTS.md | 좋은 프롬프트 발견 시 | 주 1-2회 |

---

### 🤖 AI (Claude/ChatGPT/Cursor)

#### AI에게 제공할 Context (@파일명)

**기본 Context (항상 제공)**:
```
@L1-CLAUDE.md
```

**작업별 추가 Context**:

| 작업 단계 | 추가 문서 |
|----------|----------|
| 1. 복잡도 평가 | @L1-COMPLEXITY-MATRIX.md<br>@L1-CONSTRAINTS.md |
| 2. 구현 계획 | @L1-COMPLEXITY-MATRIX.md<br>@L2-EXAMPLES.md |
| 3. 코드 수정 | @[수정할_파일.py]<br>@L2-EXAMPLES.md |
| 4. 코드 리뷰 | @L1-CONSTRAINTS.md<br>@[수정한_파일.py] |
| 5. 테스트 계획 | @L1-TESTING.md |
| 6. 에러 디버깅 | @[에러_파일.py]<br>@L2-EXAMPLES.md |

**프롬프트 구조 (표준)**:
```
[Step X: {작업명}]

[Context Files]
@L1-CLAUDE.md
@L1-COMPLEXITY-MATRIX.md
@{기타_필요_파일}

[Request]
{구체적_요청}

[Output Format]
{원하는_출력_형식}
```

---

## 정형화된 워크플로우

### 🔄 5단계 표준 프로세스

```
┌─────────────────────────────────────────────────────────────┐
│  Step 0: 준비 (Preparation)                                 │
│  - Git backup                                               │
│  - 문서: L0-WORKFLOW-MASTER.md                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 복잡도 평가 (Complexity Analysis)                  │
│  - 사용자: 비개발자                                          │
│  - AI: Claude/ChatGPT                                       │
│  - 문서: @L1-CLAUDE.md, @L1-COMPLEXITY-MATRIX.md           │
│  - 출력: 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
         ┌────────────────┼────────────────┐
         ↓                ↓                ↓
    🟢 LOW          🟡 MEDIUM         🔴 HIGH
         │                │                │
         │                │                └→ [개발자 요청]
         │                │                   - L0-HANDOFF 참고
         │                │
         ↓                ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: 구현 (Implementation)                              │
│  - 사용자: 비개발자                                          │
│  - AI: Cursor (코드 편집)                                    │
│  - 문서: @L1-CLAUDE.md, @L2-EXAMPLES.md, @코드파일          │
│  - 출력: 수정된 코드                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: 테스트 (Testing)                                   │
│  - 사용자: 비개발자                                          │
│  - 문서: L1-TESTING.md                                      │
│  - 출력: 테스트 결과 (Pass/Fail)                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
                  ┌───────┴───────┐
                  ↓               ↓
               PASS            FAIL
                  │               │
                  │               └→ [디버깅]
                  │                  - @L2-EXAMPLES.md
                  │                  - AI 에러 분석
                  ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: 리뷰 (Review) - MEDIUM만 해당                      │
│  - 사용자: 개발자                                            │
│  - 문서: L1-CONSTRAINTS.md                                  │
│  - 출력: 승인 / 수정 요청                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 5: 문서화 (Documentation)                             │
│  - 사용자: 비개발자                                          │
│  - 문서: L2-EXAMPLES.md (업데이트)                          │
│  - 출력: 새 사례 추가                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 문서 넘버링 시스템

### 파일명 규칙

```
{Level}-{Category}-{Version}.md

Level:
  - L0: Meta (프로세스 정의)
  - L1: Project (프로젝트별)
  - L2: Living (지속 업데이트)

Category:
  - CLAUDE: AI Context
  - COMPLEXITY: 복잡도 매트릭스
  - CONSTRAINTS: 제약사항
  - TESTING: 테스트
  - EXAMPLES: 사례집
  - PROMPTS: AI 프롬프트
  - WORKFLOW: 워크플로우
  - INDEX: 인덱스
  - HANDOFF: 인수인계

Version (optional):
  - v1, v2, v3...
```

### 문서 내부 섹션 넘버링

**L1 문서 구조**:
```markdown
# [문서명]

## Metadata
- Last Updated: YYYY-MM-DD
- Version: 1.0
- Owner: [이름]
- Status: Active / Deprecated

## 1. Overview
## 2. [주요 내용 1]
## 3. [주요 내용 2]
## 4. References
   - Related L0 Documents
   - Related L1 Documents
## 5. Changelog
```

**L2 문서 구조**:
```markdown
# [문서명]

## Metadata
- Started: YYYY-MM-DD
- Last Updated: YYYY-MM-DD
- Total Entries: N개
- Contributors: [이름들]

## Index
[자동 생성 목차]

## Entries

### Entry N: [제목]
- Date: YYYY-MM-DD
- Author: [이름]
- Complexity: 🟢/🟡/🔴
- Status: ✅/❌
[내용]

---

## Statistics
[월별/난이도별 통계]
```

---

## 빠른 시작 가이드

### 🎯 개발자: 새 프로젝트에 시스템 적용하기

```bash
# 1. 템플릿 복사
cp .ai-maintenance/templates/* .

# 2. 파일명 변경
mv TEMPLATE-CLAUDE.md L1-CLAUDE.md
mv TEMPLATE-COMPLEXITY-MATRIX.md L1-COMPLEXITY-MATRIX.md
# ... (나머지도 동일)

# 3. L0-HANDOFF-CHECKLIST.md 따라 문서 작성
# 4. 비개발자에게 L0-WORKFLOW-MASTER.md 설명
# 5. 초기 사례 3-5개 작성 (L2-EXAMPLES.md)
```

**소요 시간**: 6-8시간 (1-2일)

---

### 🎯 비개발자: 첫 수정 작업하기

```bash
# 1. L0-WORKFLOW-MASTER.md 읽기 (전체 프로세스 이해)
# 2. L0-DOCUMENT-INDEX.md 읽기 (문서 위치 파악)
# 3. 실제 작업 시작

# Step 0: 백업
git add .
git commit -m "변경 전 백업"

# Step 1: 복잡도 평가 (AI 사용)
# - @L1-CLAUDE.md
# - @L1-COMPLEXITY-MATRIX.md
# - 프롬프트: L2-PROMPTS.md의 "복잡도 평가" 템플릿 사용

# Step 2-5: 워크플로우 따라 진행
```

---

### 🎯 AI: 프롬프트 표준 형식

모든 AI 프롬프트는 다음 구조를 따릅니다:

```
[STEP-{N}: {작업명}]
[PROJECT: {프로젝트명}]
[USER: Developer / Non-Technical]
[COMPLEXITY: Unknown / LOW / MEDIUM / HIGH]

[CONTEXT FILES]
@L1-CLAUDE.md
@L1-COMPLEXITY-MATRIX.md
@{기타_파일}

[BACKGROUND]
{상황 설명}

[REQUEST]
{구체적 요청}

[OUTPUT FORMAT]
{원하는 형식}

[CONSTRAINTS]
- {제약사항 1}
- {제약사항 2}
```

---

## 문서 업데이트 주기

| Level | 문서 | 업데이트 주기 | 담당자 |
|-------|------|-------------|--------|
| L0 | WORKFLOW-MASTER | 분기별 | 프로세스 관리자 |
| L0 | DOCUMENT-INDEX | 수시 (문서 추가 시) | 프로세스 관리자 |
| L0 | HANDOFF-CHECKLIST | 반기별 | 프로세스 관리자 |
| L1 | CLAUDE | 주요 변경 시 | 개발자 |
| L1 | COMPLEXITY-MATRIX | 분기별 | 개발자 + 비개발자 |
| L1 | CONSTRAINTS | 반기별 | 개발자 |
| L1 | TESTING | 주요 변경 시 | 개발자 |
| L2 | EXAMPLES | 매 작업 후 | 비개발자 |
| L2 | PROMPTS | 주 1-2회 | 비개발자 |

---

## 버전 관리

### Git 구조

```
main
  ├── .ai-maintenance/          # L0 문서들 (거의 변경 없음)
  │   ├── README.md
  │   ├── L0-*.md
  │   └── templates/
  │
  ├── L1-*.md                   # L1 문서들 (가끔 변경)
  │
  ├── L2-*.md                   # L2 문서들 (자주 변경)
  │
  └── [프로젝트 코드]
```

### Commit 메시지 규칙

```
[L0] 워크플로우 개선: ...
[L1] CLAUDE.md 업데이트: ...
[L2] 사례 추가: 타임아웃 변경 성공
[CODE] 실제 코드 수정: ...
```

---

## 품질 관리

### 월간 회고 (L2 문서 점검)

**Agenda**:
1. L2-EXAMPLES.md 리뷰
   - 이번 달 추가된 사례: N개
   - 성공률: X%
   - 배운 점 공유

2. L2-PROMPTS.md 리뷰
   - 효과적인 프롬프트 선정
   - 비효과적인 프롬프트 개선

3. L1 문서 개선 필요 사항
   - COMPLEXITY-MATRIX 조정
   - CONSTRAINTS 추가

4. 다음 달 목표

---

## 확장 가능성

### 다른 프로젝트에 적용

```bash
# 1. .ai-maintenance 폴더 통째로 복사
cp -r ProjectA/.ai-maintenance ProjectB/

# 2. L1 템플릿 복사
cp .ai-maintenance/templates/* ProjectB/

# 3. ProjectB 특성에 맞게 L1 문서 커스터마이징

# 4. L2 문서 초기화 (빈 파일로 시작)
```

**재사용률**:
- L0: 100% (그대로 사용)
- L1: 70% (템플릿 + 커스터마이징)
- L2: 0% (새로 시작)

---

## 핵심 원칙

### 1. 문서는 계층적
- L0 → L1 → L2 순서로 읽기
- 상위 레벨이 하위 레벨을 가이드

### 2. 문서는 연결됨
- 각 문서는 다른 문서 참조
- "References" 섹션 필수

### 3. 문서는 살아있음
- L2는 계속 성장
- 월간 회고로 개선
- 팀의 지식 자산

### 4. 문서는 AI 친화적
- 명확한 구조
- 표준화된 형식
- Context로 제공 가능

---

## 성공 지표

### 정량적
- L2-EXAMPLES 월간 추가 개수: 목표 5개 이상
- 비개발자 성공률: 목표 80% 이상 (LOW+MEDIUM)
- 평균 해결 시간: 목표 1시간 이내 (LOW)

### 정성적
- 비개발자 자신감 향상
- 개발자 질문 빈도 감소
- 문서 품질 향상 (명확성, 완전성)

---

## 다음 단계

1. **즉시**: L0 문서들 작성 완료
2. **1일 이내**: L1 템플릿 검증
3. **1주 이내**: 첫 번째 프로젝트에 적용
4. **1개월 이내**: L2 문서 10개 사례 축적
5. **분기 말**: 다른 프로젝트에 확산

---

**이 시스템은 단순한 문서가 아니라, AI와 함께 일하는 팀의 운영 체제(OS)입니다.**
