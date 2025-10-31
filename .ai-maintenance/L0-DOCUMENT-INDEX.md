# L0-DOCUMENT-INDEX.md

**Version**: 1.0
**Last Updated**: 2024-01-31
**Status**: Active

---

## 문서 체계 한눈에 보기

```
📁 .ai-maintenance/                    [L0: 메타 문서]
│
├── 📄 README.md                       시스템 개요, 2-Level 구조 설명
├── 📄 L0-WORKFLOW-MASTER.md          ⭐ 5단계 워크플로우 정의
├── 📄 L0-DOCUMENT-INDEX.md           이 파일 - 문서 인덱스
├── 📄 L0-HANDOFF-CHECKLIST.md        개발자 인수인계 체크리스트
│
└── 📁 templates/                      템플릿 폴더
    ├── TEMPLATE-CLAUDE.md
    ├── TEMPLATE-COMPLEXITY-MATRIX.md
    ├── TEMPLATE-EXAMPLES.md
    ├── TEMPLATE-AI-PROMPTS.md
    ├── TEMPLATE-CONSTRAINTS.md
    └── TEMPLATE-TESTING.md

📁 (프로젝트 루트)/                    [L1: 프로젝트 문서]
│
├── 📄 L1-CLAUDE.md                   ⭐ AI Context (항상 제공)
├── 📄 L1-COMPLEXITY-MATRIX.md        ⭐ 복잡도 기준
├── 📄 L1-CONSTRAINTS.md              ⭐ 제약사항
├── 📄 L1-TESTING.md                  ⭐ 테스트 절차
│
├── 📄 L2-EXAMPLES.md                 ⭐ 사례집 (살아있는 문서)
├── 📄 L2-PROMPTS.md                  ⭐ 프롬프트 모음
│
└── 📁 change-requests/                변경 요청 기록
    ├── CR-YYYYMMDD-001-REQUEST.md
    ├── CR-YYYYMMDD-001-ANALYSIS.md
    ├── CR-YYYYMMDD-001-IMPLEMENTATION.md
    ├── CR-YYYYMMDD-001-TESTING.md
    ├── CR-YYYYMMDD-001-REVIEW-*.md
    └── completed/                     완료된 요청들
```

---

## 빠른 참조 (Quick Reference)

### "나는 지금 뭘 읽어야 하지?"

| 상황 | 읽을 문서 | 순서 |
|------|----------|------|
| **처음 시작** | README.md → L0-WORKFLOW-MASTER.md | 1→2 |
| **수정 작업 시작 전** | L0-WORKFLOW-MASTER.md (Step 0-1) | 1 |
| **복잡도 판단 시** | L1-COMPLEXITY-MATRIX.md | 1 |
| **수정 금지 사항 확인** | L1-CONSTRAINTS.md | 1 |
| **구현 중** | L2-EXAMPLES.md (유사 사례) | 1 |
| **테스트 시** | L1-TESTING.md | 1 |
| **AI 프롬프트 작성 시** | L2-PROMPTS.md | 1 |
| **개발자 인수인계** | L0-HANDOFF-CHECKLIST.md | 1 |

### "AI에게 뭘 줘야 하지?"

| 작업 단계 | 제공할 문서 (@) |
|----------|----------------|
| **복잡도 평가** | @L1-CLAUDE.md<br>@L1-COMPLEXITY-MATRIX.md<br>@L1-CONSTRAINTS.md |
| **구현 계획** | @L1-CLAUDE.md<br>@L2-EXAMPLES.md<br>@{수정할_파일} |
| **코드 리뷰** | @L1-CONSTRAINTS.md<br>@{수정한_파일} |
| **테스트 계획** | @L1-TESTING.md |
| **에러 디버깅** | @L1-CLAUDE.md<br>@{에러_파일}<br>@L2-EXAMPLES.md |

---

## L0 Documents (메타 문서)

### 📄 README.md
**위치**: `.ai-maintenance/README.md`
**레벨**: L0
**소유자**: 프로세스 관리자
**업데이트**: 분기별

**용도**:
- 전체 시스템 개요
- 2-Level 구조 설명
- 사용자별 문서 매핑
- 빠른 시작 가이드

**읽어야 할 때**:
- ✅ 처음 시스템 접할 때
- ✅ 전체 구조 이해가 필요할 때
- ✅ 다른 프로젝트에 적용할 때

**AI 제공**: ❌ 불필요

---

### 📄 L0-WORKFLOW-MASTER.md
**위치**: `.ai-maintenance/L0-WORKFLOW-MASTER.md`
**레벨**: L0
**소유자**: 프로세스 관리자
**업데이트**: 분기별

**용도**:
- ⭐ **가장 중요한 문서**
- 5단계 표준 워크플로우 정의
- 각 단계별 상세 절차
- 입출력, Gate Criteria

**읽어야 할 때**:
- ✅ 모든 작업 시작 전 (Step 0-1 참조)
- ✅ 막혔을 때 (어느 단계인지 확인)
- ✅ 프로세스 이해가 필요할 때

**AI 제공**: ⚠️ 선택적 (복잡도 평가 시 도움)

**핵심 섹션**:
- Step 0: 준비 (백업, 환경)
- Step 1: 복잡도 평가 ⭐
- Step 2: 구현 ⭐
- Step 3: 테스트 ⭐
- Step 4: 리뷰 (MEDIUM만)
- Step 5: 문서화

---

### 📄 L0-DOCUMENT-INDEX.md
**위치**: `.ai-maintenance/L0-DOCUMENT-INDEX.md`
**레벨**: L0
**소유자**: 프로세스 관리자
**업데이트**: 수시 (문서 추가 시)

**용도**:
- 이 문서 - 모든 문서의 인덱스
- "어디에 뭐가 있는지" 빠른 참조
- 문서별 용도, 사용 시점

**읽어야 할 때**:
- ✅ 문서를 찾을 때
- ✅ "어떤 문서를 읽어야 하지?" 궁금할 때

**AI 제공**: ❌ 불필요

---

### 📄 L0-HANDOFF-CHECKLIST.md
**위치**: `.ai-maintenance/L0-HANDOFF-CHECKLIST.md`
**레벨**: L0
**소유자**: 프로세스 관리자
**업데이트**: 반기별

**용도**:
- 개발자가 프로젝트 완료 시 확인할 체크리스트
- L1 문서 작성 가이드
- 인수인계 절차

**읽어야 할 때**:
- ✅ 개발자: 프로젝트 완료 시
- ✅ 개발자: 비개발자에게 인수인계 시

**AI 제공**: ❌ 불필요

---

### 📁 templates/
**위치**: `.ai-maintenance/templates/`
**레벨**: L0
**소유자**: 프로세스 관리자
**업데이트**: 분기별

**용도**:
- 새 프로젝트에 복사할 템플릿들
- L1 문서의 기본 구조 제공

**사용 시점**:
- ✅ 새 프로젝트 시작 시
- ✅ L1 문서 작성 시 참고

**포함 파일**:
```
templates/
├── TEMPLATE-CLAUDE.md
├── TEMPLATE-COMPLEXITY-MATRIX.md
├── TEMPLATE-EXAMPLES.md
├── TEMPLATE-AI-PROMPTS.md
├── TEMPLATE-CONSTRAINTS.md
└── TEMPLATE-TESTING.md
```

---

## L1 Documents (프로젝트 문서)

### 📄 L1-CLAUDE.md
**위치**: `(프로젝트 루트)/L1-CLAUDE.md`
**레벨**: L1
**소유자**: 개발자 (작성) → 비개발자 (유지보수)
**업데이트**: 주요 변경 시

**용도**:
- ⭐ **AI에게 제공하는 핵심 Context**
- 프로젝트 개요, 아키텍처
- 주요 실행 명령어
- 파일 구조 및 역할
- 공통 패턴

**읽어야 할 때**:
- ✅ 프로젝트 이해가 필요할 때
- ✅ 전체 구조 파악 시

**AI 제공**: ✅ **항상 제공** (모든 프롬프트에)

**작성 가이드**:
- 개발자가 1-2시간 투자하여 작성
- 템플릿: `templates/TEMPLATE-CLAUDE.md`
- 포함 사항:
  - 프로젝트 개요
  - 실행 명령어
  - 주요 파일 및 폴더 구조
  - 아키텍처 (비동기, API, 데이터 흐름)
  - 공통 패턴

**예시 구조**:
```markdown
# L1-CLAUDE.md

## Metadata
- Version: 1.0
- Last Updated: YYYY-MM-DD

## Project Overview
## Running Commands
## File Structure
## Architecture
## Common Patterns
## References
```

---

### 📄 L1-COMPLEXITY-MATRIX.md
**위치**: `(프로젝트 루트)/L1-COMPLEXITY-MATRIX.md`
**레벨**: L1
**소유자**: 개발자 (작성) → 비개발자 (피드백)
**업데이트**: 분기별

**용도**:
- ⭐ **복잡도 판단 기준**
- 이 프로젝트에서 LOW/MEDIUM/HIGH 분류
- 구체적인 예시 제공

**읽어야 할 때**:
- ✅ Step 1: 복잡도 평가 시 ⭐
- ✅ "이거 내가 할 수 있나?" 판단 시

**AI 제공**: ✅ 복잡도 평가 시 필수

**작성 가이드**:
- 개발자가 1시간 투자하여 작성
- 템플릿: `templates/TEMPLATE-COMPLEXITY-MATRIX.md`
- 포함 사항:
  - 🟢 LOW: 쉬운 수정들 (예시 5개 이상)
  - 🟡 MEDIUM: 주의 필요 (예시 3개 이상)
  - 🔴 HIGH: 개발자 필수 (명확한 기준)
  - 의사결정 플로우차트

**프로젝트별 커스터마이징 필수**:
- 범용 템플릿 → 이 프로젝트 특화
- 실제 파일명, 라인 번호 예시
- 프로젝트 특수 상황 반영

---

### 📄 L1-CONSTRAINTS.md
**위치**: `(프로젝트 루트)/L1-CONSTRAINTS.md`
**레벨**: L1
**소유자**: 개발자 (작성)
**업데이트**: 반기별

**용도**:
- ⭐ **절대 금지 사항**
- 조심해야 할 사항
- 안전하게 수정 가능한 것

**읽어야 할 때**:
- ✅ 수정 작업 시작 전 ⭐
- ✅ "이거 건드려도 되나?" 확인 시

**AI 제공**: ✅ 복잡도 평가 시, 코드 리뷰 시

**작성 가이드**:
- 개발자가 1시간 투자하여 작성
- 템플릿: `templates/TEMPLATE-CONSTRAINTS.md`
- 포함 사항:
  - ⛔ 절대 금지 (async/await, 의존성 등)
  - ⚠️ 주의 필요 (CSS 선택자, 조건문 등)
  - ✅ 안전 (숫자, 문자열, 데이터 값)

**중요**:
- 명확한 이유 설명
- 구체적인 예시 코드
- "왜 위험한가" 설명

---

### 📄 L1-TESTING.md
**위치**: `(프로젝트 루트)/L1-TESTING.md`
**레벨**: L1
**소유자**: 개발자 (작성) → 비개발자 (실행)
**업데이트**: 주요 변경 시

**용도**:
- ⭐ **프로젝트별 테스트 절차**
- 최소 테스트 (빠른 확인)
- 전체 테스트 (완전 검증)
- 엣지 케이스

**읽어야 할 때**:
- ✅ Step 3: 테스트 시 ⭐
- ✅ "어떻게 테스트하지?" 궁금할 때

**AI 제공**: ✅ 테스트 계획 수립 시

**작성 가이드**:
- 개발자가 1-2시간 투자하여 작성
- 템플릿: `templates/TEMPLATE-TESTING.md`
- 포함 사항:
  - 기본 검증 (문법, import, 의존성)
  - 프로젝트별 최소 테스트 (5-10분)
  - 전체 테스트 (30분-1시간)
  - 엣지 케이스
  - 회귀 테스트

**프로젝트별 필수 정보**:
- 정확한 실행 명령어
- 성공/실패 판단 기준
- 결과 파일 확인 방법

---

## L2 Documents (살아있는 문서)

### 📄 L2-EXAMPLES.md
**위치**: `(프로젝트 루트)/L2-EXAMPLES.md`
**레벨**: L2 (Living Document)
**소유자**: 비개발자 (주 작성자) + 개발자 (초기 작성)
**업데이트**: 매 작업마다

**용도**:
- ⭐ **실제 사례 모음**
- 성공 사례 + 실패 사례
- 사용한 AI 프롬프트
- 배운 점

**읽어야 할 때**:
- ✅ Step 2: 구현 시 (유사 사례 참고)
- ✅ "이거 전에 누가 해봤나?" 확인 시
- ✅ 월간 회고 시

**AI 제공**: ✅ 구현, 에러 디버깅 시

**작성 가이드**:
- 개발자: 초기 3-5개 예시 작성 (2시간)
- 비개발자: 작업 완료마다 추가 (Step 5)
- 템플릿: L0-WORKFLOW-MASTER.md Step 5 참조

**사례 구조**:
```markdown
## 사례 N: {제목}
- 날짜, 수정자, 난이도, 성공 여부
- 문제 상황
- 해결 방법
- 수정 전/후 코드
- AI 프롬프트
- 테스트 방법
- 배운 점
```

**통계 추적**:
- 월별 작업 건수
- 성공률
- 난이도별 분포
- 평균 소요 시간

---

### 📄 L2-PROMPTS.md
**위치**: `(프로젝트 루트)/L2-PROMPTS.md`
**레벨**: L2 (Living Document)
**소유자**: 비개발자 (주 작성자)
**업데이트**: 주 1-2회

**용도**:
- ⭐ **검증된 AI 프롬프트 모음**
- 작업별 프롬프트 템플릿
- 성공률 높은 프롬프트

**읽어야 할 때**:
- ✅ AI 프롬프트 작성 시 ⭐
- ✅ "어떻게 물어봐야 하지?" 막힐 때

**AI 제공**: ❌ 불필요 (사람이 읽고 복사)

**작성 가이드**:
- 템플릿: `templates/TEMPLATE-AI-PROMPTS.md`
- 초기: 기본 템플릿 10개
- 지속: 효과 좋은 프롬프트 추가

**카테고리**:
1. 복잡도 평가
2. 구현 계획
3. CSS 선택자 찾기
4. 코드 리뷰
5. 에러 해결
6. 테스트 계획
7. Rollback
8. 개발자 요청
9. (프로젝트별 추가)

**프롬프트 구조**:
```markdown
## {카테고리}: {제목}

### 용도
[언제 사용하는지]

### 프롬프트 템플릿
```
{실제 프롬프트 - 복사해서 사용}
```

### 사용 예시
[구체적 예시]

### 효과
[이 프롬프트가 왜 좋은지]
```

---

## 변경 요청 기록

### 📁 change-requests/
**위치**: `(프로젝트 루트)/change-requests/`
**레벨**: 작업 산출물
**소유자**: 비개발자
**정리**: 월간 (완료된 것은 completed/로 이동)

**용도**:
- 각 변경 작업의 모든 문서 보관
- 추적 가능성 (Traceability)
- 감사 (Audit)

**파일 구조**:
```
change-requests/
├── CR-20240131-001-REQUEST.md
├── CR-20240131-001-ANALYSIS.md
├── CR-20240131-001-IMPLEMENTATION.md
├── CR-20240131-001-TESTING.md
├── CR-20240131-001-REVIEW-REQUEST.md
├── CR-20240131-001-REVIEW-RESULT.md
└── completed/
    └── [완료된 요청들]
```

**파일명 규칙**:
```
CR-{YYYYMMDD}-{일련번호}-{단계}.md

단계:
- REQUEST: 변경 요청서
- ANALYSIS: 복잡도 평가 결과
- IMPLEMENTATION: 구현 로그
- TESTING: 테스트 보고서
- REVIEW-REQUEST: 리뷰 요청서
- REVIEW-RESULT: 리뷰 결과서
```

---

## 문서 읽는 순서

### 🎯 시나리오별 가이드

#### 시나리오 1: 완전 처음 시작
```
1. .ai-maintenance/README.md (시스템 이해)
   ↓
2. .ai-maintenance/L0-WORKFLOW-MASTER.md (프로세스 이해)
   ↓
3. L1-CLAUDE.md (프로젝트 이해)
   ↓
4. L1-COMPLEXITY-MATRIX.md (난이도 기준 이해)
   ↓
5. L2-EXAMPLES.md (사례 몇 개 읽기)
```

#### 시나리오 2: 수정 작업 시작
```
1. L0-WORKFLOW-MASTER.md Step 0 (백업)
   ↓
2. L0-WORKFLOW-MASTER.md Step 1 (복잡도 평가)
   + L1-COMPLEXITY-MATRIX.md
   + L1-CONSTRAINTS.md
   ↓
3. [LOW/MEDIUM이면]
   L0-WORKFLOW-MASTER.md Step 2 (구현)
   + L2-EXAMPLES.md (유사 사례)
   + L2-PROMPTS.md (프롬프트 템플릿)
   ↓
4. L0-WORKFLOW-MASTER.md Step 3 (테스트)
   + L1-TESTING.md
   ↓
5. [MEDIUM이면]
   L0-WORKFLOW-MASTER.md Step 4 (리뷰)
   ↓
6. L0-WORKFLOW-MASTER.md Step 5 (문서화)
```

#### 시나리오 3: 막혔을 때
```
1. L0-DOCUMENT-INDEX.md (이 파일 - 어디서 찾을지)
   ↓
2. L2-EXAMPLES.md (비슷한 상황 찾기)
   ↓
3. L1-CONSTRAINTS.md (금지 사항 위배했나?)
   ↓
4. [여전히 막혔으면]
   개발자에게 문의
```

---

## 문서 업데이트 책임

| 문서 | 초기 작성 | 지속 업데이트 | 검토 | 주기 |
|------|----------|-------------|------|------|
| **L0** | 프로세스 관리자 | 프로세스 관리자 | 팀 | 분기 |
| **L1-CLAUDE** | 개발자 | 개발자 | - | 주요 변경 시 |
| **L1-COMPLEXITY** | 개발자 | 개발자+비개발자 | - | 분기 |
| **L1-CONSTRAINTS** | 개발자 | 개발자 | - | 반기 |
| **L1-TESTING** | 개발자 | 개발자 | - | 주요 변경 시 |
| **L2-EXAMPLES** | 개발자 (3-5개) | 비개발자 | - | 매 작업 |
| **L2-PROMPTS** | 개발자 (기본) | 비개발자 | - | 주 1-2회 |

---

## 문서 찾기 치트시트

### "이거 어디서 찾아?"

| 찾고 싶은 것 | 문서 | 섹션 |
|------------|------|------|
| 전체 프로세스 | L0-WORKFLOW-MASTER.md | 전체 |
| 백업 방법 | L0-WORKFLOW-MASTER.md | Step 0 |
| 복잡도 판단 | L1-COMPLEXITY-MATRIX.md | 전체 |
| 금지 사항 | L1-CONSTRAINTS.md | 절대 금지 |
| 테스트 방법 | L1-TESTING.md | 프로젝트별 |
| 비슷한 사례 | L2-EXAMPLES.md | Entry 검색 |
| 프롬프트 | L2-PROMPTS.md | 카테고리별 |
| 프로젝트 구조 | L1-CLAUDE.md | File Structure |
| 실행 명령어 | L1-CLAUDE.md | Running Commands |
| 롤백 방법 | L0-WORKFLOW-MASTER.md | Step 0.1 |
| 리뷰 요청 | L0-WORKFLOW-MASTER.md | Step 4 |
| 문서화 | L0-WORKFLOW-MASTER.md | Step 5 |

---

## 버전 관리

### Git 구조
```
.
├── .ai-maintenance/          # L0 (거의 변경 없음)
│   └── ...
├── L1-*.md                   # L1 (가끔 변경)
├── L2-*.md                   # L2 (자주 변경)
└── change-requests/          # 작업 기록
```

### Commit 메시지 규칙
```
[L0] {변경 내용}     # L0 문서 수정
[L1] {변경 내용}     # L1 문서 수정
[L2] {변경 내용}     # L2 문서 수정
[CODE] {변경 내용}   # 실제 코드 수정
```

---

## 다음에 읽을 문서

### 역할별 추천

**비개발자 (처음)**:
1. ✅ README.md → 시스템 이해
2. ✅ L0-WORKFLOW-MASTER.md → 프로세스 학습
3. ✅ L1-CLAUDE.md → 프로젝트 이해

**비개발자 (작업 시)**:
1. ✅ L0-WORKFLOW-MASTER.md Step 0-1
2. ✅ L1-COMPLEXITY-MATRIX.md
3. ✅ L2-EXAMPLES.md

**개발자 (인수인계)**:
1. ✅ L0-HANDOFF-CHECKLIST.md
2. ✅ templates/ 폴더
3. ✅ L0-WORKFLOW-MASTER.md (프로세스 설명용)

---

## 참고 사항

### 문서가 너무 많아 보이나요?

**실제로 자주 읽는 문서**는 3-4개뿐입니다:
- L0-WORKFLOW-MASTER.md (프로세스)
- L1-CLAUDE.md (AI Context)
- L1-COMPLEXITY-MATRIX.md (난이도)
- L2-EXAMPLES.md (사례)

나머지는 **필요할 때만** 참고!

### 문서 읽기 시간

- **처음 시작**: 2-3시간 (README + WORKFLOW + CLAUDE + 사례 몇 개)
- **작업 시**: 10-15분 (해당 단계 문서만)
- **숙련 후**: 5분 (치트시트만)

---

## Changelog

### v1.0 (2024-01-31)
- 초기 버전 작성
- 모든 문서 인덱스 생성
- 빠른 참조 가이드 추가
- 시나리오별 가이드 추가
- 치트시트 추가
