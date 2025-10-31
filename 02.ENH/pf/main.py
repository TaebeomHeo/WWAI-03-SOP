"""
main.py - 글로벌 삼성 SHOP 네비게이션 구조 자동 추출/분석 메인 엔트리

이 애플리케이션은 다음과 같은 기능을 제공합니다:
- 여러 국가/사이트의 삼성 SHOP 구조를 자동으로 추출하고 트리 형태로 분석합니다.
- Playwright 기반 브라우저 자동화로 실제 페이지 이동, 로그인, 스크롤, 메뉴 탐색, 링크 유효성 검사까지 수행합니다.
- Zest API와 연동하여 URL 예약, 분석 결과 전송, 워커 등록 등 백엔드와 실시간 데이터 교환이 가능합니다.
- 명령행 옵션으로 특정 스냅샷 인덱스(SSI) 지정 시 Zest API에서 URL을 예약받아 처리, 미지정 시 내장 DEFAULT_TARGETS 전체를 순차 처리합니다.
- 모든 실행/오류/경고 메시지는 프로젝트 표준 logger(영문, [YY/MM/DD HH:MM:SS Level main] 포맷)로 출력됩니다.
- 주요 함수/클래스/코드 블록은 한글로 문서화되어 있습니다.

사용 예시:
    python main.py --ssi 1234
    python main.py

작성자: (작성자명)
최종수정: (수정일)
"""

import argparse
import asyncio
import time
import os
from dotenv import load_dotenv

# env.user 파일을 명시적으로 로드하여 환경변수 사용
load_dotenv('env.user')

from zest.dto import AnalysisAdd, WorkerAdd, UrlDto
from zest.config import create_zest
from zest.util import generate_random_digit
from playwright.async_api import async_playwright
from utility.aem import check_login, scroll_for_lazyload, wds_sso_login, check_and_handle_relogin, click_p6_button
from pf import save_product_list, extract_pf_structure, extract_main_category, print_product_list
from utility.orangelogger import log

# 여러 개의 테스트/운영 URL을 한 번에 처리할 수 있도록 배열로 선언
DEFAULT_TARGETS = [
    # {"url": "https://p6-pre-qa3.samsung.com/za/smartphones/all-smartphones/", "siteCode": "ZA"},
    # {"url": "https://p6-pre-qa3.samsung.com/za/tvs/all-tvs/", "siteCode": "ZA"},
    # {"url": "https://p6-pre-qa3.samsung.com/za/computers/all-computers/", "siteCode": "ZA"},
    {"url": "https://p6-pre-qa3.samsung.com/br/monitors/all-monitors/", "siteCode": "BR"},
]


async def _get_current_active_main_tab_index(page) -> int:
    """
    현재 활성화된 메인탭의 인덱스를 반환합니다.
    
    동작 방식:
    - 현재 활성화된 메인탭 요소 찾기
    - 모든 메인탭 요소들과 비교하여 인덱스 확인
    
    파라미터:
        page: Playwright Page 객체
        
    반환값:
        int: 현재 활성화된 메인탭의 인덱스 (0부터 시작, 찾을 수 없으면 -1)
    """
    try:
        # 현재 활성화된 메인탭 확인
        active_tab_element = await page.query_selector(
            ".nv19-pd-category-main .nv19-pd-category-main__item--active"
        )
        
        if not active_tab_element:
            log.warning("No active main tab found")
            return -1
        
        # 모든 메인탭 요소들 가져오기
        all_tab_items = await page.query_selector_all(
            ".nv19-pd-category-main .nv19-pd-category-main__item"
        )
        
        if not all_tab_items:
            log.warning("No main tab items found")
            return -1
        
        # 현재 활성화된 탭의 인덱스 찾기
        for i, tab_item in enumerate(all_tab_items):
            if await tab_item.is_visible() and await tab_item.evaluate("el => el.classList.contains('nv19-pd-category-main__item--active')"):
                return i
        
        log.warning("Could not determine active tab index")
        return -1
        
    except Exception as e:
        log.error(f"Error getting current active main tab index: {e}")
        return -1


def main() -> None:
    """메인 애플리케이션 실행 함수: PF 페이지 구조 추출 및 검증"""
    # 1. 명령줄 인수 파싱
    parser = argparse.ArgumentParser(description="웹 페이지 분석 앱")
    parser.add_argument("--ssi", type=str, help="스냅샷 인덱스 (필수)", required=False)
    parser.add_argument("--no-validate", action="store_true", help="링크 유효성 검사 생략 플래그")

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
                        continue # 다음 URL로 넘어감
                        
                else:
                    # 일반 로그인을 사용하는 경우: 새 컨텍스트 생성
                    log.info("Creating new context for URL processing")
                    context = await browser.new_context()
                    page = await context.new_page()
                    
                    # 대상 URL로 이동 (최초 진입)
                    log.info(f"Navigating to target URL: {target_url_dto.url}")
                    response = await page.goto(target_url_dto.url)
                    
                    # 로그인 필요 여부 확인 및 자동 로그인 처리
                    log.debug("Checking login status and handling login if needed")
                    await check_login(page, response, target_url_dto.url)
                
                try:
                    # DOMContentLoaded까지 페이지 로드 대기
                    log.debug("Waiting for DOMContentLoaded event")
                    await page.wait_for_load_state("domcontentloaded")
                    log.info("Page basic loading completed")
                    
                    # 지연 로딩(스크롤 기반) 컨텐츠 모두 로드
                    log.info("Scrolling page to trigger lazy-loaded content")
                    await scroll_for_lazyload(page)
                    log.info("Full page scroll completed")
                    
                    # SHOP 메뉴 구조 추출 및 트리 출력
                    total_start_time = time.time()
                    log.info("Extracting PF structure")
                    all_shop_result = []
                    main_categories = await extract_main_category(page)
                    log.info(f"Main Category discovered: {len(main_categories)}")
                    
                    # 각 메인 카테고리별로 구조 추출
                    for idx, main_category_node in enumerate(main_categories):
                        log.info(f"Prepare Main Category [{idx+1}/{len(main_categories)}]: {main_category_node.name}")
                        
                        # 현재 활성화된 메인탭의 인덱스 확인 (각 반복마다 다시 확인)
                        current_active_index = await _get_current_active_main_tab_index(page)
                        log.info(f"Current active main tab index: {current_active_index}")
                        
                        # 현재 활성화된 메인탭이 아닌 경우에만 페이지 이동
                        if idx != current_active_index:
                            log.info(f"Navigating to main tab {idx+1}: {main_category_node.name}")
                            await page.goto(main_category_node.url, timeout=0)
                            await page.wait_for_load_state("domcontentloaded")
                        else:
                            log.info(f"Main tab {idx+1} is already active: {main_category_node.name}")
                        
                        await scroll_for_lazyload(page)
                        log.info("Full page scroll completed")
                        
                        # 메인탭 에러 페이지 체크
                        error_page_element = await page.query_selector(".ot02-error-page")
                        is_error_page = error_page_element is not None
                        
                        if is_error_page:
                            log.warning(f"Error page detected for main category: {main_category_node.name}")
                            # 에러 페이지인 경우 빈 결과로 처리하고 다음 메인탭으로 이동
                            main_category_with_children = main_category_node
                            main_category_with_children.children = []
                            print_product_list(main_category_with_children)
                            all_shop_result.append(main_category_with_children)
                            continue
                        
                        # 페이지 이동 후 nv19-pd-category-main__item swiper-slide의 data-menu-idx 확인
                        try:
                            # 현재 활성화된 메인 탭의 data-menu-idx 추출
                            active_main_tab = await page.query_selector(".nv19-pd-category-main__item.swiper-slide.nv19-pd-category-main__item--active")
                            if active_main_tab:
                                data_menu_idx = await active_main_tab.get_attribute("data-menu-idx")
                                # 완전히 다른 사이트로 이동한 경우 감지 (원래 A,B,C → B,D,X 같은 경우)
                                # 첫 번째 메인탭이 아닌데 data-menu-idx가 0인 경우는 다른 사이트
                                if idx != 0 and data_menu_idx == "0":
                                    log.info(f"Completely different page detected: expected to be on main tab {idx}, but got data-menu-idx={data_menu_idx} (different site structure)")
                                    continue
                                # 또는 data-menu-idx가 예상 범위를 벗어나는 경우
                                elif data_menu_idx and int(data_menu_idx) >= len(main_categories):
                                    log.info(f"Completely different page detected: data-menu-idx={data_menu_idx} exceeds expected range (0-{len(main_categories)-1})")
                                    continue
                        except Exception as e:
                            log.warning(f"Error checking data-menu-idx: {e}")
                        
                        log.info(f"Processing Main Category [{idx+1}/{len(main_categories)}]: {main_category_node.name}")
                        
                        # pf.py의 extract_pf_structure 함수 호출하여 nv20 구조 추출
                        main_category_with_children = await extract_pf_structure(page, main_category_node, browser, wds_page)
                        print_product_list(main_category_with_children)
                        all_shop_result.append(main_category_with_children)
                        
                        if not main_category_with_children.children:
                            log.error("Navigation validation failed. No results returned.")
                            continue  # 다음 URL로 넘어감

                    # 전체 처리 시간 로그
                    total_end_time = time.time()
                    total_processing_time = total_end_time - total_start_time
                    log.info(f"All Main Categories processing completed in {total_processing_time:.2f} seconds")
                    log.info(f"Total results: {len(all_shop_result)} subtabs extracted")

                    # 분석 결과 전송 및 로그 출력, add_analysis 호출은 ssi가 있을 때만 수행
                    if args.ssi:
                        def collect_analysis_add_list(node, main_node_name: str = "", path: list = None) -> list:
                            """
                            SubCategoryNode의 검증 결과를 메인카테고리이름_서브카테고리이름_검증항목 형식의 tcId로 항목별 라인(링크/헤드라인/결과수/필터/구매/브레드크럼)으로 분리하여 AnalysisAdd 리스트를 생성합니다.

                            Args:
                                node: SubCategoryNode 객체
                                main_node_name: 메인 카테고리 노드의 이름
                                path: 현재까지의 경로 리스트

                            Returns:
                                list: 메인카테고리이름_서브카테고리이름_검증항목 형식의 tcId를 가진 여러 AnalysisAdd 객체 리스트
                            """
                            if path is None:
                                path = []
                            result = []
                            
                            # tcId 생성: 메인카테고리이름 / 서브카테고리이름 / 검증항목
                            main_category = main_node_name or ''
                            sub_category = getattr(node, 'name', '') or ''
                            
                            # 특수 nv20: Link 검증 라인만 생성 (항상 link_status/desc 포함)
                            if node.is_special:
                                # tcId: 메인카테고리이름 / 서브카테고리이름 / Link
                                link_note = node.link_validate_desc
                                tc_id = f"{main_category} / {sub_category} / Link"
                                result.append(AnalysisAdd(tcId=tc_id, tcresult=10 if node.link_validate else 0, tcresultNote=link_note))
                                return result

                            # 일반 nv20: 항목별로 개별 라인 생성
                            # Link 검증: 항상 1줄 생성
                            link_note = node.link_validate_desc
                            tc_id = f"{main_category} / {sub_category} / Link"
                            result.append(AnalysisAdd(tcId=tc_id, tcresult=10 if node.link_validate else 0, tcresultNote=link_note))

                            # Headline/Result/Breadcrumb/Purchase/Filter 항목별 생성
                            validations: list[tuple[str, str, bool, str | None]] = [
                                #     ("navigation_visible", "Navigation_Visible", getattr(node, 'navigation_visible_validate', False), getattr(node, 'navigation_visible_validate_desc', '')),
                                #     ("headline", "Headline", node.headline_validate, getattr(node, 'headline_validate_desc', '')),
                                #     ("result", "Result_count", node.result_validate, getattr(node, 'result_validate_desc', '')),
                                #     ("faq", "FAQ", getattr(node, 'faq_validate', False), getattr(node, 'faq_validate_desc', '')),
                                #     ("disclaimer", "Disclaimer", getattr(node, 'disclaimer_validate', False), getattr(node, 'disclaimer_validate_desc', '')),
                                ("nv17", "nv17-breadcrumb", getattr(node, 'nv17_validate', False), getattr(node, 'nv17_validate_desc', '')),
                            ]

                            # Headline/Result 라인 생성 (desc를 그대로 사용)
                            for key, validation_type, is_valid, desc in validations:
                                tc_result = 10 if is_valid else 0
                                tc_id = f"{main_category} / {sub_category} / {validation_type}"
                                
                                # desc를 그대로 tcNote에 사용
                                note = desc
                                result.append(AnalysisAdd(tcId=tc_id, tcresult=tc_result, tcresultNote=note))

                            # # 필터 테스트 대상이면 Filter와 Filter_Purchase를 분리하여 생성
                            # if node.is_filter_testable:
                            #     fi = getattr(node, 'filter_validate_info', None) or {}
                            #     test_details = fi.get('test_details', [])
                            #     if test_details:
                            #         # 필터별 인덱스 관리 (개별 테스트용)
                            #         filter_indices = {}
                                    
                            #         for t in test_details:
                            #             combo = (t.get('combo') or '').replace('[', '').replace(']', '')
                            #             passed = bool(t.get('passed'))
                            #             desc = t.get('desc') or ''
                                        
                            #             # combo에서 필터 정보 추출하여 tcId 생성
                            #             # 예: "[Display Size: 6.0\" - 6.2\"]" -> "Display Size"
                            #             # 예: "[Display Size: 6.0\" - 6.2\" | Colour: Black]" -> "Display Size_Colour"
                                        
                            #             # 필터명들 추출
                            #             filter_names = []
                            #             if ' | ' in combo:
                            #                 # 여러 필터 조합 (랜덤 테스트)
                            #                 parts = combo.split(' | ')
                            #                 for part in parts:
                            #                     if ':' in part:
                            #                         filter_name = part.split(':')[0].strip()
                            #                         filter_names.append(filter_name)
                            #             else:
                            #                 # 단일 필터 (개별 테스트)
                            #                 if ':' in combo:
                            #                     filter_name = combo.split(':')[0].strip()
                            #                     filter_names.append(filter_name)
                                        
                            #             # 1. Filter 검증 라인 생성 (필터 적용 자체의 성공/실패)
                            #             if len(filter_names) == 1:
                            #                 # 개별 테스트: Filter / 필터명 / idx
                            #                 filter_name = filter_names[0]
                            #                 if filter_name not in filter_indices:
                            #                     filter_indices[filter_name] = 0
                            #                 filter_indices[filter_name] += 1
                            #                 filter_tc_id = f"{main_category} / {sub_category} / Filter / {filter_name} / {filter_indices[filter_name]:02d}"
                            #             else:
                            #                 # 랜덤 조합 테스트: Filter / 적용한필터명_적용한필터명
                            #                 filter_combination = "_".join(filter_names)
                            #                 filter_tc_id = f"{main_category} / {sub_category} / Filter / {filter_combination}"
                                        
                            #             # Filter 검증 결과 (필터 적용 성공/실패)
                            #             # 분리된 검증 결과 정보 추출
                            #             text_validation = t.get('text_validation', {})
                            #             purchase_validation = t.get('purchase_validation', {})
                                        
                            #             # Filter tcresultNote: 적용한 필터들과 검증 결과
                            #             text_passed = text_validation.get('passed', False)
                            #             text_desc = text_validation.get('desc', '')
                                        
                            #             # 적용한 필터들 정보 구성
                            #             applied_filters = []
                            #             for filter_name in filter_names:
                            #                 applied_filters.append(f"{filter_name}")
                                        
                            #             if text_passed:
                            #                 # True: 적용한 필터들만 표시
                            #                 filter_note = f"filter: ({', '.join(applied_filters)})"
                            #             else:
                            #                 # False: 적용한 필터들과 일치하지 않는 체크박스 표시
                            #                 filter_note = f"filter: ({', '.join(applied_filters)}) | unmatch: {text_desc}"
                                        
                            #             # Filter 검증 로그
                            #             log.info(f"[Filter Validation] {filter_tc_id}: {text_passed} - {filter_note}")
                            #             result.append(AnalysisAdd(tcId=filter_tc_id, tcresult=10 if text_passed else 0, tcresultNote=filter_note))
                                        
                            #             # 2. Filter_Purchase 검증 라인 생성 (필터 적용 후 구매 가능 여부)
                            #             if len(filter_names) == 1:
                            #                 # 개별 테스트: Filter_Purchase / 필터명 / idx
                            #                 filter_name = filter_names[0]
                            #                 filter_purchase_tc_id = f"{main_category} / {sub_category} / Filter_Purchase / {filter_name} / {filter_indices[filter_name]:02d}"
                            #             else:
                            #                 # 랜덤 조합 테스트: Filter_Purchase / 적용한필터명_적용한필터명
                            #                 filter_combination = "_".join(filter_names)
                            #                 filter_purchase_tc_id = f"{main_category} / {sub_category} / Filter_Purchase / {filter_combination}"
                                        
                            #             # Filter_Purchase 검증 결과 (필터 적용 후 구매 가능 여부)
                            #             # purchase_validation 정보 사용
                            #             purchase_passed = purchase_validation.get('passed', False)
                            #             purchase_desc = purchase_validation.get('desc', '')
                                        
                            #             # Filter_Purchase tcresultNote: 구매 검증 결과
                            #             if purchase_passed:
                            #                 # True: 빈 문자열
                            #                 filter_purchase_note = ""
                            #             else:
                            #                 # False: 가격 정보가 없는 상품명
                            #                 filter_purchase_note = purchase_desc
                                        
                            #             # Filter_Purchase 검증 로그
                            #             log.info(f"[Filter_Purchase Validation] {filter_purchase_tc_id}: {purchase_passed} - {filter_purchase_note}")
                                        
                            #             # Filter_Purchase tcresultNote: 구매 검증 결과만 포함
                            #             result.append(AnalysisAdd(tcId=filter_purchase_tc_id, tcresult=10 if purchase_passed else 0, tcresultNote=filter_purchase_note))

                            # # Purchase 검증 라인 (전체 결과를 1개 TC로 통합)
                            # p_note = getattr(node, 'purchase_validate_desc', '')
                            # tc_id = f"{main_category} / {sub_category} / Purchase"
                            # result.append(AnalysisAdd(tcId=tc_id, tcresult=10 if node.purchase_validate else 0, tcresultNote=p_note))

                            # # BreadCrumb 검증 라인 (desc를 그대로 사용)
                            # bc_note = getattr(node, 'breadcrumb_validate_desc', '')
                            # tc_id = f"{main_category} / {sub_category} / Breadcrumb"
                            # result.append(AnalysisAdd(tcId=tc_id, tcresult=10 if node.breadcrumb_validate else 0, tcresultNote=bc_note))

                            return result

                        # all_shop_result는 list[MainCategoryNode]이므로, 각 메인 카테고리의 서브 노드들을 순회하여 결과를 합침
                        analysis_add_list = []
                        for main_node in all_shop_result:
                            if main_node.children:
                                for sub_node in main_node.children:
                                    analysis_add_list.extend(collect_analysis_add_list(sub_node, main_node.name))
                        
                        # 생성된 분석 결과 리스트를 로그로 출력
                        for idx, analysis in enumerate(analysis_add_list, 1):
                            log.info(f"[AnalysisAdd {idx}] tcId: {analysis.tcId}, tcresult: {analysis.tcresult}, tcresultNote: {analysis.tcresultNote}")
                        
                        log.info(f"add_analysis index:{target_url_dto.index} status:{200}")
                        await zest.add_analysis(target_url_dto.index, 200, analysis_add_list, note="-")
                    
                    # PF 트리 구조를 JSON 파일로 저장
                    if not all_shop_result:
                        log.error("Navigation validation failed. No results returned.")
                        continue  # 다음 URL로 넘어감
                    save_product_list(all_shop_result, target_url_dto.url, target_url_dto.siteCode)
                    log.debug("Operation completed successfully")
                except Exception as e:
                    # 예외 발생 시 상세 로그 기록
                    log.error(f"Error occurred: {e}", exc_info=True)
                    pass
                finally:
                    # WDS 로그인 모드가 아닌 경우에만 컨텍스트/페이지 종료
                    if not wds_login:
                        log.debug("Closing browser context and page (non-WDS mode)")
                        try:
                            if 'page' in locals() and page:
                                await page.close()
                            if 'context' in locals() and context:
                                await context.close()
                        except Exception as e:
                            log.warning(f"Error closing context/page: {e}")
                    else:
                        # WDS 모드에서는 새로 생성된 탭만 닫기
                        log.debug("Closing current tab (WDS mode)")
                        try:
                            if 'page' in locals() and page:
                                await page.close()
                                log.info("Current tab closed successfully")
                        except Exception as e:
                            log.warning(f"Error closing current tab: {e}")
            
            # 최종 정리: WDS 컨텍스트 및 브라우저 인스턴스 종료 (모든 URL 처리 후)
            if wds_login:
                log.info("Closing WDS page and context")
                try:
                    if 'wds_page' in locals() and wds_page:
                        await wds_page.close()
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
            try:
                if zest:
                    await zest.close()
            except Exception:
                pass  # Zest API 종료 실패는 무시하고 계속 진행
            log.info("Zest api instance closed successfully")

    # 4. 비동기 메인 실행
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt: Graceful shutdown")


if __name__ == "__main__":
    main()