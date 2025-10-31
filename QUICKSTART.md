# QUICKSTART - AI-Assisted Maintenance System

**최종 업데이트**: 2024-01-31
**버전**: 1.0

---

## 🎯 지금 바로 시작하기

### 역할별 바로가기

#### 👨‍💻 개발자 (프로젝트 완료 후)
```
1. 📖 읽기: .ai-maintenance/L0-HANDOFF-CHECKLIST.md
2. ⏱️ 예상 시간: 6-8시간 (1-2일)
3. 🎬 시작: 문서 작성 → 코드 정리 → 교육
```
**[상세 가이드: .ai-maintenance/L0-HANDOFF-CHECKLIST.md]**

---

#### 👤 비개발자 (처음 시작)
```
1. 📖 읽기 (순서대로):
   ① .ai-maintenance/README.md (30분) - 시스템 이해
   ② .ai-maintenance/L0-WORKFLOW-MASTER.md (1시간) - 프로세스 학습
   ③ L1-CLAUDE.md (30분) - 프로젝트 이해

2. ⏱️ 예상 시간: 2-3시간 (학습)

3. 🎬 시작: 개발자와 함께 첫 실습
```
**[상세 가이드: .ai-maintenance/README.md]**

---

#### 👤 비개발자 (수정 작업 시)
```
Step 0: 백업
  git add . && git commit -m "변경 전 백업"

Step 1: 복잡도 평가 (AI 사용)
  → 프롬프트: L2-PROMPTS.md 복사
  → Context: @L1-CLAUDE.md @L1-COMPLEXITY-MATRIX.md
  → 결과: 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH

Step 2-5: 워크플로우 진행
  → 가이드: .ai-maintenance/L0-WORKFLOW-MASTER.md
```
**[상세 가이드: .ai-maintenance/L0-WORKFLOW-MASTER.md]**

---

## 📁 문서 구조 한눈에 보기

```
프로젝트/
│
├── 📂 .ai-maintenance/           ⭐ L0: 범용 가이드 (모든 프로젝트 공통)
│   ├── README.md                 시스템 개요, 2-Level 구조
│   ├── L0-WORKFLOW-MASTER.md     ⭐⭐⭐ 5단계 워크플로우 (가장 중요!)
│   ├── L0-DOCUMENT-INDEX.md      문서 찾기, 빠른 참조
│   ├── L0-HANDOFF-CHECKLIST.md   개발자 인수인계 가이드
│   │
│   ├── 📂 templates/             새 프로젝트용 템플릿들
│   └── 📂 archive/               참고 문서 보관
│
├── 📄 L1-CLAUDE.md               ⭐⭐⭐ AI Context (AI에 항상 제공)
├── 📄 L1-COMPLEXITY-MATRIX.md    ⭐⭐⭐ 복잡도 판단 기준
├── 📄 L1-CONSTRAINTS.md          ⭐⭐⭐ 절대 금지 사항
├── 📄 L1-TESTING.md              ⭐⭐⭐ 테스트 절차
│
├── 📄 L2-EXAMPLES.md             ⭐⭐ 사례집 (계속 추가됨)
├── 📄 L2-PROMPTS.md              ⭐ AI 프롬프트 모음
│
├── 📂 change-requests/           변경 요청 기록
│   └── completed/                완료된 요청들
│
└── [프로젝트 코드 파일들]
```

---

## 🔍 "나는 지금 뭘 읽어야 하지?" 빠른 참조

| 상황 | 읽을 문서 | 시간 |
|------|----------|------|
| **완전 처음** | .ai-maintenance/README.md | 30분 |
| **프로세스 학습** | .ai-maintenance/L0-WORKFLOW-MASTER.md | 1시간 |
| **프로젝트 이해** | L1-CLAUDE.md | 30분 |
| **수정 시작 전** | .ai-maintenance/L0-WORKFLOW-MASTER.md Step 0-1 | 10분 |
| **난이도 판단** | L1-COMPLEXITY-MATRIX.md | 5분 |
| **금지사항 확인** | L1-CONSTRAINTS.md | 5분 |
| **유사 사례 찾기** | L2-EXAMPLES.md | 10분 |
| **AI 프롬프트** | L2-PROMPTS.md | 5분 |
| **테스트 방법** | L1-TESTING.md | 10분 |
| **문서 찾기** | .ai-maintenance/L0-DOCUMENT-INDEX.md | 2분 |

---

## 🤖 "AI에게 뭘 줘야 하지?" 빠른 참조

| 작업 | 제공할 Context (@파일명) |
|------|------------------------|
| **복잡도 평가** | @L1-CLAUDE.md<br>@L1-COMPLEXITY-MATRIX.md<br>@L1-CONSTRAINTS.md |
| **구현** | @L1-CLAUDE.md<br>@L2-EXAMPLES.md<br>@{수정할_파일.py} |
| **코드 리뷰** | @L1-CONSTRAINTS.md<br>@{수정한_파일.py} |
| **테스트 계획** | @L1-TESTING.md |
| **에러 해결** | @L1-CLAUDE.md<br>@{에러_파일.py}<br>@L2-EXAMPLES.md |

---

## 🚀 첫 작업 5분 체크리스트

### Step 0: 준비 (1분)
```bash
# Git 백업
git add .
git commit -m "변경 전 백업"

# 커밋 해시 기록 (롤백용)
git log -1 --oneline
# 출력: abc1234 변경 전 백업
# 이 해시를 메모!
```

### Step 1: 복잡도 평가 (3분)

**AI 프롬프트** (L2-PROMPTS.md에서 복사):
```
[STEP-1: COMPLEXITY-ANALYSIS]

[CONTEXT FILES]
@L1-CLAUDE.md
@L1-COMPLEXITY-MATRIX.md
@L1-CONSTRAINTS.md

[REQUEST]
다음 변경의 복잡도를 평가해줘:
{여기에 변경 내용 적기}

[OUTPUT FORMAT]
복잡도: 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH
근거: ...
다음 단계: ...
```

### 결과에 따른 다음 단계 (1분)

- **🟢 LOW** → Step 2로 진행 (15-30분 예상)
- **🟡 MEDIUM** → Step 2로 진행 + Step 4 리뷰 필수 (1-2시간 예상)
- **🔴 HIGH** → 개발자에게 요청

---

## 💡 핵심 원칙 (외우세요!)

### 1. 문서는 계층적
```
L0 (메타) → L1 (프로젝트) → L2 (살아있는)
범용        특화           경험
```

### 2. 안전 우선
```
백업 → 복잡도 평가 → 작은 테스트 → 전체 테스트 → 문서화
```

### 3. AI는 도구, 맹신 금지
```
AI 제안 → 이해하기 → 검증하기 → 적용하기
```

### 4. 문서는 살아있음
```
작업 완료 → L2-EXAMPLES.md에 추가 → 다음 사람이 참고
```

### 5. 의심스러우면 한 단계 위로
```
LOW 같은데? → MEDIUM으로 판단
MEDIUM 같은데? → HIGH로 판단 (안전하게)
```

---

## 📊 성공 지표

### 첫 1주
- [ ] L0-WORKFLOW-MASTER.md 정독
- [ ] L1-CLAUDE.md로 프로젝트 이해
- [ ] 개발자와 함께 실습 1회

### 첫 1개월
- [ ] 🟢 LOW 수정 3회 성공
- [ ] 🟡 MEDIUM 수정 1회 성공 (리뷰 포함)
- [ ] L2-EXAMPLES.md에 사례 3개 추가

### 2개월 후
- [ ] 독립적으로 🟢 LOW 처리
- [ ] 🟡 MEDIUM 80% 성공률
- [ ] AI 프롬프트 작성 능숙

---

## 🆘 막혔을 때

### 1단계: 문서 확인 (5분)
```
1. L0-DOCUMENT-INDEX.md에서 관련 문서 찾기
2. L2-EXAMPLES.md에서 유사 사례 찾기
3. L1-CONSTRAINTS.md에서 금지 사항 확인
```

### 2단계: AI에게 도움 요청 (10분)
```
L2-PROMPTS.md의 "에러 해결" 프롬프트 사용
+ 에러 메시지 전체 복사
+ 상황 설명
```

### 3단계: 롤백 (1분)
```bash
# 특정 파일만
git checkout {파일명}

# 전체 되돌리기
git reset --hard {백업_커밋_해시}
```

### 4단계: 개발자 요청
```
L0-WORKFLOW-MASTER.md "긴급 상황 대응" 섹션 참고
```

---

## 📞 연락처

**긴급 상황** (프로덕션 오류):
- 즉시 롤백
- 개발자 긴급 연락: [연락처]

**일반 문의**:
- Slack: #project-[이름]
- Email: [이메일]

**정기 체크인**:
- 1주차: 매일
- 2주차: 격일
- 3-4주차: 주 2회
- 1개월 후: 주 1회 (금요일 회고)

---

## 🎓 학습 자료

### 필독 (처음 2주)
1. ⭐⭐⭐ .ai-maintenance/L0-WORKFLOW-MASTER.md
2. ⭐⭐⭐ L1-CLAUDE.md
3. ⭐⭐ L2-EXAMPLES.md

### 참고 (필요 시)
- .ai-maintenance/README.md (시스템 전체 이해)
- .ai-maintenance/L0-DOCUMENT-INDEX.md (문서 찾기)
- L1-COMPLEXITY-MATRIX.md (난이도 판단)
- L1-CONSTRAINTS.md (금지 사항)
- L1-TESTING.md (테스트)

### 도구 (나중에)
- L2-PROMPTS.md (프롬프트 템플릿)

---

## 🔗 유용한 링크

### AI 도구
- **Claude**: https://claude.ai (복잡도 평가, 설명)
- **ChatGPT**: https://chat.openai.com (빠른 질문)
- **Cursor**: https://cursor.sh (코드 편집)

### 학습 자료
- Git 기초: https://git-scm.com/book/ko/v2
- Python 기초: https://docs.python.org/3/tutorial/
- Markdown 문법: https://www.markdownguide.org/

---

## 📝 다음 단계

### 개발자
1. ✅ L0-HANDOFF-CHECKLIST.md 따라 문서 작성 (6-8시간)
2. ✅ 비개발자에게 2-3시간 교육
3. ✅ 1주일간 매일 체크인

### 비개발자
1. ✅ README.md + WORKFLOW-MASTER.md 읽기 (1.5시간)
2. ✅ L1-CLAUDE.md로 프로젝트 이해 (30분)
3. ✅ 개발자와 함께 첫 실습 (1시간)
4. ✅ 1주일 내 첫 🟢 LOW 수정 시도

---

## 🎉 환영합니다!

이 시스템은 **여러분이 AI와 함께 일하는 방법**입니다.

- 처음엔 어렵고 낯설 수 있습니다
- 실수해도 괜찮습니다 (Git으로 되돌릴 수 있어요!)
- 질문하세요 (문서 개선에 도움됩니다)
- 성공하면 L2-EXAMPLES.md에 기록하세요 (다음 사람을 위해)

**함께 만들어가는 시스템입니다!**

---

**버전**: 1.0
**마지막 업데이트**: 2024-01-31
**다음 리뷰**: 2024-04-30 (3개월 후)
