# HTML Result Module Documentation

## 개요 (Overview)

`html_result.py`는 웹페이지의 HTML 요소에서 데이터를 추출하는 모듈입니다. 이 모듈은 Playwright 페이지 객체를 사용하여 웹페이지의 메인 헤드라인, 설명, 스토리 데이터 등을 수집하고, 추출된 데이터를 구조화된 형태로 저장합니다.

## 주요 기능 (Key Features)

- **HTML 요소 추출**: CSS 선택자를 사용한 정확한 HTML 요소 추출
- **메인 콘텐츠 수집**: 헤드라인과 설명 텍스트 추출
- **스토리 데이터 처리**: 스토리별 제목, 설명, 추천 제품 정보 수집
- **데이터 구조화**: 추출된 데이터를 일관된 형식으로 저장
- **비동기 처리**: Playwright의 비동기 기능을 활용한 효율적인 데이터 수집

## 클래스 구조 (Class Structure)

### htmlExtractor

웹페이지의 HTML 요소에서 데이터를 추출하는 메인 클래스입니다.

#### 초기화 (Initialization)

```python
def __init__(self, page, main_headline_tag, main_desc_tag, story_data_tag, row_data, target_columns):
```

**매개변수 (Parameters):**
- `page`: Playwright 페이지 객체
- `main_headline_tag`: 메인 헤드라인을 추출할 CSS 선택자
- `main_desc_tag`: 메인 설명을 추출할 CSS 선택자
- `story_data_tag`: 스토리 데이터를 추출할 CSS 선택자
- `row_data`: 데이터를 저장할 딕셔너리
- `target_columns`: 처리할 컬럼 리스트

**인스턴스 변수 (Instance Variables):**
- `page`: Playwright 페이지 객체
- `main_headline_tag`: 메인 헤드라인 CSS 선택자
- `main_desc_tag`: 메인 설명 CSS 선택자
- `story_data_tag`: 스토리 데이터 CSS 선택자
- `row_data`: 데이터 저장 딕셔너리
- `target_columns`: 처리할 컬럼 리스트

## 메서드 상세 설명 (Method Details)

### 1. dataframe_make()

```python
def dataframe_make(self):
```

**기능:**
- 결과 데이터를 저장할 DataFrame을 생성
- 모든 필요한 컬럼을 포함한 DataFrame 구조 정의

**반환값:**
- `pd.DataFrame`: 빈 DataFrame (target_columns로 구성)

**컬럼 구조:**
```python
target_columns = [    
    'Account',    # 계정 정보
    'main_headline', 'main_description', 'main_description1', 'main_description2',  # 메인 정보
    'storyIdRank1', 'storyIdRank2', 'storyIdRank3',  # 스토리 ID
    'storyIdRank1_title', 'storyIdRank1_desc',  # 스토리 1 제목/설명
    'storyIdRank1_rec1','storyIdRank1_rec2','storyIdRank1_rec3','storyIdRank1_rec4','storyIdRank1_rec5',  # 스토리 1 추천 제품들
    'storyIdRank2_title', 'storyIdRank2_desc',  # 스토리 2 제목/설명
    'storyIdRank2_rec1','storyIdRank2_rec2','storyIdRank2_rec3','storyIdRank2_rec4','storyIdRank2_rec5',  # 스토리 2 추천 제품들
    'storyIdRank3_title', 'storyIdRank3_desc',  # 스토리 3 제목/설명
    'storyIdRank3_rec1','storyIdRank3_rec2','storyIdRank3_rec3','storyIdRank3_rec4','storyIdRank3_rec5',  # 스토리 3 추천 제품들
    'lifeStyleIdRank1','lifeStyleIdRank2','Scenariokeyword1','Scenariokeyword2',  # 라이프스타일 및 시나리오 키워드
    'country_code','Device1','Device2','banner_text', 'banner_link_text','banner_hyperlink'  # 국가, 디바이스, 배너 정보
]
```

### 2. html_main_headline_ext()

```python
async def html_main_headline_ext(self):
```

**기능:**
- 메인 헤드라인을 HTML에서 추출
- 지정된 CSS 선택자로 메인 헤드라인 요소들을 찾음
- 모든 헤드라인 텍스트를 하나의 문자열로 결합

**처리 과정:**
1. CSS 선택자로 모든 메인 헤드라인 요소를 찾아서 텍스트 추출
2. 추출된 텍스트들을 공백으로 결합
3. 텍스트가 있으면 해당 텍스트 저장, 없으면 "없음" 저장
4. target_columns에 있는 컬럼들에 대해 데이터 저장

**코드 예시:**
```python
# CSS 선택자로 모든 메인 헤드라인 요소를 찾아서 텍스트 추출
specific_text = ' '.join([await elem.inner_text() for elem in await self.page.query_selector_all(self.main_headline_tag)])

column = 'main_headline'  # 저장할 컬럼명
if specific_text:  # 텍스트가 추출된 경우
    diff_data[column] = specific_text  # 임시 딕셔너리에 저장
    
    # target_columns에 있는 컬럼들에 대해 데이터 저장
    for col in self.target_columns:
        if col in diff_data:
            self.row_data[col] = diff_data[col]  # row_data에 최종 저장
else:  # 텍스트가 추출되지 않은 경우
    diff_data[column] = "없음"  # 기본값 설정
    self.row_data[col] = diff_data[column]  # row_data에 저장
```

### 3. html_main_description_ext()

```python
async def html_main_description_ext(self):
```

**기능:**
- 메인 설명을 HTML에서 추출
- 지정된 CSS 선택자로 메인 설명 요소들을 찾음
- 모든 설명 텍스트를 하나의 문자열로 결합

**처리 과정:**
1. CSS 선택자로 모든 메인 설명 요소를 찾아서 텍스트 추출
2. 추출된 텍스트들을 공백으로 결합
3. 텍스트가 있으면 해당 텍스트 저장, 없으면 "없음" 저장
4. target_columns에 있는 컬럼들에 대해 데이터 저장

### 4. html_story_data_ext()

```python
async def html_story_data_ext(self):
```

**기능:**
- 스토리 데이터를 HTML에서 추출
- 스토리 섹션의 모든 요소를 찾아서 처리
- 각 스토리의 제목, 설명, 추천 제품들을 추출

**처리 과정:**

#### 1단계: 스토리 섹션 찾기
```python
# 스토리 데이터 태그로 모든 스토리 섹션 찾기
top_tag = self.page.locator(self.story_data_tag)
count = await top_tag.count()  # 스토리 섹션 개수 확인
```

#### 2단계: 각 스토리별 데이터 추출
```python
# 각 스토리 섹션에 대해 처리
for i in range(count):
    top_tag_value = top_tag.nth(i)  # i번째 스토리 섹션

    # 스토리 제목 추출
    story_headline = await top_tag_value.locator('h3[class="myd26-my-story-st__headline"]').all_inner_texts()
    if story_headline:  # 제목이 존재하는 경우
        for value in story_headline:
            column = f'storyIdRank{i+1}_title'  # 컬럼명 생성 (예: storyIdRank1_title)
            diff_data[column] = value  # 임시 딕셔너리에 저장

    # 스토리 설명 추출
    story_desc = await top_tag_value.locator('p[class="myd26-my-story-st__description"]').all_inner_texts()
    if story_desc:  # 설명이 존재하는 경우
        for value in story_desc:
            column = f'storyIdRank{i+1}_desc'  # 컬럼명 생성 (예: storyIdRank1_desc)
            diff_data[column] = value  # 임시 딕셔너리에 저장

    # 스토리 추천 제품 추출
    story_product = await top_tag_value.locator('p[class="myd26-my-story-st__product-name"]').all_inner_texts()
    if story_product:  # 추천 제품이 존재하는 경우
        for idx, value in enumerate(story_product, start=1):  # 1부터 시작하는 인덱스
            column = f'storyIdRank{i+1}_rec{idx}'  # 컬럼명 생성 (예: storyIdRank1_rec1)
            diff_data[column] = value  # 임시 딕셔너리에 저장
```

#### 3단계: 데이터 저장
```python
# 모든 추출된 데이터를 row_data에 저장
for col in self.target_columns:
    if col in diff_data:
        self.row_data[col] = diff_data[col]  # row_data에 최종 저장
```

## 데이터 처리 로직 (Data Processing Logic)

### 1. HTML 요소 추출 방식

**CSS 선택자 사용:**
- `query_selector_all()`: 모든 매칭 요소 찾기
- `locator()`: 요소 위치 지정
- `inner_text()`: 텍스트 내용 추출
- `all_inner_texts()`: 모든 텍스트 내용 추출

### 2. 데이터 구조화

**컬럼명 규칙:**
- `storyIdRank{n}_title`: n번째 스토리 제목
- `storyIdRank{n}_desc`: n번째 스토리 설명
- `storyIdRank{n}_rec{m}`: n번째 스토리의 m번째 추천 제품

### 3. 에러 처리

**기본값 설정:**
- 텍스트가 추출되지 않은 경우 "없음" 저장
- 요소가 존재하지 않는 경우 빈 문자열 처리

## 사용 예시 (Usage Example)

### 1. 기본 사용법

```python
import asyncio
from playwright.async_api import async_playwright
from module.html_result import htmlExtractor

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # 페이지 이동
        await page.goto('https://www.smartthings.com')
        
        # 데이터 저장용 딕셔너리
        row_data = {}
        target_columns = [
            'main_headline', 'main_description',
            'storyIdRank1_title', 'storyIdRank1_desc',
            'storyIdRank1_rec1', 'storyIdRank1_rec2'
        ]
        
        # htmlExtractor 인스턴스 생성
        extractor = htmlExtractor(
            page=page,
            main_headline_tag='h1.main-headline',
            main_desc_tag='p.main-description',
            story_data_tag='div.story-section',
            row_data=row_data,
            target_columns=target_columns
        )
        
        # 메인 헤드라인 추출
        await extractor.html_main_headline_ext()
        
        # 메인 설명 추출
        await extractor.html_main_description_ext()
        
        # 스토리 데이터 추출
        await extractor.html_story_data_ext()
        
        # 결과 출력
        print("추출된 데이터:", row_data)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. DataFrame 생성

```python
# DataFrame 생성
df = extractor.dataframe_make()
print("DataFrame 구조:", df.columns.tolist())
```

### 3. 특정 스토리 데이터 추출

```python
# 스토리 데이터만 추출
await extractor.html_story_data_ext()

# 특정 스토리 정보 확인
story1_title = row_data.get('storyIdRank1_title', '없음')
story1_desc = row_data.get('storyIdRank1_desc', '없음')
story1_products = [
    row_data.get('storyIdRank1_rec1', ''),
    row_data.get('storyIdRank1_rec2', ''),
    row_data.get('storyIdRank1_rec3', ''),
    row_data.get('storyIdRank1_rec4', ''),
    row_data.get('storyIdRank1_rec5', '')
]

print(f"스토리 1 제목: {story1_title}")
print(f"스토리 1 설명: {story1_desc}")
print(f"스토리 1 추천 제품: {[p for p in story1_products if p]}")
```

## CSS 선택자 예시 (CSS Selector Examples)

### 1. 메인 헤드라인 선택자

```css
/* 일반적인 헤드라인 선택자 */
h1.main-headline
h1[class*="headline"]
.main-content h1
```

### 2. 메인 설명 선택자

```css
/* 일반적인 설명 선택자 */
p.main-description
.main-content p
[class*="description"]
```

### 3. 스토리 데이터 선택자

```css
/* 스토리 섹션 선택자 */
div.story-section
[class*="story"]
.story-container
```

### 4. 스토리 내부 요소 선택자

```css
/* 스토리 제목 */
h3[class="myd26-my-story-st__headline"]
.story-title
h3[class*="headline"]

/* 스토리 설명 */
p[class="myd26-my-story-st__description"]
.story-description
p[class*="description"]

/* 스토리 추천 제품 */
p[class="myd26-my-story-st__product-name"]
.story-product
p[class*="product"]
```

## 의존성 (Dependencies)

- `playwright`: 웹 브라우저 자동화 및 HTML 요소 추출
- `pandas`: DataFrame 생성 및 데이터 처리
- `asyncio`: 비동기 프로그래밍 지원

## 주의사항 (Important Notes)

1. **비동기 처리**: 모든 메서드가 비동기로 구현되어 있어 `await` 키워드 사용 필요
2. **CSS 선택자**: 정확한 CSS 선택자 사용 필요
3. **페이지 로딩**: 페이지가 완전히 로드된 후 추출 작업 수행
4. **데이터 저장**: `row_data` 딕셔너리에 직접 저장되므로 참조로 전달
5. **에러 처리**: 요소가 없는 경우 기본값 "없음" 사용

## 확장 가능성 (Extensibility)

### 1. 새로운 HTML 요소 추출 추가

```python
async def html_new_element_ext(self):
    """새로운 HTML 요소 추출 메서드"""
    diff_data = {}
    
    # 새로운 CSS 선택자로 요소 추출
    specific_text = ' '.join([await elem.inner_text() for elem in await self.page.query_selector_all(self.new_element_tag)])
    
    column = 'new_element'
    if specific_text:
        diff_data[column] = specific_text
    else:
        diff_data[column] = "없음"
    
    # target_columns에 있는 컬럼들에 대해 데이터 저장
    for col in self.target_columns:
        if col in diff_data:
            self.row_data[col] = diff_data[col]
```

### 2. 동적 컬럼 생성

```python
async def html_dynamic_story_ext(self, story_count=3):
    """동적으로 스토리 개수에 따라 컬럼 생성"""
    for i in range(story_count):
        # 스토리 제목 추출
        story_title = await self.page.locator(f'div.story-{i+1} h3').inner_text()
        self.row_data[f'storyIdRank{i+1}_title'] = story_title or "없음"
        
        # 스토리 설명 추출
        story_desc = await self.page.locator(f'div.story-{i+1} p').inner_text()
        self.row_data[f'storyIdRank{i+1}_desc'] = story_desc or "없음"
```

### 3. 조건부 추출

```python
async def html_conditional_ext(self):
    """조건에 따라 다른 요소 추출"""
    # 요소 존재 여부 확인
    headline_exists = await self.page.locator(self.main_headline_tag).count() > 0
    
    if headline_exists:
        await self.html_main_headline_ext()
    else:
        # 대체 헤드라인 추출
        await self.html_alternative_headline_ext()
```

## 성능 최적화 (Performance Optimization)

1. **선택자 최적화**: 구체적이고 효율적인 CSS 선택자 사용
2. **배치 처리**: 여러 요소를 한 번에 추출하여 처리 시간 단축
3. **캐싱**: 추출된 데이터를 메모리에 캐싱하여 중복 추출 방지
4. **비동기 처리**: 여러 추출 작업을 병렬로 처리

## 디버깅 및 로깅 (Debugging and Logging)

```python
async def html_main_headline_ext(self):
    """디버깅 기능이 추가된 메인 헤드라인 추출"""
    print(f"헤드라인 CSS 선택자: {self.main_headline_tag}")
    
    # 요소 개수 확인
    elements = await self.page.query_selector_all(self.main_headline_tag)
    print(f"발견된 헤드라인 요소 개수: {len(elements)}")
    
    # 각 요소의 텍스트 출력
    for i, elem in enumerate(elements):
        text = await elem.inner_text()
        print(f"헤드라인 {i+1}: {text}")
    
    # 기존 로직...
    specific_text = ' '.join([await elem.inner_text() for elem in elements])
    print(f"최종 헤드라인 텍스트: {specific_text}")
    
    # 나머지 처리...
```

## 테스트 케이스 (Test Cases)

### 1. 기본 케이스
- 모든 요소가 존재하는 경우
- 일부 요소만 존재하는 경우
- 요소가 전혀 없는 경우

### 2. 경계 케이스
- 빈 텍스트 요소
- 매우 긴 텍스트
- 특수 문자가 포함된 텍스트

### 3. 특수 케이스
- 동적으로 로드되는 요소
- 숨겨진 요소
- 중복된 요소

## 에러 처리 (Error Handling)

```python
async def html_main_headline_ext(self):
    """에러 처리가 추가된 메인 헤드라인 추출"""
    try:
        diff_data = {}
        
        # 요소 추출 시도
        elements = await self.page.query_selector_all(self.main_headline_tag)
        
        if not elements:
            print(f"경고: 헤드라인 요소를 찾을 수 없습니다. 선택자: {self.main_headline_tag}")
            diff_data['main_headline'] = "없음"
        else:
            # 텍스트 추출
            texts = []
            for elem in elements:
                try:
                    text = await elem.inner_text()
                    if text and text.strip():
                        texts.append(text.strip())
                except Exception as e:
                    print(f"요소 텍스트 추출 중 오류: {e}")
                    continue
            
            specific_text = ' '.join(texts) if texts else "없음"
            diff_data['main_headline'] = specific_text
        
        # 데이터 저장
        for col in self.target_columns:
            if col in diff_data:
                self.row_data[col] = diff_data[col]
                
    except Exception as e:
        print(f"헤드라인 추출 중 오류 발생: {e}")
        self.row_data['main_headline'] = "오류"
``` 