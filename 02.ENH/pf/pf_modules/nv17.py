"""
pf_modules/nv17.py - nv17 검증 모듈

PF 페이지에서 nv17-breadcrumb 요소의 부적절한 노출을 방지하는 
검증 모듈입니다. 사용자 경험을 저해할 수 있는 불필요한 네비게이션 
요소의 존재 여부를 체계적으로 검증합니다.

주요 검증 대상:
- nv17-breadcrumb 클래스를 가진 요소의 존재 여부
- 해당 요소의 visibility 상태 (보이는지 숨겨진지)
- 페이지 로드 시 부적절한 네비게이션 요소 노출 방지

핵심 기능:
- 요소 존재성 검증: nv17-breadcrumb 클래스 요소의 DOM 존재 확인
- 가시성 상태 검증: 요소가 실제로 사용자에게 보이는지 확인
- 검증 결과 상세화: 요소 존재 여부와 가시성 상태를 구분하여 보고
- 오류 상황 처리: 예상치 못한 DOM 구조 변경에 대한 안정적 대응

검증 프로세스:
1. 페이지 로드 후 nv17-breadcrumb 클래스 요소 검색
2. 요소 존재 여부 확인
3. 존재하는 경우 visibility 상태 검증
4. 검증 결과에 따른 적절한 상태 코드 반환
5. 상세한 검증 정보를 딕셔너리 형태로 제공
"""

from utility.orangelogger import log


async def validate_nv17_breadcrumb_absence(page) -> dict:
    """
    nv17-breadcrumb 요소가 존재하지 않거나 visible하지 않은지 검증합니다.
    
    동작 방식:
    - nv17-breadcrumb 클래스를 가진 요소를 찾습니다
    - 요소가 존재하지 않으면 검증 통과
    - 요소가 존재하지만 visible하지 않으면 검증 통과
    - 요소가 존재하고 visible하면 검증 실패
    
    파라미터:
        page: Playwright Page 객체
        
    반환값:
        dict: nv17-breadcrumb 검증 결과
        {
            "validate": bool,
            "description": str,
            "details": {
                "element_exists": bool,
                "element_visible": bool,
                "element_count": int
            }
        }
    """
    log.info("[validate_nv17_breadcrumb_absence] Starting nv17-breadcrumb absence validation")
    
    try:
        # nv17-breadcrumb 클래스를 가진 모든 요소 찾기
        nv17_elements = await page.query_selector_all(".nv17-breadcrumb")
        element_count = len(nv17_elements)
        
        log.info(f"[validate_nv17_breadcrumb_absence] Found {element_count} nv17-breadcrumb elements")
        
        # 요소가 존재하지 않으면 검증 통과
        if element_count == 0:
            log.info("[validate_nv17_breadcrumb_absence] No nv17-breadcrumb elements found - PASS")
            return {
                "validate": True,
                "description": ""
            }
        
        # 요소가 존재하는 경우 visibility 확인
        visible_count = 0
        for element in nv17_elements:
            try:
                is_visible = await element.is_visible()
                if is_visible:
                    visible_count += 1
                    log.info(f"[validate_nv17_breadcrumb_absence] Found visible nv17-breadcrumb element")
            except Exception as e:
                log.warning(f"[validate_nv17_breadcrumb_absence] Error checking element visibility: {e}")
                continue
        
        # 모든 요소가 visible하지 않으면 검증 통과
        if visible_count == 0:
            log.info("[validate_nv17_breadcrumb_absence] nv17-breadcrumb elements exist but are not visible - PASS")
            return {
                "validate": True,
                "description": "nv17-breadcrumb elements exist but are not visible"
            }
        
        # visible한 요소가 있으면 검증 실패
        log.warning(f"[validate_nv17_breadcrumb_absence] Found {visible_count} visible nv17-breadcrumb elements - FAIL")
        return {
            "validate": False,
            "description": f"nv17-breadcrumb elements are visible ({visible_count}/{element_count} elements visible)",
        }
        
    except Exception as e:
        log.error(f"[validate_nv17_breadcrumb_absence] Error during validation: {e}")
        return {
            "validate": False,
            "description": f"Error during nv17-breadcrumb validation: {str(e)}"
        }
