"""
URL 수집 및 검증 모듈

환경 및 전제 조건:
- Windows 환경, Python 3.11.9 / Playwright Page 객체 사용.

목적:
- buying_tool_area 내 URL을 수집/정제하고, 팝업 관련 URL을 필터링합니다.

주요 기능:
- collect_links: 영역 내 URL 수집 및 절대경로화
- is_valid_link: URL 유효성 필터
- run_link_validation: URL 병렬 상태 검증
"""

import asyncio
from typing import List, Tuple, Dict, Union
from urllib.parse import urlparse
from playwright.async_api import Page
from utility.orangelogger import log
from utility.utils import refine_url
from pd_modules.selectors import SELECTORS


async def collect_links(page: Page) -> tuple[list[str], str]:
    """
    buying_tool_area 내 유효한 URL 수집 및 절대경로화.
    """
    try:
        current_url = page.url
        parsed_url = urlparse(current_url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        log.debug(f"Looking for buying tool area with selector: {SELECTORS['buying_tool_area']}")
        buying_tool_area = await page.query_selector(SELECTORS['buying_tool_area'])
        if not buying_tool_area:
            raise ValueError("Buying tool area not found")
        link_elements = await buying_tool_area.query_selector_all('* a[href]')
        if not link_elements:
            return [], "No link elements found in buying_tool_area"
        extracted_hrefs: List[str] = []
        valid_links: List[str] = []
        error_msg = ""
        for link_element in link_elements:
            try:
                # data-target-popup 속성이 있는 링크는 팝업이므로 제외
                data_target_popup = await link_element.get_attribute('data-target-popup')
                if data_target_popup:
                    log.debug(f"Skipping popup link with data-target-popup: {data_target_popup}")
                    continue
                
                # 링크가 페이지에서 visible한지 확인
                is_visible = await link_element.is_visible()
                if not is_visible:
                    log.debug("Skipping invisible link")
                    continue
                
                href = await link_element.get_attribute('href')
                if href:
                    href = href.strip()
                    # #, popup, image, javascript 제외
                    if (href and href != '#' and 
                        not href.startswith('javascript:') and 
                        'images.samsung.com' not in href):
                        refined_url = refine_url(href, base_domain)
                        valid_links.append(refined_url)
            except Exception as e:
                error_msg = f"Error extracting href from link element: {e}"
                continue
        unique_valid_links = list(set(valid_links))
        log.debug(f"Total valid refined URLs count: {len(unique_valid_links)}")
        for url in unique_valid_links:
            log.debug(f"Valid refined URL: {url}")
        return unique_valid_links, error_msg
    except Exception as e:
        log.error(f"Error in collect_links: {e}")
        raise ValueError(f"Link collection failed: {str(e)}")


async def run_link_validation(page: Page, links: List[str]) -> Dict[str, Union[bool, str]]:
    """
    URL들을 새 탭에서 열어 HTTP 상태를 병렬 검증.

    반환 형식:
        {
            "link_validate": bool,
            "link_validate_desc": str  # "valid: [...]; invalid: [...]; failed: [...]" (각 항목에 (코드, e) 포함)
        }
    """
    try:
        async def validate_single_link(link: str) -> Tuple[str, bool, Union[int, None], Union[str, None]]:
            try:
                new_page = await page.context.new_page()
                try:
                    response = await new_page.goto(link, timeout=20000, wait_until='domcontentloaded')
                    if response:
                        status_code = response.status
                        if status_code == 200:
                            return link, True, status_code, None
                        else:
                            return link, False, status_code, None
                    else:
                        return link, False, None, None
                except Exception as e:
                    return link, False, None, str(e)
                finally:
                    await new_page.close()
            except Exception as e:
                return link, False, None, str(e)

        results = await asyncio.gather(*[validate_single_link(link) for link in links], return_exceptions=True)

        valid_entries: List[str] = []
        invalid_entries: List[str] = []
        failed_entries: List[str] = []

        for result in results:
            if isinstance(result, Exception):
                log.error(f"Unexpected error in link validation: {result}")
                failed_entries.append("unknown (exception)")
                continue

            link, ok, status_code, err = result

            # 문자열로 표현할 (코드, e)
            code_str = str(status_code) if isinstance(status_code, int) else "no_response"
            err_str = err if err else "-"
            pair_str = f"{code_str}, {err_str}"

            if ok:
                valid_entries.append(f"{link} ({pair_str})")
                continue

            if isinstance(status_code, int):
                # 비-200 숫자 상태 코드는 invalid로 분류
                invalid_entries.append(f"{link} ({pair_str})")
            else:
                # no_response 또는 예외 메시지 등
                failed_entries.append(f"{link} ({pair_str})")

        link_validate = len(invalid_entries) == 0 and len(failed_entries) == 0

        # validate가 false일 때만 desc 생성
        if link_validate:
            link_validate_desc = ""
        else:
            parts: List[str] = []
            parts.append(f"valid: [{'; '.join(valid_entries)}]")
            if len(invalid_entries) > 0:
                parts.append(f"invalid: [{'; '.join(invalid_entries)}]")
            if len(failed_entries) > 0:
                parts.append(f"failed: [{'; '.join(failed_entries)}]")
            link_validate_desc = "; ".join(parts)

        if link_validate:
            log.info(f"Step 5: Link validation result: Success ({len(valid_entries)}/{len(links)} links valid)")
        else:
            log.warning(
                f"Step 5: Link validation result: Failed (valid: {len(valid_entries)}, invalid: {len(invalid_entries)}, failed: {len(failed_entries)})"
            )

        return {"link_validate": link_validate, "link_validate_desc": link_validate_desc}
    except Exception as e:
        log.error(f"Unexpected error in run_link_validation: {e}")
        return {"link_validate": False, "link_validate_desc": f"error: {e}"}
