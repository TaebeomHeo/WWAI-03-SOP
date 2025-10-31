"""
aem.py - AEM 기반 웹사이트 자동화 유틸리티 모듈

이 모듈은 Playwright 기반의 로그인 자동화 및 지연 로딩 스크롤 등 웹 자동화 유틸리티를 제공합니다.
- check_login: 로그인 필요 시 자동 로그인 처리
- scroll_for_lazyload: 지연 로딩 컨텐츠를 위한 스크롤 처리
- wds_sso_login: WDS SSO 로그인 처리 및 p6 페이지로 이동
- check_and_handle_relogin: 재로그인 요구 감지 및 자동 재로그인 처리

사용 예시:
    from utility.aem import check_login, scroll_for_lazyload, wds_sso_login, check_and_handle_relogin
"""

import asyncio
import re
import http
import os
from playwright.async_api import Page, TimeoutError, Response, Browser, BrowserContext
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

                # 쿠키 동의 버튼 처리 (두 가지 버튼 타입 지원)
                if not consent_button_clicked:
                    try:
                        button_clicked = await page.evaluate("""
                            () => {
                                // 1. 기존 버튼: #truste-consent-button
                                const trusteButton = document.querySelector('#truste-consent-button');
                                if (trusteButton && trusteButton.offsetParent !== null) {
                                    trusteButton.click();
                                    return 'truste-consent-button';
                                }
                                
                                // 2. 새로운 버튼: a 태그 with an-ac="cookie bar:accept"
                                const acceptButton = document.querySelector('a[an-ac="cookie bar:accept"]');
                                if (acceptButton && acceptButton.offsetParent !== null) {
                                    acceptButton.click();
                                    return 'cookie-bar-accept';
                                }
                                
                                return false;
                            }
                        """)
                        if button_clicked:
                            consent_button_clicked = True
                            log.info(f"Cookie consent button clicked: {button_clicked}")
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
        await asyncio.sleep(1.5)  # DOM 안정화를 위해 대기 시간 증가
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
                await page.wait_for_selector("#login-box", timeout=0)
                log.info("Login page detected, proceeding with login")
                await asyncio.sleep(0.5)
                log.debug("Filling username field")
                await page.fill("#username", loginid, timeout=0)
                log.debug("Filling password field")
                await page.fill("#password", loginpwd)
                await asyncio.sleep(0.5)
                log.debug("Clicking submit button")
                await page.click("#submit-button")
                url_pattern = re.compile(f"^{re.escape(target_url.rstrip('/'))}/?$")
                log.debug("Waiting for redirection to original URL")
                await page.wait_for_url(url_pattern, timeout=0)
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

async def wds_sso_login(browser: Browser) -> tuple[BrowserContext, Page]:
    """
    WDS SSO 로그인을 수행하고 p6 버튼이 준비된 페이지와 컨텍스트를 반환합니다.
    
    Args:
        browser (Browser): Playwright 브라우저 인스턴스
        
    Returns:
        tuple[BrowserContext, Page]: 로그인된 컨텍스트와 p6 버튼이 준비된 페이지
    """
    log.info("Starting WDS SSO login process")
    
    try:
        # 환경변수에서 WDS 로그인 정보 가져오기
        wds_username = os.getenv('WDS_USERNAME')
        wds_password = os.getenv('WDS_PASSWORD')
        wds_employee_mode = os.getenv('WDS_EMPLOYEE_MODE', 'true').lower() == 'true'
        
        if not wds_username or not wds_password:
            raise Exception("WDS_USERNAME and WDS_PASSWORD environment variables must be set")
        
        log.info(f"WDS login mode: {'Samsung Employee (popup)' if wds_employee_mode else 'Business Partner (no popup)'}")
        
        # 시크릿모드 컨텍스트 생성
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 새 페이지 생성
        page = await context.new_page()
        
        # WDS SSO 로그인 페이지로 이동
        target_url = "https://wds.samsung.com/wds/sso/login/forwardLogin.do"
        log.info(f"Navigating to WDS SSO login page: {target_url}")
        
        response = await page.goto(target_url, wait_until='domcontentloaded')
        await page.wait_for_load_state('networkidle')
        
        if wds_employee_mode:
            # ===== Samsung Employee 모드 (팝업 사용) =====
            
            # 1단계: 로그인 버튼 클릭 및 팝업 대기
            log.info("Step 1: Clicking login button and waiting for popup")
            try:
                login_button = 'a[href="javascript:SSO0101_V.sslChkAction();"]'
                await page.wait_for_selector(login_button)
                
                # 팝업이 열릴 때까지 대기하면서 버튼 클릭
                async with page.expect_popup() as popup_info:
                    await page.click(login_button)
                popup_page = await popup_info.value
                log.info("Popup window opened successfully")
                
            except TimeoutError:
                log.error("Step 1 failed: Login button not found on WDS SSO page")
                raise Exception("Step 1 failed: Login button not found on WDS SSO page")

            # 2단계: 팝업창에서 로그인 폼 입력
            log.info("Step 2: Filling login form in popup")
            try:
                await popup_page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(1.0)
                
                # 로그인 입력 폼 찾기
                await popup_page.wait_for_selector('form')
                
                # 이메일 입력 필드 찾기 및 입력
                login_id_input = await popup_page.wait_for_selector('input[name="UserName"]')
                if not login_id_input:
                    raise Exception("Login ID input field not found")
                
                await login_id_input.fill(wds_username)
                
                # 비밀번호 입력 필드 찾기 및 입력
                password_input = await popup_page.wait_for_selector('input[name="Password"]')
                if not password_input:
                    raise Exception("Password input field not found")
                
                await password_input.fill(wds_password)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                log.error(f"Step 2 failed: Unexpected error during login form filling: {e}")
                raise Exception(f"Step 2 failed: Login form filling error")
            
            # 3단계: 팝업창에서 로그인 제출
            log.info("Step 3: Submitting login form in popup")
            try:
                submit_button = await popup_page.wait_for_selector('#submitButton')
                if not submit_button:
                    raise Exception("Login submit button not found")
                
                await submit_button.click()
                await asyncio.sleep(1.0)
                
            except TimeoutError as e:
                log.error(f"Step 3 failed: Login submit button not found - timeout error: {e}")
                raise Exception(f"Step 3 failed: Login submit button not found (timeout)")
                
            except Exception as e:
                log.error(f"Step 3 failed: Unexpected error during login form submission: {e}")
                raise Exception(f"Step 3 failed: Login form submission error")
            
            # 4단계: 팝업 닫힌 후 원래 페이지에서 p6 버튼 대기
            log.info("Step 4: Waiting for p6-preqa3 button on main page")
            try:
                # 팝업이 자동으로 닫히고 원래 페이지가 p6 버튼이 있는 페이지로 이동됨
                await asyncio.sleep(2.0)
                await page.wait_for_load_state('domcontentloaded')
                return context, page
                
            except TimeoutError:
                log.error("Step 4 failed: p6-preqa3 button not found")
                raise Exception("Step 4 failed: p6-preqa3 button not found")
        
        else:
            # ===== Business Partner 모드 (팝업 없음) =====
            
            # 1단계: 로그인 버튼 클릭
            log.info("Step 1: Clicking login button")
            try:
                login_button = 'a[href="javascript:SSO0101_V.goLoginAction();"]'
                await page.wait_for_selector(login_button)
                await page.click(login_button)
            except TimeoutError:
                log.error("Step 1 failed: Login button not found on WDS SSO page")
                raise Exception("Step 1 failed: Login button not found on WDS SSO page")
            
            # 2단계: Login 버튼 클릭
            log.info("Step 2: Clicking Login button")
            try:
                await page.wait_for_selector('#loginButton.noticeBottonBtn.noticeBtnClick')
                await page.click('#loginButton.noticeBottonBtn.noticeBtnClick')
            except TimeoutError:
                log.error("Step 2 failed: Login button not found after first click")
                raise Exception("Step 2 failed: Login button not found after first click")
            
            # 3단계: 로그인 폼 입력
            log.info("Step 3: Filling login form")
            try:
                await page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(1.0)
                
                # 로그인 입력 폼 찾기
                await page.wait_for_selector('form')
                
                # 이메일 입력 필드 찾기 및 입력
                login_id_input = await page.wait_for_selector('input[name="loginId"]')
                if not login_id_input:
                    raise Exception("Login ID input field not found")
                
                await login_id_input.fill(wds_username)
                
                # 비밀번호 입력 필드 찾기 및 입력
                password_input = await page.wait_for_selector('input[name="password"]')
                if not password_input:
                    raise Exception("Password input field not found")
                
                await password_input.fill(wds_password)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                log.error(f"Step 3 failed: Unexpected error during login form filling: {e}")
                raise Exception(f"Step 3 failed: Login form filling error")
            
            # 4단계: 로그인 제출
            log.info("Step 4: Submitting login form")
            try:
                submit_button = await page.wait_for_selector('button[type="submit"][aria-label="로그인"]')
                if not submit_button:
                    raise Exception("Login submit button not found")
                
                # 버튼이 활성화되었는지 확인
                is_disabled = await submit_button.get_attribute('disabled')
                if is_disabled:
                    await page.wait_for_function(
                        '() => !document.querySelector(\'button[type="submit"][aria-label="로그인"]\').disabled'
                    )
                
                await submit_button.click()
                await asyncio.sleep(1.0)
                
            except TimeoutError as e:
                log.error(f"Step 4 failed: Login submit button not found - timeout error: {e}")
                raise Exception(f"Step 4 failed: Login submit button not found (timeout)")
                
            except Exception as e:
                log.error(f"Step 4 failed: Unexpected error during login form submission: {e}")
                raise Exception(f"Step 4 failed: Login form submission error")
            
            # 5단계: p6-preqa3 버튼 대기
            log.info("Step 5: Waiting for p6-preqa3 button")
            try:
                await asyncio.sleep(2.0)
                await page.wait_for_load_state('domcontentloaded')
                return context, page

            except TimeoutError:
                log.error("Step 5 failed: p6-preqa3 button not found")
                raise Exception("Step 5 failed: p6-preqa3 button not found")
        
    except Exception as e:
        log.error(f"WDS SSO login failed: {e}", exc_info=True)
        
        # 에러 발생 시 컨텍스트와 페이지 정리
        try:
            if 'page' in locals():
                await page.close()
            if 'context' in locals():
                await context.close()
        except Exception as cleanup_error:
            log.error(f"Error during cleanup: {cleanup_error}")
        
        raise Exception(f"WDS SSO login process failed: {e}")

async def click_p6_button(page: Page) -> Page:
    """
    p6-preqa3 버튼을 클릭하여 새 탭을 생성하고 p6 페이지를 반환합니다.
    
    Args:
        page (Page): WDS 로그인된 페이지
        
    Returns:
        Page: 새로 생성된 p6 페이지
    """
    log.info("Clicking p6-preqa3 button to create new tab")
    
    try:
        # 클릭 전 기존 페이지 수 기록
        context = page.context
        initial_page_count = len(context.pages)
        log.info(f"Initial page count: {initial_page_count}")
        
        # p6-preqa3 클릭
        p6_button = await page.query_selector('a[href="javascript:goLink(\'p6-preqa3\');"]')
        if not p6_button:
            log.error("p6-preqa3 button not found")
            raise Exception("p6-preqa3 button not found")
        await page.evaluate("goLink('p6-preqa3')")
        
        log.info("Waiting for new p6 tab to open...")
        
        # 새 탭이 열릴 때까지 무한 대기 (타임아웃 제거)
        wait_interval = 0.5
        waited_time = 0
        
        while True:
            await asyncio.sleep(wait_interval)
            waited_time += wait_interval
            
            current_page_count = len(context.pages)
            if current_page_count > initial_page_count:
                log.info(f"New tab detected! Page count increased from {initial_page_count} to {current_page_count}")
                break
            
            # 진행 상황 로그 (5초마다)
            if int(waited_time) % 5 == 0 and waited_time > 0:
                log.info(f"Still waiting for new tab... (waited {waited_time:.1f}s)")
        
        # 새로 생성된 페이지 찾기 (p6-pre-qa3.samsung.com URL 확인)
        p6_page = None
        for new_page in context.pages[initial_page_count:]:
            try:
                current_url = new_page.url
                log.info(f"Checking page URL: {current_url}")
                
                if "p6-pre-qa3.samsung.com" in current_url:
                    p6_page = new_page
                    log.info(f"Found p6 page with URL: {current_url}")
                    break
            except Exception as e:
                log.warning(f"Error checking page URL: {e}")
                continue
        
        if not p6_page:
            # p6 URL을 찾지 못한 경우, 새로 생성된 페이지 중 첫 번째 사용
            log.warning("Could not find page with p6-pre-qa3.samsung.com URL, using the newest page")
            p6_page = context.pages[-1]
            log.info(f"Using newest page with URL: {p6_page.url}")
        
        # p6 페이지 로딩 완료 대기
        await p6_page.wait_for_load_state('domcontentloaded')
        
        final_url = p6_page.url
        log.info(f"Successfully opened p6 page URL: {final_url}")
        
        return p6_page

    except Exception as e:
        log.error(f"Error clicking p6-preqa3 button: {e}")
        raise Exception(f"Failed to click p6-preqa3 button: {e}")

async def check_and_handle_relogin(browser: Browser, page: Page, target_url: str, wds_page: Page = None, retry_count: int = 0) -> tuple[BrowserContext, Page]:
    """
    페이지에서 재로그인 요구 메시지를 확인하고, 필요시 재로그인을 수행합니다.
    로그인이 풀린 경우: 로그인 풀린 탭을 닫고, WDS 로그인 탭에서 P6 버튼을 다시 누릅니다.

    동작 방식:
    - 재로그인 메시지 감지 시 p6 버튼을 클릭하여 새 탭 생성
    - 새 탭에서 다시 재로그인 체크 수행
    - 최대 3회까지 재시도하며, 초과 시 예외 발생
    
    Args:
        browser (Browser): Playwright 브라우저 인스턴스
        page (Page): 현재 페이지 객체 (로그인이 풀린 탭)
        target_url (str): 목표 URL
        wds_page (Page): WDS 로그인 탭 (선택사항)
        retry_count (int): 현재까지의 재시도 횟수 (기본값: 0)
        
    Returns:
        tuple[BrowserContext, Page]: 컨텍스트와 페이지 (재로그인 불필요시 기존 것, 필요시 새로운 것)
    
    예외 처리:
    - 재로그인 시도가 3회를 초과하면 Exception 발생하여 다음 URL로 진행
    """

    # 최대 재시도 횟수 검증
    MAX_RETRY_COUNT = 3

    log.info(f"Checking for relogin requirement (retry count: {retry_count}/{MAX_RETRY_COUNT})")

    # 재시도 횟수가 3회를 초과하면 예외 발생
    if retry_count >= MAX_RETRY_COUNT:
        log.error(f"Relogin retry count exceeded maximum limit ({MAX_RETRY_COUNT})")
        raise Exception(f"Relogin failed after {MAX_RETRY_COUNT} attempts - skipping to next URL")
    log.info("Checking for relogin requirement")
    
    try:
        # 재로그인 요구 메시지 확인
        relogin_element = await page.query_selector('coral-Heading coral-Heading--1')
        if relogin_element:
            element_text = await relogin_element.text_content()
            if element_text and "Please login through WMC" in element_text:
                log.info("Relogin required detected - starting relogin process")
                
                # 1. 로그인이 풀린 탭 닫기
                log.info("Closing the tab with expired login")
                try:
                    await page.close()
                    log.info("Expired login tab closed successfully")
                except Exception as cleanup_error:
                    log.warning(f"Error during expired tab cleanup: {cleanup_error}")
                
                # 2. p6 버튼 클릭(WDS 로그인이 풀린 경우 재로그인 수행)
                log.info("Clicking P6 button to create new tab")
                try:
                    new_page = await click_p6_button(wds_page)
                except Exception as p6_error:
                    log.error(f"Error during P6 button click: {p6_error}")
                    log.info("Performing new WDS SSO login")
                    new_context, wds_page = await wds_sso_login(browser)
                    new_page = await click_p6_button(wds_page)

                # 3. 새 페이지에서 다시 재로그인 체크 수행 (재귀 호출)
                log.info("Rechecking relogin requirement on new page")
                return await check_and_handle_relogin(browser, new_page, target_url, wds_page, retry_count + 1)
        else:
            log.debug("No relogin requirement detected")
        
        # 재로그인이 필요하지 않은 경우 기존 컨텍스트와 페이지 반환
        return page.context, page
        
    except Exception as e:
        # 재시도 횟수 초과 에러는 그대로 전파
        if "Relogin failed after" in str(e):
            raise
            
        log.error(f"Error in relogin check and handling: {e}", exc_info=True)
        # 에러 발생 시 기존 컨텍스트와 페이지 반환
        return page.context, page