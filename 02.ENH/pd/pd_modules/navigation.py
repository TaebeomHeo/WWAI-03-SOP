"""
네비게이션 및 PD 타입 판별 모듈

환경 및 전제 조건:
- Windows 환경, Python 3.11.9 / Playwright Page 객체 사용.

목적:
- PD 타입 자동 감지 및 Simple → Buy PD 전환 상태를 확인합니다.

주요 기능:
- detect_pd_type: PD 타입 자동 감지
- navigate_to_buy_pd: Simple PD에서 Buy PD 전환 확인
"""

from typing import List, Dict, Union
from playwright.async_api import Page
from utility.orangelogger import log
from pd_modules.selectors import SELECTORS
from utility.aem import scroll_for_lazyload  # 사용될 수 있으므로 노출 유지


async def detect_pd_type(page: Page) -> str:
    """
    PD 타입을 자동으로 감지합니다.

    Standard PD("add to cart" 버튼) 또는 Simple PD("buy now" 버튼)를 구분합니다.

    파라미터:
        page: Playwright Page 객체
        
    반환값:
        str: "Standard" 또는 "Simple"

    예외 처리:
        - PD 타입 컨테이너가 없거나 두 버튼 모두 없을 경우 ValueError를 발생시킵니다.
        - Playwright 상호작용 오류 등 기타 예외는 원인 메시지를 포함해 그대로 전달합니다.

    사용 예시:
        pd_type = await detect_pd_type(page)
        # pd_type == "Standard" 또는 "Simple"
    """
    try:
        container = await page.query_selector(SELECTORS['pd_type_container'])
        if not container:
            raise ValueError("PD type container not found - cannot determine PD type")
        standard_button = await page.query_selector(SELECTORS['standard_pd_button'])
        if standard_button:
            log.info("Step 3: PD type detection result: Standard PD")
            return "Standard"
        simple_button = await page.query_selector(SELECTORS['simple_pd_button'])
        if simple_button:
            log.info("Step 3: PD type detection result: Simple PD")
            return "Simple"
    except ValueError:
        error_msg = "Neither Standard nor Simple PD button found - cannot determine PD type"
        raise ValueError(error_msg)
    except Exception as e:
        raise Exception(e)


async def navigate_to_buy_pd(page: Page) -> bool:
    """
    Simple PD에서 Buy PD로 전환 여부 확인.

    간단 설명:
        - 목적: Simple PD에서 구매 페이지로 넘어갔는지 확인합니다.
        - 입력/출력: page(Page) → bool
    """
    try:
        log.info("Step 4.1: Looking for Simple PD button")
        simple_pd_button = await page.query_selector(SELECTORS['simple_pd_button'])
        if not simple_pd_button:
            log.warning("Step 4.1: Simple PD button not found")
            return False
        
        log.info("Step 4.2: Clicking Simple PD button")
        try:
            # JavaScript로 클릭 이벤트 실행 (href="javascript:;" 처리)
            await simple_pd_button.evaluate("element => element.click()")
            log.info("Step 4.2: Simple PD button clicked successfully")
        except Exception as e:
            log.error(f"Step 4.2: Error clicking Simple PD button: {e}")
            return False
        
        log.info("Step 4.3: Waiting for Buy PD page to load")
        try:
            # Buy PD 페이지에서 카트 버튼이 나타날 때까지 대기
            await page.wait_for_selector(
                SELECTORS['buy_pd_cart_button'], 
                state='visible',
                timeout=10000
            )
            log.info("Step 4.3: Buy PD page loaded and cart button found")
            return True
            
        except Exception as e:
            log.error(f"Step 4.3: Error during Buy PD navigation: {e}")
            return False
    except Exception as e:
        log.error(f"Step 4: Unexpected error during navigation to Buy PD: {e}")
        return False
