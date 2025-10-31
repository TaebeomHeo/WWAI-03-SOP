"""
pf.py - PF 페이지 제품 정보 추출 모듈

PF 페이지에서 제품 정보를 자동으로 추출하고 구조화합니다.

주요 기능:
- nv19 (main navigation) 및 nv20 (sub navigation) 추출
- 제품 정보 추출 (이름, URL, 가격, 설명, 배지 등)
- 구매 가능성 검증 (위에서부터 4개 제품)
- 필터 기능 검증 (별도 filter.py 모듈 사용)
- 결과를 계층적 구조로 구성
"""

import json
import os
import asyncio
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Union
from urllib.parse import urljoin, urlparse
from datetime import datetime
from playwright.async_api import Page
from bs4 import BeautifulSoup, Comment
from utility.orangelogger import log
from pf_modules.filter import extract_filter_structure, validate_filter
from pf_modules.live_validation import extract_breadcrumb, extract_faq, extract_disclaimer, validate_all_live_elements, validate_live_comparison, DOMNode
from pf_modules.node import PfMenuNode, SubCategoryNode, MainCategoryNode, create_navigation_node
from pf_modules.result_count import extract_result_count
from pf_modules.nv17 import validate_nv17_breadcrumb_absence
from pf_modules.purchase import validate_purchase_capability
from pf_modules.sort import validate_sort


########################################################################################
# 공통 파싱 함수 (HTML 파싱 시 사용)
########################################################################################
def _find_first_class(element) -> str | None:
    """
    요소에서 첫 번째 class명을 반환합니다.

    동작 방식:
    - element의 class 속성에서 첫 번째 클래스명 추출
    - class가 없거나 빈 리스트인 경우 None 반환

    파라미터:
        element: HTML 요소 객체 (BeautifulSoup element)

    반환값:
        str | None: 첫 번째 클래스명 (없으면 None)

    예외 처리:
    - element가 None인 경우: None 반환
    - class 속성이 없는 경우: None 반환
    - 예외 발생: None 반환

    사용 예시:
        first_class = _find_first_class(element)
        if first_class:
            print(f"First class: {first_class}")
    """
    classes = element.get("class", [])
    if classes:
        return classes[0]
    return None


def _find_nearest_class(element) -> str | None:
    """
    자신 또는 상위 요소에서 첫 번째 class명을 찾아 반환합니다.

    동작 방식:
    - 현재 요소에서 class명 확인
    - 없으면 상위 요소로 올라가면서 class명 검색
    - 최상위 요소까지 검색하여 첫 번째 class명 반환

    파라미터:
        element: HTML 요소 객체 (BeautifulSoup element)

    반환값:
        str | None: 찾은 첫 번째 클래스명 (없으면 None)

    예외 처리:
    - element가 None인 경우: None 반환
    - 상위 요소 접근 실패: None 반환
    - 예외 발생: None 반환

    사용 예시:
        nearest_class = _find_nearest_class(element)
        if nearest_class:
            print(f"Nearest class: {nearest_class}")
    """
    cur = element
    while cur:
        class_name = _find_first_class(cur)
        if class_name:
            return class_name
        cur = cur.parent if hasattr(cur, "parent") else None
    return None


########################################################################################
# 제품 정보 추출
########################################################################################
def _extract_meta_tree(element) -> dict | None:
    """
    HTML class명 기반 트리(dict) 구조로 meta를 추출합니다.
    - 각 요소의 class명을 key로 하여, 자기 자신의 모든 직접 텍스트를 합쳐 text로 저장
    - 하위 요소 중 class명이 있는 정보성 요소는 상위 dict의 key로 중첩해서 저장
    - 하위 요소가 class가 없고, UI 목적 태그(span, b, i, u 등)이며, 정보성 속성(aria-, an-, data-)이 없으면, 하위 요소의 텍스트를 상위 요소의 text에 합쳐서 저장
    - 그 외에는 기존 트리 구조 유지
    - hidden class는 제외
    - 정보성 속성(aria-, an-, data-)도 value에 포함
    - HTML 주석(Comment), 공백/줄바꿈만 있는 텍스트는 meta에 포함하지 않음
    """
    if "hidden" in element.get("class", []):
        return None
    key = _find_first_class(element) or _find_nearest_class(element)
    if not key:
        return None
    # 자기 자신의 모든 직접 텍스트 합치기(주석 제외)
    direct_texts = [
        t for t in element.contents if isinstance(t, str) and not isinstance(t, Comment)
    ]
    text = "".join(direct_texts).strip()
    info_attrs = {
        k: v
        for k, v in element.attrs.items()
        if (k.startswith("aria") or k.startswith("an-") or k.startswith("data-"))
        and v
        and v != "NaN"
    }
    children = [
        child
        for child in element.find_all(recursive=False)
        if getattr(child, "name", None)
    ]
    child_dict = {}
    ui_tags = {"span", "b", "i", "u"}
    for child in children:
        child_key = _find_first_class(child) or _find_nearest_class(child)
        # UI 목적 태그 + class 없음 + 정보성 속성 없음 → 상위 text에 합침
        is_ui = child.name in ui_tags
        has_class = bool(child.get("class", []))
        has_info_attr = any(
            (k.startswith("aria") or k.startswith("an-") or k.startswith("data-"))
            and v
            and v != "NaN"
            for k, v in child.attrs.items()
        )
        if not has_class and is_ui and not has_info_attr:
            # 하위의 모든 직접 텍스트(주석 제외)
            child_direct_texts = [
                t
                for t in child.contents
                if isinstance(t, str) and not isinstance(t, Comment)
            ]
            child_text = "".join(child_direct_texts).strip()
            if child_text:
                text = (text + " " + child_text).strip() if text else child_text
            continue
        # 그 외에는 기존 트리 구조 유지
        if not child_key:
            continue
        child_val = _extract_meta_tree(child)
        if child_val is not None:
            if child_key in child_dict:
                if isinstance(child_dict[child_key], list):
                    child_dict[child_key].append(child_val[child_key])
                else:
                    child_dict[child_key] = [
                        child_dict[child_key],
                        child_val[child_key],
                    ]
            else:
                child_dict.update(child_val)
    value = {}
    if text:
        value["text"] = text
    if info_attrs:
        value.update(info_attrs)
    if child_dict:
        value.update(child_dict)
    if not value:
        return None
    return {key: value}


def _extract_meta_dynamic(content_wrap) -> dict:
    """
    content-wrap에서 class명 기반 트리 구조로 meta를 추출합니다.
    - 최상위 요소의 하위 class 요소들만 meta에 포함
    """
    meta = {}
    for child in content_wrap.find_all(recursive=False):
        child_val = _extract_meta_tree(child)
        if child_val:
            meta.update(child_val)
    return meta


async def load_more_product(page: Page) -> None:
    """
    'View more' 버튼을 한 번만 클릭하여 추가 제품을 로드합니다.
    - 버튼 탐색은 'pd19-product-finder__view-more-btn' 클래스와 an-ac='view more' 속성 기준으로만 수행
    """
    log.info("[load_more_product] Try clicking 'View more' button once.")
    btn = await page.query_selector(
        "button.pd19-product-finder__view-more-btn[an-ac='view more']"
    )
    if not btn:
        log.info("[load_more_product] No 'View more' button found.")
        return
    try:
        await btn.click(force=True)
        log.info("[load_more_product] Clicked 'View more' button once.")
    except Exception as e:
        log.warning(f"[load_more_product] Exception while clicking 'View more': {e}")
    log.info("[load_more_product] Done. Products loaded (if any).")


async def extract_product(page: Page) -> List[PfMenuNode]:
    """
    현재 페이지에 로드된 모든 제품 카드를 파싱하여 PfMenuNode 리스트로 반환합니다.
    
    추출 정보:
    - 제품명, URL, 설명, 배지
    - 가격 정보 (레거시)
    - CTA 버튼의 an-la 속성 (구매 가능 여부 판단용)
    - 메타 정보 (동적 추출)
    
    파라미터:
        page (Page): Playwright Page 객체

    반환값:
        List[PfMenuNode]: 추출된 제품 정보 리스트
    """
    log.info("[extract_product] Start extracting all product cards from page.")
    html_content = await page.content()
    soup = BeautifulSoup(html_content, "html.parser")
    parsed = urlparse(page.url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"
    product_cards = soup.select("div.pd21-product-card__item")
    log.info(f"[extract_product] Found {len(product_cards)} product card candidates.")

    products: List[PfMenuNode] = []
    banner_count = 0

    for card in product_cards:
        productidx = card.get("data-productidx", "").strip()
        itemidx = card.get("data-item-idx", "").strip()
        class_attr = " ".join(card.get("class", []))

        # 디버깅: 상품 카드 정보 출력
        log.debug(
            f"[extract_product] Product card: data-productidx='{productidx}', data-item-idx='{itemidx}', class='{class_attr}'"
        )

        # data-productidx 또는 data-item-idx 중 하나라도 있으면 상품으로 인정
        if not productidx and not itemidx:
            log.debug(
                f"[extract_product] Skipping card without data-productidx or data-item-idx"
            )
            continue

        # 배너 제외 로직 강화
        is_banner = False

        # 방법 1: card 자체가 pd21-product-card__banner 클래스를 가진 경우
        card_classes = card.get("class", [])
        if "pd21-product-card__banner" in card_classes:
            is_banner = True

        # 방법 2: card 내부에 pd21-product-card__banner 클래스를 가진 요소가 있는 경우
        if not is_banner and card.select_one(".pd21-product-card__banner"):
            is_banner = True

        # 방법 3: card의 data-card-type이 "vertical"이고 pd21-product-card__banner 클래스를 가진 경우
        if not is_banner:
            card_type = card.get("data-card-type", "")
            if card_type == "vertical" and card.select_one(
                ".pd21-product-card__banner"
            ):
                is_banner = True

        if is_banner:
            banner_count += 1
            log.debug(f"[extract_product] Excluded banner product: {class_attr}")
            continue

        # display: none인 제품 카드 제외
        style = card.get("style", "")
        if "display: none" in style:
            continue

        badge_tag = card.select_one(".badge-icon.badge-icon--label-v2 ")
        badge = badge_tag.get_text(strip=True) if badge_tag else ""

        name = ""
        url = ""
        price = ""
        cta_an_la = ""
        desc = ""
        meta = {}

        if card:
            name_tag = card.select_one(".pd21-product-card__name")
            if name_tag:
                name = name_tag.get_text(strip=True)
                url = (
                    urljoin(base_domain, name_tag.get("href", ""))
                    if name_tag.has_attr("href")
                    else ""
                )

            # 가격 정보 추출: cta-wrap > data-modelprice 우선
            cta_price_tag = card.select_one(
                ".pd21-product-card__cta-wrap [data-modelprice]"
            )
            if cta_price_tag and cta_price_tag.has_attr("data-modelprice"):
                price = cta_price_tag["data-modelprice"]
            else:
                price_tag = card.select_one(
                    ".pd21-product-card__price, .product-card__price, .product-card__price--final, .price"
                )
                if price_tag:
                    price = price_tag.get_text(strip=True)
            
            # CTA 버튼의 an-la 속성 추출
            cta_button = card.select_one('button.cta--contained.cta--black')
            if cta_button and cta_button.has_attr('an-la'):
                cta_an_la = cta_button['an-la']
                    
            desc_tag = card.select_one(".pd21-product-card__desc")
            desc = desc_tag.get_text(strip=True) if desc_tag else ""

            meta = _extract_meta_dynamic(card)

        node = PfMenuNode(
            name=name,
            url=url,
            price=price,
            cta_an_la=cta_an_la,
            desc=desc,
            badge=badge,
            meta=meta
        )
        products.append(node)
        log.debug(
            f"[extract_product] Valid product added: name='{name}', productidx='{productidx}', itemidx='{itemidx}'"
        )

    log.info(
        f"[extract_product] Extracted {len(products)} valid product cards (excluded {banner_count} banner items)."
    )
    return products


########################################################################################
# 페이지 정보 추출
########################################################################################
async def _extract_subtab_info(
    page: Page, current_url: str
) -> tuple[str, List[dict]] | None:
    """
    현재 페이지에서 현재 탭 이름과 href가 있는 nv20 (sub navigation)들을 추출합니다.

    파라미터:
        page (Page): Playwright Page 객체
        current_url (str): 현재 페이지 URL

    반환값:
        None: .tab__item-title이 없는 경우 (단일 페이지)
        tuple[str, List[dict]]: (현재 탭 이름, href가 있는 nv20 (sub navigation)들)
    """
    try:
        current_tab_name = None

        # .tab__item-title 요소 확인
        tab_title_elements = await page.query_selector_all(".tab__item-title")
        if not tab_title_elements:
            log.info(
                "[_extract_subtab_info] No tab__item-title elements found. Single page detected."
            )
            return current_tab_name, None

        # 모든 nv20 요소 처리 (visibility 확인 제거)
        log.info(
            f"[_extract_subtab_info] Found {len(tab_title_elements)} tab title elements"
        )
        subtabs = []

        for element in tab_title_elements:
            try:
                # nv20 (sub navigation) 이름 추출
                name = await element.inner_text()
                name = name.strip()
                if not name:
                    log.debug("[_extract_subtab_info] Skipping element with empty name")
                    continue

                # href 속성 확인
                href = await element.get_attribute("href")

                if not href:
                    # href가 없는 경우 = 현재 활성 탭
                    current_tab_name = name
                    log.debug(f"[_extract_subtab_info] Found current tab: {name}")
                    continue

                # href가 있는 경우 = 다른 nv20
                # 절대 URL로 변환
                log.debug(f"[_extract_subtab_info] Base URL: {current_url}")
                log.debug(f"[_extract_subtab_info] Relative href: {href}")

                # Base URL이 빈 문자열이거나 유효하지 않은 경우 page.url 사용
                if not current_url or not current_url.startswith("http"):
                    log.warning(
                        f"[_extract_subtab_info] Invalid base URL: '{current_url}', using page URL: {page.url}"
                    )
                    current_url = page.url

                url = urljoin(current_url, href)
                log.debug(f"[_extract_subtab_info] urljoin result: {url}")

                # URL 유효성 검사 및 로깅
                if not url or url.strip() == "":
                    log.warning(f"[_extract_subtab_info] Empty URL for subtab: {name}")
                    continue

                if not url.startswith("http"):
                    log.warning(
                        f"[_extract_subtab_info] Invalid URL format for subtab {name}: {url}"
                    )
                    log.warning(f"[_extract_subtab_info] Base URL was: {current_url}")
                    continue

                log.debug(f"[_extract_subtab_info] Subtab {name}: {href} -> {url}")

                subtabs.append({"name": name, "url": url})

            except Exception as e:
                log.warning(
                    f"[_extract_subtab_info] Error processing subtab element: {e}"
                )
                continue

        log.info(
            f"[_extract_subtab_info] Current tab: {current_tab_name}, Other subtabs: {len(subtabs)}"
        )
        return current_tab_name, subtabs

    except Exception as e:
        log.error(f"[_extract_subtab_info] Error extracting subtab info: {e}")
        return current_tab_name, None


async def _validate_headline(page: Page) -> tuple[bool, bool, str]:
    """
    현재 페이지에서 헤드라인의 DOM 존재 여부, 가시성, 텍스트를 확인합니다.
    
    동작 방식:
    - .co77-text-block-home__headline 요소의 DOM 존재 여부 확인
    - 요소가 존재하는 경우 is_visible() 메서드로 가시성 확인
    - 텍스트 추출
    
    파라미터:
        page (Page): Playwright Page 객체

    반환값:
        tuple[bool, bool, str]: (DOM 존재 여부, visible 여부, 헤드라인 텍스트)
    
    예외 처리:
    - 예외 발생 시 (False, False, "") 반환
    """
    try:
        # 헤드라인 요소 선택자 (.co77-text-block-home__headline 클래스)
        headline_element = await page.query_selector(".co77-text-block-home__headline")
        
        if not headline_element:
            # DOM에 존재하지 않음
            log.warning("Headline element does not exist in DOM")
            return False, False, ""
        
        # DOM에 존재하는 경우 가시성 확인
        is_visible = await headline_element.is_visible()
        
        if not is_visible:
            # DOM에는 존재하나 visible하지 않음
            log.warning("Headline element exists in DOM but is not visible")
            return True, False, ""
        
        # visible한 경우 텍스트 추출
        headline_text = await headline_element.inner_text()
        headline_text = headline_text.strip()
        log.info(f"Headline element exists and is visible: {headline_text}")
        return True, True, headline_text
        
    except Exception as e:
        log.error(f"Error extracting headline: {e}")
        return False, False, ""


########################################################################################
# nv20 (sub navigation) 처리
########################################################################################
async def _process_subtab(
    page: Page,
    subtab: dict,
    main_category_node: MainCategoryNode,
    is_new_tab: bool = False,
    browser=None,
    wds_page=None,
) -> SubCategoryNode:
    """
    통합 nv20 (sub navigation) 처리 함수 - 현재 탭과 새 탭 모두에서 사용

    동작 방식:
    - 특수 nv20 여부 확인 (요소 존재 및 메인 탭 비교)
    - 링크 상태 검증 (HTTP 응답 코드 확인)
    - 네비게이션 가시성 검증 (nv19/nv20 요소 존재 및 표시 여부)
    - 헤드라인 검증 (제품명과 헤드라인 일치 여부)
    - 결과 수 추출 및 검증
    - 필터 검증 (현재 탭인 경우에만)

    파라미터:
        page (Page): 처리할 페이지 (현재 탭 또는 새 탭)
        subtab (dict): nv20 (sub navigation) 정보
        main_category_node (MainCategoryNode): nv19 (main navigation) 노드
        is_new_tab (bool): 새 탭 여부

    반환값:
        SubCategoryNode: 검증 결과가 포함된 nv20 노드
    """
    try:
        log.info(
            f"Processing subtab {'in new tab' if is_new_tab else 'in current tab'}: {subtab['name']} -> {subtab['url']}"
        )

        # 서브탭 처리 전 재로그인 체크 (새 탭인 경우에만)
        if is_new_tab and browser and wds_page:
            log.info("Checking login status before processing subtab")
            try:
                from utility.aem import check_and_handle_relogin

                context, page = await check_and_handle_relogin(
                    browser, page, subtab["url"], wds_page
                )
                log.info(
                    "Login status check completed - proceeding with subtab processing"
                )
            except Exception as relogin_error:
                log.error(f"Relogin check failed: {relogin_error}")
                log.warning(
                    "Continuing with current page despite relogin check failure"
                )

        # 새 탭인 경우 페이지로 이동
        response = None
        if is_new_tab:
            try:
                # URL 유효성 검사
                target_url = subtab["url"]
                if not target_url or target_url.strip() == "":
                    log.error(f"Empty URL for subtab: {subtab['name']}")
                    raise Exception(f"Empty URL for subtab: {subtab['name']}")

                # 상대 경로 URL을 절대 경로로 변환
                if not target_url.startswith("http"):
                    # 현재 페이지의 base URL을 사용하여 절대 URL 생성
                    from urllib.parse import urljoin

                    current_url = page.url
                    target_url = urljoin(current_url, target_url)
                    log.info(
                        f"Converted relative subtab URL to absolute: {subtab['url']} -> {target_url}"
                    )

                # 최종 URL 유효성 검사
                if not target_url.startswith("http"):
                    log.error(f"Invalid URL format after conversion: {target_url}")
                    raise Exception(
                        f"Invalid URL format after conversion: {target_url}"
                    )

                log.info(f"Navigating to subtab URL: {target_url}")

                # 타임아웃을 늘리고 더 안정적인 로딩 대기
                response = await page.goto(target_url, timeout=0)  # 타임아웃 제거

                # DOM 구조 로딩 완료 대기
                await page.wait_for_load_state("domcontentloaded", timeout=0)
                log.info(f"Page structure loaded for {subtab['name']}")

                # 추가로 중요한 요소들이 로딩될 때까지 대기
                try:
                    # 메인 컨텐츠 영역이 로딩될 때까지 대기
                    await page.wait_for_selector("body", timeout=0)
                    # 잠시 추가 대기 (동적 컨텐츠 로딩)
                    await page.wait_for_timeout(2000)
                except Exception as wait_e:
                    log.warning(f"Element wait timeout for {subtab['name']}: {wait_e}")

                log.info("Subtab page loading completed")
            except Exception as goto_e:
                log.error(f"Page goto failed for {subtab['name']}: {goto_e}")
                response = None

        # nv20 (sub navigation) 노드 생성
        sub_category_node = create_navigation_node(subtab["name"], subtab["url"])

        # 특수 nv20 여부 확인 (요소 존재 확인 후 판단)
        sub_category_node.is_special = False

        # 1. 완전히 다른 페이지로 이동하는 경우
        try:
            nv19_exists = (
                await page.query_selector(".nv19-pd-category-main") is not None
            )
            nv20_exists = await page.query_selector(".nv20-pd-category-sub") is not None
            filter_exists = await page.query_selector(".pd21-filter") is not None

            if not nv19_exists and not nv20_exists and not filter_exists:
                log.info(
                    f"Missing nv19, nv20, and filter elements - treating as special nv20"
                )
                sub_category_node.is_special = True
        except Exception as e:
            log.warning(f"Error checking page elements: {e}")

        # 2. 다른 nv19로 이동하는 경우
        if not sub_category_node.is_special:
            try:
                current_active_nv19 = await page.query_selector(
                    ".nv19-pd-category-main__item--active .nv19-pd-category-main__name .nv19-pd-category-main__maxchar--pc-only"
                )
                if current_active_nv19:
                    current_nv19_name = await current_active_nv19.inner_text()
                    current_nv19_name = (
                        current_nv19_name.strip() if current_nv19_name else ""
                    )

                    if current_nv19_name != main_category_node.name:
                        log.info(
                            f"Different nv19 detected: current='{current_nv19_name}' vs expected='{main_category_node.name}' - treating as special nv20"
                        )
                        sub_category_node.is_special = True
            except Exception as e:
                log.warning(f"Error checking current nv19: {e}")

        # 필터 테스트 대상 여부 판단 (현재 탭인 경우에만)
        is_filter_testable = not is_new_tab
        sub_category_node.is_filter_testable = is_filter_testable

        if is_filter_testable:
            log.info(f"This subtab will undergo filter testing: {subtab['name']}")

        # nv20 (sub navigation) 요소 visibility 확인
        nv19_element = await page.query_selector(".nv19-pd-category-main")
        nv20_element = await page.query_selector(".nv20-pd-category-sub")

        nv19_visible = False
        nv20_visible = False

        if nv19_element:
            nv19_visible = await nv19_element.is_visible()
        if nv20_element:
            nv20_visible = await nv20_element.is_visible()

        # 링크 상태 검증
        if is_new_tab and response:
            sub_category_node.link_status = response.status
        else:
            # 현재 탭인 경우
            sub_category_node.link_status = 200

        # 에러 페이지 감지 (HTTP 200이어도 에러 페이지가 표시될 수 있음)
        error_page_element = await page.query_selector(".ot02-error-page")
        is_error_page = error_page_element is not None

        # 링크 검증 로직 (새 탭과 현재 탭 공통)
        if sub_category_node.link_status == 200 and not is_error_page:
            sub_category_node.link_validate = True
        elif is_error_page:
            sub_category_node.link_validate = False
            sub_category_node.link_validate_desc = "error페이지"
            log.warning(
                f"Error page detected for {subtab['name']}, setting link_validate to False"
            )
        else:
            sub_category_node.link_validate = False
            sub_category_node.link_validate_desc = (
                f"status: {sub_category_node.link_status}"
            )
            log.warning(
                f"HTTP error {sub_category_node.link_status} for {subtab['name']}, setting link_validate to False"
            )

        # HTTP 상태 코드가 200이 아니거나 에러 페이지인 경우 모든 검증을 False로 설정
        if sub_category_node.link_status != 200 or is_error_page:
            # 모든 검증을 False로 설정
            sub_category_node.navigation_visible_validate = False
            sub_category_node.navigation_visible_validate_desc = "not exist"
            sub_category_node.headline_validate = False
            sub_category_node.headline_validate_desc = "not exist"
            sub_category_node.result_validate = False
            sub_category_node.result_validate_desc = "not exist"
            sub_category_node.purchase_validate = False
            sub_category_node.purchase_validate_desc = "not exist"
            sub_category_node.sort_validate = False
            sub_category_node.sort_validate_desc = "not exist"
            sub_category_node.nv17_validate = False
            sub_category_node.nv17_validate_desc = "not exist"

            log.info(
                f"All validations set to False for {subtab['name']} due to HTTP error or error page"
            )
            return sub_category_node

        # # 네비게이션 가시성 검증 로직 (별도 TC)
        # if sub_category_node.link_status == 200 and not is_error_page:
        #     if sub_category_node.is_special:
        #         log.info(f"Special subtab detected - skipping detailed processing: {subtab['name']}")
        #         return sub_category_node
        #     else:
        #         # nv19 (main navigation) visible 확인 (nv20은 없을 수도 있음)
        #         if nv19_visible:
        #             sub_category_node.navigation_visible_validate = True
        #         else:
        #             # nv19 (main navigation)이 존재하지 않거나 보이지 않는 경우
        #             if not nv19_element:
        #                 # 요소 자체가 존재하지 않는 경우
        #                 sub_category_node.navigation_visible_validate_desc = "not exist"
        #             else:
        #                 # 요소는 존재하지만 보이지 않는 경우
        #                 sub_category_node.navigation_visible_validate_desc = (
        #                     "not visible"
        #                 )
        # else:
        #     # 링크 상태가 200이 아니거나 에러 페이지인 경우
        #     sub_category_node.navigation_visible_validate_desc = "not exist"
            
        # # 페이지 로딩이 성공한 경우 nv20 (sub navigation) 유형에 따른 처리
        # # nv19 (main navigation)와 nv20 (sub navigation)이 visible하지 않아도 다른 검증들은 그대로 진행
        if sub_category_node.link_status == 200:
        #     # 특수 nv20 (sub navigation)이 아닌 경우에만 정상적인 페이지 처리 진행
        #     if not sub_category_node.is_special:
        #         # 현재 열려있는 탭이면 스크롤 스킵
        #         if is_new_tab:
        #             from utility.aem import scroll_for_lazyload

        #             log.info("Scrolling subtab page to trigger lazy-loaded content")
        #             await scroll_for_lazyload(page)
        #             log.info("Subtab page scroll completed")

                # nv17-breadcrumb 검증
                nv17_result = await validate_nv17_breadcrumb_absence(page)
                sub_category_node.nv17_validate = nv17_result["validate"]
                if not nv17_result["validate"]:
                    sub_category_node.nv17_validate_desc = nv17_result["description"]
                    log.info(
                        f"nv17-breadcrumb validation for {subtab['name']}: {sub_category_node.nv17_validate_desc}"
                    )
                else:
                    log.info(f"nv17-breadcrumb validation for {subtab['name']}: PASSED")

        #         # BreadCrumb 추출
        #         breadcrumb = await extract_breadcrumb(page)
        #         sub_category_node.breadcrumb = breadcrumb

        #         # FAQ 추출
        #         faq = await extract_faq(page)
        #         sub_category_node.faq = faq.to_dict() if faq else None

        #         # Disclaimer 추출
        #         disclaimer = await extract_disclaimer(page)
        #         sub_category_node.disclaimer = (
        #             disclaimer.to_dict() if disclaimer else None
        #         )

        #         # 헤드라인 추출 및 검증
        #         dom_exists, is_visible, headline = await _validate_headline(page)
        #         sub_category_node.headline = headline
                
        #         if dom_exists and is_visible:
        #             # 헤드라인이 DOM에 존재하고 visible함
        #             sub_category_node.headline_validate = True
        #             sub_category_node.headline_validate_desc = ""
        #             log.info(f"Headline validation passed for {subtab['name']}: '{headline}'")
        #         elif not dom_exists:
        #             # 헤드라인이 DOM에 존재하지 않음
        #             sub_category_node.headline_validate = False
        #             sub_category_node.headline_validate_desc = "Headline does not exist"
        #             log.warning(f"Headline validation failed for {subtab['name']}: {sub_category_node.headline_validate_desc}")
        #         else:
        #             # 헤드라인이 DOM에는 존재하나 visible하지 않음
        #             sub_category_node.headline_validate = False
        #             sub_category_node.headline_validate_desc = "Headline is not visible"
        #             log.warning(f"Headline validation failed for {subtab['name']}: {sub_category_node.headline_validate_desc}")
                
        #         # 결과 수 추출 및 검증
        #         displayed_result_count, actual_card_count, result_desc, has_no_result = (
        #             await extract_result_count(page)
        #         )
        #         sub_category_node.result_count = displayed_result_count

        #         # result_desc가 있으면 에러가 발생한 경우
        #         if result_desc:
        #             sub_category_node.result_validate_desc = result_desc
        #             log.warning(
        #                 f"Result count validation failed for {subtab['name']}: {sub_category_node.result_validate_desc}"
        #             )
        #         elif has_no_result:
        #             # no-result 요소가 있는 경우 0이 정상
        #             sub_category_node.result_validate = True
        #             sub_category_node.result_validate_desc = "No results element found - 0 is expected"
        #             log.info(
        #                 f"Result count validation for {subtab['name']}: No results element found, validation passed"
        #             )
        #         elif displayed_result_count == 0:
        #             # 결과 수 요소가 보이지 않는 경우 검증 실패
        #             sub_category_node.result_validate_desc = "Result count not visible"
        #             log.warning(
        #                 f"Result count validation failed for {subtab['name']}: {sub_category_node.result_validate_desc}"
        #             )
        #         else:
        #             sub_category_node.result_validate = (
        #                 actual_card_count <= displayed_result_count
        #             )
        #             if not sub_category_node.result_validate:
        #                 sub_category_node.result_validate_desc = f"displayed={displayed_result_count}, actual={actual_card_count}"
        #         log.info(
        #             f"Result count validation: displayed={displayed_result_count}, actual={actual_card_count} -> {sub_category_node.result_validate}"
        #         )

        #         products = await extract_product(page)
        #         sub_category_node.children = products
        #         log.info(
        #             f"Extracted {len(products)} detailed products from subtab: {subtab['name']}"
        #         )

        #         # 구매 가능성 검증 (요구사항 3: 위에서부터 4개 제품 검증)
        #         if products:
        #             # 상위 4개 제품만 검증 (필터가 아닌 경우)
        #             products_to_validate = products[:4]
        #             purchase_result = await validate_purchase_capability(
        #                 products_to_validate, page
        #             )
        #             sub_category_node.purchase_validate = purchase_result["validate"]
        #             sub_category_node.purchase_validate_info = purchase_result[
        #                 "details"
        #             ]
        #             if not purchase_result["validate"]:
        #                 # 실패 시 description을 desc로 설정
        #                 sub_category_node.purchase_validate_desc = purchase_result[
        #                     "description"
        #                 ]
        #                 log.info(
        #                     f"Purchase validation for {subtab['name']}: {sub_category_node.purchase_validate_desc}"
        #                 )
        #             else:
        #                 log.info(f"Purchase validation for {subtab['name']}: PASSED")
        #         else:
        #             sub_category_node.purchase_validate_desc = (
        #                 "No products found for purchase validation"
        #             )
        #             sub_category_node.purchase_validate_info = {
        #                 "total_checked": 0,
        #                 "purchasable_count": 0,
        #             }

        #         # 정렬 기능 검증
        #         sort_result = await validate_sort(page)
        #         sub_category_node.sort_validate = sort_result["validate"]
        #         sub_category_node.sort_validate_info = sort_result["details"]
        #         if not sort_result["validate"]:
        #             sub_category_node.sort_validate_desc = sort_result["description"]
        #             log.info(
        #                 f"Sort validation for {subtab['name']}: {sub_category_node.sort_validate_desc}"
        #             )
        #         else:
        #             log.info(f"Sort validation for {subtab['name']}: PASSED")

        #         # 필터 구조 추출 (요구사항 5: 필터 테스트 대상인 경우에만)
        #         if is_filter_testable:
        #             log.info(f"Extracting filter structure for {subtab['name']}")
        #             filter_structure = await extract_filter_structure(page)
        #             sub_category_node.filter_info = filter_structure
        #             log.info(
        #                 f"Filter structure extracted for {subtab['name']}: {len(filter_structure.get('random_combination_filters', []))} random combination filters, {len(filter_structure.get('individual_test_filters', []))} individual test filters"
        #             )
        #         else:
        #             sub_category_node.filter_info = {}

        #         # 페이지 처리 완료 후 라이브 URL로 이동하여 데이터 추출
        #         live_page = None
        #         should_close_live_page = False

        #         try:
        #             # 라이브 URL로 변환
        #             from pf_modules.live_validation import convert_to_live_url

        #             live_url = convert_to_live_url(subtab["url"])
        #             log.info(f"Converting to live URL: {subtab['url']} -> {live_url}")

        #             # 라이브 URL 유효성 검사
        #             if not live_url or live_url.strip() == "":
        #                 log.warning(
        #                     f"Live URL is empty for {subtab['name']}, skipping live page processing"
        #                 )
        #                 # 빈 URL인 경우 라이브 데이터를 빈 값으로 설정
        #                 sub_category_node.live_breadcrumb = []
        #                 sub_category_node.live_faq = None
        #                 sub_category_node.live_disclaimer = None
        #                 return sub_category_node

        #             # 라이브 URL 형식 검사
        #             if not live_url.startswith("http"):
        #                 log.warning(
        #                     f"Invalid live URL format for {subtab['name']}: {live_url}, skipping live page processing"
        #                 )
        #                 # 잘못된 URL 형식인 경우 라이브 데이터를 빈 값으로 설정
        #                 sub_category_node.live_breadcrumb = []
        #                 sub_category_node.live_faq = None
        #                 sub_category_node.live_disclaimer = None
        #                 return sub_category_node

        #             # 라이브 URL로 이동 (탭 처리 방식만 다름)
        #             if is_new_tab:
        #                 # 현재 탭에서 라이브 URL로 이동
        #                 log.info(f"Navigating current tab to live URL: {live_url}")
        #                 live_response = await page.goto(live_url, timeout=0)
        #                 live_page = page
        #             else:
        #                 # 새 탭을 열어 라이브 URL로 이동
        #                 log.info(f"Opening new tab for live URL: {live_url}")
        #                 live_page = await page.context.new_page()
        #                 live_response = await live_page.goto(live_url, timeout=0)
        #                 should_close_live_page = True

        #             # DOM 구조 로딩 완료 대기
        #             await live_page.wait_for_load_state("domcontentloaded", timeout=0)

        #             # 라이브 페이지에서 스크롤하여 lazy loading 트리거
        #             from utility.aem import scroll_for_lazyload

        #             await scroll_for_lazyload(live_page)

        #             log.info("Live page loaded and scrolled successfully")

        #             # 라이브 데이터 추출
        #             log.info(f"Extracting live data for: {subtab['name']}")

        #             # 라이브 BreadCrumb 추출
        #             live_breadcrumb = await extract_breadcrumb(live_page)
        #             sub_category_node.live_breadcrumb = live_breadcrumb

        #             # 라이브 FAQ 추출
        #             live_faq = await extract_faq(live_page)
        #             sub_category_node.live_faq = (
        #                 live_faq.to_dict() if live_faq else None
        #             )

        #             # 라이브 Disclaimer 추출
        #             live_disclaimer = await extract_disclaimer(live_page)
        #             sub_category_node.live_disclaimer = (
        #                 live_disclaimer.to_dict() if live_disclaimer else None
        #             )

        #             log.info(
        #                 f"Live data extracted for {subtab['name']}: breadcrumb={len(live_breadcrumb)}, faq={'yes' if live_faq else 'no'}, disclaimer={'yes' if live_disclaimer else 'no'}"
        #             )

        #         except Exception as live_e:
        #             log.error(
        #                 f"Error processing live page for {subtab['name']}: {live_e}"
        #             )
        #             # 라이브 데이터 추출 실패 시 빈 값으로 설정
        #             sub_category_node.live_breadcrumb = []
        #             sub_category_node.live_faq = None
        #             sub_category_node.live_disclaimer = None
        #         finally:
        #             # 라이브 탭 정리
        #             if should_close_live_page and live_page:
        #                 try:
        #                     await live_page.close()
        #                     log.info(f"Closed live page tab for: {subtab['name']}")
        #                 except Exception as close_e:
        #                     log.warning(
        #                         f"Error closing live page tab for {subtab['name']}: {close_e}"
        #                     )
        # else:
        #     log.warning(
        #         f"Failed to load subtab page: {subtab['name']}, skipping product extraction"
        #     )

        return sub_category_node

    except Exception as e:
        log.error(f"Error processing subtab {subtab['name']}: {e}")
        # 에러 발생 시에도 노드는 생성하되 에러 정보 기록
        error_node = create_navigation_node(subtab["name"], subtab["url"])
        error_node.link_status = -1
        error_node.link_validate_desc = f"Error: {str(e)}"
        error_node.children = []
        return error_node
    finally:
        # 새 탭인 경우 탭 정리
        if is_new_tab:
            try:
                await page.close()
                log.info(f"Closed subtab page: {subtab['name']}")
            except Exception as e:
                log.warning(f"Error closing subtab page {subtab['name']}: {e}")


########################################################################################
# 메인 실행 함수
########################################################################################
async def extract_main_category(page: Page) -> List[MainCategoryNode]:
    """
    현재 페이지에서 모든 nv19 (main navigation) 정보를 추출하여 MainCategoryNode 리스트로 반환합니다.
    현재 활성화된 메인탭부터 시작하여 모든 메인탭을 순차적으로 처리합니다.

    동작 방식:
    - 현재 활성화된 메인탭의 인덱스 확인
    - 모든 메인탭 정보 추출 및 MainCategoryNode 리스트 생성
    - 현재 활성화된 메인탭부터 시작하여 순차적으로 처리

    파라미터:
        page (Page): Playwright Page 객체

    반환값:
        List[MainCategoryNode]: nv19 (main navigation) 노드 리스트
    """
    try:
        log.info("Extracting all main tab information")
        
        main_category_nodes = []

        # nv19-pd-category-main 클래스 내의 모든 nv19 (main navigation) 아이템 추출
        main_tab_items = await page.query_selector_all(
            ".nv19-pd-category-main .nv19-pd-category-main__item"
        )

        if not main_tab_items:
            log.warning("No main tab items found")
            return []

        log.info(f"Found {len(main_tab_items)} main tab items")

        # 모든 탭의 기본 정보 수집 및 MainCategoryNode 생성
        for i, item in enumerate(main_tab_items):
            try:
                # 탭의 기본 정보 추출
                inner_element = await item.query_selector(
                    ".nv19-pd-category-main__item-inner"
                )
                if not inner_element:
                    continue

                # 이름 추출
                name_element = await item.query_selector(
                    ".nv19-pd-category-main__name .nv19-pd-category-main__maxchar--pc-only"
                )
                name = ""
                if name_element:
                    name = await name_element.inner_text()

                # URL 추출 및 처리
                href = await inner_element.get_attribute("href")
                if href:
                    # href가 존재하는 경우 도메인 추가
                    if not href.startswith("http"):
                        from urllib.parse import urljoin

                        url = urljoin(page.url, href)
                        log.debug(
                            f"Main tab {name}: converted relative URL to absolute: {href} -> {url}"
                        )
                    else:
                        url = href
                        log.debug(f"Main tab {name}: using absolute URL: {url}")
                else:
                    # href가 없는 경우 (현재 활성화된 탭) 현재 페이지 URL 사용
                    url = page.url
                    log.debug(
                        f"Main tab {name}: no href found, using current page URL: {url}"
                    )

                # MainCategoryNode 생성
                main_category_node = MainCategoryNode(name=name.strip(), url=url)

                main_category_nodes.append(main_category_node)
                log.info(f"Added main category node: {name.strip()}")

            except Exception as e:
                log.error(f"Error processing main tab item {i}: {e}")
                continue

        log.info(
            f"Successfully extracted {len(main_category_nodes)} main category nodes"
        )
        return main_category_nodes

    except Exception as e:
        log.error(f"Error extracting main category information: {e}")
        return []


async def extract_pf_structure(
    page: Page, main_category_node: MainCategoryNode, browser=None, wds_page=None
) -> MainCategoryNode:
    """
    PF 페이지의 구조를 추출합니다.

    동작 방식:
    - nv20 (sub navigation) 링크 및 이름 추출
    - 현재 탭과 다른 nv20들을 병렬 처리
    - 각 nv20에 대해 검증 수행 (링크, 네비게이션, 헤드라인, 결과 수 등)
    - 필터 검증 (현재 탭에서만)
    - 라이브 비교 검증 (테스트 vs 라이브)

    파라미터:
        page (Page): Playwright Page 객체
        main_category_node (MainCategoryNode): nv19 (main navigation) 노드

    반환값:
        MainCategoryNode: nv20 (sub navigation)들이 추가된 nv19 (main navigation) 노드
    """
    log.info(f"Starting PF structure extraction for {main_category_node.url}")

    try:
        # 1. 현재 페이지의 nv19 정보 추출
        log.info(f"Main tab name: {main_category_node.name}")
        url = main_category_node.url
        log.info(f"Using main category URL: {url}")

        # 2. nv20 링크 및 이름 추출 (href가 있는 다른 nv20들만)
        log.info("Extracting subtab links and names")
        current_tab_name, other_subtabs = await _extract_subtab_info(page, url)

        # nv20 (sub navigation)이 없는 경우 처리
        if other_subtabs is None:
            other_subtabs = []
            log.info("Single page detected. No other subtabs found.")
        else:
            log.info(f"Found {len(other_subtabs)} other subtabs")

        # 현재 탭 이름이 없으면 nv19 이름으로 대체
        if not current_tab_name:
            current_tab_name = main_category_node.name
            log.info(
                f"No current tab name found, using main tab name: {current_tab_name}"
            )

        # 3. 현재 탭 nv20 생성 (href가 없는 tab__item-title에서 이름 추출)
        # 현재 페이지 URL을 사용하되, 빈 문자열인 경우 현재 페이지 URL 사용
        current_subtab_url = url if url and url.strip() else page.url

        # URL 유효성 검사
        if not current_subtab_url or not current_subtab_url.startswith("http"):
            log.error(f"Invalid current subtab URL: {current_subtab_url}")
            current_subtab_url = page.url
            log.info(f"Using page URL as fallback: {current_subtab_url}")

        current_subtab = {
            "name": current_tab_name,
            "url": current_subtab_url,
            "is_special": False,
        }

        log.info(f"Current subtab URL: {current_subtab_url}")

        # nv20 (sub navigation)이 보이지 않는 경우 현재 탭의 link_validate를 실패 처리
        if other_subtabs == "no_visible_tabs":
            current_subtab["no_visible_tabs"] = True

        # 4. 병렬 처리 작업에 포함
        tasks = []

        # 현재 탭 처리 작업 추가
        log.info(f"Adding current tab task: {current_subtab['name']}")
        current_task = _process_subtab(
            page,
            current_subtab,
            main_category_node,
            is_new_tab=False,
            browser=browser,
            wds_page=wds_page,
        )
        tasks.append(current_task)

        # 다른 nv20들을 새 탭에서 병렬 처리
        if other_subtabs:
            for subtab in other_subtabs:
                log.info(f"Adding new tab task: {subtab['name']}")
                # 현재 페이지의 context를 사용하여 새 탭 생성
                new_page = await page.context.new_page()
                task = _process_subtab(
                    new_page,
                    subtab,
                    main_category_node,
                    is_new_tab=True,
                    browser=browser,
                    wds_page=wds_page,
                )
                tasks.append(task)
        else:
            log.info("No other subtabs to process - single page structure")

        # 5. 모든 작업을 병렬로 실행
        log.info(f"Starting parallel processing of {len(tasks)} subtabs")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 6. 결과 처리
        shop_result = []
        for result in results:
            if isinstance(result, SubCategoryNode):
                shop_result.append(result)
            elif isinstance(result, Exception):
                log.error(f"Task failed with unhandled exception: {result}")
                # _process_subtab에서 이미 에러 노드를 반환하므로 여기서는 로그만
            else:
                log.warning(f"Unexpected result type: {type(result)}")

        # 6. 필터 검증 수행 (현재 탭에서만) - 정상 노드만 대상
        # 에러가 있는 노드는 검증 함수 내에서 제외됨
        log.info("Starting filter validation for current tab...")
        await validate_filter(shop_result, page)

        # 7. 라이브 비교 검증 수행 (테스트 vs 라이브) - 정상 노드만 대상
        # 에러가 있는 노드는 검증 함수 내에서 제외됨
        log.info("Starting live comparison validation (test vs live)...")
        await validate_live_comparison(shop_result)

        # 8. MainCategoryNode에 서브 노드들 추가
        main_category_node.children = shop_result

        log.info(
            f"PF structure extraction completed. Generated MainCategoryNode with {len(shop_result)} subcategory nodes"
        )
        return main_category_node

    except Exception as e:
        log.error(f"Error during PF structure extraction: {e}")
        # 에러 발생 시에도 MainCategoryNode에 빈 children 설정
        main_category_node.children = []
        return main_category_node


########################################################################################
# 출력 및 저장
########################################################################################
def print_product_list(main_category_node: MainCategoryNode) -> None:
    """
    nv19 (main navigation) 노드를 logger로 예쁘게 출력합니다.
    """
    log.info(f"[SUMMARY] Main Category: {main_category_node.name}")
    log.info(
        f"[SUMMARY] Total subcategories: {len(main_category_node.children) if main_category_node.children else 0}"
    )
    main_category_node.print_tree(indent=0)


def save_product_list(
    main_category_nodes: List[MainCategoryNode],
    url: str,
    site_code: str,
    output_dir: str = "crawlstore",
) -> str:
    """
    MainCategoryNode 리스트를 JSON 파일로 저장합니다.

    동작 방식:
        - output_dir 폴더가 없으면 생성
        - 파일명: {site_code}_pf_{날짜}_{도메인}.json (url 기반)
        - JSON 최상위에 추출 시각, URL, site_code, tree 리스트 포함
        - 저장 경로/파일명 logger로 출력

    파라미터:
        main_category_nodes (List[MainCategoryNode]): 저장할 nv19 (main navigation) 노드 리스트
        url (str): 추출 대상 URL
        site_code (str): 사이트 코드
        output_dir (str): 저장 폴더명(기본값: crawlstore)
    반환값:
        str: 저장된 파일 경로
    예외:
        - 파일 저장 실패 시 logger로 에러 기록
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    now = datetime.now().strftime("%y%m%d-%H%M%S")
    url_wo_protocol = re.sub(r"^https?://", "", url)
    safe_url = (
        url_wo_protocol.replace("/", "_")
        .replace("?", "_")
        .replace("&", "_")
        .replace(":", "_")
    )
    filename = f"{site_code}_pf_{now}_{safe_url}.json"
    filepath = os.path.join(output_dir, filename)

    # MainCategoryNode 리스트의 to_dict() 메서드를 사용하여 딕셔너리 리스트로 변환
    main_categories_data = [
        main_category_node.to_dict() for main_category_node in main_category_nodes
    ]

    json_obj = {
        "extracted_at": now,
        "extracted_url": url,
        "site_code": site_code,
        "tree": main_categories_data,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(json_obj, f, ensure_ascii=False, indent=2)
    log.info(f"Product list saved to: {filepath}")
    return filepath
