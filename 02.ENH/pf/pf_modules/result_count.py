"""
pf_modules/result_count.py - 결과 수 검증 모듈

PF 페이지에서 표시된 결과 수와 실제 렌더링된 제품 카드 수 간의 
일치성을 검증하는 핵심 모듈입니다. 사용자에게 정확한 검색 결과 정보를 
제공하는 데 필수적인 검증 기능을 수행합니다.

주요 검증 대상:
- 페이지 상단에 표시된 결과 수 텍스트 추출
- 실제 렌더링된 제품 카드의 개수 계산
- 배너 카드 및 특수 카드 제외 처리
- PICK 제품 배지가 있는 제품의 식별 및 제외

핵심 기능:
- 결과 수 텍스트 파싱: 정규식을 통한 숫자 추출 및 정규화
- 제품 카드 개수 계산: DOM 요소 기반의 정확한 카운팅
- 특수 카드 필터링: 배너, PICK 제품 등 검색 결과에 포함되지 않는 카드 제외
- 동적 클래스명 대응: PICK 제품 식별을 위한 클래스명 변경 추적
- 필터 적용 후 검증: 필터링된 결과에서도 정확한 개수 매칭 확인

검증 프로세스:
1. 페이지 로드 후 결과 수 표시 영역에서 텍스트 추출
2. 정규식을 사용하여 숫자 부분만 추출 및 정규화
3. 제품 카드 컨테이너에서 실제 카드 요소들 수집
4. 배너 카드 및 특수 카드 제외 처리
5. 표시된 수와 실제 카드 수 비교하여 일치성 검증
"""

import re
from utility.orangelogger import log


async def extract_result_count(page) -> tuple[int, int, str, bool]:
    """
    현재 페이지에서 표시된 결과 수와 실제 카드 수를 추출합니다.
    
    변동 가능성 및 개발 계획:
    - 현재: 배너 카드만 제외하고 개수 계산
    - 향후: PICK 배지 제품도 제외하고 개수 계산 예정
    - PICK 제품은 상단 4개로 고정될 예정이며, API 값이 아닌 클래스명으로 식별
    - 클래스명 변경 가능성이 있어 주기적인 업데이트 필요
    - 필터 적용 후에도 PICK 제품 제외 로직 적용 필요
    
    파라미터:
        page: Playwright Page 객체
        
    반환값:
        tuple[int, int, str, bool]: (표시된 결과 수, 실제 카드 수, 설명, no-result 요소 존재 여부)
        
    주의사항:
        PICK 제품 관련 클래스명이 추가되면 이 함수의 필터링 로직을 수정해야 함
    """
    try:
        # 0. no-result 요소 확인
        no_result_element = await page.query_selector(".pd21-product-finder__no-result")
        has_no_result = no_result_element is not None
        
        if has_no_result:
            log.info("No result element found - this is expected for empty search results")
            return 0, 0, "", True
        
        # 1. 페이지에 표시된 결과 수 추출
        displayed_count = 0
        result_count_element = await page.query_selector(".pd21-top__result-count")
        if result_count_element:
            result_count_text = await result_count_element.inner_text()
            log.info(f"Result count text found: {result_count_text}")
            # 숫자만 추출 (예: "123 results" -> 123)
            numbers = re.findall(r'\d+', result_count_text)
            if numbers:
                displayed_count = int(numbers[0])
                log.info(f"Extracted displayed result count from text: {displayed_count}")
        
        # 2. 실제 제품 카드 수 계산 (배너 카드 제외)
        all_cards = await page.query_selector_all("div.pd21-product-card__item")
        product_cards = []
        banner_cards = []
        
        for card in all_cards:
            class_list = await card.get_attribute("class")
            if class_list and "pd21-product-card__banner" in class_list:
                banner_cards.append(card)
            else:
                product_cards.append(card)
        
        actual_count = len(product_cards)
        log.info(f"Total cards found: {len(all_cards)}, Product cards: {actual_count}, Banner cards: {len(banner_cards)}")
        
        # 표시된 결과 수가 없으면 0으로 유지
        if displayed_count == 0:
            log.info("No displayed count found, keeping as 0")
        
        return displayed_count, actual_count, "", False
        
    except Exception as e:
        log.error(f"Error extracting result count: {e}")
        return 0, 0, "Error extracting result count", False
