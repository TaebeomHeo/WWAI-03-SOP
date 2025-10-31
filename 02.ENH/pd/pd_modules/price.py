"""
기본 요소 및 가격 검증 모듈

환경 및 전제 조건:
- Windows 환경, Python 3.11.9 / Playwright Page 객체 사용.

목적:
- 기본 요소(rating/가격) 검증과 카트 가격 일치 검증을 제공합니다.

주요 기능:
- validate_basic_elements: rating/가격 요소 검증 및 가격 추출
- validate_price_match: PD 가격과 카트 가격 일치 검증
"""

import re
from typing import Dict, Union
from playwright.async_api import Page
from utility.orangelogger import log
from pd_modules.selectors import SELECTORS


async def validate_basic_elements(page: Page) -> dict:
    """
    기본 요소(rating/가격) 검증 및 가격 텍스트 추출.
    """
    try:
        rating_check = False
        try:
            rating_container = await page.query_selector(SELECTORS['rating_container'])
            if rating_container:
                rating_element = await rating_container.query_selector('.rating')
                rating_check = rating_element is not None
                if rating_check:
                    log.info("Step 1: Rating element validation result: Found")
                else:
                    log.warning("Step 1: Rating element validation result: Not found")
            else:
                log.warning("Step 1: Rating element validation result: Container not found")
        except Exception as e:
            log.error(f"Error checking rating element: {e}")
            rating_check = False
        price_check = False
        price_info = ""
        try:
            price_element = await page.query_selector(SELECTORS['price_element'])
            if price_element:
                price_info = await price_element.text_content()
                price_check = True
                log.info(f"Step 2: Price element validation result: Found - '{price_info.strip() if price_info else ''}'")
            else:
                log.warning("Step 2: Price element validation result: Not found")
        except Exception as e:
            log.error(f"Error extracting price: {e}")
            price_check = False
            price_info = ""
        return {"rating_check": rating_check, "price_check": price_check, "price_info": price_info}
    except Exception as e:
        log.error(f"Unexpected error in validate_basic_elements: {e}")
        return {"rating_check": False, "price_check": False, "price_info": ""}


async def validate_price_match(page: Page, pd_price: str, cart_price_text: str) -> Dict[str, Union[bool, str]]:
    """
    PD 가격과 카트 가격을 정규화 후 비교.
    """
    try:
        def normalize_price(price: str) -> str:
            return re.sub(r'[ ,\s]', '', price.strip())
        if not pd_price or pd_price.strip() == "":
            log.warning("PD price is empty or None")
            return {"price_validate": False, "price_validate_desc": "PD price is empty or None"}
        try:
            pd_price_normalized = normalize_price(pd_price)
            log.debug(f"PD price normalized: '{pd_price}' -> '{pd_price_normalized}'")
        except Exception as e:
            log.error(f"Error normalizing PD price: {e}")
            return {"price_validate": False, "price_validate_desc": f"Error normalizing PD price: {str(e)}"}
        if not cart_price_text or cart_price_text.strip() == "":
            log.warning("Cart price text not provided or empty")
            return {"price_validate": False, "price_validate_desc": "Cart price text not provided or empty"}
        cart_price = cart_price_text.strip()
        if not cart_price:
            log.warning("Cart price text is empty")
            return {"price_validate": False, "price_validate_desc": "Cart price text is empty"}
        log.debug(f"Cart price received: '{cart_price}'")
        try:
            cart_price_normalized = normalize_price(cart_price)
            log.debug(f"Cart price normalized: '{cart_price}' -> '{cart_price_normalized}'")
        except Exception as e:
            log.error(f"Error normalizing cart price: {e}")
            return {"price_validate": False, "price_validate_desc": f"Error normalizing cart price: {str(e)}"}
        log.info(f"Comparing prices - PD: '{pd_price_normalized}' vs Cart: '{cart_price_normalized}'")
        price_match = pd_price_normalized == cart_price_normalized
        if price_match:
            log.info(f"Step 7: Price validation result: Success - prices match: '{pd_price_normalized}'")
            return {"price_validate": True, "price_validate_desc": ""}
        else:
            log.warning(f"Step 7: Price validation result: Failed - prices do not match (PD: '{pd_price_normalized}', Cart: '{cart_price_normalized}')")
            return {"price_validate": False, "price_validate_desc": f"Prices do not match - PD: {pd_price_normalized}, Cart: {cart_price_normalized}"}
    except Exception as e:
        log.error(f"Unexpected error in validate_price_match: {e}")
        return {"price_validate": False, "price_validate_desc": f"Unexpected error: {str(e)}"}
