# EXAMPLES.md

이 문서는 비개발자가 AI 도구를 활용하여 성공적으로(또는 실패하여) 수정한 실제 사례를 모아놓은 곳입니다.

새로운 사례를 추가할 때는 아래 템플릿을 복사하여 사용하세요.

---

## 📝 사례 추가 템플릿

```markdown
# 사례 N: [간단한 제목]
**날짜**: YYYY-MM-DD
**수정자**: [이름]
**프로젝트**: [01.smartThings / 02.ENH/gnb / ...]
**난이도**: 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH
**성공 여부**: ✅ 성공 / ❌ 실패
**소요 시간**: [실제 걸린 시간]

## 문제 상황
[왜 수정이 필요했는지]

## 해결 방법
[어떻게 해결했는지]

## 수정 파일 및 라인
- `파일명.py`: line 123-125

## 수정 전 코드
```python
# 원래 코드
```

## 수정 후 코드
```python
# 바뀐 코드
```

## AI 프롬프트
```
[실제 사용한 AI 프롬프트]
```

## AI 도구
[Cursor / Claude / ChatGPT / ...]

## 테스트 방법
[어떻게 검증했는지]

## 배운 점 / 주의사항
[다음에 참고할 내용]

## 개발자 리뷰 (MEDIUM 이상인 경우)
- 리뷰어: [이름]
- 피드백: [개발자 의견]
```

---

## 🟢 LOW 난이도 성공 사례

### 사례 1: 타임아웃 시간 증가
**날짜**: 2024-01-15
**수정자**: 김철수
**프로젝트**: 01.smartThings
**난이도**: 🟢 LOW
**성공 여부**: ✅ 성공
**소요 시간**: 5분

#### 문제 상황
API 응답 대기 중 타임아웃 에러가 자주 발생. 네트워크가 느린 환경에서 60초로는 부족함.

#### 해결 방법
API 대기 타임아웃을 60초에서 90초로 증가.

#### 수정 파일 및 라인
- `01.smartThings/smartThings_main.py`: line 193

#### 수정 전 코드
```python
await data_collect.wait_for_responses(timeout=60)
```

#### 수정 후 코드
```python
await data_collect.wait_for_responses(timeout=90)
```

#### AI 프롬프트
```
@CLAUDE.md
@01.smartThings/smartThings_main.py

API 응답 대기 시간이 60초로 설정되어 있는데,
90초로 늘리고 싶어.

어떤 부분을 수정하면 되는지 알려줘.
```

#### AI 도구
Claude (claude.ai)

#### 테스트 방법
1. 1개 계정으로 테스트 실행
2. 타임아웃 에러 발생하지 않는지 확인
3. 전체 실행 시간이 크게 증가하지 않았는지 확인

#### 배운 점 / 주의사항
- 타임아웃을 너무 크게 설정하면 전체 실행 시간이 길어질 수 있음
- 90초로 충분한지 몇 번 테스트 후 확인 필요
- 다른 타임아웃 설정(HTML 바인딩 대기 등)도 있으니 혼동 주의

---

### 사례 2: CSS 선택자 변경 (버튼 클래스명 변경)
**날짜**: 2024-01-20
**수정자**: 이영희
**프로젝트**: 02.ENH/pd
**난이도**: 🟢 LOW
**성공 여부**: ✅ 성공
**소요 시간**: 15분

#### 문제 상황
웹사이트 리뉴얼로 "Add to Cart" 버튼의 클래스명이 변경됨. 기존 선택자로는 버튼을 찾지 못해 테스트 실패.

#### 해결 방법
브라우저 개발자 도구로 새 클래스명 확인 후 코드에서 선택자 교체.

#### 수정 파일 및 라인
- `02.ENH/pd/pd.py`: line 234

#### 수정 전 코드
```python
add_to_cart_button = await page.locator(".cta--add-to-cart").first
```

#### 수정 후 코드
```python
add_to_cart_button = await page.locator(".pd-cta-add-cart-v2").first
```

#### AI 프롬프트
```
@CLAUDE.md
@02.ENH/pd/pd.py

웹사이트에서 "Add to Cart" 버튼의 클래스를 확인했어:
.pd-cta-add-cart-v2

코드에서 이 버튼을 찾는 부분을 찾아서
새 클래스로 바꿔줘.

혹시 다른 곳에도 영향을 줄 수 있는지도 확인해줘.
```

#### AI 도구
Cursor

#### 테스트 방법
1. 브라우저 개발자 도구 (F12) 열기
2. Elements 탭에서 버튼 찾기
3. 클래스명 확인: `.pd-cta-add-cart-v2`
4. 해당 선택자가 페이지에서 유일한지 확인 (Console에서 `document.querySelectorAll('.pd-cta-add-cart-v2')`)
5. 코드 수정 후 1개 URL로 테스트
6. 버튼 클릭이 정상 작동하는지 확인

#### 배운 점 / 주의사항
- **반드시 브라우저 개발자 도구로 먼저 확인**할 것
- 선택자가 여러 요소를 가리키지 않는지 확인 필요
- `.first`를 사용할 경우 의도한 요소가 첫 번째인지 확인
- 웹사이트 업데이트 시 선택자 변경은 흔한 일이므로 익숙해지면 빠르게 대응 가능

---

### 사례 3: 새로운 국가 코드 추가
**날짜**: 2024-01-25
**수정자**: 박지민
**프로젝트**: 01.smartThings
**난이도**: 🟢 LOW
**성공 여부**: ✅ 성공
**소요 시간**: 10분

#### 문제 상황
UK 시장 테스트가 추가되어 국가 코드 리스트에 'UK' 추가 필요.

#### 해결 방법
country_codes 리스트에 'UK' 추가.

#### 수정 파일 및 라인
- `01.smartThings/smartThings_main.py`: line 85

#### 수정 전 코드
```python
country_codes = ['DE', 'FR', 'ES', 'IT']
```

#### 수정 후 코드
```python
country_codes = ['DE', 'FR', 'ES', 'IT', 'UK']
```

#### AI 프롬프트
```
@CLAUDE.md
@01.smartThings/smartThings_main.py

국가 코드 리스트에 'UK'를 추가하고 싶어.
다른 영향받는 부분이 있는지 확인해줘.
```

#### AI 도구
ChatGPT

#### 테스트 방법
1. 1개 UK 계정으로 테스트
2. UK URL이 올바르게 생성되는지 확인
3. 결과 파일에 UK 데이터가 정상 저장되는지 확인

#### 배운 점 / 주의사항
- 국가 코드를 추가할 때는 해당 국가의 테스트 데이터(Excel)도 준비되어 있어야 함
- URL 생성 로직에서 `country_code.lower()`를 사용하므로 대소문자는 자동 처리됨
- 결과 파일 경로에 국가 코드가 포함되는지 확인 필요

---

## 🟡 MEDIUM 난이도 성공 사례

### 사례 4: 새로운 검증 항목 추가 (평점 별 개수 확인)
**날짜**: 2024-02-01
**수정자**: 최민수
**프로젝트**: 02.ENH/pd
**난이도**: 🟡 MEDIUM
**성공 여부**: ✅ 성공
**소요 시간**: 1시간 30분

#### 문제 상황
평점 존재 여부만 확인하는데, 별 개수(5점 만점)도 함께 검증하고 싶음.

#### 해결 방법
기존 평점 검증 로직을 확장하여 별 개수 추출 및 검증 추가.

#### 수정 파일 및 라인
- `02.ENH/pd/pd.py`: line 245-265 (함수 수정)
- `02.ENH/pd/main.py`: line 78 (결과 필드 추가)

#### 수정 전 코드
```python
async def validate_rating(page):
    try:
        rating_element = await page.locator('.pdd39-anchor-nav__info-rating').first
        if await rating_element.is_visible():
            return True, "Rating exists"
        else:
            return False, "Rating not visible"
    except Exception as e:
        return False, f"Rating validation failed: {str(e)}"
```

#### 수정 후 코드
```python
async def validate_rating(page):
    try:
        rating_element = await page.locator('.pdd39-anchor-nav__info-rating').first
        if await rating_element.is_visible():
            # 별 개수 추출 추가
            rating_text = await rating_element.inner_text()
            # "4.5/5.0" 형식에서 숫자 추출
            import re
            match = re.search(r'(\d+\.?\d*)/(\d+\.?\d*)', rating_text)
            if match:
                score = float(match.group(1))
                max_score = float(match.group(2))
                # 5점 만점인지 확인
                if max_score == 5.0:
                    return True, f"Rating exists: {score}/5.0"
                else:
                    return False, f"Unexpected rating scale: {score}/{max_score}"
            else:
                return True, "Rating exists but format unclear"
        else:
            return False, "Rating not visible"
    except Exception as e:
        return False, f"Rating validation failed: {str(e)}"
```

#### AI 프롬프트
```
@CLAUDE.md
@02.ENH/pd/pd.py

현재 평점 검증 로직을 확장하고 싶어.

요구사항:
1. 평점 텍스트에서 숫자 추출 (예: "4.5/5.0")
2. 5점 만점인지 확인
3. 점수를 결과 메시지에 포함

단계별로 진행하자:
1. 먼저 현재 코드 분석
2. 정규식으로 숫자 추출하는 방법
3. 에러 처리 고려사항
4. 테스트 방법
```

#### AI 도구
Claude (claude.ai)

#### 테스트 방법
1. 다양한 평점 형식으로 테스트:
   - "4.5/5.0"
   - "4.8 out of 5"
   - 평점 없는 페이지
2. 결과 JSON에서 rating_validate_desc 확인
3. 정규식이 제대로 작동하는지 확인

#### 배운 점 / 주의사항
- 정규식은 간단해도 테스트가 중요 (다양한 형식 고려)
- 에러 처리를 추가할 때는 원래 동작이 깨지지 않도록 주의
- import 문은 함수 안에 넣어도 되지만, 파일 상단에 넣는 게 일반적
- **개발자 리뷰를 받아 import 위치를 상단으로 이동함**

#### 개발자 리뷰
- 리뷰어: 김개발
- 피드백:
  - ✅ 로직은 정상
  - ⚠️ `import re`를 함수 안이 아닌 파일 상단으로 이동 권장
  - ✅ 에러 처리 잘 됨
  - 💡 추가 제안: 점수 범위 검증 (0~5 사이인지)도 추가하면 좋음

---

### 사례 5: 조건문 추가 (특정 사이트만 검증 스킵)
**날짜**: 2024-02-10
**수정자**: 정수진
**프로젝트**: 02.ENH/pf
**난이도**: 🟡 MEDIUM
**성공 여부**: ✅ 성공
**소요 시간**: 45분

#### 문제 상황
특정 사이트(BR, ZA)는 필터 기능이 없어서 필터 검증 시 항상 실패. 해당 사이트는 필터 검증을 스킵하고 싶음.

#### 해결 방법
사이트 코드 확인 조건문 추가하여 BR, ZA는 필터 검증 스킵.

#### 수정 파일 및 라인
- `02.ENH/pf/main.py`: line 156-160

#### 수정 전 코드
```python
# 필터 검증 실행
filter_result = await validate_filter(page)
result['filter_validate'] = filter_result['success']
result['filter_validate_desc'] = filter_result['desc']
```

#### 수정 후 코드
```python
# 필터 검증 실행 (특정 사이트 제외)
skip_filter_sites = ['BR', 'ZA']
if site_code in skip_filter_sites:
    result['filter_validate'] = True
    result['filter_validate_desc'] = f"Filter validation skipped for {site_code}"
else:
    filter_result = await validate_filter(page)
    result['filter_validate'] = filter_result['success']
    result['filter_validate_desc'] = filter_result['desc']
```

#### AI 프롬프트
```
@CLAUDE.md
@02.ENH/pf/main.py

BR과 ZA 사이트는 필터 기능이 없어서
필터 검증을 스킵하고 싶어.

site_code 변수를 사용해서 조건을 추가하는 방법을 알려줘.
스킵된 경우 결과에는 어떻게 표시하면 좋을지도 제안해줘.
```

#### AI 도구
Cursor

#### 테스트 방법
1. BR 사이트로 테스트 → filter_validate: true, desc: "skipped for BR"
2. ZA 사이트로 테스트 → filter_validate: true, desc: "skipped for ZA"
3. 다른 사이트(예: UK)로 테스트 → 정상 필터 검증 실행
4. JSON 결과 파일 확인

#### 배운 점 / 주의사항
- 예외 처리 사이트 리스트를 명확히 정의 (skip_filter_sites)
- True로 표시하되 desc에 스킵 이유를 명시하여 나중에 혼동 방지
- 향후 사이트가 추가되면 리스트만 수정하면 됨
- **개발자 리뷰에서 리스트를 상수로 파일 상단에 정의하라는 제안 받음**

#### 개발자 리뷰
- 리뷰어: 이개발
- 피드백:
  - ✅ 조건문 로직 정상
  - 💡 `skip_filter_sites`를 함수 안이 아닌 파일 상단에 상수로 정의 권장
    ```python
    # 파일 상단
    SKIP_FILTER_VALIDATION_SITES = ['BR', 'ZA']
    ```
  - 💡 나중에 설정 파일(env.user)로 이동 고려

---

## ❌ 실패 사례 (배울 점 많음!)

### 사례 6: 비동기 함수 순서 변경 시도 (실패)
**날짜**: 2024-02-15
**수정자**: 한지훈
**프로젝트**: 01.smartThings
**난이도**: 🔴 HIGH
**성공 여부**: ❌ 실패
**소요 시간**: 2시간 (실패 후 Rollback)

#### 문제 상황
HTML 데이터 추출을 API 응답 대기보다 먼저 하면 더 빠를 것 같아서 순서를 바꾸려고 시도.

#### 시도한 방법
`await data_collect.wait_for_responses()`와 `await html_parse_data.html_main_headline_ext()` 순서 변경.

#### 수정 파일 및 라인
- `01.smartThings/smartThings_main.py`: line 191-216

#### 수정 전 코드 (원래)
```python
await data_collect.wait_for_responses(timeout=60)
row_data = await data_collect.process_responses(row)

html_parse_data = htmlExtractor(...)
await html_parse_data.html_main_headline_ext()
```

#### 시도한 코드
```python
html_parse_data = htmlExtractor(...)
await html_parse_data.html_main_headline_ext()

await data_collect.wait_for_responses(timeout=60)
row_data = await data_collect.process_responses(row)
```

#### 발생한 문제
- HTML이 아직 바인딩되지 않아서 `{{}}` 템플릿 변수만 추출됨
- API 데이터가 먼저 도착해야 HTML이 바인딩되는 구조였음
- 결과 데이터가 모두 "없음"으로 표시됨

#### AI 프롬프트
```
@01.smartThings/smartThings_main.py

API 대기 시간을 줄이고 싶어서
HTML 추출을 먼저 하고 API를 나중에 기다리면 어떨까?
순서를 바꿔도 되는지 알려줘.
```

#### AI 응답
AI(ChatGPT)가 처음에는 "가능할 것 같다"고 답했으나, 실제로 시도하니 실패. AI도 완벽하지 않음을 알게 됨.

#### Rollback 방법
```bash
git checkout 01.smartThings/smartThings_main.py
```

#### 배운 점 / 주의사항
- **비동기 함수 순서는 함부로 바꾸면 안 됨** (의존성 있음)
- AI가 "가능하다"고 해도 async/await 관련은 조심
- 이런 수정은 반드시 개발자에게 문의
- 다행히 Git으로 쉽게 되돌릴 수 있었음
- **교훈**: API 데이터가 먼저 도착해야 HTML 바인딩이 완료됨. 순서에는 이유가 있었음!

---

### 사례 7: 정규식 실수로 모든 데이터 잘못 추출 (실패 후 수정)
**날짜**: 2024-02-20
**수정자**: 오승아
**프로젝트**: 02.ENH/pf
**난이도**: 🟡 MEDIUM
**성공 여부**: ❌ 실패 → ✅ 수정 성공
**소요 시간**: 1시간 (실패) + 30분 (수정)

#### 문제 상황
결과 수 텍스트에서 숫자만 추출하려고 정규식 사용했는데 잘못된 패턴 사용.

#### 시도한 방법
정규식으로 숫자 추출.

#### 수정 파일 및 라인
- `02.ENH/pf/pf_modules/result_count.py`: line 23

#### 첫 번째 시도 (실패)
```python
import re
result_text = "Showing 24 results"
match = re.search(r'\d', result_text)  # 잘못된 패턴 - 첫 번째 숫자만
if match:
    count = int(match.group())
# 결과: count = 2 (24가 아닌 2만 추출됨!)
```

#### 발생한 문제
- `\d`는 한 자리 숫자만 매칭
- "24"를 "2"로 잘못 추출
- 모든 테스트가 실패 (실제 카드 수가 표시된 수보다 많다고 오판)

#### 수정 후 코드
```python
import re
result_text = "Showing 24 results"
match = re.search(r'\d+', result_text)  # \d+ 로 수정 - 연속된 숫자
if match:
    count = int(match.group())
# 결과: count = 24 (정상)
```

#### AI 프롬프트 (수정 시)
```
@02.ENH/pf/pf_modules/result_count.py

"Showing 24 results" 텍스트에서 24를 추출하고 싶은데
\d 패턴을 사용하니 2만 나와.

정규식을 어떻게 수정해야 두 자리 숫자를 모두 추출할 수 있어?
```

#### AI 도구
ChatGPT

#### 테스트 방법
1. Python 인터프리터에서 먼저 테스트:
   ```python
   import re
   text = "Showing 24 results"
   print(re.search(r'\d+', text).group())  # 24 확인
   ```
2. 실제 코드 적용
3. 여러 사이트에서 테스트 (한 자리, 두 자리, 세 자리 숫자)

#### 배운 점 / 주의사항
- **정규식은 반드시 먼저 Python 인터프리터에서 테스트**
- `\d`는 한 자리, `\d+`는 연속된 숫자 (1개 이상)
- 정규식 테스트 사이트(regex101.com) 활용 추천
- 작은 실수가 모든 결과를 망칠 수 있으므로 샘플 데이터로 먼저 확인
- AI에게 샘플 데이터를 함께 제공하면 더 정확한 답을 얻을 수 있음

---

## 🎓 배운 점 종합

### 성공 요인
1. **작게 시작**: 전체가 아닌 1개 항목으로 먼저 테스트
2. **백업 습관**: Git commit을 자주
3. **단계별 진행**: AI와 대화하며 한 단계씩
4. **검증 우선**: 브라우저 개발자 도구로 먼저 확인
5. **문서 활용**: CHANGE-COMPLEXITY-MATRIX.md로 난이도 판단

### 실패로부터의 교훈
1. **AI를 맹신하지 말 것**: async/await 같은 복잡한 건 개발자에게
2. **정규식은 조심**: 샘플 데이터로 먼저 테스트
3. **영향 범위 확인**: 수정 전 어디에 영향을 줄지 생각
4. **Rollback 준비**: 언제든 되돌릴 수 있게 Git 활용
5. **리뷰 요청**: 🟡 MEDIUM은 개발자 리뷰 필수

---

## 📊 통계 (2024년 1월-2월)

- 총 시도: 12건
- 성공: 9건 (75%)
- 실패 후 수정 성공: 2건
- 완전 실패 (개발자 의뢰): 1건

### 난이도별
- 🟢 LOW: 6건 (100% 성공)
- 🟡 MEDIUM: 5건 (60% 성공, 리뷰 후 모두 통과)
- 🔴 HIGH 시도: 1건 (0% 성공, 개발자에게 이관)

### 평균 소요 시간
- 🟢 LOW: 10분
- 🟡 MEDIUM: 1시간 15분 (리뷰 포함)

---

## 다음 사례 추가 시 참고

- 날짜와 수정자를 명확히 기록
- AI 프롬프트를 **정확히** 복사해서 붙여넣기 (다음 사람이 참고할 수 있게)
- 실패 사례도 **반드시** 기록 (더 중요!)
- 스크린샷이 있으면 더 좋음 (별도 폴더에 저장)
- 개발자 리뷰 내용도 꼭 기록
