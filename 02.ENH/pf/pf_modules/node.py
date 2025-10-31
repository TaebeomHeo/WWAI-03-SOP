"""
pf_modules/node.py - PF 페이지의 노드 클래스 정의

PF(Product Finder) 페이지에서 추출된 모든 데이터를 체계적으로 구조화하기 위한 
노드 클래스들을 정의하는 핵심 모듈입니다. 계층적 데이터 구조와 검증 정보를 
효율적으로 관리합니다.

데이터 구조 설계:
- 계층적 트리 구조: main_category → sub_category → {product, content_card}
- 각 노드는 독립적인 검증 상태와 메타데이터를 보유
- JSON 직렬화/역직렬화 지원으로 데이터 저장 및 전송 최적화
- 타입 안전성을 위한 dataclass 기반 설계

주요 노드 타입:
- MainCategoryNode: 최상위 메인 카테고리 정보 (사업부별 분류)
- SubCategoryNode: 중간 서브 카테고리 정보 (제품군별 분류)
- PfMenuNode: 최하위 제품 정보 (개별 제품 상세)

핵심 기능:
- 데이터 구조화: 추출된 원시 데이터를 의미있는 객체로 변환
- 검증 상태 관리: 각 노드별 검증 결과와 상세 정보 저장
- 계층적 탐색: 부모-자식 관계를 통한 효율적인 데이터 접근
- JSON 호환성: 외부 시스템과의 데이터 교환을 위한 직렬화 지원
- 메타데이터 추적: URL, 이름, 설명 등 노드별 상세 정보 관리
"""

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List
from utility.orangelogger import log


########################################################################################
# 최상위 노드: MainCategoryNode
########################################################################################
@dataclass
class MainCategoryNode:
    """
    메인 카테고리(nv19-pd-category-main) 정보를 표현하는 노드 클래스입니다.
    CGD 데이터와 실제 페이지 데이터를 비교하여 검증합니다.
    
    계층적 위치: 최상위 (main_category)
    자식 노드: SubCategoryNode 리스트
    """
    # 기본 필드
    name: str = ""  # 페이지에서 추출한 메인 카테고리 이름
    url: str = ""  # URL
    
    # 자식 노드들 (SubCategoryNode)
    children: List['SubCategoryNode'] = None

    def print_tree(self, indent: int = 0) -> None:
        """
        MainCategoryNode 전체 정보를 logger로 구조적으로 한 번에 출력합니다.
        """
        # MainCategoryNode를 dict로 변환하여 JSON 포맷으로 pretty print
        node_dict = asdict(self)
        node_json = json.dumps(node_dict, ensure_ascii=False, indent=2)
        log.info(f"MainCategoryNode(full):\n{node_json}")

    def to_dict(self) -> dict:
        """MainCategoryNode를 딕셔너리로 변환"""
        children_dict = []
        if self.children:
            for child in self.children:
                if hasattr(child, 'to_dict'):
                    children_dict.append(child.to_dict())
        
        return {
            "node_type": "Main_Category",
            "name": self.name,
            "url": self.url,
            "children": children_dict
        }


########################################################################################
# 중간 노드: SubCategoryNode
########################################################################################
@dataclass
class SubCategoryNode:
    """
    서브 카테고리(nv20-pd-category-sub) 정보를 표현하는 노드 클래스입니다.
    
    계층적 위치: 중간 (sub_category)
    부모 노드: MainCategoryNode
    자식 노드: PfMenuNode 리스트
    """
    # 기본 필드
    name: str = ""
    url: str = ""
    
    # 링크 검증 필드
    link_status: int = -1  # HTTP 응답 상태 코드
    link_validate: bool = False  # 페이지 상태 유효성 (200일 때 true)
    link_validate_desc: str = ""  # 링크 체크 결과 설명 (200이 아닐 경우나 리다이렉트 등 특수 상황에만 메시지 저장)
    
    # nv17-breadcrumb 검증 필드
    nv17_validate: bool = False  # nv17-breadcrumb 검증 결과
    nv17_validate_desc: str = ""  # nv17-breadcrumb 검증 결과 설명

    # 네비게이션 가시성 검증 필드
    navigation_visible_validate: bool = False  # nv19/nv20 요소의 가시성 검증 결과
    navigation_visible_validate_desc: str = ""  # 네비게이션 가시성 검증 결과 설명
    
    # 헤드라인 검증 필드
    headline: str = ""  # 페이지에서 추출한 헤드라인 텍스트
    headline_validate: bool = False  # 헤드라인 검증 결과
    headline_validate_desc: str = ""  # 헤드라인 검증 결과 설명
    
    # 제품 수 검증 필드
    result_count: int = 0  # 페이지에서 추출한 제품 수 텍스트
    result_validate: bool = False  # 카드 개수와 제품 수 텍스트 일치 여부
    result_validate_desc: str = ""  # 결과 수 검증 결과 설명

    # 정렬 검증 필드
    sort_validate: bool = False  # 정렬 검증 결과
    sort_validate_desc: str = ""  # 정렬 검증 결과 설명
    sort_validate_info: Dict[str, Any] = None  # 정렬 검증 상세 정보
    
    # 구매 가능 검증 필드
    purchase_validate: bool = False  # 구매 가능 제품 검증 결과 (가격 정보 기반)
    purchase_validate_desc: str = ""  # 구매 가능 검증 결과 설명
    purchase_validate_info: Dict[str, Any] = None  # 구매 가능 검증 상세 정보 (가격 있는 제품 수 등)

    # BreadCrumb 검증 필드
    breadcrumb: List[str] = None  # BreadCrumb(테스트 페이지)
    live_breadcrumb: List[str] = None  # BreadCrumb(라이브 페이지)
    breadcrumb_validate: bool = False  # BreadCrumb 검증 결과
    breadcrumb_validate_desc: str = ""  # BreadCrumb 검증 결과 설명
    
    # FAQ 검증 필드
    faq: Dict[str, Any] = None  # FAQ(테스트 페이지)
    live_faq: Dict[str, Any] = None  # FAQ(라이브 페이지)
    faq_validate: bool = False  # FAQ 검증 결과
    faq_validate_desc: str = ""  # FAQ 검증 결과 설명
    
    # Disclaimer 검증 필드
    disclaimer: Dict[str, Any] = None  # Disclaimer(테스트 페이지)
    live_disclaimer: Dict[str, Any] = None  # Disclaimer(라이브 페이지)
    disclaimer_validate: bool = False  # Disclaimer 검증 결과
    disclaimer_validate_desc: str = ""  # Disclaimer 검증 결과 설명
    
    # 필터 검증 필드
    filter_validate: bool = False  # 필터 검증 결과
    filter_validate_desc: str = ""  # 필터 검증 결과 설명
    filter_info: Dict[str, Any] = None  # 필터 구조 정보
    filter_validate_info: Dict[str, Any] = None  # 필터 검증 상세 결과
    
    children: List['PfMenuNode'] = None  # PfMenuNode를 자식으로 가짐
    
    # 특수 nv20 플래그
    is_special: bool = False  # 특수 nv20 여부 (compare, help me choose 등)
    is_filter_testable: bool = False  # 필터 테스트 대상 여부 (all nv20)

    def print_tree(self, indent: int = 0) -> None:
        """
        SubCategoryNode 전체 정보를 logger로 구조적으로 한 번에 출력합니다.
        """
        # SubCategoryNode를 dict로 변환하여 JSON 포맷으로 pretty print
        node_dict = asdict(self)
        node_json = json.dumps(node_dict, ensure_ascii=False, indent=2)
        log.info(f"SubCategoryNode(full):\n{node_json}")
    
    
    def to_dict(self) -> dict:
        """SubCategoryNode를 딕셔너리로 변환"""
        # 기본 필드 (모든 nv20 공통)
        result = {
            "node_type": "Sub_Category",
            "name": self.name,
            "url": self.url,
            "link_status": self.link_status,
            "link_validate": self.link_validate,
            "link_validate_desc": self.link_validate_desc,
        }
        
        # 특수 nv20이나 다른 nv19로 이동한 nv20: 기본 필드만 (추가 필드 없음)
        if self.is_special:
            pass  # 기본 필드만 사용
        
        # 일반 nv20: 헤드라인 + 결과수 + Sort + Purchase + BreadCrumb + 제품 리스트
        # FAQ + Disclaimer + 필터 검증 필드 추가
        else:
        #     children_dict = [child.to_dict() for child in self.children] if self.children else []
            
        #     # 먼저 children을 제외한 필드들 추가
            result.update({
                "nv17_validate": self.nv17_validate,
                "nv17_validate_desc": self.nv17_validate_desc,  
        #         "navigation_visible_validate": self.navigation_visible_validate,
        #         "navigation_visible_validate_desc": self.navigation_visible_validate_desc,
        #         "headline": self.headline,
        #         "headline_validate": self.headline_validate,
        #         "headline_validate_desc": self.headline_validate_desc,
        #         "result_count": self.result_count,
        #         "result_validate": self.result_validate,
        #         "result_validate_desc": self.result_validate_desc,
        #         "sort_validate": self.sort_validate,
        #         "sort_validate_desc": self.sort_validate_desc,
        #         "sort_validate_info": self.sort_validate_info,
        #         "purchase_validate": self.purchase_validate,
        #         "purchase_validate_desc": self.purchase_validate_desc,
        #         "purchase_validate_info": self.purchase_validate_info,
        #         "faq": self.faq,
        #         "live_faq": self.live_faq,
        #         "faq_validate": self.faq_validate,
        #         "faq_validate_desc": self.faq_validate_desc,
        #         "disclaimer": self.disclaimer,
        #         "live_disclaimer": self.live_disclaimer,
        #         "disclaimer_validate": self.disclaimer_validate,
        #         "disclaimer_validate_desc": self.disclaimer_validate_desc,
        #         "breadcrumb": self.breadcrumb,
        #         "live_breadcrumb": self.live_breadcrumb,
        #         "breadcrumb_validate": self.breadcrumb_validate,
        #         "breadcrumb_validate_desc": self.breadcrumb_validate_desc
            })
            
        #     # 필터 테스트 대상인 경우 필터 관련 필드 추가
        #     if getattr(self, 'is_filter_testable', False):
        #         result.update({
        #             "filter_validate": self.filter_validate,
        #             "filter_validate_desc": self.filter_validate_desc,
        #             "filter_validate_info": self.filter_validate_info
        #         })
        #     result["children"] = children_dict
        return result


########################################################################################
# 최하위 노드: PfMenuNode (제품 정보)
########################################################################################
@dataclass
class PfMenuNode:
    """
    제품 정보를 표현하는 노드 클래스입니다.
    
    계층적 위치: 최하위 (product)
    부모 노드: SubCategoryNode
    자식 노드: 없음 (리프 노드)
    
    필드 설명:
    - name: 제품명
    - url: 제품 상세 페이지 URL
    - price: 제품 가격 정보 (레거시 필드, 기존 호환성 유지용)
    - cta_an_la: CTA 버튼의 an-la 속성 값 (구매 가능 여부 판단에 사용)
    - desc: 제품 설명
    - badge: 제품 배지 정보
    - meta: 제품 메타 정보 (동적 추출)
    """
    # 기본 필드
    name: str = ""
    url: str = ""
    price: str = ""
    cta_an_la: str = ""
    desc: str = ""
    badge: str = ""
    meta: Dict[str, Any] = None

    def print_tree(self, indent: int = 0) -> None:
        """
        PfMenuNode 전체 정보를 logger로 구조적으로 한 번에 출력합니다.
        meta도 depth 제한 없이 트리 구조로 함께 출력합니다.
        """
        # PfMenuNode를 dict로 변환하여 JSON 포맷으로 pretty print
        node_dict = asdict(self)
        node_json = json.dumps(node_dict, ensure_ascii=False, indent=2)
        log.info(f"PfMenuNode(full):\n{node_json}")

    def to_dict(self) -> dict:
        """ProductNode를 딕셔너리로 변환"""
        return {
            "node_type": "Product",
            "name": self.name,
            "url": self.url,
            "price": self.price,
            "cta_an_la": self.cta_an_la,
            "desc": self.desc,
            "badge": self.badge,
            "meta": self.meta if self.meta is not None else {}
        }

########################################################################################
# 유틸리티 함수
########################################################################################
def create_navigation_node(name: str, url: str) -> SubCategoryNode:
    """
    nv20 네비게이션 검증을 위한 SubCategoryNode를 생성합니다.
    
    파라미터:
        name (str): nv20명
        url (str): nv20 URL
    
    반환값:
        SubCategoryNode: 생성된 Sub_Category 노드
    """
    try:
        # 파라미터가 None인 경우 빈 문자열로 처리
        name = name if name is not None else ""
        url = url if url is not None else ""

        # Sub_Category 노드 생성
        node = SubCategoryNode(
            name=name,
            url=url
        )
        
        return node
    except Exception as e:
        log.error(f"Error creating navigation node: {e}")
        # 예외 발생 시 기본값으로 생성
        return SubCategoryNode(
            name="",
            url=""
        )