"""
pf_modules/purchase.py - 구매 검증 모듈

PF 페이지에서 표시된 제품들의 실제 구매 가능성을 검증하는 
핵심 모듈입니다. 사용자가 제품을 구매할 수 있는 상태인지 
정확하게 판단하여 구매 경험의 품질을 보장합니다.

주요 검증 대상:
- 제품 카드의 CTA 버튼 an-la 속성 값
- 구매 가능 상태 판단 (an-la="pf product card:buy")
- 라이브 페이지와 테스트 페이지 간의 구매 가능성 일치성
- 모든 제품의 구매 가능성 통합 검증

핵심 기능:
- CTA 버튼 an-la 속성 기반 구매 가능성 판단: an-la="pf product card:buy"인 경우 구매 가능
- 제품별 개별 검증: 각 제품의 구매 상태를 독립적으로 검증
- 통합 구매 가능성 검증: 모든 제품이 구매 가능해야 전체 검증 통과
- 상세한 검증 결과 제공: 구매 불가능한 제품의 구체적인 정보 제공
- 라이브 환경 대응: 실제 구매 환경에서의 정확한 상태 반영

검증 프로세스:
1. 제품 리스트에서 각 제품의 CTA 버튼 an-la 속성 값 추출
2. an-la 속성 값에 따른 구매 가능성 판단 ("pf product card:buy" = 구매 가능)
3. 모든 제품의 구매 가능성 상태 종합 분석
4. 구매 불가능한 제품이 있는 경우 상세 정보 수집
5. 전체 구매 가능성 검증 결과 및 상세 설명 제공
"""

from typing import List
from utility.orangelogger import log


async def validate_purchase_capability(products: List, page=None) -> dict:
    """
    제품 리스트에 대해 구매 가능성을 검증합니다.
    
    동작 방식:
    - 전달받은 모든 제품을 검사 (상위 4개 제한 없음)
    - 각 제품의 CTA 버튼 an-la 속성 값 확인
    - an-la="pf product card:buy"이면 구매 가능한 제품으로 판단
    - 모든 제품이 구매 가능해야 검증 통과 (1개라도 구매 불가능이면 검증 실패)
    - no-result 요소가 있는 경우 제품이 0개여도 검증 통과
    
    제외 대상:
    - pd21-product-card__banner 클래스를 가진 요소들은 이미 extract_product에서 제외됨
    - display: none 스타일이 적용된 제품 카드들도 이미 extract_product에서 제외됨
    - 구매 검증 대상은 전달받은 제품 리스트 전체 (보이는 제품들만)
    
    파라미터:
        products (List): 제품 리스트 (배너 제외된 제품들, 검사할 제품 수는 호출자가 결정)
        page: Playwright Page 객체 (no-result 요소 확인용, 선택사항)
        
    반환값:
        dict: 구매 가능성 검증 결과
        {
            "validate": bool,
            "description": str,
            "details": {
                "total_checked": int,
                "purchasable_count": int,
                "products": List[dict]  # 각 상품별 구매 가능 결과 상세
            }
        }
    """
    log.info("[validate_purchase_capability] Starting purchase capability validation")
    
    # no-result 요소 확인 (제품이 0개인 경우 정상 처리)
    has_no_result = False
    if page:
        try:
            no_result_element = await page.query_selector(".pd21-product-finder__no-result")
            has_no_result = no_result_element is not None
            if has_no_result:
                log.info("[validate_purchase_capability] No result element found - purchase validation passes for empty results")
        except Exception as e:
            log.warning(f"[validate_purchase_capability] Error checking no-result element: {e}")
    
    # 전달받은 모든 제품 검사 (상위 4개 제한 없음)
    total_checked = len(products)
    purchasable_count = 0
    
    log.info(f"[validate_purchase_capability] Checking {total_checked} products")
    
    per_product_details = []
    for idx, product in enumerate(products, 1):
        # CTA 버튼의 an-la 속성 값으로 구매 가능성 판단
        is_purchasable = (product.cta_an_la == "pf product card:buy")
        
        if is_purchasable:
            purchasable_count += 1
        
        # 개별 제품 _desc 생성
        if is_purchasable:
            # 성공 시: 제품명만
            product_desc = product.name
        else:
            # 실패 시: 제품명, 이유
            reason = f"CTA an-la is '{product.cta_an_la}' (expected 'pf product card:buy')"
            product_desc = f"{product.name}, {reason}"
        
        per_product_details.append({
            "name": product.name,
            "url": product.url,
            "price": product.price,
            "cta_an_la": product.cta_an_la,
            "badge": product.badge,
            "purchasable": is_purchasable,
            "desc": product_desc
        })
        
        log.info(f"[validate_purchase_capability] Product {idx}: {product.name} - "
                    f"CTA an-la: '{product.cta_an_la}', "
                    f"Purchasable: {is_purchasable}")
    
    # 검증 결과 생성 - 모든 제품이 구매 가능해야 통과 (no-result 요소가 있으면 제품이 0개여도 통과)
    if has_no_result:
        validate_result = True  # no-result 요소가 있으면 제품이 0개여도 검증 통과
        description = "No result element found - purchase validation passes for empty results"
    else:
        validate_result = purchasable_count == total_checked  # 모든 제품이 구매 가능해야 통과
    
    if not validate_result and not has_no_result:
        # purchase_validate가 false일 경우 구매 불가능한 제품의 위치와 CTA 정보 구성
        unpurchasable_positions = []
        for idx, product in enumerate(per_product_details, 1):
            if not product.get('purchasable', False):
                cta_an_la = product.get('cta_an_la', '')
                # CTA 값 처리: "pf product card:" 접두사가 있으면 제거, 없으면 그대로 표시
                if cta_an_la.startswith("pf product card:"):
                    cta_display = cta_an_la.removeprefix("pf product card:")
                else:
                    cta_display = cta_an_la if cta_an_la else "empty"
                unpurchasable_positions.append(f"[{idx}/{total_checked}]({cta_display})")
        
        # 구매 불가능한 제품이 있으면 해당 위치들만 표시, 없으면 빈 문자열
        if unpurchasable_positions:
            description = ", ".join(unpurchasable_positions)
        else:
            description = ""  # 구매 불가능한 제품이 없으면 빈 문자열
    elif has_no_result:
        # no-result 요소가 있는 경우 이미 description이 설정됨
        pass
    else:
        description = ""  # 성공 시에는 desc 정보를 추가하지 않음
    
    result = {
        "validate": validate_result,
        "description": description,
        "details": {
            "total_checked": total_checked,
            "purchasable_count": purchasable_count,
            "products": per_product_details
        }
    }
    
    log.info(f"[validate_purchase_capability] {description}")
    return result
