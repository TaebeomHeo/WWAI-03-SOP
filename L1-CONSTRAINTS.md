# PROJECT-CONSTRAINTS.md

이 문서는 WWAI-03-SOP 프로젝트에서 **절대 수정하면 안 되는 것들**과 **조심히 수정해야 하는 것들**을 명시합니다.

---

## ⛔ 절대 금지 (NEVER)

### 1. 비동기 (async/await) 구조 변경

#### ❌ 절대 하지 마세요
```python
# 함수 순서 변경
async def function1():
    await step_a()
    await step_b()  # 이 순서를 바꾸면 안 됨!

# await 제거/추가
result = await something()  # await 제거하면 안 됨!
result = something()        # await 추가해야 하는데 빠뜨리면 안 됨!

# 병렬 처리로 변경
await api1()
await api2()
# → asyncio.gather()로 바꾸려 하면 안 됨!
```

#### 왜 위험한가?
- **데드락**: 프로그램이 멈춰서 영원히 끝나지 않음
- **레이스 컨디션**: 실행 순서가 꼬여서 잘못된 결과
- **데이터 불일치**: API 응답이 순서대로 와야 하는데 뒤죽박죽

#### 영향받는 파일
- `01.smartThings/smartThings_main.py` (전체 메인 로직)
- `01.smartThings/smartThings_module/response_handler.py`
- 모든 `02.ENH/*/main.py` 파일

#### 개발자에게 요청하세요!

---

### 2. Python 버전 변경

#### ❌ 절대 하지 마세요
```bash
# Python 버전 업그레이드 시도
pyenv install 3.12.0
python --version  # 3.12로 바뀜 → 위험!

# 가상환경을 다른 Python 버전으로 재생성
python3.12 -m venv .venv  # 안 됨!
```

#### 왜 위험한가?
- 문법 호환성 문제 (새 버전에서만 작동하거나 구 버전에서만 작동)
- 의존성 패키지 호환성 깨짐
- Playwright, Pandas 등 주요 라이브러리 오작동

#### 고정된 버전
- **Python 3.11.9** (다른 버전 사용 금지)

#### 확인 방법
```bash
python --version
# Python 3.11.9 확인
```

---

### 3. requirements.txt 임의 수정

#### ❌ 절대 하지 마세요
```bash
# 패키지 임의 업그레이드
pip install --upgrade playwright  # 안 됨!
pip install --upgrade pandas      # 안 됨!

# requirements.txt 버전 변경
playwright==1.40.0  # 현재 버전
playwright==1.45.0  # 임의로 바꾸면 안 됨!
```

#### 왜 위험한가?
- **API 변경**: 새 버전에서 함수가 사라지거나 바뀔 수 있음
- **의존성 충돌**: A 패키지를 올리면 B 패키지와 충돌
- **버그**: 새 버전의 알려지지 않은 버그

#### 허용되는 경우
- **개발자 지시가 있을 때만**
- 보안 취약점 패치 (개발자 확인 후)

#### 안전한 설치 방법
```bash
# 정확히 명시된 버전으로 설치
pip install -r requirements.txt

# 특정 패키지 재설치 (버전 유지)
pip install --force-reinstall playwright==1.40.0
```

---

### 4. Class 구조 변경

#### ❌ 절대 하지 마세요
```python
# Class 이름 변경
class RowDataExcel:  # 이름 바꾸면 안 됨!
    pass

# 상속 구조 변경
class Child(Parent):  # Parent를 바꾸면 안 됨!
    pass

# 메서드 시그니처 변경
def method(self, param1, param2):  # 파라미터 순서/개수 바꾸면 안 됨!
    pass

# Class 삭제
class SomeClass:  # 다른 곳에서 사용 중일 수 있음!
    pass
```

#### 왜 위험한가?
- 전체 아키텍처 붕괴
- 다른 파일에서 import하는 코드가 모두 깨짐
- 객체지향 설계 원칙 위반

#### 영향받는 파일
- `01.smartThings/smartThings_module/`의 모든 파일
- `02.ENH/*/pf_modules/`, `pd_modules/` 등

#### 개발자에게 요청하세요!

---

### 5. Git에 민감 정보 커밋

#### ❌ 절대 하지 마세요
```bash
# env.user 파일을 Git에 추가
git add env.user  # 안 됨!
git commit -m "환경 설정"  # API 키가 노출됨!

# 코드에 API 키 하드코딩
api_key = "sk-abcd1234..."  # 절대 안 됨!
password = "mypassword123"   # 절대 안 됨!
```

#### 왜 위험한가?
- **보안 위험**: API 키 유출 → 비용 발생, 해킹
- **개인정보 유출**: 계정 정보 노출
- **규정 위반**: 회사 보안 정책 위반

#### 안전한 방법
```bash
# .gitignore 확인
cat .gitignore
# env.user가 포함되어 있는지 확인

# 실수로 추가했다면
git reset HEAD env.user
git checkout -- env.user

# 이미 커밋했다면
git reset --soft HEAD^  # 마지막 커밋 취소
git restore --staged env.user
```

#### 민감 정보 목록
- `env.user` (API 키, 비밀번호)
- `*.env`
- API 키, 토큰
- 계정 정보
- 내부 URL

---

### 6. 데이터 파일 구조 변경

#### ❌ 절대 하지 마세요
```python
# Excel/CSV 컬럼 순서 변경
# 원래: Account, 관심사키워드, 보유제품
# 변경: 보유제품, Account, 관심사키워드  # 안 됨!

# 컬럼명 변경
Account → account_name  # 코드가 깨짐!

# JSON 스키마 변경
{
  "url": "...",
  "site_code": "...",  # 필드명 바꾸면 안 됨!
  "tree": [...]
}
```

#### 왜 위험한가?
- 코드가 특정 컬럼 순서/이름에 의존
- 결과 파일 포맷이 달라져서 다른 도구와 호환 안 됨
- 데이터 처리 로직 전체가 깨짐

#### 안전한 방법
- **데이터 값만 변경** (구조는 유지)
- 새 컬럼 추가는 **맨 뒤에**
- 필수 컬럼은 절대 삭제 금지

#### 영향받는 파일
- `01.smartThings/` 관련 Excel 파일
- `02.ENH/smartthings-logic/data/*.csv`
- 모든 결과 JSON 파일

---

### 7. 핵심 알고리즘 수정

#### ❌ 절대 하지 마세요
```python
# 5단계 추천 로직 변경
# (smartthings-logic의 복잡한 정렬 로직)

# 제품 우선순위 계산 변경
# (product_result.py의 get_priority 함수)

# 트리 비교 알고리즘 변경
# (gnb의 재귀적 비교 로직)
```

#### 왜 위험한가?
- 비즈니스 로직의 핵심
- 엣지 케이스 처리가 복잡
- 전체 결과에 영향
- 회귀 테스트 필요

#### 영향받는 파일
- `02.ENH/smartthings-logic/processor.py`
- `01.smartThings/smartThings_module/product_result.py`
- `01.smartThings/smartThings_module/compare_result.py`
- `02.ENH/gnb/gnb.py`, `cgd.py`

#### 허용되는 경우
- 프롬프트 수정 (.md 파일): 🟢 OK
- 알고리즘 자체 수정: 🔴 개발자 필수

---

## ⚠️ 주의 필요 (CAUTION)

### 1. CSS 선택자 변경

#### ⚠️ 신중하게
```python
# 선택자 문자열 교체는 OK
button = page.locator(".old-class")
button = page.locator(".new-class")  # 검증 필수!
```

#### 반드시 확인할 것
1. **브라우저 개발자 도구로 검증**
   ```javascript
   // 브라우저 콘솔에서
   document.querySelectorAll('.new-class')
   // 1개만 나와야 함!
   ```

2. **페이지 로딩 후에도 존재하는지**
   - 동적으로 생성되는 요소인가?
   - 스크롤 후에 나타나는가?

3. **테스트**
   - 1개 URL로 먼저 테스트
   - 버튼 클릭이 정상 작동하는지

#### 주의사항
- `.first`, `.nth(0)` 사용 시 의도한 요소가 맞는지 확인
- 여러 페이지에서 동일한 선택자가 작동하는지 확인

---

### 2. 타임아웃 값 변경

#### ⚠️ 신중하게
```python
# 타임아웃 증가는 비교적 안전
await page.wait_for_timeout(2000)  # 2초
await page.wait_for_timeout(5000)  # 5초로 증가 - OK

# 타임아웃 감소는 주의
timeout=60  # 원래
timeout=30  # 줄이면 에러 가능성 ⚠️
```

#### 고려사항
1. **너무 크게 설정하면**
   - 전체 실행 시간 증가
   - 실제 에러를 놓칠 수 있음

2. **너무 작게 설정하면**
   - 타임아웃 에러 빈발
   - 느린 네트워크 환경에서 실패

#### 권장 접근
1. 원래 값의 1.5배 이내로 증가
2. 여러 환경에서 테스트
3. 로그로 실제 소요 시간 확인

---

### 3. 파일 경로 변경

#### ⚠️ 신중하게
```python
# Windows 경로
path = r'C:\Users\WW\Desktop\파일'

# macOS 경로로 변경
path = '/Users/bombbie/Desktop/파일'
```

#### 주의사항
1. **경로 구분자**
   - Windows: `\` (역슬래시) 또는 `\\`
   - macOS/Linux: `/` (슬래시)

2. **절대 경로 vs 상대 경로**
   - 절대 경로: `/Users/bombbie/...`
   - 상대 경로: `./data/account.csv` (권장)

3. **파일 존재 확인**
   ```bash
   ls /Users/bombbie/Desktop/파일
   # 파일이 실제로 있는지 확인!
   ```

4. **권한 확인**
   ```bash
   ls -la /path/to/file
   # 읽기 권한이 있는지 확인!
   ```

---

### 4. 로그 메시지 추가

#### ⚠️ 신중하게
```python
# print 추가는 비교적 안전
print(f"현재 처리 중: {account}")

# 하지만 민감 정보 출력 주의!
print(f"API Key: {api_key}")  # 안 됨!
print(f"Password: {password}")  # 안 됨!
```

#### 주의사항
1. **민감 정보 출력 금지**
   - API 키, 비밀번호, 토큰
   - 개인정보

2. **너무 많은 로그**
   - 성능 저하 가능
   - 로그 파일 용량 증가

3. **로그 위치**
   - 중요한 루프 안에 넣으면 엄청나게 출력됨
   - 적절한 위치 선택

---

### 5. 조건문 추가/수정

#### ⚠️ 신중하게
```python
# 단순 비교값 변경 - 비교적 안전
if count > 10:  # 원래
if count > 20:  # 변경 - OK

# 조건 추가 - 주의 필요
if site_code == 'BR':  # 원래
if site_code in ['BR', 'ZA']:  # 변경 - 테스트 필요!

# 복잡한 조건 - 위험!
if (cond1 and cond2) or (cond3 and not cond4):  # 개발자 상담!
```

#### 체크리스트
- [ ] 모든 분기(branch) 테스트했는가?
- [ ] True일 때 동작 확인
- [ ] False일 때 동작 확인
- [ ] 엣지 케이스 (None, 빈 문자열 등) 고려

---

## ✅ 안전하게 수정 가능 (SAFE)

### 1. 숫자 상수
```python
# 타임아웃, 재시도 횟수 등
TIMEOUT = 60  → TIMEOUT = 90
MAX_RETRIES = 3  → MAX_RETRIES = 5
```

### 2. 문자열 상수
```python
# URL, 경로, 메시지
URL = "https://old.com"  → URL = "https://new.com"
MESSAGE = "처리 중"  → MESSAGE = "처리 중입니다"
```

### 3. 리스트에 항목 추가
```python
# 국가 코드, 사이트 코드
codes = ['A', 'B', 'C']
codes = ['A', 'B', 'C', 'D']  # 추가 - OK
```

### 4. 주석 추가
```python
# 주석은 실행에 영향 없음
# 이 함수는 뭐뭐를 합니다  # OK!
```

### 5. 데이터 파일 값 변경 (구조 유지)
```csv
# CSV 파일의 값만 변경
Account, Keyword, Product
old@test.com, A, B  → new@test.com, C, D  # OK!
```

### 6. 프롬프트 텍스트 (.md 파일)
```markdown
# smartthings-logic의 .md 파일
완벽 매칭 조건을 더 명확하게 설명  # OK!
예시 추가  # OK!
```

---

## 🎯 의사결정 플로우

수정하기 전에 자신에게 물어보세요:

```
1. async/await와 관련있나?
   YES → 🔴 개발자 필수

2. Python 버전, 패키지 버전 변경인가?
   YES → 🔴 개발자 필수

3. Class 구조를 바꾸는가?
   YES → 🔴 개발자 필수

4. 데이터 파일 구조(컬럼 순서/이름)를 바꾸는가?
   YES → 🔴 개발자 필수

5. 핵심 알고리즘을 수정하는가?
   YES → 🔴 개발자 필수

6. CSS 선택자 변경인가?
   YES → ⚠️ 브라우저 검증 후 진행

7. 조건문 추가/수정인가?
   YES → ⚠️ 모든 분기 테스트 후 진행

8. 숫자, 문자열, 리스트 값 변경인가?
   YES → ✅ 안전, 진행 OK

9. 확실하지 않다면?
   → 🔴 개발자 상담 또는 AI 복잡도 평가
```

---

## 📞 도움 요청 기준

### 즉시 개발자에게 연락
- 프로덕션 오류 발생
- 데이터 손실 위험
- 보안 관련 이슈
- 위 "절대 금지" 항목 수정 필요

### AI에게 먼저 물어보기
- 수정 방법을 모르겠을 때
- 복잡도 판단이 애매할 때
- 테스트 방법을 모를 때

### 스스로 진행 가능
- 문서에 명시된 "안전" 항목
- 이전에 성공한 비슷한 작업
- 영향 범위가 명확한 단순 수정

---

## 🔒 요약

### 절대 안 됨 (개발자 필수)
- async/await 구조
- Python/패키지 버전
- Class 구조
- 민감 정보 커밋
- 데이터 파일 구조
- 핵심 알고리즘

### 주의해서 진행 (AI + 테스트)
- CSS 선택자
- 조건문
- 파일 경로
- 타임아웃 값

### 안전하게 진행 가능
- 숫자/문자열 상수
- 리스트 항목 추가
- 주석
- 데이터 값 (구조 유지)
- 프롬프트 텍스트

**의심스러우면 AI 복잡도 평가 먼저!**
**안전이 최우선입니다.**
