"""
main.py - 글로벌 삼성 Product Page 자동화 테스트 시스템

이 애플리케이션은 삼성 제품 페이지(PD)의 자동화 테스트를 수행하는 메인 모듈입니다.
Standard PD, Simple PD, Dimension 기능을 체계적으로 검증하여 제품 페이지의 품질을 보장합니다.

환경 및 전제 조건:
- Windows 환경, Python 3.11.9를 전제로 합니다.
- Playwright, 프로젝트 로거(`utility.orangelogger.log`), `env.user` 환경 구성이 사전에 준비되어야 합니다.

실행 흐름 요약:
- 인자 파싱 → Playwright 세션 생성 → (선택) WDS SSO 로그인 → URL 순회 → PD 페이지 검증 호출 → 결과 저장/전송 → 자원 정리

로깅 정책:
- 모든 콘솔 출력은 Logger 사용(영문), Docstring/주석은 한국어로 작성합니다.

주요 기능:
- PD 타입 자동 감지 및 분기 처리
- Dimension 유무/테스트 가능성 판단 및 Fit/Not Fit 검증
- URL 검증 및 카트 전환/가격 일치 검증
- PlateAPI 연동(예약/결과 전송/워커 등록)

사용법:
    python main.py --ssi 1234  # PlateAPI에서 예약된 URL로 PD 테스트 실행
    python main.py              # DEFAULT_TARGETS의 모든 URL을 순차적으로 PD 테스트
"""

import argparse
import asyncio
import os
from dotenv import load_dotenv

# env.user 파일을 명시적으로 로드하여 환경변수 사용
load_dotenv('env.user')

from zest.dto import AnalysisAdd, WorkerAdd, UrlDto
from zest.config import create_zest
from zest.util import generate_random_digit
from playwright.async_api import async_playwright
from utility.orangelogger import log
from utility.aem import check_login, scroll_for_lazyload, wds_sso_login, check_and_handle_relogin, click_p6_button
from pd import validate_pd_page, save_pd_result_to_json

# 여러 개의 테스트/운영 URL을 한 번에 처리할 수 있도록 배열로 선언
DEFAULT_TARGETS = [
    # {"url": "https://p6-pre-qa3.samsung.com//test/refrigerators/top-mount-freezer/rt6300c-top-mount-freezer-bespoke-design-867l-clean-white-rt42cb664412me/", "siteCode": "TEST"},
    # {"url": "https://p6-pre-qa3.samsung.com//test/washers-and-dryers/washing-machines/ww3000tm-front-loading-quick-wash-drum-clean-delay-end-25kg-silver-ww80t3040bs-lp/", "siteCode": "TEST"},
    {"url": "https://www.samsung.com/ca/refrigerators/side-by-side/rs5300cc-22-6-cu-ft-clean-white-rs23cb760012aa/", "siteCode": "CA"},
    {"url": "https://www.samsung.com/ca/laundry/washing-machines/wf8700b-front-loading-bespoke-design-5-3-cu-ft-ultra-capacity-5-2-cu-ft-black-wf53bb8700avus/", "siteCode": "CA"},
    {"url": "https://www.samsung.com/ca/cooking-appliances/range/electric-range-ne63t8711sg-ac/", "siteCode": "CA"},   
    {"url": "https://www.samsung.com/ae/washers-and-dryers/washing-machines/ww5000d-front-loading-smartthings-ai-energy-mode-a-10-percent-extra-energy-efficiency-ai-ecobubble-9kg-white-ww90dg5u34aegu/", "siteCode": "UK"},   
]



def main() -> None:
    """
    메인 애플리케이션 실행 함수.

    목적:
        - 명령줄 인수를 파싱하고 Playwright 비동기 세션을 시작하여 URL별 PD 테스트를 순차 실행합니다.

    반환값:
        None

    예외 처리:
        - 내부에서 처리하며, KeyboardInterrupt는 우아한 종료로 처리합니다.

    사용 예시:
        python main.py --ssi 1234
        python main.py
    """
    # 명령줄 인수 파싱
    parser = argparse.ArgumentParser(description="PD 테스트 웹 페이지 분석 앱")
    parser.add_argument("--ssi", type=str, help="스냅샷 인덱스 (필수)", required=False)

    args = parser.parse_args()

    # 3. Playwright 세션 시작
    async def async_main():
        """Playwright 비동기 세션에서 URL별 PF 구조 추출 및 검증 실행"""
        async with async_playwright() as playwright:
            zest = create_zest()
            # 시크릿모드로 브라우저 시작 (WDS SSO 로그인용)
            browser = await playwright.chromium.launch(
                headless=False,
                args=['--incognito', '--disable-web-security', '--disable-features=VizDisplayCompositor']
            )
            taskid = generate_random_digit()
            default_target_idx = 0  # DEFAULT_TARGETS 배열 인덱스
            log.info(f"Starting PF test application with ssi: {args.ssi}, taskid: {taskid}")
            
            # WDS_LOGIN 환경변수 확인 및 조건부 로그인 처리
            wds_login = os.getenv('WDS_LOGIN', 'false').lower() == 'true'
            log.info(f"WDS Login mode: {wds_login}")
            
            if wds_login:
                # WDS SSO 로그인 실행 (전체 테스트 시작 전)
                log.info("Starting WDS SSO login process")
                try:
                    wds_context, wds_page = await wds_sso_login(browser)
                    log.debug(f"WDS SSO login completed successfully: {wds_page.url}")
                    log.info("WDS SSO login completed successfully")
                    log.info("WDS page ready for P6 button clicks")
                except Exception as e:
                    log.error(f"WDS SSO login failed: {e}")
                    log.error("Cannot proceed without WDS login - terminating application")
                    await browser.close()
                    return
            else:
                log.info("WDS login disabled - using regular browser contexts per URL")
                wds_context, wds_page = None, None
            while True:
                # ssi 인자가 있으면 reserve_url로 URL 예약, 없으면 DEFAULT_TARGETS의 모든 URL을 순차적으로 처리
                if args.ssi:
                    # Zest에서 처리할 URL 예약
                    target_url_dto = await zest.reserve_url(args.ssi)
                    if not target_url_dto:
                        log.warning("No URLs available for processing")
                        break
                    added_worker = await zest.add_worker(target_url_dto.index, WorkerAdd(taskId=taskid))
                    if added_worker is None:
                        log.error(f"task id: {taskid} => failed to add worker info")
                        break     
                else:
                    # ssi 미지정 시: DEFAULT_TARGETS 의 여러 URL을 순차적으로 처리
                    if default_target_idx >= len(DEFAULT_TARGETS):
                        break
                    target = DEFAULT_TARGETS[default_target_idx]
                    target_url_dto = UrlDto(index=0, snapshotIndex=0, status=0, url=target["url"], siteCode=target["siteCode"])
                    default_target_idx += 1
                log.info(f"Target URL: {target_url_dto.url}, UrlIndex: {target_url_dto.index}")
                
                # 리소스 추적을 위한 변수 초기화
                page = None
                context = None
                new_page = None
                
                try:
                    # WDS_LOGIN 여부에 따른 분기 처리
                    if wds_login:
                        # WDS 로그인을 사용하는 경우: P6 버튼 클릭으로 새 탭 생성
                        log.info("Using WDS login with P6 button click for URL processing")
                        
                        # P6 버튼 클릭하여 새 탭 생성
                        new_page = await click_p6_button(wds_page)
                        if not new_page:
                            log.error("Failed to create new tab via P6 button click")
                            continue
                        
                        # 새 탭에서 대상 URL로 이동
                        log.info(f"Navigating to target URL in new tab: {target_url_dto.url}")
                        response = await new_page.goto(target_url_dto.url)
                        
                        # 로그인 필요 여부 확인 및 자동 로그인 처리
                        # log.debug("Checking login status and handling login if needed")
                        # await check_login(new_page, response, target_url_dto.url)
                        
                        # WDS 로그인 세션 만료 확인 및 재로그인 처리
                        log.debug("Checking for WDS login session expiration")
                        try:
                            context, page = await check_and_handle_relogin(browser, new_page, target_url_dto.url, wds_page)
                            log.info("WDS login session check completed")
                        except Exception as relogin_error:
                            log.warning(f"WDS relogin check failed: {relogin_error}")
                            raise  # finally 블록에서 정리되도록 예외 전파
                            
                    else:
                        # 일반 로그인을 사용하는 경우: 새 컨텍스트 생성
                        log.info("Creating new context for URL processing")
                        context = await browser.new_context()
                        page = await context.new_page()
                        
                        # 대상 URL로 이동 (최초 진입)
                        log.info(f"Navigating to target URL: {target_url_dto.url}")
                        response = await page.goto(target_url_dto.url)
                        
                        # 로그인 필요 여부 확인 및 자동 로그인 처리
                        # log.debug("Checking login status and handling login if needed")
                        # await check_login(page, response, target_url_dto.url)
                    
                    # DOMContentLoaded까지 페이지 로드 대기
                    log.debug("Waiting for DOMContentLoaded event")
                    await page.wait_for_load_state("domcontentloaded")
                    log.info("Page basic loading completed")
                    
                    # 지연 로딩(스크롤 기반) 컨텐츠 모두 로드
                    log.info("Scrolling page to trigger lazy-loaded content")
                    await scroll_for_lazyload(page)
                    log.info("Full page scroll completed")
                    
                    # 페이지 완전 안정화를 위한 추가 대기
                    log.info("Waiting for complete page stabilization after lazy loading")
                    await page.wait_for_load_state('domcontentloaded')
                    await asyncio.sleep(2)  # 추가 안정화 대기
                    
                    # PD 테스트 실행
                    log.info("Starting PD page validation")
                    pd_result = await validate_pd_page(page, target_url_dto.url)
                    log.info("PD page validation completed")
                    
                    # 결과를 JSON으로 저장
                    log.info("Saving PD test result to JSON")
                    result_file_path = save_pd_result_to_json(pd_result, target_url_dto.url, target_url_dto.siteCode)
                    log.info(f"PD test result saved to: {result_file_path}")
                    
                    # ssi가 있는 경우 Zest API로 결과 전송
                    if args.ssi:
                        def convert_pd_to_analysis(pd_result) -> list:
                            """
                            PD 테스트 결과를 Zest API의 AnalysisAdd 형식으로 변환합니다.
                            PD 검증 결과를 종합하여 tcresult를 결정하고, 모든 검증이 통과하면 tcresult=10, 
                            하나라도 실패하면 tcresult=0으로 설정합니다. tcresultNote에는 각 검증 항목별 결과가 포함됩니다.
                            
                            파라미터:
                                pd_result: PDNode 객체
                                
                            반환값:
                                list: AnalysisAdd 객체 리스트
                                
                            사용 예시:
                                analysis_list = convert_pd_to_analysis(pd_result)
                            """
                            # tcId는 URL의 마지막 '/' 이후 부분을 사용
                            from urllib.parse import urlparse
                            parsed_url = urlparse(pd_result.url)
                            url_suffix = parsed_url.path.strip('/').split('/')[-1] or "root"

                            # 각 검증 항목을 개별 행으로 변환
                            # 지정된 순서: Rating, Link, Dimension(있는 경우), Transition, Price
                            items = [
                                # ("Rating", getattr(pd_result, "rating_validate", None), getattr(pd_result, "rating_validate_desc", "")),
                                # ("Link", getattr(pd_result, "link_validate", None), getattr(pd_result, "link_validate_desc", "")),
                            ]
                            # if getattr(pd_result, "dimension_validate", None) is not None:
                                # items.append(("Dimension", getattr(pd_result, "dimension_validate", None), getattr(pd_result, "dimension_validate_desc", "")))
                            items.extend([
                                ("Transition", getattr(pd_result, "transition_validate", None), getattr(pd_result, "transition_validate_desc", "")),
                                # ("Price", getattr(pd_result, "price_validate", None), getattr(pd_result, "price_validate_desc", "")),
                            ])

                            analysis_rows = []
                            for name, is_valid, desc in items:
                                if is_valid is None:
                                    continue
                                tcresult = 10 if is_valid else 0
                                note = desc or ""
                                # tcId는 URL 마지막 부분 + validate 항목으로 구성
                                tc_id = f"{url_suffix}/{name}"
                                analysis_rows.append(AnalysisAdd(tcId=tc_id, tcresult=tcresult, tcresultNote=note))

                            return analysis_rows
                        
                        log.info("Converting PD result to Zest API format")
                        analysis_add_list = convert_pd_to_analysis(pd_result)
                        
                        # 생성된 분석 결과 리스트 로그 출력
                        for idx, analysis in enumerate(analysis_add_list, 1):
                            log.info(f"[AnalysisAdd {idx}] tcId: {analysis.tcId}, tcresult: {analysis.tcresult}, tcresultNote: {analysis.tcresultNote}")
                        
                        log.info(f"add_analysis index:{target_url_dto.index} status:{200}")
                        await zest.add_analysis(target_url_dto.index, 200, analysis_add_list, note="-")
                        log.info("Analysis result sent to Zest API successfully")
                    
                    log.debug("Operation completed successfully")
                    
                except Exception as e:
                    # 예외 상세 로깅
                    log.error(f"Error occurred: {e}", exc_info=True)
                    
                finally:
                    # 모든 경우에 열린 페이지와 컨텍스트를 확실하게 닫기
                    log.debug("Starting cleanup: closing all opened pages and contexts")
                    
                    # WDS 모드: new_page와 page 닫기 (WDS 페이지는 유지)
                    if wds_login:
                        # new_page 닫기 (check_and_handle_relogin에서 이미 닫혔을 수도 있음)
                        if new_page:
                            try:
                                await new_page.close()
                                log.debug("new_page closed successfully")
                            except Exception as e:
                                log.debug(f"new_page already closed or error: {e}")
                        
                        # page 닫기 (재로그인 후 새로 생성된 페이지)
                        if page:
                            try:
                                await page.close()
                                log.info("Test page closed successfully (WDS mode)")
                            except Exception as e:
                                log.debug(f"page already closed or error: {e}")
                    
                    # non-WDS 모드: page와 context 닫기
                    else:
                        if page:
                            try:
                                await page.close()
                                log.debug("page closed successfully")
                            except Exception as e:
                                log.debug(f"page already closed or error: {e}")
                        
                        if context:
                            try:
                                await context.close()
                                log.info("Context closed successfully (non-WDS mode)")
                            except Exception as e:
                                log.debug(f"context already closed or error: {e}")
                    
                    log.debug("Cleanup completed")
            
            # 최종 정리: 모든 URL 처리 완료 후 자원 정리
            if wds_login:
                log.info("Closing WDS page and context")
                try:
                    if 'page' in locals() and page:
                        await page.close()
                        log.info("WDS page closed successfully")
                    if 'wds_context' in locals() and wds_context:
                        await wds_context.close()
                        log.info("WDS context closed successfully")
                except Exception as e:
                    log.warning(f"Error closing WDS resources: {e}")
            
            log.info("Closing browser instance")
            try:
                await browser.close()
            except Exception:
                pass
            log.info("Browser instance closed successfully")
            
            try:
                if zest:
                    await zest.close()
            except Exception:
                pass
            log.info("Plate api instance closed successfully")

    # 4. 비동기 메인 실행
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt: Graceful shutdown")


if __name__ == "__main__":
    main()