# TESTING-CHECKLIST.md

코드를 수정한 후 반드시 거쳐야 할 테스트 체크리스트입니다.

**원칙**: "작동하는 것 같다"가 아니라 "테스트로 확인했다"

---

## 🔍 기본 검증 (모든 수정 후 필수)

### ✅ 1단계: 문법 검증 (Syntax Check)

```bash
# 수정한 파일의 Python 문법 확인
python -m py_compile [수정한_파일.py]

# 예시
python -m py_compile 01.smartThings/smartThings_main.py
```

**성공**: 아무 출력 없음
**실패**: SyntaxError 메시지 → 즉시 수정 필요

---

### ✅ 2단계: Import 검증

```bash
# Python 인터프리터에서 import 테스트
python

>>> import sys
>>> sys.path.append('/path/to/project')
>>> import [모듈명]
>>> exit()
```

**성공**: 에러 없이 import 됨
**실패**: ImportError, ModuleNotFoundError → 경로 또는 의존성 문제

---

### ✅ 3단계: 의존성 확인

```bash
# 가상환경 활성화 확인
which python
# .venv/bin/python 또는 .venv\Scripts\python.exe 확인

# 필요한 패키지 설치 확인
pip list | grep playwright
pip list | grep pandas
```

**성공**: 필요한 패키지가 모두 설치되어 있음
**실패**: 패키지 미설치 → `pip install -r requirements.txt`

---

## 📊 프로젝트별 테스트

### 01.smartThings

#### 최소 테스트 (5-10분)
```bash
# 1개 계정으로 테스트
python 01.smartThings/smartThings_main.py
```

**확인 사항**:
- [ ] 브라우저가 정상 실행되는가?
- [ ] 로그인이 성공하는가?
- [ ] API 응답을 기다리는가? (타임아웃 없이)
- [ ] HTML 데이터 추출이 성공하는가?
- [ ] 스크린샷이 생성되는가?
- [ ] Excel 결과 파일이 생성되는가?
- [ ] 브라우저가 정상 종료되는가?

**결과 파일 확인**:
```bash
# Excel 결과 확인
ls -la ~/Desktop/테스트_결과_*.xlsx

# 스크린샷 확인
ls -la result_*/[Account].png
```

#### 전체 테스트 (30분-1시간)
- [ ] 모든 국가 코드 (DE, FR, ES, IT, ...)
- [ ] 최소 3개 계정
- [ ] 결과 비교 로직 정상 작동
- [ ] 모든 결과 파일 생성 확인

---

### 02.ENH/gnb

#### 최소 테스트 (2-3분)
```bash
# 1. CGD 변환 (Excel → JSON)
cd 02.ENH/gnb
python cgd.py
```

**확인**:
- [ ] `cgdstore/` 폴더에 JSON 파일 생성
- [ ] JSON 파일이 정상적으로 열림

```bash
# 2. GNB 추출 및 검증
python main.py
```

**확인**:
- [ ] 브라우저 실행
- [ ] 로그인 성공 (AEM)
- [ ] GNB 메뉴 추출 성공
- [ ] 링크 검증 실행
- [ ] `crawlstore/` 폴더에 결과 JSON 생성

**결과 파일 확인**:
```bash
cat crawlstore/[날짜시간]_*.json | jq '.verification_summary'
```

---

### 02.ENH/pd

#### 최소 테스트 (3-5분)
```bash
cd 02.ENH/pd
python main.py
```

**확인 사항**:
- [ ] 브라우저 실행
- [ ] WDS 로그인 성공 (설정된 경우)
- [ ] 평점 검증 실행
- [ ] 카트 전이 검증 실행
- [ ] Broken Link 검증 실행
- [ ] Dimension 검증 실행 (해당 페이지인 경우)
- [ ] 가격 일치 검증 실행
- [ ] `result/` 폴더에 JSON 생성

**결과 파일 확인**:
```bash
cat result/[SITECODE]_*.json | jq '.'
```

**검증 필드 확인**:
```bash
cat result/[SITECODE]_*.json | jq '{
  rating: .rating_validate,
  cart: .transition_validate,
  link: .link_validate,
  dimension: .dimension_validate,
  price: .price_validate
}'
```

#### 엣지 케이스 테스트
- [ ] Standard PD 페이지
- [ ] Simple PD 페이지
- [ ] Dimension 없는 페이지
- [ ] 평점 없는 페이지

---

### 02.ENH/pf

#### 최소 테스트 (5-7분)
```bash
cd 02.ENH/pf
python main.py
```

**11개 검증 항목 확인**:
- [ ] 1. Broken Link
- [ ] 2. Navigation Visible
- [ ] 3. nv17 BreadCrumb
- [ ] 4. Headline
- [ ] 5. Result Count
- [ ] 6. Sort
- [ ] 7. Purchase
- [ ] 8. Filter
- [ ] 9. BreadCrumb (Test vs Live)
- [ ] 10. FAQ (Test vs Live)
- [ ] 11. Disclaimer (Test vs Live)

**결과 파일 확인**:
```bash
cat crawlstore/[SITECODE]_pf_*.json | jq '.tree[0].children[0] | {
  link_validate,
  navigation_visible_validate,
  nv17_validate,
  headline_validate,
  result_validate,
  sort_validate,
  purchase_validate,
  filter_validate,
  breadcrumb_validate,
  faq_validate,
  disclaimer_validate
}'
```

#### 엣지 케이스 테스트
- [ ] 필터 있는 PF
- [ ] 필터 없는 PF
- [ ] 서브 카테고리 여러 개
- [ ] 서브 카테고리 1개만

---

### 02.ENH/shop

#### 최소 테스트 (3-5분)
```bash
cd 02.ENH/shop
python main.py
```

**확인 사항**:
- [ ] L0 메뉴 추출
- [ ] L1 메뉴 추출
- [ ] Product 목록 추출
- [ ] 링크 유효성 검증
- [ ] `crawlstore/` 폴더에 JSON 생성

**결과 파일 확인**:
```bash
cat crawlstore/[SITECODE]_shop_*.json | jq '.tree | length'
# L0 메뉴 개수 확인

cat crawlstore/[SITECODE]_shop_*.json | jq '.tree[0].children | length'
# 첫 번째 L0의 L1 개수 확인
```

---

### 02.ENH/smartthings-logic

#### 최소 테스트 (1-2분)
```bash
cd 02.ENH/smartthings-logic

# 환경 변수 확인
cat env.user | grep OPENAI_API_KEY

# 1개 계정으로 테스트
python main.py
```

**확인 사항**:
- [ ] OpenAI API 호출 성공
- [ ] 스토리 추천 완료
- [ ] 제품 추천 완료 (스토리 추천 성공한 경우)
- [ ] `output/` 폴더에 파일 생성
  - [ ] `story_reasoning_*.md`
  - [ ] `product_reasoning_*.md`
  - [ ] `final_results_*.xlsx`

**결과 확인**:
```bash
ls -la output/
cat output/story_reasoning_*.md
open output/final_results_*.xlsx
```

#### 검증 항목
- [ ] 추천 결과 형식 확인 ("37-1, 39-1" 또는 "중 랜덤")
- [ ] 단계별 분석 내용 확인
- [ ] Excel에 모든 계정 결과 포함

---

## 🔄 회귀 테스트 (Regression Testing)

수정 후 **기존 기능이 깨지지 않았는지** 확인:

### 체크리스트
- [ ] 수정하지 않은 다른 기능도 테스트
- [ ] 이전 버전의 결과와 비교
- [ ] 동일한 입력으로 동일한 출력 나오는지

### 비교 방법
```bash
# 수정 전 결과 백업
cp result/old_result.json result/backup_old.json

# 수정 후 결과와 비교
diff result/backup_old.json result/new_result.json

# 또는 JSON 비교 도구
jq -S . result/backup_old.json > /tmp/old_sorted.json
jq -S . result/new_result.json > /tmp/new_sorted.json
diff /tmp/old_sorted.json /tmp/new_sorted.json
```

---

## 🧪 엣지 케이스 테스트

일반적인 경우 외에 특수한 경우도 테스트:

### 공통 엣지 케이스
- [ ] 빈 데이터 (계정 없음, 결과 없음)
- [ ] 매우 긴 데이터 (긴 텍스트, 많은 항목)
- [ ] 특수 문자 포함 (한글, 이모지, HTML 태그)
- [ ] 네트워크 느린 환경
- [ ] 타임아웃 발생 시나리오

### 프로젝트별 엣지 케이스

**01.smartThings**:
- [ ] API 응답 없을 때
- [ ] HTML 바인딩 실패 시
- [ ] 재시도 3회 모두 실패 시

**02.ENH/pd**:
- [ ] Dimension 없는 제품
- [ ] 평점 없는 제품
- [ ] Simple PD vs Standard PD

**02.ENH/pf**:
- [ ] 필터 없는 PF
- [ ] 제품 0개 (No Result)
- [ ] Test vs Live 차이 있을 때

---

## ⚡ 성능 테스트

수정 후 실행 시간이 크게 늘어나지 않았는지 확인:

### 측정 방법
```bash
# 실행 시간 측정
time python main.py

# 또는 코드에 추가
import time
start = time.time()
# ... 작업 ...
print(f"소요 시간: {time.time() - start:.2f}초")
```

### 기준
- 타임아웃 변경: ±타임아웃 변경분만큼 차이
- 로그 추가: 1-2초 이내 증가 허용
- 검증 항목 추가: 항목당 5-10초 증가 허용

**주의**: 10배 이상 느려지면 문제 있음!

---

## 🔍 코드 리뷰 체크리스트

개발자 리뷰 전 스스로 확인:

### 코드 품질
- [ ] 들여쓰기가 일관되는가?
- [ ] 변수명이 명확한가?
- [ ] 불필요한 주석이 없는가?
- [ ] 중복 코드가 없는가?
- [ ] 매직 넘버를 상수로 정의했는가?

### 에러 처리
- [ ] try-except로 감쌌는가?
- [ ] 에러 메시지가 명확한가?
- [ ] 에러 발생 시 프로그램이 종료되지 않는가?

### 테스트
- [ ] 모든 분기(if/else)를 테스트했는가?
- [ ] 정상 케이스 테스트
- [ ] 에러 케이스 테스트
- [ ] 엣지 케이스 테스트

---

## 📋 최종 체크리스트 (배포 전)

프로덕션에 배포하기 전 최종 확인:

### 코드
- [ ] 모든 파일 문법 검증 통과
- [ ] Import 에러 없음
- [ ] 개발자 리뷰 완료 (MEDIUM 이상)

### 테스트
- [ ] 최소 테스트 통과
- [ ] 회귀 테스트 통과
- [ ] 엣지 케이스 테스트
- [ ] 성능 테스트 (기준 내)

### 문서
- [ ] EXAMPLES.md에 사례 추가
- [ ] 수정 내용 주석 추가
- [ ] README 업데이트 (필요시)

### Git
- [ ] 의미 있는 커밋 메시지
- [ ] 민감 정보 포함 안 됨 (env.user 등)
- [ ] .gitignore 확인

### 백업
- [ ] 수정 전 상태 백업 (Git commit)
- [ ] 중요 데이터 백업
- [ ] Rollback 방법 확인

---

## 🚨 테스트 실패 시 대응

### 1단계: 에러 메시지 수집
```bash
# 전체 에러 로그 저장
python main.py 2>&1 | tee error.log
```

### 2단계: 에러 분석
- 에러 메시지 전문 읽기
- 어떤 파일, 어떤 라인에서 발생?
- 마지막으로 수정한 부분과 관련 있나?

### 3단계: AI에게 도움 요청
```
@CLAUDE.md
@[에러_발생_파일.py]

에러가 발생했어. 도와줘.

[에러 메시지]
[전체 에러 로그 붙여넣기]

[상황]
- 무엇을 수정했는지
- 언제 에러가 났는지

[요청]
1. 에러 원인
2. 해결 방법
```

### 4단계: Rollback
```bash
# 특정 파일만 되돌리기
git checkout [파일명]

# 모든 변경 되돌리기
git reset --hard HEAD
```

### 5단계: 재시도
- 작게 나누어 시도
- 한 번에 하나씩만 수정
- 각 단계마다 테스트

---

## 📊 테스트 결과 기록

테스트 결과를 기록하여 다음에 참고:

### 템플릿
```markdown
# 테스트 결과

**날짜**: YYYY-MM-DD
**수정자**: [이름]
**수정 내용**: [간단한 설명]

## 테스트 항목
- [x] 문법 검증 - 통과
- [x] 최소 테스트 - 통과
- [x] 엣지 케이스 - 통과
- [ ] 회귀 테스트 - 실패 (상세 내용)

## 발견된 문제
1. [문제 1] - [해결 방법]
2. [문제 2] - [미해결, 개발자 문의 예정]

## 성능
- 수정 전: 30초
- 수정 후: 32초
- 차이: +2초 (허용 범위)

## 최종 결과
✅ 배포 가능 / ⚠️ 리뷰 필요 / ❌ 재작업 필요
```

---

## 💡 테스트 팁

### 효율적인 테스트
1. **작게 시작**: 1개 항목으로 빠르게 확인
2. **자주 테스트**: 큰 수정 후가 아닌 작은 수정마다
3. **자동화**: 반복되는 테스트는 스크립트로
4. **문서화**: 테스트 방법과 결과를 기록

### 테스트 시간 절약
```bash
# 환경 변수로 빠른 테스트
QUICK_TEST=1 python main.py  # 1개 항목만

# 특정 부분만 테스트
python -m pytest tests/test_specific.py::test_function
```

### 테스트 실패 패턴
- **ImportError**: 가상환경 확인
- **TimeoutError**: 타임아웃 증가 또는 네트워크 확인
- **SyntaxError**: 문법 오류, py_compile로 확인
- **AttributeError**: 변수/함수명 오타 확인
- **KeyError**: 딕셔너리 키 존재 여부 확인

---

**원칙**: 테스트 없이 배포 없다!
**목표**: 자신 있게 "테스트 완료"라고 말할 수 있을 때까지!
