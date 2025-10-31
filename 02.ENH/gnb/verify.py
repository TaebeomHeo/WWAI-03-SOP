"""
verify.py - GNB/CGD 트리 구조 자동 비교 도구

이 모듈은 웹에서 추출한 GNB 트리(gnbtree)와 CGD 엑셀에서 추출한 트리(cgdtree)를 비교하여,
텍스트 및 링크 일치 여부를 자동으로 검증합니다.

주요 기능:
- cgdstore 폴더에서 최신 UK_*.json 파일의 tree 필드(cgdtree) 로드
- gnbtree(샘플 하드코딩)와 cgdtree를 계층 구조로 비교
- 동일 부모 하에서 gnbtree.refined_name == cgdtree.name이면 TextVerify True
- TextVerify True이고 refined_url이 있으면 url도 비교해 LinkVerify True
- 비교 결과는 gnbtree 각 노드에 기록, 매칭 실패 시 로그만 남김
- 모든 예외는 로깅만 하고 프로그램은 계속 진행
- 테스트를 위해 하드코딩된 샘플 트리 사용(실제 연동 시 함수만 교체)

실행 예시:
    python verify.py
"""

import os
import json
from typing import Optional
from gnb import GnbMenuNode
from cgd import CgdMenuNode
from utility.utils import compare_name, compare_url_without_domain
from utility.orangelogger import log

def load_latest_cgdtree(prefix: str) -> Optional[tuple[list[CgdMenuNode], str]]:
    """
    cgdstore 폴더에서 prefix로 시작하는 최신 *_*.json 파일의 tree 필드를 CgdMenuNode 리스트로 로드하고, 파일명을 함께 반환합니다.

    파라미터:
        prefix (str): 파일명 접두어(예: 'UK', 'DE' 등)
    반환값:
        Optional[tuple[list[CgdMenuNode], str]]: (CgdMenuNode 트리의 루트 노드 리스트, 파일명) 튜플. 예외 발생 시 (None, None) 반환
    """
    try:
        files = [f for f in os.listdir('cgdstore') if f.lower().startswith(f'{prefix.lower()}_gnb_') and f.endswith('.json')]
        if not files:
            log.error(f"No {prefix}_*.json file found in cgdstore.")
            return None, None
        files.sort(reverse=True)
        latest_file = files[0]
        with open(os.path.join('cgdstore', latest_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        tree_list = data.get('tree', [])
        if not tree_list:
            log.error(f"No 'tree' field in {latest_file}.")
            return None, None
        def from_dict(data: dict) -> CgdMenuNode:
            node = CgdMenuNode(
                node_type=data.get('node_type', 'L0'),
                name=data.get('name', ''),
                url=data.get('url', ''),
                analytics=data.get('analytics', ''),
                url_name=data.get('url_name', '')
            )
            for child in data.get('children', []):
                node.add_child(from_dict(child))
            return node
        roots = [from_dict(item) for item in tree_list]
        log.info(f"Loaded CGD tree from {latest_file} (root count: {len(roots)})")
        return roots, latest_file
    except Exception as e:
        log.error(f"Failed to load CGD tree: {e}")
        return None, None

def verify_gnb_vs_cgd(gnb_roots: list[GnbMenuNode], cgd_roots: list[CgdMenuNode], parent_path: str = "") -> None:
    """
    GNB 트리 루트 리스트와 CGD 트리 루트 리스트를 받아 전체 트리 구조를 자동으로 비교합니다.

    동작 방식:
    - GNB와 CGD의 루트 노드 리스트를 받아, 각 루트 노드 쌍에 대해 내부적으로 재귀 비교를 수행합니다.
    - CGD 트리가 없으면 경고 로그를 남기고 아무 작업도 하지 않습니다.
    - 각 루트 노드 쌍에 대해 _verify_gnb_vs_cgd_single()을 호출하여 하위 노드까지 재귀적으로 비교합니다.
    - 모든 비교 결과와 과정은 logger로 상세하게 기록합니다.

    파라미터:
        gnb_roots (list[GnbMenuNode]): 비교할 GNB 트리의 루트 노드 리스트
        cgd_roots (list[CgdMenuNode]): 비교할 CGD 트리의 루트 노드 리스트
        parent_path (str): 현재까지의 트리 경로(루트부터 현재 노드까지, 재귀용)

    반환값:
        없음

    예외 처리:
    - CGD 트리가 없거나, 비교 중 예외가 발생해도 프로그램은 중단되지 않고 로그만 남깁니다.

    사용 예시:
        verify_gnb_vs_cgd(gnb_roots, cgd_roots)
        # 각 GNB 노드의 name_verify, url_verify 필드에 비교 결과가 저장됨

    데이터 구조:
    - GnbMenuNode, CgdMenuNode: 각각 GNB/CGD 트리의 노드 객체
    """
    if not cgd_roots:
        log.warning("No CGD tree loaded for comparison.")
        return
    for gnb_root, cgd_root in zip(gnb_roots, cgd_roots):
        _verify_gnb_vs_cgd_single(gnb_root, cgd_root, parent_path)

def _verify_gnb_vs_cgd_single(gnb_node: GnbMenuNode, cgd_node: CgdMenuNode, parent_path: str = "") -> None:
    """
    GNB 메뉴 트리와 CGD 메뉴 트리의 각 메뉴(노드)를 한 쌍씩 비교해서,
    메뉴 이름과 링크가 서로 잘 맞는지 확인하는 함수입니다.

    동작 방식(쉽게 설명):
    - GNB(웹에서 추출한 메뉴)와 CGD(엑셀에서 추출한 메뉴)에서, 같은 위치(경로)에 있는 메뉴를 한 쌍씩 짝지어 비교합니다.
    - 먼저, 메뉴 이름이 같은지 비교합니다.
      * 이름 비교는 단순히 글자가 같은지만 보는 것이 아니라, 공백이나 대소문자 등도 무시하고 비교합니다.
    - 이름이 같으면, 그 다음에는 메뉴에 연결된 주소(링크)가 같은지도 비교합니다.
      * 링크 비교는 '도메인(사이트 주소)' 부분은 무시하고, 실제 경로만 비교합니다.
    - 이름과 링크가 모두 같으면, 해당 메뉴는 "정상"으로 표시합니다.
    - 만약 이름은 같지만 링크가 다르면, "이름은 맞지만 링크가 다름"으로 표시합니다.
    - 이름이 다르면, 그 메뉴는 "불일치"로 표시하고, 하위 메뉴(자식)까지 계속해서 같은 방식으로 비교합니다.
    - 메뉴 구조가 복잡할 수 있으므로, 한 메뉴 아래에 여러 하위 메뉴가 있을 때도, 각각 이름이 같은지, 링크가 같은지 위 규칙대로 반복해서 확인합니다.
    - 비교 결과는 모두 기록(로그)으로 남기고, 각 메뉴 노드에 결과를 저장합니다.

    파라미터:
        gnb_node (GnbMenuNode): 비교할 GNB 트리의 단일 노드
        cgd_node (CgdMenuNode): 비교할 CGD 트리의 단일 노드
        parent_path (str): 현재까지의 트리 경로(루트부터 현재 노드까지, 재귀용)

    반환값:
        없음

    예외 처리:
        비교 중 예외가 발생해도 프로그램은 중단되지 않고 로그만 남깁니다.

    사용 예시:
        _verify_gnb_vs_cgd_single(gnb_node, cgd_node)
        # gnb_node의 name_verify, url_verify 필드에 비교 결과가 저장됨

    데이터 구조:
        - GnbMenuNode, CgdMenuNode: 각각 GNB/CGD 트리의 노드 객체

    (비유: 두 개의 메뉴 나무에서, 같은 위치에 있는 가지(메뉴)를 하나씩 짝지어
    "이름이 같은지, 주소가 같은지"를 차례로 확인하고, 다르면 어디가 다른지 표시해주는 일입니다.)
    """
    # 현재까지의 트리 경로를 path로 구성 (루트부터 현재 노드까지)
    path = f"{parent_path}/{gnb_node.name}" if parent_path else gnb_node.name
    matched_cgd = None
    # 1. 현재 GNB 노드와 compare_name으로 이름이 일치하는 CGD 노드(자식 포함)를 찾음
    for sibling in [cgd_node] + cgd_node.children:
        if compare_name(sibling.name, gnb_node.name):
            matched_cgd = sibling
            break
    # 2. 비교 시작 로그 출력
    log.info(f"[COMPARE] Path: {path} | GNB Text: '{gnb_node.name}' | GNB Link: '{gnb_node.url}'")
    if matched_cgd:
        # 3. 이름이 일치하는 CGD 노드를 찾은 경우
        gnb_node.name_verify = True
        gnb_url = gnb_node.url
        cgd_url = matched_cgd.url
        if gnb_url and cgd_url:
            # 4. 두 노드 모두 URL이 존재하면 compare_url_without_domain으로 비교
            gnb_node.url_verify = compare_url_without_domain(gnb_url, cgd_url)
            link_result = "OK" if gnb_node.url_verify else "FAIL"
            log.info(f"[RESULT] Text: OK | Link: {link_result} | GNB: '{gnb_url}' | CGD: '{cgd_url}' | Path: {path}")
        else:
            # 5. URL이 하나라도 없으면 URL 비교는 SKIP 처리
            gnb_node.url_verify = False
            log.info(f"[RESULT] Text: OK | Link: SKIP (missing URL) | GNB: '{gnb_url}' | CGD: '{cgd_url}' | Path: {path}")
        # 6. 하위 노드(자식) 비교: GNB의 각 자식에 대해 CGD의 자식 중 compare_name이 일치하는 노드를 찾아 재귀 비교
        for g_child in gnb_node.children:
            cgd_sibling = next((c for c in matched_cgd.children if compare_name(c.name, g_child.name)), None)
            if cgd_sibling:
                # 6-1. 이름이 일치하는 자식이 있으면 해당 쌍으로 재귀 비교
                _verify_gnb_vs_cgd_single(g_child, cgd_sibling, path)
            else:
                # 6-2. 일치하는 자식이 없으면 name/url 검증 False로 설정, 하위 자식에 대해 전체 CGD 서브트리와 재귀 비교
                log.info(f"[CHILD_MISMATCH] Path: {path}/{g_child.name} | GNB Text: '{g_child.name}' | No matching CGD node found.")
                g_child.name_verify = False
                g_child.url_verify = False
                for gc in g_child.children:
                    _verify_gnb_vs_cgd_single(gc, cgd_node, path + '/' + g_child.name)
    else:
        # 7. 이름이 일치하는 CGD 노드를 찾지 못한 경우 (매칭 실패)
        gnb_node.name_verify = False
        gnb_node.url_verify = False
        log.info(f"[NO_MATCH] Path: {path} | GNB Text: '{gnb_node.name}' | No matching CGD node found.")
        # 8. 하위 노드(자식) 전체에 대해 동일한 CGD 노드와 재귀 비교 (CGD 트리 전체에서 매칭 시도)
        for g_child in gnb_node.children:
            _verify_gnb_vs_cgd_single(g_child, cgd_node, path)

def main() -> None:
    """
    실제 데이터 구조와 유사한 다양한 테스트 케이스를 포함한 gnbtree/cgdtree를 생성하여 비교 검증을 수행하는 메인 함수
    - 여러 L0(최상위) 노드, 다양한 L1/Featured, 일부러 불일치/누락/URL mismatch 등 포함
    """
    # GNB 트리 샘플 생성 (gnb.py의 GNBMenuNode 사용)
    gnb_l0a = GnbMenuNode("L0", "Shop", "/uk/shop/")
    gnb_l0b = GnbMenuNode("L0", "Support", "/uk/support/")
    gnb_l0c = GnbMenuNode("L0", "Promotion", "/uk/promo/")
    # L1/Featured/불일치/누락 등 다양한 자식 노드 추가
    gnb_l1a1 = GnbMenuNode("L1", "Galaxy S25 Ultra", "/uk/smartphones/galaxy-s25-ultra/buy/")
    gnb_l1a2 = GnbMenuNode("L1", "Galaxy S25 Edge", "/uk/smartphones/galaxy-s25-edge/buy/")
    gnb_l1a3 = GnbMenuNode("L1", "Galaxy S25 Ultra Special", "/uk/smartphones/galaxy-s25-ultra-special/buy/")  # CGD에 없음
    gnb_l1a4 = GnbMenuNode("L1", "Galaxy S25 Edge", "/uk/smartphones/galaxy-s25-edge/buy-different/")  # URL 불일치
    gnb_l0a.add_child(gnb_l1a1)
    gnb_l0a.add_child(gnb_l1a2)
    gnb_l0a.add_child(gnb_l1a3)
    gnb_l0a.add_child(gnb_l1a4)
    # L0B에 자식 없음(누락 케이스)
    # L0C에 Featured, L1, 불일치 등 혼합
    gnb_l1c1 = GnbMenuNode("Featured", "Summer Sale", "/uk/promo/summer/")
    gnb_l1c2 = GnbMenuNode("Featured", "Winter Sale", "/uk/promo/winter/")
    gnb_l1c3 = GnbMenuNode("L1", "Exclusive", "/uk/promo/exclusive/")
    gnb_l1c4 = GnbMenuNode("L1", "NotInCGD", "/uk/promo/notincgd/")  # CGD에 없음
    gnb_l0c.add_child(gnb_l1c1)
    gnb_l0c.add_child(gnb_l1c2)
    gnb_l0c.add_child(gnb_l1c3)
    gnb_l0c.add_child(gnb_l1c4)
    gnbtree_roots = [gnb_l0a, gnb_l0b, gnb_l0c]

    # CGD 트리 샘플 생성 (cgd.py의 CgdMenuNode 사용)
    cgd_l0a = CgdMenuNode("L0", "Shop", "/uk/shop/")
    cgd_l1a1 = CgdMenuNode("L1_Product", "Galaxy S25 Ultra", "/uk/smartphones/galaxy-s25-ultra/buy/")
    cgd_l1a2 = CgdMenuNode("L1_Product", "Galaxy S25 Edge", "/uk/smartphones/galaxy-s25-edge/buy/")
    cgd_l0a.add_child(cgd_l1a1)
    cgd_l0a.add_child(cgd_l1a2)
    cgd_l0b = CgdMenuNode("L0", "Support", "/uk/support/")
    # L0B에 자식 없음
    cgd_l0c = CgdMenuNode("L0", "Promotion", "/uk/promo/")
    cgd_l1c1 = CgdMenuNode("L1_Banner", "Summer Sale", "/uk/promo/summer/")
    cgd_l1c2 = CgdMenuNode("L1_Banner", "Winter Sale", "/uk/promo/winter/")
    cgd_l1c3 = CgdMenuNode("L1_Product", "Exclusive", "/uk/promo/exclusive/")
    cgd_l0c.add_child(cgd_l1c1)
    cgd_l0c.add_child(cgd_l1c2)
    cgd_l0c.add_child(cgd_l1c3)
    cgd_roots = [cgd_l0a, cgd_l0b, cgd_l0c]

    # 실제 비교 수행 (여러 루트 노드)
    verify_gnb_vs_cgd(gnbtree_roots, cgd_roots)

    # 결과 요약 출력
    for gnb_root in gnbtree_roots:
        log.info(f"[SUMMARY] L0: {gnb_root.name} | TextVerify: {gnb_root.name_verify}, LinkVerify: {gnb_root.url_verify}")
        for child in gnb_root.children:
            log.info(f"[SUMMARY]   Child: {child.name} | TextVerify: {child.name_verify}, LinkVerify: {child.url_verify}")

if __name__ == "__main__":
    main() 