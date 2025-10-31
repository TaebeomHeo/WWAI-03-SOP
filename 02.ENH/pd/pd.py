"""
pd.py - Samsung Product Page 자동화 테스트 시스템

이 모듈은 삼성 제품 페이지(PD)의 자동화 테스트를 수행하여 Standard PD, Simple PD, Dimension 기능을 체계적으로 검증합니다.

환경 및 전제 조건:
- Windows 환경, Python 3.11.9를 전제로 합니다.
- Playwright의 Page 객체와 프로젝트 로거(`utility.orangelogger.log`)가 사전에 준비되어 있어야 합니다.

실행 흐름 요약:
- 페이지 로드 → 기본 요소(rating/가격) 검증 → PD 타입 판별 → 타입별 네비게이션 → Dimension/URL 병렬 검증 → 카트 가격 확인 및 PD 가격과 비교 → 결과(JSON) 저장

로깅 정책:
- 모든 콘솔 출력은 Logger를 사용하며 메시지는 영어로 기록합니다. Docstring/주석은 한국어로 작성합니다.

주요 기능:
- PD 타입 자동 감지 (Standard PD vs Simple PD)
- Dimension 영역 존재 여부 확인
- 기본 요소 검증 (rating, 가격)
- URL 상태 검증 및 카트 전환 검증
- 시나리오별 자동 분기 처리
- 병렬 검증으로 효율성 극대화
- 결과를 JSON 형식으로 통합 출력
- 상세한 예외 처리 및 로깅 지원
"""

import asyncio
from typing import Dict, List, Tuple, Union
from playwright.async_api import Page
from utility.orangelogger import log
from utility.aem import scroll_for_lazyload
from pd_modules.selectors import SELECTORS
from pd_modules.navigation import detect_pd_type, navigate_to_buy_pd
from pd_modules.links import collect_links, run_link_validation
from pd_modules.dimension import check_dimension_area, validate_dimension_fit
from pd_modules.price import validate_price_match


class PDNode:
    """
    PD 테스트 결과를 수집·요약해 JSON 구조로 제공하는 컨테이너.

    전제조건: URL은 절대경로 문자열.
    사후조건: to_dict()가 조건부 필드 포함 규칙을 만족.
    부작용: 없음.
    예외: 없음.

    속성:
        url (str): 대상 페이지 URL.
        pd_type (str): "Standard"|"Simple"|"Unknown" (기본값: "").
        rating_check (bool): 평점 요소 검증 결과.
        link_validate (bool): 링크 검증 결과.
        link_validate_desc (dict|str): 실패 상세 또는 빈 문자열.
        is_dimension (bool): Dimension 영역 존재 여부.
        dimension_validate (bool|None): 존재 시 결과, 없으면 None.
        dimension_validate_desc (dict|None|str): 실패 상세/None/빈 문자열.
        transition_validate (bool): 카트 전환 결과.
        transition_validate_desc (str): 전환 실패 상세 또는 빈 문자열.
        price_validate (bool): 가격 일치 결과.
        price_validate_desc (str): 가격 불일치 상세 또는 빈 문자열.

    예시:
        node = PDNode(url)
        data = node.to_dict()
    """
    
    def __init__(self, url: str, pd_type: str = ""):
        """
        인스턴스를 생성하고 결과 필드를 기본 상태로 초기화.

        파라미터:
            url (str): 대상 페이지 URL(절대경로 권장).
            pd_type (str): "Standard"|"Simple"|""(미확정).

        반환값:
            None

        예외:
            없음

        전제조건: url은 비어있지 않음.
        사후조건: 검증 결과 필드는 실패/None/빈 문자열로 초기화.
        부작용: 없음
        예시:
            node = PDNode(url)
        """
        # 기본 필드
        self.url = url
        self.pd_type = pd_type
        
        # 검증 결과 필드
        self.rating_validate = False
        self.rating_validate_desc = ""
        self.link_validate = False
        self.link_validate_desc = {}
        self.is_dimension = False  # Dimension 영역 존재 여부
        self.dimension_validate = None  # Dimension이 있는 경우만
        self.dimension_validate_desc = None
        self.transition_validate = False
        self.transition_validate_desc = ""
        self.price_validate = False
        self.price_validate_desc = ""
    
    def to_dict(self) -> dict:
        """
        검증 결과를 JSON 직렬화용 dict로 변환.

        전제조건: self.url이 설정됨.
        사후조건: is_dimension==True일 때만 dimension 필드 포함.

        파라미터:
            없음

        반환값:
            dict: url, pd_type, rating/link/transition/price 결과와 조건부 dimension 필드.

        예외:
            없음

        부작용:
            없음

        예시:
            data = node.to_dict()
        """
        result = {
            "url": self.url,
            "pd_type": self.pd_type,
            "rating_validate": self.rating_validate,
            "rating_validate_desc": self.rating_validate_desc,
            "link_validate": self.link_validate,
            "link_validate_desc": self.link_validate_desc,
            "transition_validate": self.transition_validate,
            "transition_validate_desc": self.transition_validate_desc,
            "price_validate": self.price_validate,
            "price_validate_desc": self.price_validate_desc
        }
        
        # Dimension 관련 필드는 Dimension이 있는 경우에만 포함
        if self.is_dimension:
            result["dimension_validate"] = self.dimension_validate
            result["dimension_validate_desc"] = self.dimension_validate_desc
        
        return result

 

 

async def validate_pd_page(page: Page, url: str) -> PDNode:
    """
    PD 페이지 종합 검증을 수행하고 결과를 반환.

    간단 설명:
        - 목적: PD 타입/요소/링크/Dimension/카트/가격을 순차·병렬로 검증합니다.
        - 입력/출력: page(Page), url(str) → PDNode

    파라미터:
        page (Page): Playwright 페이지.
        url (str): 대상 URL.

    반환값:
        PDNode: 검증 결과 객체.

    예외: 내부 처리, 오류 시 기본 PDNode 반환.
    전제조건: 대상 URL 로드 가능.
    사후조건: 필요 시 카트 페이지 진입/삭제 시도.
    부작용: 네트워크/탭/클릭/대기 다수.

    AI 요청 템플릿(복붙 가능):
        - "병렬 검증에서 링크 검증을 먼저 시작하고, Dimension 검증은 팝업 준비 후 시작해줘."
        - "검증 실패 요약을 PDNode의 summary 필드(옵션)로 추가하되 기존 필드는 유지해줘."
        - "로그 레벨을 정보/경고/오류로 재분류해 중요도에 따라 출력해줘."
        - "각 단계의 시작과 종료 시점을 한 줄 로그로 남겨 타임라인을 보이게 해줘."
    예시:
        node = await validate_pd_page(page, url)
    """
    try:
        log.info(f"Starting PD page validation for URL: {url}")
        
        # PDNode 초기화
        pd_node = PDNode(url)
        
        # # 1단계: rate 검증 (메인 함수 내 직접 처리)
        # log.info("Step 1: Rate validation")
        # try:
        #     # 페이지 안정화를 위한 추가 대기
        #     await page.wait_for_load_state('domcontentloaded')
        #     await asyncio.sleep(1)  # 페이지 완전 로드 대기
            
        #     rating_container = await page.query_selector(SELECTORS['rating_container'])
        #     if rating_container:
        #         # pdd39-anchor-nav__info-rating 클래스 내에 a 태그가 있고, 그 내에 rating 클래스가 있는지 확인
        #         a_tag = await rating_container.query_selector('a')
        #         if a_tag:
        #             rating_element = await a_tag.query_selector('.rating')
        #             pd_node.rating_validate = rating_element is not None
        #             if not pd_node.rating_validate:
        #                 pd_node.rating_validate_desc = "Rating element not found in anchor tag"
        #         else:
        #             log.warning("Rating container found but no anchor tag inside")
        #             pd_node.rating_validate = False
        #             pd_node.rating_validate_desc = "No anchor tag found in rating container"
        #     else:
        #         log.warning("Rating container not found")
        #         pd_node.rating_validate = False
        #         pd_node.rating_validate_desc = "Rating container not found"
        # except Exception as e:
        #     log.error(f"Error in rate validation: {e}")
        #     pd_node.rating_validate = False
        #     pd_node.rating_validate_desc = f"Rate validation error: {str(e)}"
        
        # # 2단계: 가격 추출 (메인 함수 내 직접 처리)
        # log.info("Step 2: Price extraction")
        # pd_price = ""
        # try:
        #     # 페이지 안정화를 위한 추가 대기
        #     await page.wait_for_load_state('domcontentloaded')
        #     await asyncio.sleep(1)  # 페이지 완전 로드 대기
            
        #     price_element = await page.query_selector(SELECTORS['price_element'])
        #     if price_element:
        #         pd_price = await price_element.text_content()
        #         log.info(f"Step 2: PD price extracted: '{pd_price}'")
        #     else:
        #         log.warning("Price element not found on PD page")
        # except Exception as e:
        #     # Execution context destroyed 에러 처리
        #     if "Execution context was destroyed" in str(e):
        #         log.warning("Price extraction failed due to page navigation - retrying after page stabilization")
        #         try:
        #             # 페이지 안정화 대기
        #             await page.wait_for_load_state('domcontentloaded')
        #             await asyncio.sleep(2)
                    
        #             # 재시도
        #             price_element = await page.query_selector(SELECTORS['price_element'])
        #             if price_element:
        #                 pd_price = await price_element.text_content()
        #                 log.info(f"Step 2: PD price extracted (retry): '{pd_price}'")
        #             else:
        #                 log.warning("Price element not found on PD page (retry)")
        #         except Exception as retry_e:
        #             log.error(f"Price extraction retry also failed: {retry_e}")
        #     else:
        #         log.error(f"Error extracting price from PD page: {e}")
        
        # 3단계: PD 타입 검증 (서브함수 호출)
        log.info("Step 3: PD type detection")
        try:
            pd_type = await detect_pd_type(page)
            pd_node.pd_type = pd_type
        except Exception as e:
            log.error(f"Error in PD type detection: {e}")
            pd_node.pd_type = "Unknown"
        
        # 4단계: PD 타입에 따른 이동
        log.info("Step 4: Navigation based on PD type")
        if pd_node.pd_type == "Simple":
            try:
                log.info("Step 4: Starting navigation to Buy PD for Simple PD")
                navigation_success = await navigate_to_buy_pd(page)
                if navigation_success:
                    log.info("Step 4: Navigation successful - scrolling for lazy load")
                    await scroll_for_lazyload(page)
                else:
                    log.warning("Step 4: Failed to navigate to Buy PD page")
            except Exception as e:
                log.error(f"Step 4: Error during navigation: {e}")
        else:
            log.info("Step 4: Standard PD - no navigation needed")
        
        # # 5단계: Dimension & Link 병렬 검증
        # # WHY: 병렬 실행이 가능한 검증들을 묶어 총 소요 시간을 단축합니다.
        # # >>> chunk: parallel_validation
        # log.info("Step 5: Parallel validation(Dimension & Link)")
        # validation_tasks = []

        # # 5.1단계: Dimension 확인 및 예시값 수집
        # log.info("Step 5.1: Dimension area check")
        # has_dimension = False
        # can_test_dimension = False
        # dimension_examples = []
        # try:
        #     has_dimension, can_test_dimension, dimension_examples = await check_dimension_area(page)
        #     pd_node.is_dimension = has_dimension  # Dimension 영역 존재 여부 설정
        #     if has_dimension and can_test_dimension and dimension_examples:
        #         dimension_task = asyncio.create_task(validate_dimension_fit(page, dimension_examples))
        #         validation_tasks.append(("dimension", dimension_task))
        # except Exception as e:
        #     log.error(f"Error checking dimension area: {e}")
        #     pd_node.is_dimension = False
        
        # # 5.2단계: 링크 추출
        # log.info("Step 5.2: Link collection")
        # # 페이지 안정화를 위한 추가 대기 제거
        # links = []
        # try:
        #     links, link_error_msg = await collect_links(page)
        #     if links:
        #         link_task = asyncio.create_task(run_link_validation(page, links))
        #         validation_tasks.append(("link", link_task))
        #         if link_error_msg:
        #             pd_node.link_validate_desc = link_error_msg
        #     else:
        #         pd_node.link_validate = True
        #         pd_node.link_validate_desc = link_error_msg
        # except Exception as e:
        #     # 링크 추출 실패 시 실패 처리
        #     log.error(f"Unexpected error in link collection: {e}")
        #     pd_node.link_validate = False
        #     pd_node.link_validate_desc = f"Unexpected error in link collection: {e}"

        # # 병렬 실행 및 결과 수집
        # if validation_tasks:
        #     try:
        #         # 모든 태스크를 동시에 실행하고 완료될 때까지 대기
        #         task_names, tasks = zip(*validation_tasks)
        #         results = await asyncio.gather(*tasks, return_exceptions=True)
                
        #         # 결과 처리
        #         for task_name, result in zip(task_names, results):
        #             if isinstance(result, Exception):
        #                 log.error(f"Error in {task_name} validation: {result}")
        #                 if task_name == "dimension":
        #                     pd_node.dimension_validate = False
        #                     pd_node.dimension_validate_desc = {"error": str(result)}
        #                 elif task_name == "link":
        #                     pd_node.link_validate = False
        #                     pd_node.link_validate_desc = {"total_links": len(links), "failed_links": [str(result)]}
        #             else:
        #                 if task_name == "dimension":
        #                     pd_node.dimension_validate = result['dimension_validate']
        #                     pd_node.dimension_validate_desc = result['dimension_validate_desc']
        #                 elif task_name == "link":
        #                     pd_node.link_validate = result['link_validate']
        #                     pd_node.link_validate_desc = result['link_validate_desc']
                
        #     except Exception as e:
        #         log.error(f"Error in parallel validation execution: {e}")
        #         # 개별 태스크 결과 확인
        #         for task_name, task in validation_tasks:
        #             try:
        #                 if not task.done():
        #                     task.cancel()
        #             except Exception as cancel_error:
        #                 pass
        # # <<<

        # 5.5단계: PD 버튼 상태 사전 검증
        log.info("Step 5.5: PD button validation")
        button_validation_passed = True
        try:
            # 버튼 컨테이너가 DOM에 나타날 때까지 대기 (최대 10초)
            log.debug("Step 5.5: Waiting for button container to appear")
            button_container = await page.wait_for_selector(
                SELECTORS['pd_type_container'],
                state='attached',
                timeout=10000
            )
            
            if button_container:
                log.debug("Step 5.5: Button container found, looking for button element")
                # 컨테이너 내의 a 태그가 나타날 때까지 추가 대기
                await page.wait_for_selector(
                    f"{SELECTORS['pd_type_container']} a",
                    state='visible',
                    timeout=5000
                )
                button_element = await button_container.query_selector('a')
                
                if button_element:
                    log.debug("Step 5.5: Button element found, validating properties")
                    # 조건 1: aria-disabled="true" 확인
                    aria_disabled = await button_element.get_attribute('aria-disabled')
                    if aria_disabled == 'true':
                        log.warning("Step 5.5: Button is disabled (aria-disabled=true)")
                        pd_node.transition_validate = False
                        pd_node.transition_validate_desc = "Button is disabled (aria-disabled=true)"
                        button_validation_passed = False
                    else:
                        # 조건 2: 알려진 선택자(Standard/Simple)인지 확인
                        log.debug("Step 5.5: Checking button type (Standard or Simple)")
                        
                        # Standard PD 버튼 확인 (타임아웃 3초로 짧게 설정)
                        is_standard_button = None
                        try:
                            is_standard_button = await page.wait_for_selector(
                                SELECTORS['standard_pd_button'],
                                state='attached',
                                timeout=3000
                            )
                            log.debug("Step 5.5: Standard PD button type detected")
                        except:
                            log.debug("Step 5.5: Not a Standard PD button")
                        
                        # Simple PD 버튼 확인 (타임아웃 3초로 짧게 설정)
                        is_simple_button = None
                        try:
                            is_simple_button = await page.wait_for_selector(
                                SELECTORS['simple_pd_button'],
                                state='attached',
                                timeout=3000
                            )
                            log.debug("Step 5.5: Simple PD button type detected")
                        except:
                            log.debug("Step 5.5: Not a Simple PD button")
                        
                        if not is_standard_button and not is_simple_button:
                            # 알려진 선택자가 아닌 경우 an-la 값 추출
                            an_la_value = await button_element.get_attribute('an-la')
                            log.warning(f"Step 5.5: Unknown button type with an-la='{an_la_value}'")
                            pd_node.transition_validate = False
                            pd_node.transition_validate_desc = f"Unknown button type: an-la='{an_la_value}'"
                            button_validation_passed = False
                        else:
                            button_type = "Standard" if is_standard_button else "Simple"
                            log.info(f"Step 5.5: Button validation passed - {button_type} PD button type found")
                else:
                    log.warning("Step 5.5: No button element found in container")
                    pd_node.transition_validate = False
                    pd_node.transition_validate_desc = "No button element found in container"
                    button_validation_passed = False
            else:
                log.warning("Step 5.5: Button container not found after waiting")
                pd_node.transition_validate = False
                pd_node.transition_validate_desc = "Button container not found"
                button_validation_passed = False
        except Exception as e:
            log.error(f"Error in button validation: {e}")
            pd_node.transition_validate = False
            pd_node.transition_validate_desc = f"Button validation error: {str(e)}"
            button_validation_passed = False

        # 6단계: 카트로 이동 (버튼 검증 통과 시에만 실행)
        log.info("Step 6: Navigation to cart")
        cart_navigation_success = False
        cart_price_text = None
        
        if button_validation_passed:
            try:
                # PD 타입에 따라 적절한 카트 버튼 클릭
                if pd_node.pd_type == "Simple":
                    log.info("Step 6: Simple PD - clicking cart button in Buy PD")
                    cart_button = await page.query_selector(SELECTORS['buy_pd_cart_button'])
                    if cart_button:
                        log.debug(f"Step 6: Cart button found at selector: {SELECTORS['buy_pd_cart_button']}")
                        await cart_button.evaluate("element => element.click()")
                        log.debug("Step 6: Cart button clicked successfully")
                        
                        # 임시 코드: Simple PD에서 스크롤 후 추가 "go to cart" 버튼 클릭
                        log.info("Step 6: Simple PD - scrolling to bottom and clicking go to cart button")
                        try:
                            # 페이지 맨 아래로 스크롤
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            log.debug("Step 6: Scrolled to bottom of page")
                            
                            # 잠시 대기 후 go to cart 버튼 찾기
                            await asyncio.sleep(2)
                            go_to_cart_button = await page.query_selector('a.cta.cta--contained.cta--emphasis.cta--2line.add-special-tagging.js-buy-now.tg-continue[an-la="add-on:go to cart"]')
                            if go_to_cart_button:
                                log.debug("Step 6: Go to cart button found after scrolling")
                                await go_to_cart_button.evaluate("element => element.click()")
                                log.debug("Step 6: Go to cart button clicked successfully")
                            else:
                                log.warning("Step 6: Go to cart button not found after scrolling")
                        except Exception as e:
                            log.warning(f"Step 6: Error scrolling and clicking go to cart button: {e}")
                        
                        cart_navigation_success = True
                    else:
                        log.warning("Step 6: Cart button not found in Buy PD")
                        cart_navigation_success = False
                else:
                    log.info("Step 6: Standard PD - clicking Add to basket button")
                    cart_button = await page.query_selector(SELECTORS['standard_pd_button'])
                    if cart_button:
                        log.debug(f"Step 6: Add to basket button found at selector: {SELECTORS['standard_pd_button']}")
                        await cart_button.click()
                        log.debug("Step 6: Add to basket button clicked successfully")
                        cart_navigation_success = True
                    else:
                        log.warning("Step 6: Add to basket button not found")
                        cart_navigation_success = False
                
                # 카트 버튼 클릭 성공 시 공통 후처리
                if cart_navigation_success:
                    # 화면이 뜰 때까지 대기 및 지연
                    await page.wait_for_load_state('domcontentloaded')
                    await asyncio.sleep(15)

                    # 쿠키 동의 버튼이 뜰 때까지 대기
                    try:
                        cookie_consent_button = await page.query_selector('#truste-consent-button')
                        if cookie_consent_button:
                            await cookie_consent_button.click()
                            log.info("Step 6: Cookie consent button clicked")
                        else:
                            log.info("Step 6: Cookie consent button not found")
                    except Exception as e:
                        log.warning(f"Error handling cookie consent: {e}")
                    
                    # 국가 선택 모달 처리
                    try:
                        log.info("Step 6: Checking for country selector modal")
                        # 모달이 나타날 때까지 잠시 대기
                        await asyncio.sleep(2)
                        
                        # 국가 선택 모달 확인
                        country_modal = await page.query_selector(SELECTORS['country_selector_modal'])
                        if country_modal:
                            log.info("Step 6: Country selector modal found")
                            
                            # 체크박스 찾기 및 체크
                            checkbox = await page.query_selector(SELECTORS['country_selector_checkbox'])
                            if checkbox:
                                # 체크박스가 이미 체크되어 있는지 확인
                                is_checked = await checkbox.is_checked()
                                if not is_checked:
                                    await checkbox.click()
                                    log.info("Step 6: Country selector checkbox checked")
                                else:
                                    log.info("Step 6: Country selector checkbox already checked")
                            else:
                                log.warning("Step 6: Country selector checkbox not found")
                            
                            # Cancel 버튼 클릭
                            cancel_button = await page.query_selector(SELECTORS['country_selector_cancel'])
                            if cancel_button:
                                await cancel_button.click()
                                log.info("Step 6: Country selector cancel button clicked")
                                # 모달이 닫힐 때까지 대기
                                await asyncio.sleep(2)
                            else:
                                log.warning("Step 6: Country selector cancel button not found")
                        else:
                            log.info("Step 6: Country selector modal not found")
                    except Exception as e:
                        log.warning(f"Error handling country selector modal: {e}")
                    
                    # 모달 처리 후 페이지 안정화 대기
                    log.info("Step 6: Waiting for page stabilization after modal handling")
                    await asyncio.sleep(3)
                    
                    # 가격 요소가 visible한 상태가 될 때까지 대기
                    try:
                        log.debug(f"Step 6: Waiting for cart price element: {SELECTORS['cart_price_element']}")
                        
                        # 먼저 attached 상태 확인 (DOM에 존재하는지)
                        await page.wait_for_selector(
                            SELECTORS['cart_price_element'], 
                            state='attached'
                        )
                        log.debug(f"Step 6: Cart price element is attached to DOM")
                        
                        # Angular 렌더링 완료 대기
                        await asyncio.sleep(2)
                        
                        # visible 상태 확인 시도 (최대 3회 재시도)
                        for attempt in range(3):
                            try:
                                log.debug(f"Step 6: Attempt {attempt + 1}/3 - Checking if cart price element is visible")
                                cart_price_element = await page.query_selector(SELECTORS['cart_price_element'])
                                
                                if cart_price_element:
                                    # 요소가 보이는지 확인
                                    is_visible = await cart_price_element.is_visible()
                                    log.debug(f"Step 6: Cart price element visibility: {is_visible}")
                                    
                                    if is_visible:
                                        cart_price_text = await cart_price_element.text_content()
                                        log.info(f"Step 7: Cart price loaded: '{cart_price_text.strip()}'")
                                        log.debug(f"Step 6: Cart price element found and loaded successfully")
                                        pd_node.transition_validate = True
                                        pd_node.transition_validate_desc = ""
                                        break
                                    else:
                                        # 보이지 않으면 스크롤 시도
                                        log.debug(f"Step 6: Cart price element not visible, trying to scroll into view")
                                        await cart_price_element.scroll_into_view_if_needed()
                                        await asyncio.sleep(2)
                                else:
                                    log.warning(f"Step 6: Cart price element not found in attempt {attempt + 1}")
                                    
                                if attempt < 2:
                                    await asyncio.sleep(3)
                            except Exception as retry_e:
                                log.warning(f"Step 6: Attempt {attempt + 1} failed: {retry_e}")
                                if attempt < 2:
                                    await asyncio.sleep(3)
                        
                        # 모든 재시도 실패
                        if not cart_price_text:
                            log.warning(f"Step 6: Cart price element found but not visible after all retries")
                            pd_node.transition_validate = False
                            pd_node.transition_validate_desc = "Cart navigation succeeded but price element not visible"
                        
                    except Exception as e:
                        log.warning(f"Cart price element not found within timeout: {e}")
                        pd_node.transition_validate = False
                        pd_node.transition_validate_desc = f"Cart navigation succeeded but price element not found: {str(e)}"
                else:
                    pd_node.transition_validate = False
                    pd_node.transition_validate_desc = "Cart button not found"
                    
            except Exception as e:
                log.error(f"Error navigating to cart: {e}")
                pd_node.transition_validate = False
                pd_node.transition_validate_desc = f"Navigation error: {str(e)}"
        else:
            log.info("Step 6: Skipping cart navigation - button validation failed")
        
        # 7단계: 카트 가격과 PD 가격 검증
        log.info("Step 7: Price match validation")
        # log.info(f"Step 7: PD price available: {bool(pd_price)} ('{pd_price}')")
        log.info(f"Step 7: Cart navigation successful: {pd_node.transition_validate}")
        # log.info(f"Step 7: Cart price text available: {bool(cart_price_text)}")

        # if pd_price and pd_node.transition_validate and cart_price_text:
        #     try:
        #         price_result = await validate_price_match(page, pd_price, cart_price_text.strip())
        #         pd_node.price_validate = price_result['price_validate']
        #         pd_node.price_validate_desc = price_result['price_validate_desc']

        #     except Exception as e:
        #         log.error(f"Error in price validation: {e}")
        #         pd_node.price_validate = False
        #         pd_node.price_validate_desc = f"Price validation error: {str(e)}"
        # else:
        #     reason = []
        #     if not pd_price:
        #         reason.append("PD price not available")
        #     if not pd_node.transition_validate:
        #         reason.append("Cart navigation failed")
        #     if not cart_price_text:
        #         reason.append("Cart price text not available")
        #     log.warning(f"Step 7: Price validation failed - {', '.join(reason)}")
            
        #     # transition이 실패하면 price도 실패해야 함
        #     pd_node.price_validate = False
        #     pd_node.price_validate_desc = "Price validation failed because cart navigation failed"
        
        # 8단계: 카트에서 상품 삭제 (가격 검증 완료 후)
        log.info("Step 8: Removing item from cart")
        try:
            # 카트 삭제 버튼 찾기
            log.debug(f"Step 8: Looking for remove button at selector: {SELECTORS['cart_remove_button']}")
            remove_button = await page.query_selector(SELECTORS['cart_remove_button'])
            
            # 삭제 버튼을 찾았는지 확인
            if remove_button:
                log.debug("Step 8: Remove button found")
                # 버튼이 클릭 가능한 상태인지 확인
                try:
                    is_visible = await remove_button.is_visible()
                    is_enabled = not await remove_button.evaluate('button => button.disabled')
                    log.debug(f"Step 8: Remove button state - visible: {is_visible}, enabled: {is_enabled}")
                    
                    if is_visible and is_enabled:
                        # 삭제 버튼 클릭
                        await remove_button.click()
                        log.debug("Step 8: Remove button clicked successfully")
                
                        # 삭제 확인 모달 처리
                        try:
                            log.info("Step 8: Checking for remove confirmation modal")
                            # 모달이 나타날 때까지 잠시 대기
                            await asyncio.sleep(1)
                            
                            # 삭제 확인 모달 확인
                            confirm_modal = await page.query_selector(SELECTORS['cart_remove_confirm_modal'])
                            if confirm_modal:
                                log.info("Step 8: Remove confirmation modal found")
                                
                                # Yes 버튼 클릭
                                yes_button = await page.query_selector(SELECTORS['cart_remove_confirm_yes'])
                                if yes_button:
                                    await yes_button.click()
                                    log.info("Step 8: Remove confirmation 'Yes' button clicked")
                                    # 모달이 닫히고 삭제가 완료될 때까지 대기
                                    await asyncio.sleep(2)
                                else:
                                    log.warning("Step 8: Remove confirmation 'Yes' button not found")
                            else:
                                log.info("Step 8: Remove confirmation modal not found")
                        except Exception as e:
                            log.warning(f"Error handling remove confirmation modal: {e}")
                        
                        # 삭제 완료를 위한 대기
                        await asyncio.sleep(1.0)
                    else:
                        log.debug("Step 8: Remove button not clickable (not visible or disabled)")
                        
                except Exception as e:
                    log.error(f"Error clicking remove button: {e}")
                    log.debug(f"Step 8: Remove button click failed: {str(e)}")
            else:
                log.debug(f"Step 8: Remove button not found at selector: {SELECTORS['cart_remove_button']}")
                    
        except Exception as e:
            log.error(f"Error removing item from cart: {e}", exc_info=True)
            log.debug(f"Step 8: Cart removal process failed with error: {str(e)}")
            log.warning("Continuing with test despite cart removal failure")
        
        # 10단계: 최종 검증 완료
        log.info("Step 10: Final validation completion")
        return pd_node
        
    except Exception as e:
        log.error(f"Unexpected error in validate_pd_page: {e}")
        # 에러 발생 시에도 기본 PDNode 반환
        pd_node = PDNode(url)
        pd_node.pd_type = "Error"
        return pd_node


def save_pd_result_to_json(pd_result: PDNode, url: str, site_code: str) -> str:
    """
    검증 결과를 result/에 JSON으로 저장.

    간단 설명:
        - 목적: PD 검증 결과를 파일로 저장하고, 저장 경로를 반환합니다.
        - 입력: pd_result(PDNode), url(str), site_code(str, 예: "UK")
        - 출력: 저장된 JSON 파일 경로(str)
        - 주의: 디스크에 쓰기 수행(권한 필요), UTF-8/ensure_ascii=False/indent=2

    파라미터:
        pd_result (PDNode): 결과 객체.
        url (str): 대상 URL.
        site_code (str): 사이트 코드(예: UK).

    반환값:
        str: 저장된 파일 경로.

    예외: 파일/디렉터리 작업 실패 시 예외.
    전제조건: 쓰기 권한.
    사후조건: 파일 생성.
    부작용: 파일 시스템에 쓰기.

    AI 요청 템플릿(복붙 가능):
        - "파일명을 'SITE_YYYYMMDD_HHMMSS_taskid.json' 형식으로 저장할 수 있게 옵션을 추가해줘. 기존 형식도 유지해줘."
        - "저장에 실패하면 2초 간격으로 최대 3회까지 자동 재시도해줘. 모두 실패하면 파일 경로와 원인을 포함해 예외를 알려줘."
        - "결과 JSON에 선택적으로 'env' 섹션(Windows 버전, Python 버전)을 추가할 수 있게 해줘. 기존 구조는 깨지지 않게 유지해줘."

    예시:
        path = save_pd_result_to_json(node, url, "UK")
    """
    import json
    import os
    from datetime import datetime
    from pathlib import Path
    
    try:
        # result 폴더 생성
        result_dir = Path("result")
        result_dir.mkdir(exist_ok=True)
        
        # 현재 시간을 파일명에 포함
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{site_code}_{timestamp}.json"
        file_path = result_dir / filename
        
        # PD 결과를 딕셔너리로 변환
        result_data = {
            "url": url,
            "site_code": site_code,
            "timestamp": timestamp,
            "result": pd_result.to_dict()
        }
        
        # JSON 파일로 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        log.info(f"Step 10: PD test result saved to: {file_path}")
        return str(file_path)
        
    except Exception as e:
        log.error(f"Failed to save PD result to JSON: {e}")
        raise
