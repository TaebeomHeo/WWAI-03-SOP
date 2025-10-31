"""
pf_modules - Product Family 페이지 처리 모듈 패키지

Samsung Product Family(PF) 페이지의 모든 데이터 추출, 구조화, 검증 기능을 
통합 관리하는 핵심 패키지입니다. PF 시스템의 품질 보장을 위한 
종합적인 검증 프레임워크를 제공합니다.

패키지 구성:
- node.py: PF 페이지 데이터 구조화를 위한 노드 클래스 정의
- headline.py: 헤드라인과 nv20명 간의 일치성 검증
- live_validation.py: 테스트-라이브 환경 간 콘텐츠 일관성 검증
- filter.py: 필터 시스템의 기능성 및 정확성 검증
- cgd_verify.py: CGD 데이터와 PF 페이지 데이터 간 일치성 검증
- result_count.py: 결과 수와 실제 카드 수 간의 일치성 검증
- nv17.py: nv17-breadcrumb 요소의 부적절한 노출 방지 검증
- purchase.py: 제품 구매 가능성 검증
"""

from .node import PfMenuNode, SubCategoryNode, MainCategoryNode, create_navigation_node

__all__ = [
    'PfMenuNode',
    'SubCategoryNode', 
    'MainCategoryNode',
    'create_navigation_node'
]
