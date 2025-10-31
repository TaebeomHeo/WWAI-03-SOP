# WWAI-03-SOP - Samsung Web Automation & AI-Assisted Maintenance

**최종 업데이트**: 2024-10-31
**버전**: 2.0

---

## 📋 프로젝트 개요

이 저장소는 두 가지 핵심 구성 요소로 이루어져 있습니다:

### 1. Samsung 웹 자동화 및 검증 도구
- **01.smartThings/**: SmartThings 자동화 테스트 프레임워크
- **02.ENH/**: Samsung 글로벌 웹사이트 검증 도구 (6개 서브 프로젝트)
  - gnb: GNB/CGD 메뉴 검증
  - pd: 제품 페이지 검증
  - pf: Product Finder 검증
  - shop: SHOP 네비게이션 추출
  - smartthings-logic: AI 기반 스토리 추천

### 2. AI-Assisted Maintenance System ⭐ NEW
개발자가 완성한 코드를 **비개발자가 AI 도구와 함께 유지보수**할 수 있도록 하는 표준 작업 절차(SOP) 시스템

---

## 🚀 빠른 시작

### 역할에 따라 선택하세요

#### 👨‍💻 개발자 (프로젝트 인수인계 시)
```
1. 읽기: .ai-maintenance/L0-HANDOFF-CHECKLIST.md
2. 예상 시간: 6-8시간
3. 다음: 문서 작성 → 코드 정리 → 비개발자 교육
```
**→ [바로 시작하기: .ai-maintenance/L0-HANDOFF-CHECKLIST.md]**

#### 👤 비개발자 (처음 시작)
```
1. 읽기 순서:
   ① QUICKSTART.md (5분) - 빠른 참조
   ② .ai-maintenance/README.md (30분) - 시스템 이해
   ③ .ai-maintenance/L0-WORKFLOW-MASTER.md (1시간) - 프로세스
   ④ L1-CLAUDE.md (30분) - 프로젝트 이해

2. 예상 시간: 2-3시간 (학습)
3. 다음: 개발자와 함께 첫 실습
```
**→ [바로 시작하기: QUICKSTART.md]**

#### 👤 비개발자 (수정 작업 시)
```
Step 0: git add . && git commit -m "백업"
Step 1: 복잡도 평가 (AI 사용, L2-PROMPTS.md 참고)
Step 2-5: L0-WORKFLOW-MASTER.md 따라 진행
```
**→ [워크플로우 가이드: .ai-maintenance/L0-WORKFLOW-MASTER.md]**

#### 🤖 AI (Claude, ChatGPT, Cursor)
```
Context 제공:
- 복잡도 평가: @L1-CLAUDE.md @L1-COMPLEXITY-MATRIX.md
- 구현: @L1-CLAUDE.md @L2-EXAMPLES.md @{파일명}
- 리뷰: @L1-CONSTRAINTS.md @{파일명}
```
**→ [AI 프롬프트: L2-PROMPTS.md]**

---

## 📁 문서 구조

### L0: 메타 문서 (범용, 모든 프로젝트 공통)
📂 `.ai-maintenance/`
- **README.md** - 시스템 개요, 2-Level 아키텍처
- **L0-WORKFLOW-MASTER.md** ⭐⭐⭐ - 5단계 워크플로우 (가장 중요!)
- **L0-DOCUMENT-INDEX.md** - 문서 찾기, 빠른 참조
- **L0-HANDOFF-CHECKLIST.md** - 개발자 인수인계 체크리스트

### L1: 프로젝트 문서 (이 프로젝트 특화)
📄 프로젝트 루트:
- **L1-CLAUDE.md** ⭐⭐⭐ - AI Context (AI에 항상 제공)
- **L1-COMPLEXITY-MATRIX.md** ⭐⭐⭐ - 복잡도 판단 기준
- **L1-CONSTRAINTS.md** ⭐⭐⭐ - 절대 금지 사항
- **L1-TESTING.md** ⭐⭐⭐ - 테스트 절차

### L2: 살아있는 문서 (계속 업데이트됨)
📄 프로젝트 루트:
- **L2-EXAMPLES.md** ⭐⭐ - 성공/실패 사례집
- **L2-PROMPTS.md** ⭐ - AI 프롬프트 템플릿 모음

### 지원 파일
- **QUICKSTART.md** - 5분 빠른 참조 가이드
- **change-requests/** - 변경 요청 추적 폴더

---

## 💡 핵심 개념

### AI-Assisted Maintenance란?
개발자가 만든 코드를 **비개발자가 AI(Claude, ChatGPT, Cursor)와 함께** 안전하게 수정/유지보수할 수 있도록 하는 시스템입니다.

### 3단계 복잡도 시스템
- 🟢 **LOW**: 비개발자 단독 수정 가능 (15-30분)
- 🟡 **MEDIUM**: AI 도움 + 개발자 리뷰 필요 (1-2시간)
- 🔴 **HIGH**: 개발자에게 요청 필수

### 5단계 워크플로우
1. **Step 0**: 준비 (Git 백업)
2. **Step 1**: 복잡도 평가 (AI 사용)
3. **Step 2**: 구현 (AI와 함께)
4. **Step 3**: 테스트 (L1-TESTING.md 참고)
5. **Step 4**: 리뷰 (MEDIUM 복잡도만)
6. **Step 5**: 문서화 (L2-EXAMPLES.md 업데이트)

### 안전 우선 원칙
```
백업 → 복잡도 평가 → 작은 테스트 → 전체 테스트 → 문서화
```

---

## 🛠️ 기술 스택

### 공통 기술
- **Python**: 3.11.9 (고정 버전)
- **Playwright**: 브라우저 자동화
- **asyncio**: 비동기 실행
- **Pandas**: 데이터 처리

### 프로젝트별 상세 정보
자세한 기술 스택, 아키텍처, 실행 방법은 **L1-CLAUDE.md**를 참조하세요.

---

## 📊 성공 지표

### 첫 1주일
- [ ] QUICKSTART.md + L0-WORKFLOW-MASTER.md 정독
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

## 🆘 문제 해결

### 막혔을 때
1. **문서 확인** (5분): L0-DOCUMENT-INDEX.md에서 관련 문서 찾기
2. **AI 도움** (10분): L2-PROMPTS.md의 "에러 해결" 프롬프트 사용
3. **롤백** (1분): `git reset --hard {백업_커밋_해시}`
4. **개발자 요청**: L0-WORKFLOW-MASTER.md "긴급 상황 대응" 섹션 참고

### 긴급 상황 (프로덕션 오류)
1. 즉시 롤백: `git reset --hard {이전_커밋}`
2. 개발자 긴급 연락
3. 로그 및 에러 메시지 캡처

---

## 📚 학습 자료

### 필독 (처음 2주)
1. ⭐⭐⭐ QUICKSTART.md
2. ⭐⭐⭐ .ai-maintenance/L0-WORKFLOW-MASTER.md
3. ⭐⭐⭐ L1-CLAUDE.md

### 참고 (필요 시)
- .ai-maintenance/README.md (시스템 전체 이해)
- L1-COMPLEXITY-MATRIX.md (난이도 판단)
- L1-CONSTRAINTS.md (금지 사항)
- L1-TESTING.md (테스트)

### 도구 (작업 시)
- L2-PROMPTS.md (AI 프롬프트 템플릿)
- L2-EXAMPLES.md (유사 사례 찾기)

---

## 🔗 관련 링크

### AI 도구
- **Claude Code**: https://claude.ai/code
- **Claude**: https://claude.ai
- **ChatGPT**: https://chat.openai.com
- **Cursor**: https://cursor.sh

### 학습 자료
- Git 기초: https://git-scm.com/book/ko/v2
- Python 기초: https://docs.python.org/3/tutorial/
- Playwright: https://playwright.dev/python/

---

## 📞 연락처

**긴급 상황** (프로덕션 오류):
- 즉시 롤백 후 개발자 연락
- 연락처: [개발자 연락처 입력]

**일반 문의**:
- Slack: [채널명]
- Email: [이메일]

**정기 체크인 일정**:
- 1주차: 매일
- 2주차: 격일
- 3-4주차: 주 2회
- 1개월 후: 주 1회

---

## 🎉 환영합니다!

이 시스템은 **개발자와 비개발자가 함께 AI를 활용하여** 코드를 안전하게 유지보수하는 방법입니다.

### 핵심 원칙
1. **안전 우선**: 항상 백업 먼저
2. **복잡도 평가**: 의심스러우면 한 단계 높게
3. **AI는 도구**: 맹신하지 말고 이해하고 검증
4. **문서는 살아있음**: 작업 완료 후 사례 추가
5. **질문하세요**: 문서 개선에 도움됩니다

### 다음 단계
- **개발자**: `.ai-maintenance/L0-HANDOFF-CHECKLIST.md` 시작
- **비개발자**: `QUICKSTART.md` 읽고 시작

---

**버전**: 2.0
**마지막 업데이트**: 2024-10-31
**다음 리뷰**: 2025-01-31 (3개월 후)
