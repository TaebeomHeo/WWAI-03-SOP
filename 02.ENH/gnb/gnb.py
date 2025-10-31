"""
gnb.py - GNB(Global Navigation Bar) 구조 추출 및 계층 트리 변환 모듈

이 모듈은 웹사이트의 GNB(Global Navigation Bar) 구조를 분석하여 계층적 트리로 추출하고,
링크 유효성 검사 및 JSON 저장 기능을 제공합니다.

주요 기능:
- GNB 메뉴의 L0/L1/Featured 계층 구조 추출
- BeautifulSoup 기반 HTML 파싱 및 메뉴 정보 수집
- 메뉴명/URL 정제 및 표준화
- 트리 구조(GNBMenuNode)로 변환 및 계층적 출력
- 링크 유효성 검사(Playwright 활용)
- 결과를 JSON 파일로 저장
- 상세한 예외 처리 및 로깅 지원
"""

from playwright.async_api import Page
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime
import re
import asyncio
from urllib.parse import urlparse
from utility.utils import standardize_url, refine_url
from utility.orangelogger import log

class GnbMenuNode:
    """
    GNB(Global Navigation Bar) 메뉴 트리의 한 노드를 표현하는 클래스입니다.

    이 클래스는 메뉴명, URL, 타입, 정제 정보, 검증 상태, 하위 메뉴 리스트 등
    GNB 메뉴의 계층적 구조와 링크 상태를 관리하는 데 사용됩니다.

    속성:
        node_type (str): 메뉴 타입("L0", "L1", "Featured" 등)
        children (list[GnbMenuNode]): 하위 메뉴 리스트

        name (str): 메뉴명
        url (str): 메뉴 URL

        name_verify (bool): 메뉴명 검증 여부
        url_verify (bool): 링크 검증 여부

        link_status (int): 링크 응답 HTTP status
        link_validate (bool): 링크 정상 여부
        link_validate_desc (str): 링크 체크 결과 설명
    """
    def __init__(self, node_type: str = "L0", name: str = "", url: str = ""):
        """
        GnbMenuNode 인스턴스를 초기화합니다.

        파라미터:
            node_type (str): 메뉴 타입
            name (str): 메뉴명
            url (str): 메뉴 URL
        반환값:
            없음
        """
        self.node_type = node_type
        self.children: List["GnbMenuNode"] = []
        self.name = name
        self.url = url
        self.name_verify: bool = False
        self.url_verify: bool = False
        self.link_status: int = -1
        self.link_validate: bool = False
        self.link_validate_desc: str = ""

    def add_child(self, child: "GnbMenuNode") -> None:
        """
        하위 메뉴 노드를 현재 노드의 children 리스트에 추가합니다.

        파라미터:
            child (GnbMenuNode): 추가할 하위 노드
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
        필드 순서는 name_verify, url_verify, link_status, link_validate, link_validate_desc로 맞춥니다.

        반환값:
            dict: 노드의 정보를 담은 딕셔너리
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
            "children": [child.to_dict() for child in self.children]
        }

def print_gnb_tree(gnb_roots: List[GnbMenuNode]) -> None:
    """
    GNB 트리 구조를 logger로 출력합니다.
    각 L0 메뉴별로 트리 구조를 출력하며, 하위 메뉴는 들여쓰기하여 계층적으로 표시합니다.

    파라미터:
        gnb_roots (list[GnbMenuNode]): 트리 루트 노드 리스트
    반환값:
        없음
    """
    log.info("===== GNB Menu Tree =====")
    l0_count = len(gnb_roots)
    total_l1_count = 0
    total_featured_count = 0
    link_count = 0
    brief_logs = []
    for i, root in enumerate(gnb_roots, 1):
        log.info(f"[L0] Tree for menu #{i}:")
        root.print_tree()
        # 각 L0별 L1/Featured 개수 카운트
        l1_count = 0
        featured_count = 0
        def count_l1_featured(node):
            nonlocal l1_count, featured_count
            for child in node.children:
                if child.node_type == "L1":
                    l1_count += 1
                elif child.node_type == "Featured":
                    featured_count += 1
                count_l1_featured(child)
        count_l1_featured(root)
        # 링크 개수 카운트(루트 포함, url이 존재하는 노드)
        def count_links(node):
            cnt = 1 if node.url else 0
            for child in node.children:
                cnt += count_links(child)
            return cnt
        l0_link_count = count_links(root)
        link_count += l0_link_count
        total_l1_count += l1_count
        total_featured_count += featured_count
        brief_logs.append(f"[BRIEF] L0 '{root.name}': L1 nodes: {l1_count}, Featured nodes: {featured_count}, Nodes with link: {l0_link_count}")
    # 모든 L0별 BRIEF 로그를 한꺼번에 출력
    for log_entry in brief_logs:
        log.info(log_entry)
    log.info(f"[SUMMARY] L0 nodes: {l0_count}, L1 nodes: {total_l1_count}, Featured nodes: {total_featured_count}, Nodes with link: {link_count}")

def save_gnb_tree_to_json(gnb_roots: List[GnbMenuNode], url: str, output_dir: str = "crawlstore") -> str:
    """
    GNB 트리 구조를 JSON 파일로 저장합니다.
    - result 폴더가 없으면 생성
    - 파일명: yymmdd-hhmmss_url.json (url은 안전하게 가공)
    - 파일 최상위에 추출 시간, URL 정보를 문자열 필드로 포함
    - 각 노드의 필드 순서는 name_verify, url_verify, link_status, link_validate, link_validate_desc로 맞춤

    파라미터:
        gnb_roots (list[GnbMenuNode]): GnbMenuNode 리스트(트리 루트)
        url (str): 추출 대상 URL
        output_dir (str): 저장 폴더명(기본값: result)
    반환값:
        str: 저장된 파일 경로
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    now = datetime.now().strftime("%y%m%d-%H%M%S")
    url_wo_protocol = re.sub(r'^https?://', '', url)
    safe_url = url_wo_protocol.replace('/', '_').replace('?', '_').replace('&', '_').replace(':', '_')
    filename = f"{now}_{safe_url}.json"
    filepath = os.path.join(output_dir, filename)
    tree_data = [root.to_dict() for root in gnb_roots]
    json_obj = {
        "extracted_at": now,
        "extracted_url": url,
        "tree": tree_data
    }
    json_body = json.dumps(json_obj, ensure_ascii=False, indent=2)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json_body)
    log.info(f"GNB menu tree saved to: {filepath}")
    return filepath

async def extract_gnb_structure(page: Page) -> List[GnbMenuNode]:
    """
    웹페이지의 GNB(Global Navigation Bar) 전체 구조를 트리 형태로 추출합니다.

    동작 방식:
    - Playwright Page 객체에서 HTML 전체 소스를 가져와 BeautifulSoup으로 파싱합니다.
    - GNB 최상위 메뉴 컨테이너(.nv00-gnb-v4__l0-menu-list--left)를 탐색하여 L0(최상위) 메뉴 항목을 모두 추출합니다.
      * 각 L0 메뉴는 .nv00-gnb-v4__l0-menu 요소로 구분됩니다.
      * 메뉴명/URL 추출 우선순위: a(.nv00-gnb-v4__l0-menu-link) > span(.nv00-gnb-v4__l0-menu-text) > button(.nv00-gnb-v4__l0-menu-btn)
    - 각 L0 메뉴별로 하위 L1(서브 메뉴)와 Featured 메뉴를 추출합니다.
      * L1: .nv00-gnb-v4__l1-menu-list > .nv00-gnb-v4__l1-menu-link
      * Featured: .nv00-gnb-v4__l1-featured-list > .nv00-gnb-v4__l1-featured-link
    - 각 메뉴 항목의 이름, URL, 계층 구조를 GnbMenuNode 트리로 구성합니다.
    - 메뉴명/URL이 비어 있거나, 메뉴 구조가 비정상인 경우 경고 로그를 남깁니다.
    - 추출된 전체 트리의 루트(L0) 노드 리스트를 반환합니다.

    파라미터:
        page (Page): Playwright Page 객체 (웹 페이지를 조작하는 도구)

    반환값:
        list[GnbMenuNode]: GNB 트리의 루트 노드 리스트 (L0 메뉴들의 목록)

    예외 처리:
    - GNB 컨테이너, 메뉴 항목 등이 없을 경우 경고 로그를 남기고, 빈 리스트 또는 부분 결과를 반환합니다.
    - 메뉴명/URL이 비어 있거나, 구조가 예상과 다를 경우에도 경고 로그를 남깁니다.

    사용 예시:
        gnb_roots = await extract_gnb_structure(page)
        # gnb_roots는 GnbMenuNode 트리의 루트(L0) 노드 리스트

    메뉴 구조:
    - L0 (최상위 메뉴): 예) TV, 냉장고, 세탁기 등
    - L1 (서브 메뉴): L0의 하위 메뉴 (예: TV > QLED, Neo QLED 등)
    - Featured: L1과 별도로 강조되는 메뉴 (예: TV > 추천상품 등)
    """
    log.debug("Starting GNB structure extraction (tree version)")
    gnb_roots: list[GnbMenuNode] = []

    # 1. HTML 전체 소스코드를 가져와 BeautifulSoup으로 파싱합니다.
    html_content = await page.content()
    log.debug("Retrieved page HTML content")
    soup = BeautifulSoup(html_content, 'html.parser')
    log.debug("Parsing HTML with BeautifulSoup")

    # 2. GNB 최상위 메뉴 컨테이너(div.nv00-gnb-v4__l0-menu-list--left)를 탐색합니다.
    #    - .nv00-gnb-v4__l0-menu-list.nv00-gnb-v4__l0-menu-list--left 클래스를 가진 div가 GNB 최상위 메뉴 컨테이너입니다.
    l0_menu_list = soup.select_one(".nv00-gnb-v4__l0-menu-list.nv00-gnb-v4__l0-menu-list--left")

    # 3. L0 메뉴 항목(.nv00-gnb-v4__l0-menu)을 모두 추출합니다.
    #    - 각 .nv00-gnb-v4__l0-menu 요소가 하나의 L0 메뉴를 의미합니다.
    if not l0_menu_list:
        log.warning("Left menu list (.nv00-gnb-v4__l0-menu-list--left) not found")
        l0_menu_items = []
    else:
        l0_menu_items = l0_menu_list.select(".nv00-gnb-v4__l0-menu")
        log.info(f"Found {len(l0_menu_items)} L0 menu items")

    # 4. 각 L0 메뉴 항목별로 트리 구조를 생성합니다.
    for l0_idx, l0_item in enumerate(l0_menu_items, 1):
        log.debug(f"Processing L0 menu item #{l0_idx}")
        # --- L0 메뉴명/URL 추출 우선순위 ---
        # 1순위: <a class="nv00-gnb-v4__l0-menu-link">의 직접 텍스트(하위 태그 제외)
        # 2순위: <a class="nv00-gnb-v4__l0-menu-link"> 내부 <span class="nv00-gnb-v4__l0-menu-text">의 직접 텍스트(하위 태그 제외)
        # 3순위: <button class="nv00-gnb-v4__l0-menu-btn">의 직접 텍스트(하위 태그 제외)
        # 모두 없으면 빈 문자열 처리
        l0_link = l0_item.select_one(".nv00-gnb-v4__l0-menu-link")
        l0_btn = l0_item.select_one(".nv00-gnb-v4__l0-menu-btn")
        l0_text = ""
        l0_url = ""
        if l0_link:
            # a 태그에서 직접 텍스트 추출 (하위 태그 제외)
            l0_text = l0_link.find(text=True, recursive=False)
            if l0_text:
                l0_text = l0_text.strip()
            # a 내부 .nv00-gnb-v4__l0-menu-text에서 직접 텍스트 추출 (하위 태그 제외)
            if not l0_text:
                l0_text_span = l0_link.select_one(".nv00-gnb-v4__l0-menu-text")
                if l0_text_span:
                    l0_text = l0_text_span.find(text=True, recursive=False)
                    if l0_text:
                        l0_text = l0_text.strip()
            l0_url = l0_link.get("href", "")
            if not l0_text:
                log.warning(f"L0 menu #{l0_idx} has empty text in .nv00-gnb-v4__l0-menu-link and .nv00-gnb-v4__l0-menu-text")
            if not l0_url:
                log.warning(f"L0 menu '{l0_text}' has empty URL")
        elif l0_btn:
            # 버튼(.nv00-gnb-v4__l0-menu-btn)에서 직접 텍스트 추출 (하위 태그 제외)
            l0_text = l0_btn.find(text=True, recursive=False)
            if l0_text:
                l0_text = l0_text.strip()
            if not l0_text:
                log.warning(f"L0 menu button has empty text")
            l0_url = ""
        else:
            # 모든 경우에 해당하지 않으면 빈 문자열 처리
            log.error(f"L0 menu has no link or button element")
        # --- L0 노드 생성 및 트리에 추가 ---
        l0_node = GnbMenuNode(node_type="L0", name=l0_text, url=l0_url)

        # --- L1/Featured 메뉴 추출 ---
        #   - L1: .nv00-gnb-v4__l1-menu-list > .nv00-gnb-v4__l1-menu-link
        #   - Featured: .nv00-gnb-v4__l1-featured-list > .nv00-gnb-v4__l1-featured-link
        l1_container = l0_item.select_one(".nv00-gnb-v4__l1-menu-container")
        if l1_container:
            # L1 메뉴 추출 (여러 .nv00-gnb-v4__l1-menu-list 모두 순회)
            l1_menu_lists = l1_container.select(".nv00-gnb-v4__l1-menu-list")
            for l1_menu_list in l1_menu_lists:
                l1_links = l1_menu_list.select(".nv00-gnb-v4__l1-menu-link")
                log.info(f"Found {len(l1_links)} L1 submenu items for '{l0_text}'")
                for l1_idx, l1_link in enumerate(l1_links, 1):
                    # L1 메뉴명 추출: .nv00-gnb-v4__l1-menu-text 클래스가 키워드 역할
                    l1_text = ""
                    l1_text_element = l1_link.select_one(".nv00-gnb-v4__l1-menu-text")
                    if l1_text_element:
                        l1_text = l1_text_element.get_text(strip=True)
                    if not l1_text:
                        log.warning(f"L1 menu #{l1_idx} under '{l0_text}' has empty text")
                    # L1 노드 생성 및 L0에 추가
                    l1_node = GnbMenuNode(node_type="L1", name=l1_text, url=l1_link.get("href", ""))
                    l0_node.add_child(l1_node)
            # Featured 메뉴 추출
            featured_list = l1_container.select_one(".nv00-gnb-v4__l1-featured-list")
            if featured_list:
                featured_links = featured_list.select(".nv00-gnb-v4__l1-featured-link")
                log.info(f"Found {len(featured_links)} featured items for '{l0_text}'")
                for ft_idx, feature_link in enumerate(featured_links, 1):
                    # Featured 메뉴명 추출: .nv00-gnb-v4__l1-featured-text 클래스가 키워드 역할
                    feature_text = ""
                    feature_text_element = feature_link.select_one(".nv00-gnb-v4__l1-featured-text")
                    if feature_text_element:
                        feature_text = feature_text_element.get_text(strip=True)
                    if not feature_text:
                        log.warning(f"Featured item #{ft_idx} under '{l0_text}' has empty text")
                    # Featured 노드 생성 및 L0에 추가
                    ft_node = GnbMenuNode(node_type="Featured", name=feature_text, url=feature_link.get("href", ""))
                    l0_node.add_child(ft_node)
        # 완성된 L0 노드를 트리 루트에 추가
        gnb_roots.append(l0_node)
    log.info(f"Extracted {len(gnb_roots)} L0 menus (tree version)")
    return gnb_roots

async def check_link_validity(nodes: List[GnbMenuNode], page: Page) -> None:
    """
    트리 전체에서 링크가 존재하는 노드만 추출하여, 각 링크의 유효성을 비동기적으로 검사합니다.

    동작 방식:
    - 트리 구조의 모든 노드 중 url이 존재하는 노드만 flatten하여 검사 대상으로 만듭니다.
      * flatten_with_link() 재귀 함수를 통해 트리 전체를 순회하며 url이 있는 노드만 리스트로 만듭니다.
    - 검사 대상 노드를 큐에 넣고, 환경변수 LINKVALIDATE_COUNT(기본 2)만큼 워커가 병렬로 처리합니다.
      * 각 워커는 큐에서 노드를 하나씩 꺼내 validate_node()를 호출하여 링크 유효성 검사를 수행합니다.
      * 각 링크는 Playwright context에서 새 탭(context.new_page)으로 열고, 검사 후 즉시 닫습니다.
    - 링크 유효성 검사는 최대 5회까지 재시도하며, 성공/실패/예외/네트워크 오류 등 모든 상황을 상세 로그로 남깁니다.
      * HTTP 200 응답이면 정상(OK), 리다이렉트 발생 시 최종 URL을 desc에 기록합니다.
      * 응답이 없거나 예외 발생 시, 원인 메시지를 desc에 저장합니다.
    - 각 노드의 진행률, 재시도 횟수, 원본 name/url, 상태를 한 줄 요약 로그로 출력합니다.
    - KeyboardInterrupt(인터럽트) 발생 시, 모든 워커를 안전하게 종료합니다.

    파라미터:
        nodes (list[GnbMenuNode]): 검사할 메뉴 트리의 루트 노드 리스트
        page (Page): Playwright Page 객체 (브라우저 컨텍스트)

    반환값:
        없음

    예외 처리:
    - 네트워크 오류, 타임아웃, 잘못된 URL 등 모든 예외 상황을 포착하여 각 노드의 desc에 원인 메시지를 기록합니다.
    - KeyboardInterrupt 발생 시, 모든 워커를 안전하게 종료합니다.

    사용 예시:
        await check_link_validity(gnb_tree_roots, page)
        # 각 노드의 link_validate, link_status, link_validate_desc 필드에 검사 결과가 저장됨

    메뉴 구조:
    - L0/L1 등 계층 구조의 모든 노드 중 url이 있는 노드만 flatten하여 검사
    - 각 노드는 검사 결과에 따라 link_validate(성공/실패), link_status(HTTP 코드), link_validate_desc(상세 메시지)가 갱신됨
    """
    max_concurrent = int(os.getenv("LINKVALIDATE_COUNT", 2))
    context = page.context

    def flatten_with_link(node: GnbMenuNode) -> list[GnbMenuNode]:
        result = []
        if node.url:
            result.append(node)
        for child in node.children:
            result.extend(flatten_with_link(child))
        return result

    all_nodes = []
    for root in nodes:
        all_nodes.extend(flatten_with_link(root))

    total = len(all_nodes)
    queue: asyncio.Queue[tuple[GnbMenuNode, int, int]] = asyncio.Queue()
    for idx, node in enumerate(all_nodes, 1):
        await queue.put((node, idx, total))

    async def validate_node(node: GnbMenuNode, idx: int, total: int, max_retries: int = 5):
        """
        링크 유효성 검사 - 진행률, 재시도, 원본 name/url, 상태를 한 줄로 요약 로그로 출력
        """
        status_code = -1
        node.link_validate = False
        node.link_status = -1
        node.link_validate_desc = ""
        name = node.name
        url = node.url
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