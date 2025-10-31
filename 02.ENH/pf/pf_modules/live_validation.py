"""
live_validation.py - 라이브 페이지와 비교하는 검증 모듈

PF(Product Finder) 시스템에서 테스트 환경과 라이브 환경 간의
콘텐츠 일관성을 검증하는 핵심 모듈입니다.

주요 검증 대상:
- BreadCrumb 네비게이션 경로 검증
- FAQ 섹션의 DOM 구조 및 콘텐츠 검증
- Disclaimer 섹션의 DOM 구조 및 콘텐츠 검증
- 테스트 URL을 라이브 URL로 자동 변환

핵심 기능:
- DOM 구조 기반 정밀 검증: HTML 태그, 속성, 텍스트를 재귀적으로 비교
- URL 도메인 변환: p6-pre-qa3.samsung.com → www.samsung.com
- 일괄 검증 처리: 모든 SubCategoryNode에 대한 통합 검증 수행
- 상세한 차이점 분석: 구조적 불일치 시 구체적인 mismatch 정보 제공
- 특수 nv20 제외 처리: 검증 대상에서 제외되는 특수 케이스 관리

검증 프로세스:
1. 테스트 페이지에서 BreadCrumb, FAQ, Disclaimer 데이터 추출
2. 테스트 URL을 라이브 URL로 변환하여 라이브 페이지 접근
3. 라이브 페이지에서 동일한 데이터 추출
4. DOM 구조를 재귀적으로 비교하여 구조적 동일성 검증
5. 각 노드별 검증 결과를 validate 필드에 저
"""

import asyncio
from typing import List, Optional, Dict, Any
from playwright.async_api import Page
from bs4 import BeautifulSoup
from utility.orangelogger import log


########################################################################################
# 1. URL 변환 함수
########################################################################################
def convert_to_live_url(test_url: str) -> str:
    """
    테스트 URL을 라이브 URL로 변환합니다.

    동작 방식:
    - p6-pre-qa3.samsung.com을 www.samsung.com으로 변경
    - 기타 도메인은 그대로 유지

    파라미터:
        test_url (str): 변환할 테스트 URL

    반환값:
        str: 변환된 라이브 URL
    """
    if "p6-pre-qa3.samsung.com" in test_url:
        return test_url.replace("p6-pre-qa3.samsung.com", "www.samsung.com")
    else:
        return test_url


########################################################################################
# 2. BreadCrumb 관련 함수
########################################################################################
async def extract_breadcrumb(page: Page) -> List[str]:
    """
    현재 페이지에서 BreadCrumb 정보를 추출합니다.

    동작 방식:
    - .breadcrumb__path li .breadcrumb__text-desktop 요소들을 찾아서 텍스트 추출
    - 각 요소의 텍스트를 리스트로 반환
    - 요소가 나타날 때까지 최대 10초 대기

    파라미터:
        page (Page): Playwright Page 객체

    반환값:
        List[str]: BreadCrumb 텍스트 리스트
    """
    try:
        # BreadCrumb 요소가 나타날 때까지 대기 (최대 10초)
        try:
            await page.wait_for_selector(
                ".breadcrumb__path li .breadcrumb__text-desktop",
                timeout=10000,
                state="visible",
            )
            log.info("BreadCrumb elements found and visible")
        except Exception as wait_error:
            log.warning(f"BreadCrumb selector wait timeout: {wait_error}")
            # 타임아웃 발생 시에도 계속 진행하여 현재 DOM 확인

        # BreadCrumb 요소들 찾기
        breadcrumb_elements = await page.query_selector_all(
            ".breadcrumb__path li .breadcrumb__text-desktop"
        )

        breadcrumb_texts = []
        for element in breadcrumb_elements:
            text = await element.text_content()
            if text and text.strip():
                breadcrumb_texts.append(text.strip())

        if breadcrumb_texts:
            log.info(f"Extracted breadcrumb: {breadcrumb_texts}")
        else:
            log.warning("BreadCrumb elements not found or empty")

        return breadcrumb_texts

    except Exception as e:
        log.error(f"Error extracting breadcrumb: {e}")
        return []


def compare_breadcrumbs(
    test_breadcrumb: List[str], live_breadcrumb: List[str]
) -> tuple[bool, str]:
    """
    테스트 페이지와 라이브 페이지의 BreadCrumb을 비교하여 검증합니다.

    반환값:
        tuple[bool, str]: (검증 결과, 설명 메시지)
    """
    try:
        # 빈 리스트 처리 - FAQ/Disclaimer와 동일한 방식
        test_empty = not test_breadcrumb or len(test_breadcrumb) == 0
        live_empty = not live_breadcrumb or len(live_breadcrumb) == 0

        if test_empty and live_empty:
            # 둘 다 없는 경우
            log.info("[compare_breadcrumbs] Both breadcrumbs are empty")
            return True, "BreadCrumb does not exist"
        elif test_empty:
            # 테스트에만 없는 경우
            log.warning("[compare_breadcrumbs] Test breadcrumb is empty")
            return False, "BreadCrumb does not exist in test page"
        elif live_empty:
            # 라이브에만 없는 경우
            log.warning("[compare_breadcrumbs] Live breadcrumb is empty")
            return False, "BreadCrumb does not exist in live page"

        # 길이 비교
        if len(test_breadcrumb) != len(live_breadcrumb):
            log.info(
                f"[compare_breadcrumbs] Length mismatch - Test: {len(test_breadcrumb)}, Live: {len(live_breadcrumb)}"
            )
            return (
                False,
                f"Breadcrumb length mismatch: test={len(test_breadcrumb)} vs live={len(live_breadcrumb)}",
            )

        # 정규화 함수
        def normalize_text(text: str) -> str:
            return text.strip().lower()

        # 각 요소를 순서대로 비교
        for i, (test_item, live_item) in enumerate(
            zip(test_breadcrumb, live_breadcrumb)
        ):
            test_normalized = normalize_text(test_item)
            live_normalized = normalize_text(live_item)

            if test_normalized != live_normalized:
                log.info(
                    f"[compare_breadcrumbs] Mismatch at index {i}: Test='{test_item}' vs Live='{live_item}'"
                )
                return (
                    False,
                    f"Breadcrumb item mismatch at index {i}: test='{test_item}' vs live='{live_item}'",
                )

        # 모든 요소가 일치하는 경우
        log.info(f"[compare_breadcrumbs] BreadCrumb validation PASSED")
        return True, ""

    except Exception as e:
        log.error(f"[compare_breadcrumbs] Error during breadcrumb validation: {e}")
        return False, f"Error during breadcrumb validation: {str(e)}"


########################################################################################
# 3. DOM 구조 클래스
########################################################################################
class DOMNode:
    """
    FAQ와 Disclaimer의 DOM 구조를 저장하는 공통 클래스입니다.

    주요 필드:
        tag_name (str): HTML 태그명
        attributes (Dict[str, str]): HTML 속성들
        text (str): 요소의 텍스트 내용
        children (List[DOMNode]): 자식 요소들
    """

    def __init__(
        self,
        tag_name: str = "",
        attributes: Dict[str, str] = None,
        text: str = "",
        children: List["DOMNode"] = None,
    ):
        """
        DOMNode 객체를 초기화합니다.

        파라미터:
            tag_name (str): HTML 태그명
            attributes (Dict[str, str]): HTML 속성들
            text (str): 요소의 텍스트 내용
            children (List[DOMNode]): 자식 요소들
        """
        self.tag_name = tag_name
        self.attributes = attributes or {}
        self.text = text
        self.children = children or []

    def to_dict(self) -> Dict[str, Any]:
        """
        DOMNode 객체를 딕셔너리로 변환합니다.

        반환값:
            Dict[str, Any]: 변환된 딕셔너리
        """
        return {
            "tag_name": self.tag_name,
            "attributes": self.attributes,
            "text": self.text,
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DOMNode":
        """
        딕셔너리에서 DOMNode 객체를 생성합니다.

        파라미터:
            data (Dict[str, Any]): 변환할 딕셔너리

        반환값:
            DOMNode: 생성된 DOMNode 객체
        """
        if not data:
            return cls()

        children = []
        if "children" in data and data["children"]:
            children = [cls.from_dict(child_data) for child_data in data["children"]]

        return cls(
            tag_name=data.get("tag_name", ""),
            attributes=data.get("attributes", {}),
            text=data.get("text", ""),
            children=children,
        )

    def __eq__(self, other) -> bool:
        """
        두 DOMNode 객체의 구조적 동일성을 비교합니다.

        동작 방식:
        - 태그명, 속성, 텍스트, 자식 요소들을 재귀적으로 비교
        - 모든 요소가 일치해야 True 반환

        파라미터:
            other: 비교할 다른 DOMNode 객체

        반환값:
            bool: 구조적으로 동일하면 True, 아니면 False
        """
        if not isinstance(other, DOMNode):
            return False

        # 태그명 비교
        if self.tag_name != other.tag_name:
            return False

        # 속성 비교
        if self.attributes != other.attributes:
            return False

        # 텍스트 비교
        if self.text != other.text:
            return False

        # 자식 요소 개수 비교
        if len(self.children) != len(other.children):
            return False

        # 자식 요소들 재귀적 비교
        for self_child, other_child in zip(self.children, other.children):
            if self_child != other_child:
                return False

        return True

    def __repr__(self) -> str:
        """
        DOMNode 객체의 문자열 표현을 반환합니다.

        반환값:
            str: DOMNode의 문자열 표현
        """
        return f"DOMNode(tag='{self.tag_name}', text='{self.text[:50]}...', children={len(self.children)})"


########################################################################################
# 4. DOM 공통 함수들
########################################################################################
def _extract_dom_from_element(element) -> DOMNode:
    """
    HTML 요소를 DOMNode로 변환합니다.

    동작 방식:
    - 요소의 태그명, 속성, 텍스트, 자식 요소들을 재귀적으로 추출
    - BeautifulSoup 요소를 DOMNode 객체로 변환

    파라미터:
        element: BeautifulSoup 요소 객체

    반환값:
        DOMNode: 변환된 DOM 노드
    """
    if not element:
        return DOMNode()

    # 태그명 추출
    tag_name = element.name if hasattr(element, "name") else ""

    # 속성 추출
    attributes = {}
    if hasattr(element, "attrs"):
        for key, value in element.attrs.items():
            if isinstance(value, list):
                attributes[key] = " ".join(value)
            else:
                attributes[key] = str(value)

    # 텍스트 추출 (직접 자식 텍스트만)
    text = ""
    if element.string:
        text = element.string.strip()

    # 자식 요소들 추출
    children = []
    for child in element.children:
        if hasattr(child, "name") and child.name:  # 태그 요소만
            child_dom = _extract_dom_from_element(child)
            if child_dom.tag_name:  # 유효한 DOM 노드만 추가
                children.append(child_dom)

    return DOMNode(
        tag_name=tag_name, attributes=attributes, text=text, children=children
    )


def _get_dom_mismatch_details(
    test_node: DOMNode, live_node: DOMNode, node_type: str
) -> str:
    """
    DOM 노드 간의 차이점을 분석하여 상세한 설명을 제공합니다.

    동작 방식:
    - 태그명, 속성, 텍스트, 자식 요소의 차이점을 재귀적으로 분석
    - 구체적인 mismatch 정보를 문자열로 반환

    파라미터:
        test_node (DOMNode): 테스트 페이지 DOM 노드
        live_node (DOMNode): 라이브 페이지 DOM 노드
        node_type (str): 노드 타입 ("FAQ" 또는 "Disclaimer")

    반환값:
        str: 차이점에 대한 상세 설명
    """
    try:
        if not test_node or not live_node:
            return f"{node_type} node is empty"

        # 태그명 차이
        if test_node.tag_name != live_node.tag_name:
            return f"{node_type} tag name mismatch: test='{test_node.tag_name}' vs live='{live_node.tag_name}'"

        # 속성 차이 - 실제로 다른 부분만 표시
        if test_node.attributes != live_node.attributes:
            test_attrs = test_node.attributes or {}
            live_attrs = live_node.attributes or {}

            # test에만 있는 속성들
            test_only = {
                k: v
                for k, v in test_attrs.items()
                if k not in live_attrs or live_attrs[k] != v
            }
            # live에만 있는 속성들
            live_only = {
                k: v
                for k, v in live_attrs.items()
                if k not in test_attrs or test_attrs[k] != v
            }

            # 실제로 다른 속성들만 표시
            different_attrs = {}
            for k in set(test_attrs.keys()) | set(live_attrs.keys()):
                if test_attrs.get(k) != live_attrs.get(k):
                    different_attrs[k] = {
                        "test": test_attrs.get(k),
                        "live": live_attrs.get(k),
                    }

            if different_attrs:
                test_diff = {k: v["test"] for k, v in different_attrs.items()}
                live_diff = {k: v["live"] for k, v in different_attrs.items()}
                return f"{node_type} attributes mismatch: test: {test_diff} | live: {live_diff}"
            else:
                return f"{node_type} attributes mismatch: test={test_attrs} vs live={live_attrs}"

        # 텍스트 차이 - 실제로 다른 부분만 표시
        if test_node.text != live_node.text:
            test_text = test_node.text or ""
            live_text = live_node.text or ""
            return f"{node_type} text mismatch: test: '{test_text[:100]}...' | live: '{live_text[:100]}...'"

        # 자식 요소 개수 차이
        if len(test_node.children) != len(live_node.children):
            return f"{node_type} children count mismatch: test: {len(test_node.children)} | live: {len(live_node.children)}"

        # 자식 요소들 재귀적 비교
        for i, (test_child, live_child) in enumerate(
            zip(test_node.children, live_node.children)
        ):
            if test_child != live_child:
                child_mismatch = _get_dom_mismatch_details(
                    test_child, live_child, f"{node_type}[{i}]"
                )
                return f"{node_type} child {i} mismatch: {child_mismatch}"

        return f"{node_type} structures are identical"

    except Exception as e:
        return f"Error analyzing {node_type} mismatch: {str(e)}"


########################################################################################
# 5. FAQ 관련 함수
########################################################################################
async def extract_faq(page: Page) -> DOMNode:
    """
    현재 페이지에서 FAQ 정보를 추출합니다 (DOM 구조 기반).

    동작 방식:
    - .su12-accordion-faqs ul 요소를 찾아서 전체 DOM 구조 추출
    - ul > li > h3(a > div, span(svg, svg)), div 구조를 DOMNode로 저장
    - 질문과 답변을 별도로 수집하지 않고 DOM 구조만 저장
    - 한 페이지에 하나의 FAQ만 존재하므로 단일 DOMNode 반환

    파라미터:
        page (Page): Playwright Page 객체

    반환값:
        DOMNode: FAQ DOM 구조 (없으면 빈 DOMNode)
    """
    try:
        # FAQ ul 요소 찾기
        faq_ul = await page.query_selector(".su12-accordion-faqs")
        if not faq_ul:
            log.info("FAQ ul element not found")
            return DOMNode()

        # HTML 내용을 BeautifulSoup으로 파싱
        html_content = await faq_ul.inner_html()
        soup = BeautifulSoup(html_content, "html.parser")

        # ul 요소를 DOMNode로 변환
        faq_dom = _extract_dom_from_element(soup)

        log.info(
            f"Extracted FAQ DOM structure with {len(faq_dom.children)} li elements"
        )
        return faq_dom

    except Exception as e:
        log.error(f"Error extracting FAQ DOM: {e}")
        return DOMNode()


########################################################################################
# 6. Disclaimer 관련 함수
########################################################################################
async def extract_disclaimer(page: Page) -> DOMNode:
    """
    현재 페이지에서 Disclaimer 정보를 추출합니다 (DOM 구조 기반).

    동작 방식:
    - #disclaimer .text-editor__column.description-text-size--small 요소를 찾아서 전체 DOM 구조 추출
    - 모든 p 태그와 그 자식 요소들을 포함한 완전한 DOM 구조를 DOMNode로 저장
    - 텍스트를 별도로 수집하지 않고 DOM 구조만 저장

    파라미터:
        page (Page): Playwright Page 객체

    반환값:
        DOMNode: Disclaimer DOM 구조
    """
    try:
        disclaimer_element = await page.query_selector(
            "#disclaimer .text-editor__column.description-text-size--small"
        )
        if not disclaimer_element:
            log.info("Disclaimer element not found")
            return DOMNode()

        # HTML 내용을 BeautifulSoup으로 파싱
        html_content = await disclaimer_element.inner_html()
        soup = BeautifulSoup(html_content, "html.parser")

        # disclaimer 요소를 DOMNode로 변환
        disclaimer_dom = _extract_dom_from_element(soup)

        log.info(
            f"Extracted disclaimer DOM structure with {len(disclaimer_dom.children)} child elements"
        )
        return disclaimer_dom

    except Exception as e:
        log.error(f"Error extracting disclaimer DOM: {e}")
        return DOMNode()


########################################################################################
# 7. 검증 함수들
########################################################################################
def _is_empty_dom_node(dom_dict) -> bool:
    """
    DOMNode 딕셔너리가 비어있는지 확인합니다.

    동작 방식:
    - None이거나 빈 딕셔너리이면 True 반환
    - tag_name이 비어있으면 True 반환

    파라미터:
        dom_dict: 확인할 DOMNode 딕셔너리

    반환값:
        bool: 비어있으면 True, 아니면 False
    """
    if not dom_dict:
        return True

    if isinstance(dom_dict, dict):
        tag_name = dom_dict.get("tag_name", "")
        return not tag_name or tag_name == ""

    return False


def compare_dom_nodes(
    test_node: DOMNode, live_node: DOMNode, node_type: str
) -> tuple[bool, str]:
    """
    테스트 페이지와 라이브 페이지의 DOM 구조를 비교하여 검증합니다.

    동작 방식:
    - DOM 구조를 비교하여 구조적 동일성 검증
    - 모든 속성과 텍스트를 재귀적으로 비교
    - DOMNode의 __eq__ 메서드를 사용하여 재귀적 비교
    - mismatch 발생 시 구체적인 차이점을 설명 메시지로 제공

    파라미터:
        test_node (DOMNode): 테스트 페이지 DOM 구조
        live_node (DOMNode): 라이브 페이지 DOM 구조
        node_type (str): 노드 타입 ("FAQ" 또는 "Disclaimer")

    반환값:
        tuple[bool, str]: (검증 결과, 설명 메시지)
    """
    try:
        # 입력값 검증
        if not test_node or not live_node:
            log.warning(f"[compare_dom_nodes] Empty {node_type} provided")
            return False, f"Empty {node_type} provided"

        # DOM 구조 비교
        if test_node != live_node:
            # 구체적인 mismatch 정보 추출
            mismatch_details = _get_dom_mismatch_details(
                test_node, live_node, node_type
            )
            log.info(
                f"[compare_dom_nodes] {node_type} DOM structure mismatch: {mismatch_details}"
            )
            return False, mismatch_details

        # 일치하는 경우
        log.info(f"[compare_dom_nodes] {node_type} DOM validation PASSED")
        return True, ""

    except Exception as e:
        log.error(f"[compare_dom_nodes] Error during {node_type} validation: {e}")
        return False, f"Error during {node_type} validation: {str(e)}"


async def validate_live_comparison(shop_results) -> None:
    """
    각 노드의 테스트 데이터와 라이브 데이터를 비교하여 라이브 검증을 수행합니다.

    동작 방식:
    - 각 노드는 테스트 데이터와 라이브 데이터를 모두 가지고 있음
    - 같은 노드 내에서 테스트 데이터와 라이브 데이터를 직접 비교
    - BreadCrumb, FAQ, Disclaimer 검증 결과를 각 노드의 validate 필드에 저장

    파라미터:
        shop_results: 검증할 SubCategoryNode 리스트 (각 노드가 테스트+라이브 데이터 포함)

    반환값:
        None: 결과는 각 노드의 validate 필드에 저장됨
    """
    try:
        log.info(
            f"[validate_live_comparison] Starting live comparison validation for {len(shop_results)} nodes"
        )

        # 검증할 노드 필터링 (특수 nv20, 에러 페이지, HTTP 에러 제외)
        nodes_to_validate = []
        for node in shop_results:
            if node.is_special:
                # 특수 nv20은 검증 스킵
                node.breadcrumb_validate = False
                node.faq_validate = False
                node.disclaimer_validate = False
                log.info(
                    f"[validate_live_comparison] Skipping validation for special node: {node.name}"
                )
                continue

            # 에러 페이지만 검증 스킵 (HTTP 에러는 검증 진행)
            if hasattr(node, "link_validate_desc") and node.link_validate_desc:
                if "error페이지" in str(node.link_validate_desc):
                    node.breadcrumb_validate = False
                    node.faq_validate = False
                    node.disclaimer_validate = False
                    log.info(
                        f"[validate_live_comparison] Skipping validation for error page: {node.name} ({node.link_validate_desc})"
                    )
                    continue

            # 라이브 데이터가 있는 노드만 검증 대상
            if hasattr(node, "live_breadcrumb") and node.live_breadcrumb is not None:
                nodes_to_validate.append(node)
                log.info(
                    f"[validate_live_comparison] Added node for validation: {node.name}"
                )
            else:
                log.warning(
                    f"[validate_live_comparison] No live data found for node: {node.name}"
                )
                node.breadcrumb_validate = False
                node.faq_validate = False
                node.disclaimer_validate = False

        log.info(
            f"[validate_live_comparison] Validating {len(nodes_to_validate)} nodes"
        )

        # 각 노드의 테스트 데이터와 라이브 데이터 비교
        for node in nodes_to_validate:
            log.info(
                f"[validate_live_comparison] Comparing test vs live data for: {node.name}"
            )

            # BreadCrumb 비교
            breadcrumb_result, breadcrumb_desc = compare_breadcrumbs(
                node.breadcrumb or [], node.live_breadcrumb or []
            )
            node.breadcrumb_validate = breadcrumb_result
            node.breadcrumb_validate_desc = breadcrumb_desc

            # FAQ 비교
            faq_result = False
            faq_desc = ""

            # FAQ가 둘 다 비어있는지 확인
            test_faq_empty = _is_empty_dom_node(node.faq)
            live_faq_empty = _is_empty_dom_node(node.live_faq)

            if not test_faq_empty and not live_faq_empty:
                # 둘 다 있는 경우 비교
                test_faq = DOMNode.from_dict(node.faq)
                live_faq = DOMNode.from_dict(node.live_faq)
                faq_result, faq_desc = compare_dom_nodes(test_faq, live_faq, "FAQ")
            elif test_faq_empty and live_faq_empty:
                # 둘 다 없는 경우 성공
                faq_result = True
                faq_desc = "FAQ does not exist"
            else:
                # 하나만 있는 경우 - 어느 쪽에 없는지 명시
                if test_faq_empty:
                    faq_desc = "FAQ does not exist in test page"
                else:
                    faq_desc = "FAQ does not exist in live page"

            node.faq_validate = faq_result
            node.faq_validate_desc = faq_desc

            # Disclaimer 비교
            disclaimer_result = False
            disclaimer_desc = ""

            # Disclaimer가 둘 다 비어있는지 확인
            test_disclaimer_empty = _is_empty_dom_node(node.disclaimer)
            live_disclaimer_empty = _is_empty_dom_node(node.live_disclaimer)

            if not test_disclaimer_empty and not live_disclaimer_empty:
                # 둘 다 있는 경우 비교
                test_disclaimer = DOMNode.from_dict(node.disclaimer)
                live_disclaimer = DOMNode.from_dict(node.live_disclaimer)
                disclaimer_result, disclaimer_desc = compare_dom_nodes(
                    test_disclaimer, live_disclaimer, "Disclaimer"
                )
            elif test_disclaimer_empty and live_disclaimer_empty:
                # 둘 다 없는 경우 성공
                disclaimer_result = True
                disclaimer_desc = "Disclaimer does not exist"
            else:
                # 하나만 있는 경우 - 어느 쪽에 없는지 명시
                if test_disclaimer_empty:
                    disclaimer_desc = "Disclaimer does not exist in test page"
                else:
                    disclaimer_desc = "Disclaimer does not exist in live page"

            node.disclaimer_validate = disclaimer_result
            node.disclaimer_validate_desc = disclaimer_desc

            log.info(
                f"[validate_live_comparison] Validation result for {node.name}: Breadcrumb={breadcrumb_result}, FAQ={faq_result}, Disclaimer={disclaimer_result}"
            )

        # 검증 완료 요약
        breadcrumb_validated_count = sum(
            1 for node in nodes_to_validate if node.breadcrumb_validate
        )
        faq_validated_count = sum(1 for node in nodes_to_validate if node.faq_validate)
        disclaimer_validated_count = sum(
            1 for node in nodes_to_validate if node.disclaimer_validate
        )

        log.info(f"[validate_live_comparison] Live comparison validation completed:")
        log.info(
            f"  - Breadcrumb: {breadcrumb_validated_count}/{len(nodes_to_validate)} nodes passed"
        )
        log.info(
            f"  - FAQ: {faq_validated_count}/{len(nodes_to_validate)} nodes passed"
        )
        log.info(
            f"  - Disclaimer: {disclaimer_validated_count}/{len(nodes_to_validate)} nodes passed"
        )

    except Exception as e:
        log.error(
            f"[validate_live_comparison] Error during live comparison validation: {e}"
        )
        # 에러 발생 시 모든 노드를 False로 설정
        for node in shop_results:
            if not node.is_special:
                if hasattr(node, "breadcrumb_validate"):
                    node.breadcrumb_validate = False
                if hasattr(node, "faq_validate"):
                    node.faq_validate = False
                if hasattr(node, "disclaimer_validate"):
                    node.disclaimer_validate = False


async def validate_all_live_elements(shop_results) -> None:
    """
    모든 SubCategoryNode에 대해 라이브 검증을 일괄 수행합니다.

    동작 방식:
    - validate_live_comparison 함수를 호출하여 통합 검증 수행
    - 각 노드의 테스트 데이터와 라이브 데이터를 직접 비교

    파라미터:
        shop_results: 검증할 SubCategoryNode 리스트

    반환값:
        None: 결과는 각 노드의 validate 필드에 저장됨
    """
    try:
        log.info(
            f"[validate_all_live_elements] Starting batch live validation for {len(shop_results)} nodes"
        )

        # validate_live_comparison 함수 호출하여 통합 검증 수행
        await validate_live_comparison(shop_results)

        log.info("[validate_all_live_elements] Batch live validation completed")

    except Exception as e:
        log.error(
            f"[validate_all_live_elements] Error during batch live validation: {e}"
        )
        # 에러 발생 시 모든 노드를 False로 설정
        for node in shop_results:
            if hasattr(node, "breadcrumb_validate"):
                node.breadcrumb_validate = False
            if hasattr(node, "faq_validate"):
                node.faq_validate = False
            if hasattr(node, "disclaimer_validate"):
                node.disclaimer_validate = False
