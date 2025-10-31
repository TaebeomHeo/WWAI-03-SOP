"""
Dimension 영역 검증 모듈

환경 및 전제 조건:
- Windows 환경, Python 3.11.9 / Playwright Page 객체 사용.

목적:
- Dimension 영역의 존재/테스트 가능 여부를 확인하고, Fit/Not Fit 시나리오를 검증합니다.

주요 기능:
- check_dimension_area: Dimension 영역 탐지 및 예시값 수집
- validate_dimension_fit: Fit/Not Fit 시나리오 검증
- close_dimension_popup: 팝업 닫기
"""

import asyncio
import re
import random
from typing import List, Dict, Union
from playwright.async_api import Page
from utility.orangelogger import log
from pd_modules.selectors import SELECTORS


async def check_dimension_area(page: Page) -> tuple[bool, bool, list[str]]:
    """
    Dimension 영역 존재/테스트 가능 여부 확인 및 예시값 수집.
    
    각 단계별 타임아웃:
    - Dimension area 탐지: 10초
    - Start measuring 버튼 탐지: 10초
    - Dimension 팝업 표시 대기: 20초
    """
    try:
        # Dimension area 탐지 (타임아웃: 10초)
        try:
            dimension_area = await page.wait_for_selector(SELECTORS['dimension_area'], timeout=10000, state='attached')
        except Exception:
            log.info("Step 5.1: Dimension area detection result: Not found (timeout)")
            return False, False, []
        
        if not dimension_area:
            log.info("Step 5.1: Dimension area detection result: Not found")
            return False, False, []
        
        # Start measuring 버튼 탐지 (타임아웃: 10초)
        try:
            start_button = await page.wait_for_selector(SELECTORS['start_measuring_button'], timeout=10000, state='visible')
        except Exception:
            log.warning("Step 5.1: Dimension area detection result: Found but start button not found (timeout)")
            return True, False, []
        
        if not start_button:
            log.warning("Step 5.1: Dimension area detection result: Found but not testable")
            return True, False, []
        
        # Start measuring 버튼 클릭
        await start_button.click()
        log.debug("Step 5.1: Start measuring button clicked, waiting for popup...")
        
        # Dimension 팝업 표시 대기 (타임아웃: 20초)
        try:
            await page.wait_for_selector(SELECTORS['dimension_popup'], timeout=20000, state='visible')
            log.debug("Step 5.1: Dimension popup opened successfully")
        except Exception as e:
            log.warning(f"Step 5.1: Dimension area detection result: Found but popup failed to open (timeout after 20s): {e}")
            return True, False, []
        
        # 예시 값 수집
        example_elements = await page.query_selector_all(SELECTORS['dimension_examples'])
        if not example_elements:
            await close_dimension_popup(page)
            log.warning("Step 5.1: Dimension area detection result: Found but no examples available")
            return True, False, []
        
        examples: List[str] = []
        for element in example_elements:
            text = await element.text_content()
            if text and text.strip():
                examples.append(text.strip())
                log.debug(f"Step 5.1: Found dimension example: {text.strip()}")
        
        log.info(f"Step 5.1: Dimension area detection result: Found and testable with {len(examples)} examples")
        return True, True, examples
    except Exception as e:
        await close_dimension_popup(page)
        raise Exception(f"Error during dimension area check: {e}")


async def close_dimension_popup(page: Page):
    """
    Dimension 팝업을 닫습니다.
    """
    try:
        close_button = await page.query_selector('button[data-js-action="closeDimensionsPopup"]')
        if close_button:
            await close_button.click()
        else:
            log.warning("Close button not found in dimension popup")
    except Exception as e:
        log.error(f"Error closing dimension popup: {e}")


async def validate_dimension_fit(page: Page, dimension_examples: List[str]) -> Dict[str, Union[bool, str, Dict]]:
    """
    Dimension 팝업에서 Fit/Not Fit 조합 테스트를 수행합니다.
    """
    try:
        example_values: List[int] = []
        try:
            for example_text in dimension_examples:
                match = re.search(r'Ex:\s*(\d+)', example_text)
                if match:
                    example_values.append(int(match.group(1)))
            if not example_values:
                return {"dimension_validate": False, "dimension_validate_desc": "error: no example values"}
        except Exception as e:
            log.error(f"Error parsing example values: {e}")
            return {"dimension_validate": False, "dimension_validate_desc": f"error: parse examples failed - {e}"}
        input_elements = await page.query_selector_all(SELECTORS['dimension_inputs'])
        if not input_elements:
            return {"dimension_validate": False, "dimension_validate_desc": "error: input fields not found"}
        log.info("Starting Fit validation...")
        fit_combination: List[int] = []
        for i, example_value in enumerate(example_values):
            if i < len(input_elements):
                fit_value = int(example_value * random.uniform(1.1, 1.5))
                fit_combination.append(fit_value)
                try:
                    if i == 0:
                        await page.click('#spaceWidth')
                        await page.type('#spaceWidth', str(fit_value), delay=100)
                    elif i == 1:
                        await page.click('#spaceHeight')
                        await page.type('#spaceHeight', str(fit_value), delay=100)
                    elif i == 2:
                        await page.click('#spaceDepth')
                        await page.type('#spaceDepth', str(fit_value), delay=100)
                    log.debug(f"Input Fit value {i+1}: {fit_value}")
                    await asyncio.sleep(1.0)
                except Exception as e:
                    log.error(f"Error filling fit value {i+1}: {e}")
        fit_result = False
        try:
            try:
                check_fit_button = await page.query_selector('button.cta.cta--contained.cta--black:not(.cta--disabled)[an-la*="check fit"]')
                if check_fit_button:
                    is_visible = await check_fit_button.is_visible()
                    is_enabled = not await check_fit_button.evaluate('button => button.disabled')
                    if is_visible and is_enabled:
                        await check_fit_button.click()
                        await asyncio.sleep(2)
            except Exception as e:
                log.error(f"Error with Check Fit button: {e}")
            fit_result_element = await page.query_selector(SELECTORS['fit_result'])
            fit_result = fit_result_element is not None
            log.info(f"Step 5: Fit result: {fit_result}")
        except Exception as e:
            log.error(f"Error checking fit result: {e}")
        try:
            field_ids = ['#spaceWidth', '#spaceHeight', '#spaceDepth']
            for i, field_id in enumerate(field_ids):
                try:
                    input_field = await page.query_selector(field_id)
                    if not input_field:
                        continue
                    delete_button = await page.query_selector(f'{field_id} ~ button.text-field-v2__input-icon.delete')
                    if not delete_button:
                        delete_button = await page.query_selector(f'[class*="text-field-v2"] {field_id} ~ button.text-field-v2__input-icon.delete')
                    if delete_button:
                        log.debug(f"Delete button found for {field_id}, clicking...")
                        try:
                            await delete_button.click()
                            log.debug(f"Delete button clicked for {field_id}")
                        except Exception as e:
                            log.warning(f"Failed to click delete button for {field_id}: {e}")
                        await asyncio.sleep(0.5)
                    else:
                        log.warning(f"Delete button not found for {field_id}")
                except Exception as e:
                    log.error(f"Error clearing input field {i+1}: {e}")
                    continue
        except Exception as e:
            log.warning(f"Error during input clearing process: {e}")
        log.info("Starting Not Fit validation...")
        non_fit_combination: List[int] = []
        for i, example_value in enumerate(example_values):
            if i < len(input_elements):
                non_fit_value = int(example_value * random.uniform(0.8, 1.0))
                non_fit_combination.append(non_fit_value)
                try:
                    await page.wait_for_selector(f'#spaceWidth, #spaceHeight, #spaceDepth', timeout=0, state='visible')
                    if i == 0:
                        await page.click('#spaceWidth')
                        await page.type('#spaceWidth', str(non_fit_value), delay=100)
                    elif i == 1:
                        await page.click('#spaceHeight')
                        await page.type('#spaceHeight', str(non_fit_value), delay=100)
                    elif i == 2:
                        await page.click('#spaceDepth')
                        await page.type('#spaceDepth', str(non_fit_value), delay=100)
                    log.debug(f"Input Not Fit value {i+1}: {non_fit_value}")
                    await asyncio.sleep(1.0)
                except Exception as e:
                    log.error(f"Error filling non-fit value {i+1}: {e}")
        non_fit_result = False
        try:
            try:
                check_fit_button = await page.query_selector('button.cta.cta--contained.cta--black:not(.cta--disabled)[an-la*="check fit"]')
                if check_fit_button:
                    is_visible = await check_fit_button.is_visible()
                    is_enabled = not await check_fit_button.evaluate('button => button.disabled')
                    if is_visible and is_enabled:
                        await check_fit_button.click()
                        await asyncio.sleep(2)
            except Exception as e:
                log.error(f"Error with Check Fit button for Not Fit test: {e}")
            non_fit_result_element = await page.query_selector(SELECTORS['not_fit_result'])
            non_fit_result = non_fit_result_element is not None
            log.info(f"Step 5: Not Fit result: {non_fit_result}")
        except Exception as e:
            log.error(f"Error checking not-fit result: {e}")
        dimension_validate = fit_result and non_fit_result
        
        # dimension의 경우 validate 결과와 상관없이 실제 입력한 값을 항상 보여줌
        attempt_str = (
            f"fit: {fit_combination}, not_fit: {non_fit_combination}, examples: {example_values}"
        )
        
        if dimension_validate:
            log.info(f"Step 5: Dimension validation result: Success (Fit: {fit_result}, Not Fit: {non_fit_result})")
            dimension_validate_desc: Union[str, Dict] = attempt_str
        else:
            log.warning(f"Step 5: Dimension validation result: Failed (Fit: {fit_result}, Not Fit: {non_fit_result})")
            # 실패 시에도 시도한 조합 포함, 원인 맥락을 덧붙임
            reason_parts = []
            if not fit_result:
                reason_parts.append("fit result missing")
            if not non_fit_result:
                reason_parts.append("not fit result missing")
            reason = ", ".join(reason_parts) if reason_parts else "unknown"
            dimension_validate_desc = f"{attempt_str}, reason: {reason}"
        try:
            await close_dimension_popup(page)
        except Exception as e:
            log.warning(f"Error closing dimension popup after validation: {e}")
        return {"dimension_validate": dimension_validate, "dimension_validate_desc": dimension_validate_desc}
    except Exception as e:
        log.error(f"Unexpected error in validate_dimension_fit: {e}")
        return {"dimension_validate": False, "dimension_validate_desc": f"error: {e}"}
