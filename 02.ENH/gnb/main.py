"""
main.py - 웹 페이지 GNB 추출 애플리케이션의 메인 모듈

이 모듈은 삼성 웹사이트의 GNB(Global Navigation Bar) 구조를 자동으로 추출하는
애플리케이션의 진입점입니다. 다음 기능을 제공합니다:
- 명령줄 인자 파싱 (SSI)
- Zest API 연동 및 URL 예약
- 웹 크롤링을 통한 GNB 추출
- CGD와의 구조 비교 검증
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
from gnb import extract_gnb_structure, print_gnb_tree, save_gnb_tree_to_json, check_link_validity
from verify import load_latest_cgdtree, verify_gnb_vs_cgd
from utility.orangelogger import log

# 기본 분석 대상 URL 및 사이트 코드 쌍
DEFAULT_TARGETS = [
    {"url": "https://www.samsung.com/uk/", "siteCode": "UA"},  # 테스트용 기본값
    {"url": "https://www.samsung.com/ua/", "siteCode": "UA"},  # 테스트용 기본값
]

def main() -> None:
    """
    메인 애플리케이션 실행 함수
    여러 개의 URL을 예약받아 순차적으로 GNB 추출 및 링크 검사를 수행합니다.
    브라우저 인스턴스는 한 번만 생성하고, 각 URL마다 context/page만 새로 생성/종료합니다.

    파라미터:
        없음 (명령줄 인자에서 스냅샷 인덱스를 받음)
        --no-validate: 링크 유효성 검사(HTTP 응답, 정상 접근 등)를 생략하는 옵션 플래그
    반환값:
        없음
    예시:
        python main.py --ssi 1234567890
        python main.py --ssi 1234567890 --no-validate  # 링크 유효성 검사 생략
    동작:
        --no-validate 플래그가 있으면 GNB 트리 추출/비교는 수행하지만, 링크 유효성 검사는 건너뜁니다.
    """
    # 1. 명령줄 인수 파싱
    parser = argparse.ArgumentParser(description="웹 페이지 분석 앱")
    parser.add_argument("--ssi", type=str, help="스냅샷 인덱스 (필수)", required=False)
    parser.add_argument("--no-validate", action="store_true", help="링크 유효성 검사 생략 플래그")

    args = parser.parse_args()

    # 3. Playwright 세션 시작
    async def async_main():
        """
        Playwright 비동기 세션 내에서 각 URL별로 GNB 추출 및 검사 실행
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
                    # GNB 메뉴 구조 추출 및 트리 출력
                    log.info("Extracting GNB navigation menu structure")
                    gnb_result = await extract_gnb_structure(page)
                    print_gnb_tree(gnb_result)
                    # CGD 기준 트리(엑셀에서 추출된 메뉴 구조) 최신본을 로드
                    cgdtree_roots, cgd_filename = load_latest_cgdtree(target_url_dto.siteCode)
                    # GNB 트리와 CGD 트리를 계층적으로 비교하여 일치 여부를 검증
                    verify_gnb_vs_cgd(gnb_result, cgdtree_roots)
                    # GNB 트리 내 모든 링크에 대해 실제 접근성/정상 응답 검사
                    if not args.no_validate:
                        await check_link_validity(gnb_result, page)
                        log.info("GNB LinkValidation completed!")

                    # 분석 결과 전송 및 로그 출력, add_analysis 호출은 ssi가 있을 때만 수행
                    if args.ssi:
                        def collect_analysis_add_list(node, path: list = None) -> list:
                            """
                            GnbMenuNode 트리를 순회하며 각 노드의 link_validate 정보를 기반으로 AnalysisAdd 리스트를 생성합니다.
                            tc_id는 '최상위/중간/현재' 형태로 생성합니다.
                            """
                            if path is None:
                                path = []
                            result = []
                            current_path = path + [node.name]
                            tc_id = " / ".join(current_path)
                            tc_result = 10 if node.link_validate else 0
                            tc_result_note = (
                                f"name: {node.name_verify}, "
                                f"url: {node.url_verify}, "
                                f"status: {node.link_status}, desc: {node.link_validate_desc}"
                            )
                            result.append(AnalysisAdd(tcId=tc_id, tcresult=tc_result, tcresultNote=tc_result_note))
                            for child in node.children:
                                result.extend(collect_analysis_add_list(child, current_path))
                            return result

                        # gnb_result는 list[GnbMenuNode]이므로, 각 루트 노드별로 순회 결과를 합침
                        analysis_add_list = []
                        for root in gnb_result:
                            analysis_add_list.extend(collect_analysis_add_list(root))

                        # 생성된 분석 결과 리스트를 로그로 출력
                        for idx, analysis in enumerate(analysis_add_list, 1):
                            log.info(f"[AnalysisAdd {idx}] tcId: {analysis.tcId}, tcresult: {analysis.tcresult}, tcresultNote: {analysis.tcresultNote}")

                        note_str = cgd_filename if cgd_filename else "No CGD file loaded"
                        log.info(f"add_analysis index:{target_url_dto.index} status:{200} note:{note_str}")
                        await zest.add_analysis(target_url_dto.index, 200, analysis_add_list, note=note_str)

                    # GNB 트리 구조를 JSON 파일로 저장
                    save_gnb_tree_to_json(gnb_result, target_url_dto.url)
                    log.debug("Operation completed successfully")
                except Exception as e:
                    # 예외 발생 시 상세 로그 기록 후
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
