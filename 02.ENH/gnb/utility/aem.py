"""
aem.py - AEM 기반 웹사이트 자동화 유틸리티 모듈

이 모듈은 Playwright 기반의 로그인 자동화 및 지연 로딩 스크롤 등 웹 자동화 유틸리티를 제공합니다.
- check_login: 로그인 필요 시 자동 로그인 처리
- scroll_for_lazyload: 지연 로딩 컨텐츠를 위한 스크롤 처리

사용 예시:
    from utility.aem import check_login, scroll_for_lazyload
"""

import asyncio
import re
import http
import os
from playwright.async_api import Page, TimeoutError, Response
from utility.orangelogger import log

async def scroll_for_lazyload(page: Page) -> None:
    """
    페이지의 모든 컨텐츠가 로드될 수 있도록 점진적으로 스크롤합니다.
    쿠키 동의 버튼 클릭으로 인한 페이지 리다이렉트가 발생해도 안전하게 스크롤을 계속합니다.
    """
    log.debug("Starting scroll operation for lazy-loaded content")
    try:
        viewport_height = await page.evaluate("window.innerHeight")
        page_height = await page.evaluate("document.body.scrollHeight")
        log.debug(f"Viewport height: {viewport_height}px, Total page height: {page_height}px")
        scroll_step = int(viewport_height * 0.8)
        log.debug(f"Scroll step: {scroll_step}px")
        current_position = 0
        consent_button_clicked = False

        while True:
            try:
                # 현재 페이지 높이 확인
                current_height = await page.evaluate("document.body.scrollHeight")
                if current_position >= current_height:
                    break

                # 스크롤 수행
                await page.evaluate(f"window.scrollTo(0, {current_position})")
                log.debug(f"Scrolled to position: {current_position}px / {current_height}px")
                current_position += scroll_step
                await asyncio.sleep(1.0)

                # 쿠키 동의 버튼 처리
                if not consent_button_clicked:
                    try:
                        button_exists = await page.evaluate("""
                            () => {
                                const button = document.querySelector('#truste-consent-button');
                                if (button && button.offsetParent !== null) {
                                    button.click();
                                    return true;
                                }
                                return false;
                            }
                        """)
                        if button_exists:
                            consent_button_clicked = True
                            log.info("Cookie consent button clicked")
                            await asyncio.sleep(2.0)  # 쿠키 동의 후 페이지가 안정화될 때까지 대기
                    except Exception as e:
                        log.error(f"Error handling cookie consent button: {e}")

            except Exception as e:
                if "Execution context was destroyed" in str(e):
                    # 페이지가 리다이렉트되었지만, 현재 위치를 유지하고 계속 진행
                    log.info("Page reloaded, continuing scroll from current position")
                    await asyncio.sleep(2.0)  # 페이지 로드 대기
                    continue
                raise

        # 스크롤 완료 후 정리
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(0.5)
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        log.debug("Scrolled back to top of page")

    except Exception as e:
        log.error(f"Error during page scrolling: {e}", exc_info=True)

async def check_login(page: Page, response: Response, target_url: str) -> None:
    """
    로그인 필요 여부를 확인하고, 필요 시 자동으로 로그인 처리를 수행합니다.
    """
    log.info("Starting login status check")
    try:
        if response is None:
            log.error("goto() returned no response")
            raise Exception("goto() returned no response")
        if response.status != 200:
            status_description = http.HTTPStatus(response.status).phrase
            response_text = await response.text()
            # 응답 본문을 50줄로 제한하여 로그 출력
            response_lines = response_text.split('\n')
            limited_response = '\n'.join(response_lines[:50])
            limited_response += f"\n... (Showing only 50 out of {len(response_lines)} lines)" if len(response_lines) > 50 else ""
            response_headers = response.headers
            log.error(f"HTTP error: {response.status} {status_description}")
            raise Exception(f"goto() returned\nheader:{response_headers}\ntext:{limited_response}\ndescription:{status_description}")
        if response.request.redirected_from and '/apps/samsung/login/content/' in response.request.redirected_from.url:
            loginid = os.getenv('AEM_USERNAME', '')
            loginpwd = os.getenv('AEM_PASSWORD', '')
            log.debug(f"Login credentials: ID={loginid}, PWD={'*' * len(loginpwd)}")            
            redirected_from_url = response.request.redirected_from.url
            log.info(f"Redirected from: {redirected_from_url}")
            try:
                log.debug("Waiting for login form")
                await page.wait_for_selector("#login-box", timeout=10000)
                log.info("Login page detected, proceeding with login")
                await asyncio.sleep(0.5)
                log.debug("Filling username field")
                await page.fill("#username", loginid, timeout=10000)
                log.debug("Filling password field")
                await page.fill("#password", loginpwd)
                await asyncio.sleep(0.5)
                log.debug("Clicking submit button")
                await page.click("#submit-button")
                url_pattern = re.compile(f"^{re.escape(target_url.rstrip('/'))}/?$")
                log.debug("Waiting for redirection to original URL")
                await page.wait_for_url(url_pattern, timeout=30000)
                log.info(f"Login successful, redirected to original URL: {target_url}")
            except TimeoutError:
                log.error(f"Login process exception: timeout waiting for redirection")
                raise Exception("Login process failed (timeout)")
        else:
            log.info("No redirection or not a login page, login status confirmed")
    except Exception as e:
        log.error(f"Error during login check: {e}", exc_info=True)
        raise
    log.info("Login status check completed")