"""
shop.py - SHOP 메뉴 구조 추출 및 계층 트리 변환 모듈

이 모듈은 웹사이트의 SHOP 메뉴 구조를 분석하여 계층적 트리로 추출하고,
링크 유효성 검사 및 JSON 저장 기능을 제공합니다.

주요 기능:
- SHOP 메뉴의 L0/L1/Featured 계층 구조 추출
- BeautifulSoup 기반 HTML 파싱 및 메뉴 정보 수집
- 메뉴명/URL 정제 및 표준화
- 트리 구조(ShopMenuNode)로 변환 및 계층적 출력
- 링크 유효성 검사(Playwright 활용)
- 결과를 JSON 파일로 저장
- 상세한 예외 처리 및 로깅 지원
"""

from playwright.async_api import Page
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime
import re
import asyncio
from urllib.parse import urlparse
from typing import List, Dict, Any, Optional, Tuple
from utility.utils import standardize_url, refine_url
from utility.orangelogger import log

class ShopMenuNode:
    """
    SHOP 메뉴 트리의 한 노드를 표현하는 클래스입니다.

    이 클래스는 메뉴명, URL, 타입, 정제 정보, 검증 상태, 하위 메뉴 리스트, 메타정보 등
    SHOP 메뉴의 계층적 구조와 링크 상태를 관리하는 데 사용됩니다.

    속성:
        node_type (str): 메뉴 타입("L0", "L1", "Featured" 등)
        children (list[ShopMenuNode]): 하위 메뉴 리스트
        name (str): 메뉴명
        url (str): 메뉴 URL
        name_verify (bool): 메뉴명 검증 여부
        url_verify (bool): 링크 검증 여부
        link_status (int): 링크 응답 HTTP status
        link_validate (bool): 링크 정상 여부
        link_validate_desc (str): 링크 체크 결과 설명
        desc (str): 메뉴 설명
        meta (dict): button 요소에서 추출한 모든 메타정보
    """
    def __init__(self, node_type: str = "L0", name: str = "", url: str = "", desc: str = "", meta: Optional[Dict[str, Any]] = None):
        """
        ShopMenuNode 인스턴스를 초기화합니다.

        파라미터:
            node_type (str): 메뉴 타입
            name (str): 메뉴명
            url (str): 메뉴 URL
            desc (str): 메뉴 설명
            meta (dict): button 요소에서 추출한 메타정보(딕셔너리)
        반환값:
            없음
        """
        self.node_type = node_type
        self.children: List["ShopMenuNode"] = []
        self.name = name
        self.url = url
        self.name_verify: bool = False
        self.url_verify: bool = False
        self.link_status: int = -1
        self.link_validate: bool = False
        self.link_validate_desc: str = ""
        self.desc = desc
        self.meta: Dict[str, Any] = meta if meta is not None else {}

    def add_child(self, child: "ShopMenuNode") -> None:
        """
        하위 메뉴 노드를 현재 노드의 children 리스트에 추가합니다.

        파라미터:
            child (ShopMenuNode): 추가할 하위 노드
        반환값:
            없음
        """
        self.children.append(child)

    def print_tree(self, indent: int = 0) -> None:
        """
        트리 구조를 보기 좋게 logger로 출력합니다.
        각 노드의 주요 필드를 계층적으로 출력합니다.

        파라미터:
            indent (int): 들여쓰기 레벨
        반환값:
            없음
        """
        prefix = "    " * indent
        log.info(f"{prefix}[{self.node_type}] {self.name} ({self.url if self.url else 'No link'}) "
                    f"[name_verify: {self.name_verify}] [url_verify: {self.url_verify}] [link_status: {self.link_status}] "
                    f"[link_validate: {self.link_validate}] [link_validate_desc: {self.link_validate_desc}]")
        for child in self.children:
            child.print_tree(indent + 1)

    def to_dict(self) -> dict:
        """
        트리 구조를 dict(재귀)로 변환합니다.
        meta 필드도 포함합니다.
        """
        return {
            "node_type": self.node_type,
            "name": self.name,
            "url": self.url,
            "name_verify": self.name_verify,
            "url_verify": self.url_verify,
            "link_status": self.link_status,
            "link_validate": self.link_validate,
            "link_validate_desc": self.link_validate_desc,
            "desc": self.desc,
            "meta": self.meta,
            "children": [child.to_dict() for child in self.children]
        }

def print_shop_tree(shop_roots: list[ShopMenuNode]) -> None:
    """
    SHOP 트리 구조를 logger로 출력합니다.
    각 L0 메뉴별로 트리 구조를 출력하며, 하위 메뉴는 들여쓰기하여 계층적으로 표시합니다.
    BRIEF: 각 L0별 L1, Product, 링크 노드 개수와 전체 합계(SUMMARY)를 출력합니다.
    """
    log.info("===== SHOP Menu Tree =====")
    l0_count = len(shop_roots)
    total_l1_count = 0
    total_product_count = 0
    total_link_count = 0
    brief_logs = []
    for i, root in enumerate(shop_roots, 1):
        log.info(f"[L0] Tree for menu #{i}:")
        root.print_tree()
        # 각 L0별 L1/Product/링크 개수 카운트
        l1_count = 0
        product_count = 0
        link_count = 0
        def count_l1_product_link(node):
            nonlocal l1_count, product_count, link_count
            for child in node.children:
                if child.node_type == "L1":
                    l1_count += 1
                elif child.node_type == "Product":
                    product_count += 1
                if child.url:
                    link_count += 1
                count_l1_product_link(child)
        if root.url:
            link_count += 1
        count_l1_product_link(root)
        total_l1_count += l1_count
        total_product_count += product_count
        total_link_count += link_count
        brief_logs.append(f"[BRIEF] L0 '{root.name}': L1 nodes: {l1_count}, Product nodes: {product_count}, Nodes with link: {link_count}")
    # 모든 L0별 BRIEF 로그를 한꺼번에 출력
    for log_entry in brief_logs:
        log.info(log_entry)
    log.info(f"[SUMMARY] L0 nodes: {l0_count}, L1 nodes: {total_l1_count}, Product nodes: {total_product_count}, Nodes with link: {total_link_count}")

def save_shop_tree_to_json(shop_roots: List[ShopMenuNode], url: str, site_code: str, output_dir: str = "crawlstore") -> str:
    """
    SHOP 트리 구조를 JSON 파일로 저장합니다.
    - output_dir 폴더가 없으면 생성
    - 파일명: sitecode_shop_yymmdd-hhmmss_url.json (url은 안전하게 가공)
    - 파일 최상위에 추출 시간, URL, siteCode 정보를 문자열 필드로 포함
    - 각 노드의 필드 순서는 name_verify, url_verify, link_status, link_validate, link_validate_desc로 맞춤

    파라미터:
        shop_roots (list[ShopMenuNode]): ShopMenuNode 리스트(트리 루트)
        url (str): 추출 대상 URL
        site_code (str): 사이트 코드
        output_dir (str): 저장 폴더명(기본값: crawlstore)
    반환값:
        str: 저장된 파일 경로
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    now = datetime.now().strftime("%y%m%d-%H%M%S")
    url_wo_protocol = re.sub(r'^https?://', '', url)
    safe_url = url_wo_protocol.replace('/', '_').replace('?', '_').replace('&', '_').replace(':', '_')
    filename = f"{site_code}_shop_{now}_{safe_url}.json"
    filepath = os.path.join(output_dir, filename)
    tree_data = [root.to_dict() for root in shop_roots]
    json_obj = {
        "extracted_at": now,
        "extracted_url": url,
        "site_code": site_code,
        "tree": tree_data
    }
    json_body = json.dumps(json_obj, ensure_ascii=False, indent=2)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json_body)
    log.info(f"SHOP menu tree saved to: {filepath}")
    return filepath

async def extract_shop_structure(page: Page) -> List[ShopMenuNode]:
    """
    웹페이지의 SHOP(Global Navigation Bar) 구조를 트리 형태로 추출합니다.

    새로운 구조:
    - 메인메뉴: div.tab.pd22-shop-product-category__primary-tab > ul > li > button
      - 메뉴명: button의 텍스트
      - meta: button의 모든 속성(key-value)
      - url: 메인메뉴는 빈 문자열로 설정
    - 서브메뉴: id가 메인메뉴의 aria-controls 값과 일치하는 div > div.tab > ul > li > button
      - 메뉴명: button의 텍스트
      - meta: button의 모든 속성(key-value)
      - url: button의 data-view-all-url (없으면 빈 문자열)
    - 서브메뉴 없는 메인메뉴도 children 빈 리스트로 처리

    파라미터:
        page (Page): Playwright Page 객체
    반환값:
        List[ShopMenuNode]: SHOP 트리의 루트 노드 리스트
    """
    log.debug("Starting new SHOP structure extraction (button/meta version)")
    shop_roots: List[ShopMenuNode] = []

    html_content = await page.content()
    soup = BeautifulSoup(html_content, 'html.parser')

    parsed = urlparse(page.url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"

    main_menu_ul = soup.select_one("div.tab.pd22-shop-product-category__primary-tab > ul")
    if not main_menu_ul:
        log.warning("Main menu ul not found")
        return []
    main_menu_buttons = main_menu_ul.select("li > button")
    log.info(f"Found {len(main_menu_buttons)} main menu buttons")

    def attrs_to_str_dict(attrs: dict) -> dict:
        return {k: v for k, v in dict(attrs).items()}

    for main_btn in main_menu_buttons:
        name = main_btn.get_text(strip=True)
        if not name:
            log.info("[extract] Skipping main menu node with empty name.")
            continue
        meta = attrs_to_str_dict(main_btn.attrs)
        url = ""
        aria_controls = main_btn.get("aria-controls", "")
        l0_node = ShopMenuNode(node_type="L0", name=name, url=url, meta=meta)

        submenu_ul = None
        if aria_controls:
            submenu_div = soup.select_one(f"div#{aria_controls} > div.tab > ul")
            if submenu_div:
                submenu_ul = submenu_div
        if submenu_ul:
            submenu_buttons = submenu_ul.select("li > button")
            log.info(f"Found {len(submenu_buttons)} sub menu buttons for main '{name}'")
            for sub_btn in submenu_buttons:
                sub_name = sub_btn.get_text(strip=True)
                if not sub_name:
                    log.info(f"[extract] Skipping sub menu node with empty name under main '{name}'.")
                    continue
                sub_meta = attrs_to_str_dict(sub_btn.attrs)
                sub_url = sub_btn.get("data-view-all-url", "")
                sub_url = refine_url(sub_url, base_domain) if sub_url else ""
                sub_node = ShopMenuNode(node_type="L1", name=sub_name, url=sub_url, meta=sub_meta)
                l0_node.add_child(sub_node)
        shop_roots.append(l0_node)
    log.info(f"Extracted {len(shop_roots)} L0 menus (new button/meta version)")
    return shop_roots

async def check_link_validity(nodes: list[ShopMenuNode], page: Page) -> None:
    """
    메뉴 노드의 링크가 실제로 작동하는지 확인합니다.

    동작 방식:
    1. 링크 확인
       - 메뉴 노드에 URL이 있는지 확인합니다.
       - URL이 없는 경우 "No URL" 상태로 표시합니다.
       - L0/L1 노드의 경우 URL이 없어도 특별 처리합니다.

    2. 페이지 이동
       - URL이 있는 경우 새 탭에서 해당 페이지로 이동을 시도합니다.
       - 페이지 이동 후 body 요소가 로드될 때까지 최대 20초 대기합니다.
       - 최대 5번까지 재시도합니다.

    3. 상태 확인
       - 페이지 이동이 성공한 경우:
         * HTTP 상태 코드를 확인합니다 (200이면 성공).
         * 리다이렉트가 발생한 경우 최종 URL을 기록합니다.
       - 페이지 이동이 실패한 경우:
         * HTTP 상태 코드를 확인하여 "404 Not Found" 등의 상태를 표시합니다.
         * 네트워크 오류 등의 경우 "No response" 상태로 표시합니다.

    4. 결과 저장
       - 확인 결과를 메뉴 노드의 상태(link_status)와 설명(link_validate_desc)에 저장합니다.
       - 진행 상황, 재시도 횟수, 원본 이름/URL, 상태를 한 줄로 요약하여 로그로 출력합니다.

    특징:
    - 여러 개의 워커를 사용하여 동시에 여러 링크를 검사합니다.
    - 각 링크는 새 탭에서 열고 검사 후 즉시 닫습니다.
    - 메모리 사용을 최소화하고 인터럽트에도 자연스럽게 종료됩니다.

    파라미터:
        nodes (list[ShopMenuNode]): 검사할 메뉴 노드들의 리스트
        page (Page): Playwright Page 객체 (웹 페이지를 조작하는 도구)
    """
    max_concurrent = int(os.getenv("LINKVALIDATE_COUNT", 2))
    context = page.context

    def flatten_with_link(node: ShopMenuNode) -> list[ShopMenuNode]:
        result = []
        if node.url or node.node_type in ("L0", "L1"):  # L0/L1도 url 없어도 검사
            result.append(node)
        for child in node.children:
            result.extend(flatten_with_link(child))
        return result

    all_nodes = []
    for root in nodes:
        all_nodes.extend(flatten_with_link(root))

    # 검사할 노드 개수를 최대 50개로 제한
    # all_nodes = all_nodes[:20]

    total = len(all_nodes)
    queue: asyncio.Queue[tuple[ShopMenuNode, int, int]] = asyncio.Queue()
    for idx, node in enumerate(all_nodes, 1):
        await queue.put((node, idx, total))

    async def validate_node(node: ShopMenuNode, idx: int, total: int, max_retries: int = 5):
        """
        링크 유효성 검사 - 진행률, 재시도, 원본 name/url, 상태를 한 줄로 요약 로그로 출력
        """
        status_code = -1
        node.link_validate = False
        node.link_status = -1
        node.link_validate_desc = ""
        name = node.name
        url = node.url
        # --- L0/L1 노드의 url 없는 경우 특수 처리 ---
        if node.node_type == "L0" and not url:
            node.link_validate = True
            node.link_status = -1
            node.link_validate_desc = "L0 has no link by design"
            log.info(f"[{idx}/{total}][SKIP] L0 node with no url: name='{name}' desc='L0 has no link'")
            return
        if node.node_type == "L1" and not url:
            node.link_validate = False
            node.link_status = -1
            node.link_validate_desc = "Has no link"
            log.info(f"[{idx}/{total}][SKIP] L1 node with no url: name='{name}' desc='Has no link'")
            return
        if not url:
            log.info(f"[{idx}/{total}][1/1][SKIP] name='{name}' url='{url}' status=-1 desc=Empty url")
            node.link_validate_desc = f"[Status:-1] Empty url"
            return
        retries = 0
        # base_url 추출 (page.url에서 도메인 기준)
        base_url = None
        try:
            base_url = f"{urlparse(page.url).scheme}://{urlparse(page.url).netloc}"
        except Exception:
            base_url = ""
        while retries < max_retries:
            new_page = None
            try:
                # --- 새 탭(페이지) 생성 및 링크 접근 시도 ---
                #   - 각 링크마다 Playwright context에서 새로운 페이지를 생성
                #   - url을 refine_url로 도메인 보정 후 이동
                new_page = await context.new_page()
                refined = refine_url(url, base_url)
                response = await new_page.goto(refined, timeout=20000)
                await new_page.wait_for_selector("body", timeout=20000)
                # --- 응답 객체가 존재하는 경우 상태코드 및 최종 URL 확인 ---
                if response:
                    status_code = response.status
                    node.link_status = status_code
                    if status_code == 200:
                        # 최종적으로 도달한 URL을 표준화하여 리다이렉트 여부 확인
                        if standardize_url(refined) != standardize_url(response.url):
                            node.link_validate_desc = f"Redirected to {response.url}"
                        else:
                            node.link_validate_desc = ""
                        node.link_validate = True
                        log.info(f"[{idx}/{total}][{retries+1}/{max_retries}][SUCCESS] status={status_code} desc={node.link_validate_desc} ['{name}' '{url}']")
                    else:
                        node.link_validate_desc = f"HTTP {status_code}"
                        log.info(f"[{idx}/{total}][{retries+1}/{max_retries}][FAIL] status={status_code} desc={node.link_validate_desc} ['{name}' '{url}']")
                    await new_page.close()
                    return
                else:
                    # --- 응답 객체가 없는 경우(네트워크 오류 등) ---
                    node.link_validate_desc = "No response"
                    log.info(f"[{idx}/{total}][{retries+1}/{max_retries}][FAIL] status=-1 desc=No response ['{name}' '{url}']")
                    await new_page.close()
            except Exception as e:
                # --- 예외 발생 시(타임아웃, 네트워크 오류 등) ---
                node.link_validate_desc = f"Exception: {e}"
                log.info(f"[{idx}/{total}][{retries+1}/{max_retries}][EXCEPTION] status=-1 desc=Exception: {e} ['{name}' '{url}']")
                if new_page:
                    try:
                        await new_page.close()
                    except Exception:
                        pass
            retries += 1
        node.link_status = status_code

    async def worker(worker_id: int):
        while True:
            try:
                node, idx, total = await queue.get()
            except asyncio.CancelledError:
                break
            try:
                await validate_node(node, idx, total)
            finally:
                queue.task_done()

    workers = [asyncio.create_task(worker(i+1)) for i in range(max_concurrent)]

    try:
        await queue.join()  # 모든 작업이 끝날 때까지 대기
    except KeyboardInterrupt:
        log.warning("KeyboardInterrupt detected, stopping worker tasks.")
    finally:
        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True) 

async def navigate_shop_structure(page: Page) -> list[ShopMenuNode]:
    """
    실제 클릭 동작을 통해 SHOP 메뉴 구조를 트리 형태로 추출합니다.

    동작 방식:
    1. 메인 메뉴(L0) 추출
       - 페이지에서 메인 메뉴 버튼들을 찾습니다.
         * 웹 페이지에서 'div.tab.pd22-shop-product-category__primary-tab > ul > li > button'라는 위치에 있는 버튼들을 찾습니다.
         * 이는 마치 "메인 메뉴가 있는 탭 영역 > 메뉴 목록 > 각 메뉴 항목 > 버튼"을 찾는 것과 같습니다.
       - 각 메인 메뉴 버튼을 순서대로 클릭합니다.
       - 클릭 후 1초 대기하여 메뉴가 완전히 로드되도록 합니다.

    2. 서브 메뉴(L1) 추출
       - 메인 메뉴 클릭 후 서브 메뉴 패널을 찾습니다.
         * 'div.pd22-shop-product-category__primary-panel--active ul'이라는 위치에서 서브 메뉴 패널을 찾습니다.
         * 이는 "현재 활성화된 메뉴 패널 > 서브 메뉴 목록"을 찾는 것과 같습니다.
       - 서브 메뉴 패널에서 모든 서브 메뉴 버튼을 찾아 순서대로 클릭합니다.
       - 각 서브 메뉴 클릭 후 2초 대기하여 상품 목록이 로드되도록 합니다.

    3. 상품(Product) 추출
       - 서브 메뉴 클릭 후 해당 메뉴의 상품 목록을 찾습니다.
         * 'div#{aria_controls} .swiper-wrapper'라는 위치에서 상품 목록을 찾습니다.
         * 이는 "현재 선택된 메뉴의 상품 영역 > 상품 목록"을 찾는 것과 같습니다.
       - 각 상품의 이름과 링크를 추출합니다.

    4. 특수 케이스 처리
       - 상품 목록이 없는 경우:
         * 'div#{aria_controls} .pd22-shop-product-category__no-results-text'라는 위치에서 "상품이 없습니다" 등의 메시지를 찾습니다.
         * 이는 "현재 선택된 메뉴의 상품 영역 > 상품 없음 메시지"를 찾는 것과 같습니다.
         * 이 메시지를 해당 서브 메뉴의 설명(desc)으로 저장합니다.
       - 상품도 없고 설명도 없는 경우:
         * "Scenario Error"를 설명으로 저장합니다.

    메뉴 구조:
    - L0 (메인 메뉴): 최상위 메뉴 (예: TV, 냉장고, 세탁기 등)
    - L1 (서브 메뉴): 메인 메뉴의 하위 메뉴 (예: TV > QLED, Neo QLED 등)
    - Product: 서브 메뉴의 하위 상품 (예: QLED > QN90C 등)

    파라미터:
        page (Page): Playwright Page 객체 (웹 페이지를 조작하는 도구)
    반환값:
        list[ShopMenuNode]: SHOP 트리의 루트 노드 리스트 (L0 메뉴들의 목록)
    """
    log.debug("Starting SHOP structure navigation (click version)")
    shop_roots: list[ShopMenuNode] = []

    from urllib.parse import urlparse
    parsed = urlparse(page.url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"

    def attrs_to_bs4_style(attrs: dict) -> dict:
        result = {}
        for k, v in attrs.items():
            if k == "class":
                result[k] = v.split() if v else []
            elif v == "":
                result[k] = None
            else:
                result[k] = v
        return result

    main_menu_buttons = await page.query_selector_all("div.tab.pd22-shop-product-category__primary-tab > ul > li > button")
    log.info(f"Found {len(main_menu_buttons)} main menu buttons (for navigation)")

    for idx, main_btn in enumerate(main_menu_buttons, 1):
        main_btn_text = await main_btn.inner_text()
        if not main_btn_text.strip():
            log.info(f"[navigate] Skipping main menu node with empty name (index {idx}).")
            continue
        main_btn_attrs_raw = await page.evaluate(
            '(el) => { let d = {}; for (let a of el.attributes) d[a.name] = a.value; return d; }', main_btn
        )
        main_btn_attrs = attrs_to_bs4_style(main_btn_attrs_raw)
        l0_node = ShopMenuNode(node_type="L0", name=main_btn_text.strip(), url="", meta=main_btn_attrs)
        log.info(f"[MainMenu {idx}] Clicking main menu: '{main_btn_text.strip()}'")
        await main_btn.click()
        await asyncio.sleep(1)

        sub_panel = await page.query_selector("div.pd22-shop-product-category__primary-panel--active ul")
        if sub_panel:
            sub_buttons = await sub_panel.query_selector_all("li > button")
            log.info(f"[MainMenu {idx}] Found {len(sub_buttons)} sub menu buttons (for navigation)")
            for sub_idx, sub_btn in enumerate(sub_buttons, 1):
                sub_btn_text = await sub_btn.inner_text()
                if not sub_btn_text.strip():
                    log.info(f"[navigate] Skipping sub menu node with empty name (main {idx}, sub {sub_idx}).")
                    continue
                sub_btn_attrs_raw = await page.evaluate(
                    '(el) => { let d = {}; for (let a of el.attributes) d[a.name] = a.value; return d; }', sub_btn
                )
                sub_btn_attrs = attrs_to_bs4_style(sub_btn_attrs_raw)
                sub_url = sub_btn_attrs.get("data-view-all-url", "")
                sub_url = refine_url(sub_url, base_domain) if sub_url else ""
                sub_node = ShopMenuNode(node_type="L1", name=sub_btn_text.strip(), url=sub_url, meta=sub_btn_attrs)
                log.info(f"[MainMenu {idx}][SubMenu {sub_idx}] Clicking sub menu: '{sub_btn_text.strip()}'")
                await sub_btn.click()
                await asyncio.sleep(2)

                # --- Product(3단계) 항목 추출 ---
                aria_controls = sub_btn_attrs.get("aria-controls", "")
                if aria_controls:
                    # 해당 id의 div에서 .swiper-wrapper > div 항목 추출
                    product_panel = await page.query_selector(f"div#{aria_controls} .swiper-wrapper")
                    has_products = False
                    if product_panel:
                        product_divs = await product_panel.query_selector_all(":scope > div")
                        log.info(f"[MainMenu {idx}][SubMenu {sub_idx}] Found {len(product_divs)} product items.")
                        for prod_idx, prod_div in enumerate(product_divs, 1):
                            # 각 product div에서 .pd22-shop-product-category__name a 추출
                            prod_a = await prod_div.query_selector(".pd22-shop-product-category__name a")
                            if prod_a:
                                prod_name = (await prod_a.inner_text()).strip()
                                if not prod_name:
                                    log.info(f"[navigate] Skipping product node with empty name (main {idx}, sub {sub_idx}, prod {prod_idx}).")
                                    continue
                                prod_url = await prod_a.get_attribute("href")
                                prod_attrs_raw = await page.evaluate(
                                    '(el) => { let d = {}; for (let a of el.attributes) d[a.name] = a.value; return d; }', prod_a
                                )
                                prod_attrs = attrs_to_bs4_style(prod_attrs_raw)
                                prod_url = refine_url(prod_url, base_domain) if prod_url else ""
                                prod_node = ShopMenuNode(node_type="Product", name=prod_name, url=prod_url, meta=prod_attrs)
                                sub_node.add_child(prod_node)
                                has_products = True

                    # product_panel이 없거나 하위 요소가 없는 경우 desc 설정
                    if not product_panel or not has_products:
                        try:
                            swiper_wrapper = await page.query_selector(f"div#{aria_controls} .pd22-shop-product-category__no-results-text")
                            if swiper_wrapper:
                                wrapper_text = (await swiper_wrapper.inner_text()).strip()
                                if wrapper_text:
                                    sub_node.desc = wrapper_text
                                    log.info(f"[MainMenu {idx}][SubMenu {sub_idx}] Set description from swiper-wrapper text: {wrapper_text[:50]}...")
                        except Exception as e:
                            log.warning(f"[MainMenu {idx}][SubMenu {sub_idx}] Failed to get swiper-wrapper text: {e}")

                # sub_node 유효성 검사
                if not sub_node.children:
                    if not sub_node.desc or not sub_node.desc.strip():
                        sub_node.desc = "Scenario Error"
                        log.warning(f"[MainMenu {idx}][SubMenu {sub_idx}] No children and no valid description, marked as Scenario Error")
                l0_node.add_child(sub_node)
        else:
            log.info(f"[MainMenu {idx}] No sub menu panel found (may be leaf menu)")
        shop_roots.append(l0_node)
    log.info(f"Extracted {len(shop_roots)} L0 menus (navigation/click version)")
    return shop_roots 