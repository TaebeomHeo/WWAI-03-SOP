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
from utility.aem import check_login, scroll_for_lazyload
from shop import extract_shop_structure, print_shop_tree, save_shop_tree_to_json, check_link_validity, navigate_shop_structure
from utility.orangelogger import log

# DEFAULT_TARGET = {"url": "https://p6-pre-qa3.samsung.com/uk/new-shop/?co78price", "siteCode": "UK"}  # 테스트용 기본값
# 여러 개의 테스트/운영 URL을 한 번에 처리할 수 있도록 배열로 선언
DEFAULT_TARGETS = [
    # {"url": "https://www.samsung.com/fr/offer/", "siteCode": "FR"},
    # {"url": "https://www.samsung.com/au/offer/", "siteCode": "AU"},
    # {"url": "https://www.samsung.com/cn/offer/", "siteCode": "CN"},
    # {"url": "https://www.samsung.com/ph/offer/", "siteCode": "PH"},
    # {"url": "https://www.samsung.com/tr/offer/", "siteCode": "TR"},
    {"url": "https://www.samsung.com/pk/offer/", "siteCode": "PK"},
    
    # {"url": "https://p6-pre-qa3.samsung.com/nz/new-shop/?co78price", "siteCode": "NZ"},
    # {"url": "https://p6-pre-qa3.samsung.com/au/new-shop/?co78price", "siteCode": "AU"},
    # {"url": "https://p6-pre-qa3.samsung.com/hk/new-shop/?co78price", "siteCode": "HK"},
    # {"url": "https://p6-pre-qa3.samsung.com/hk_en/new-shop/?co78price", "siteCode": "HK_EN"},
    # {"url": "https://p6-pre-qa3.samsung.com/cn/new-shop/?co78price", "siteCode": "CN"},
    # {"url": "https://p6-pre-qa3.samsung.com/tw/new-shop/?co78price", "siteCode": "TW"},
    # {"url": "https://p6-pre-qa3.samsung.com/ca_fr/new-shop/?co78price", "siteCode": "CA_FR"},
    # {"url": "https://p6-pre-qa3.samsung.com/ca/new-shop/?co78price", "siteCode": "CA"},
    # {"url": "https://p6-pre-qa3.samsung.com/mx/new-shop/?co78price", "siteCode": "MX"},
    # {"url": "https://p6-pre-qa3.samsung.com/br/new-shop/?co78price", "siteCode": "BR"},
    # {"url": "https://p6-pre-qa3.samsung.com/latin/new-shop/?co78price", "siteCode": "LATIN"},
    # {"url": "https://p6-pre-qa3.samsung.com/co/new-shop/?co78price", "siteCode": "CO"},
    # {"url": "https://p6-pre-qa3.samsung.com/py/new-shop/?co78price", "siteCode": "PY"},
    # {"url": "https://p6-pre-qa3.samsung.com/uy/new-shop/?co78price", "siteCode": "UY"},
    # {"url": "https://p6-pre-qa3.samsung.com/cl/new-shop/?co78price", "siteCode": "CL"},
    # {"url": "https://p6-pre-qa3.samsung.com/pe/new-shop/?co78price", "siteCode": "PE"},
    # {"url": "https://p6-pre-qa3.samsung.com/de/new-shop/?co78price", "siteCode": "DE"},
    # {"url": "https://p6-pre-qa3.samsung.com/ch/new-shop/?co78price", "siteCode": "CH"},
    # {"url": "https://p6-pre-qa3.samsung.com/ch_fr/new-shop/?co78price", "siteCode": "CH_FR"},
    # {"url": "https://p6-pre-qa3.samsung.com/uk/new-shop/?co78price", "siteCode": "UK"},
    # {"url": "https://p6-pre-qa3.samsung.com/es/new-shop/?co78price", "siteCode": "ES"},
    # {"url": "https://p6-pre-qa3.samsung.com/ie/new-shop/?co78price", "siteCode": "IE"},
    # {"url": "https://p6-pre-qa3.samsung.com/at/new-shop/?co78price", "siteCode": "AT"},
    # {"url": "https://p6-pre-qa3.samsung.com/dk/new-shop/?co78price", "siteCode": "DK"},
    # {"url": "https://p6-pre-qa3.samsung.com/fi/new-shop/?co78price", "siteCode": "FI"},
    # {"url": "https://p6-pre-qa3.samsung.com/no/new-shop/?co78price", "siteCode": "NO"},
    # {"url": "https://p6-pre-qa3.samsung.com/ro/new-shop/?co78price", "siteCode": "RO"},
    # {"url": "https://p6-pre-qa3.samsung.com/hu/new-shop/?co78price", "siteCode": "HU"},
    # {"url": "https://p6-pre-qa3.samsung.com/cz/new-shop/?co78price", "siteCode": "CZ"},
    # {"url": "https://p6-pre-qa3.samsung.com/sk/new-shop/?co78price", "siteCode": "SK"},
    # {"url": "https://p6-pre-qa3.samsung.com/ee/new-shop/?co78price", "siteCode": "EE"},
    # {"url": "https://p6-pre-qa3.samsung.com/lt/new-shop/?co78price", "siteCode": "LT"},
    # {"url": "https://p6-pre-qa3.samsung.com/hr/new-shop/?co78price", "siteCode": "HR"},
    # {"url": "https://p6-pre-qa3.samsung.com/si/new-shop/?co78price", "siteCode": "SI"},
    # {"url": "https://p6-pre-qa3.samsung.com/ua/new-shop/?co78price", "siteCode": "UA"},
    # {"url": "https://p6-pre-qa3.samsung.com/gr/new-shop/?co78price", "siteCode": "GR"},
    # {"url": "https://p6-pre-qa3.samsung.com/nl/new-shop/?co78price", "siteCode": "NL"},
    # {"url": "https://p6-pre-qa3.samsung.com/be/new-shop/?co78price", "siteCode": "BE"},
    # {"url": "https://p6-pre-qa3.samsung.com/be_fr/new-shop/?co78price", "siteCode": "BE_FR"},
    # {"url": "https://p6-pre-qa3.samsung.com/kz_ru/new-shop/?co78price", "siteCode": "KZ_RU"},
    # {"url": "https://p6-pre-qa3.samsung.com/kz_kz/new-shop/?co78price", "siteCode": "KZ_KZ"},
    # {"url": "https://p6-pre-qa3.samsung.com/in/new-shop/?co78price", "siteCode": "IN"},
    # {"url": "https://p6-pre-qa3.samsung.com/ae/new-shop/?co78price", "siteCode": "AE"},
    # {"url": "https://p6-pre-qa3.samsung.com/ae_ar/new-shop/?co78price", "siteCode": "AE_AR"},
    # {"url": "https://p6-pre-qa3.samsung.com/il/new-shop/?co78price", "siteCode": "IL"},
    # {"url": "https://p6-pre-qa3.samsung.com/sa/new-shop/?co78price", "siteCode": "SA"},
    # {"url": "https://p6-pre-qa3.samsung.com/sa_en/new-shop/?co78price", "siteCode": "SA_EN"},
    # {"url": "https://p6-pre-qa3.samsung.com/tr/new-shop/?co78price", "siteCode": "TR"},
    # {"url": "https://p6-pre-qa3.samsung.com/levant/new-shop/?co78price", "siteCode": "LEVANT"},
    # {"url": "https://p6-pre-qa3.samsung.com/levant_ar/new-shop/?co78price", "siteCode": "LEVANT_AR"},
    # {"url": "https://p6-pre-qa3.samsung.com/iq_ar/new-shop/?co78price", "siteCode": "IQ_AR"},
    # {"url": "https://p6-pre-qa3.samsung.com/iq_ku/new-shop/?co78price", "siteCode": "IQ_KU"},
    # {"url": "https://p6-pre-qa3.samsung.com/pk/new-shop/?co78price", "siteCode": "PK"},
    # {"url": "https://p6-pre-qa3.samsung.com/eg/new-shop/?co78price", "siteCode": "EG"},
    # {"url": "https://p6-pre-qa3.samsung.com/n_africa/new-shop/?co78price", "siteCode": "N_AFRICA"},
]

def main() -> None:
    """
    메인 애플리케이션 실행 함수
    여러 개의 URL을 입력받아 순차적으로 SHOP 추출 및 링크 검사를 수행합니다.
    브라우저 인스턴스는 한 번만 생성하고, 각 URL마다 context/page만 새로 생성/종료합니다.

    파라미터:
        없음 (명령줄 인자에서 URL 리스트를 받음)
    반환값:
        없음
    예시:
        python main.py --url https://site1.com https://site2.com
        python main.py --no-validate  # 링크 유효성 검사 생략
    """
    # 1. 명령줄 인수 파싱
    parser = argparse.ArgumentParser(description="웹 페이지 분석 앱")
    parser.add_argument("--ssi", type=str, help="스냅샷 인덱스 (필수)", required=False)
    parser.add_argument("--no-validate", action="store_true", help="링크 유효성 검사 생략 플래그")

    args = parser.parse_args()
 
    # 3. Playwright 세션 시작
    async def async_main():
        """
        Playwright 비동기 세션 내에서 각 URL별로 SHOP 추출 및 검사 실행
        """
        async with async_playwright() as playwright:
            zest = create_zest()
            browser = await playwright.chromium.launch(headless=False)
            taskid = generate_random_digit()
            default_target_idx = 0  # DEFAULT_TARGETS 배열 인덱스
            log.info(f"Starting application with ssi: {args.ssi}, taskid: {taskid}")
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
                    # ssi 미지정 시: DEFAULT_TARGET 값으로 1회만 수행, 테스트 및 디버깅 용도로 필요함
                    # 기존 DEFAULT_TARGET을 배열로 대체하여 여러 URL을 순차적으로 처리
                    if default_target_idx >= len(DEFAULT_TARGETS):
                        break
                    target = DEFAULT_TARGETS[default_target_idx]
                    target_url_dto = UrlDto(index=0, snapshotIndex=0, status=0, url=target["url"], siteCode=target["siteCode"])
                    default_target_idx += 1
                log.info(f"Target URL: {target_url_dto.url}, UrlIndex: {target_url_dto.index}")
                # 각 URL별로 새로운 브라우저 컨텍스트 및 페이지 생성
                context = await browser.new_context()
                page = await context.new_page()
                
                try:
                    # 대상 URL로 이동 (최초 진입)
                    log.info(f"Navigating to target URL: {target_url_dto.url}")
                    response = await page.goto(target_url_dto.url)
                    # 로그인 필요 여부 확인 및 자동 로그인 처리
                    log.debug("Checking login status and handling login if needed")
                    await check_login(page, response, target_url_dto.url)
                    # 로그인 후 메인 페이지로 재이동
                    response = await page.goto(target_url_dto.url)
                    # DOMContentLoaded까지 페이지 로드 대기
                    log.debug("Waiting for DOMContentLoaded event")
                    await page.wait_for_load_state("domcontentloaded")
                    log.info("Page basic loading completed")
                    # 지연 로딩(스크롤 기반) 컨텐츠 모두 로드
                    log.info("Scrolling page to trigger lazy-loaded content")
                    await scroll_for_lazyload(page)
                    log.info("Full page scroll completed")
                    # SHOP 메뉴 구조 추출 및 트리 출력
                    log.info("Extracting SHOP navigation menu structure")
                    # shop_result = await extract_shop_structure(page) # DOM 구조에서 한꺼번에 추출하는 방식
                    shop_result = await navigate_shop_structure(page) # 실제 Click 탐색을 하면서 추출하는 방식
                    print_shop_tree(shop_result)
                    # SHOP 트리 내 모든 링크에 대해 실제 접근성/정상 응답 검사
                    if not args.no_validate:
                        await check_link_validity(shop_result, page)
                        log.info("SHOP LinkValidation completed!")
                    # 분석 결과 전송 및 로그 출력, add_analysis 호출은 ssi가 있을 때만 수행
                    if args.ssi:
                        def collect_analysis_add_list(node, path: list = None) -> list:
                            """
                            트리를 순회하며 각 노드의 link_validate 정보를 기반으로 AnalysisAdd 리스트를 생성합니다.
                            tc_id는 '최상위/중간/현재' 형태로 생성합니다.
                            """
                            if path is None:
                                path = []
                            result = []
                            current_path = path + [node.name]
                            tc_id = " / ".join(current_path)
                            tc_result = 10 if node.link_validate else 0
                            tc_result_note = (
                                f"status: {node.link_status}, desc: {node.link_validate_desc}"
                                f"{f' -- {node.desc}' if node.desc and node.desc.strip() else ''}"
                            )
                            result.append(AnalysisAdd(tcId=tc_id, tcresult=tc_result, tcresultNote=tc_result_note))
                            for child in node.children:
                                result.extend(collect_analysis_add_list(child, current_path))
                            return result

                        # gnb_result는 list[GnbMenuNode]이므로, 각 루트 노드별로 순회 결과를 합침
                        analysis_add_list = []
                        for root in shop_result:
                            analysis_add_list.extend(collect_analysis_add_list(root))
                        # 생성된 분석 결과 리스트를 로그로 출력
                        for idx, analysis in enumerate(analysis_add_list, 1):
                            log.info(f"[AnalysisAdd {idx}] tcId: {analysis.tcId}, tcresult: {analysis.tcresult}, tcresultNote: {analysis.tcresultNote}")
                        log.info(f"add_analysis index:{target_url_dto.index} status:{200}")
                        await zest.add_analysis(target_url_dto.index, 200, analysis_add_list, note="-")
                    # SHOP 트리 구조를 JSON 파일로 저장
                    save_shop_tree_to_json(shop_result, target_url_dto.url, target_url_dto.siteCode)
                    log.debug("Operation completed successfully")
                except Exception as e:
                    # 예외 발생 시 상세 로그 기록
                    log.error(f"Error occurred: {e}", exc_info=True)
                    pass
                finally:
                    # 컨텍스트/페이지 안전하게 종료 (리소스 누수 방지)
                    log.debug("Closing browser context and page")
                    try:
                        if page:
                            await page.close()
                    except Exception:
                        pass
                    try:
                        if context:
                            await context.close()
                    except Exception:
                        pass
            # 브라우저 인스턴스 종료 (모든 URL 처리 후)
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
            log.info("Zest api instance closed successfully")

    # 4. 비동기 메인 실행
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt: Graceful shutdown")


if __name__ == "__main__":
    main()