"""
pf_modules/sort.py - 정렬 기능 검증 모듈

Samsung Product Family 페이지의 정렬 기능을 검증하는 모듈입니다.
정렬 버튼의 텍스트와 실제 정렬 옵션 간의 일치성을 확인하여 
사용자에게 표시되는 정렬 옵션과 실제 적용되는 정렬이 일치하는지 검증합니다.

주요 검증 대상:
- 정렬 버튼의 표시 텍스트 (pd21-sort__opener-name)
- 정렬 옵션 리스트의 기본 정렬값 (data-default-sort)
- 선택된 정렬 옵션의 텍스트 (data-sort-text)

핵심 기능:
- 정렬 버튼 텍스트 추출: 현재 표시된 정렬 옵션 텍스트 확인
- 정렬 옵션 리스트 추출: 드롭다운에서 사용 가능한 모든 정렬 옵션 분석
- 기본 정렬값 확인: data-default-sort 속성값으로 설정된 기본 정렬 옵션 확인
- 선택된 옵션 검증: checked 속성이 있는 라디오 버튼의 정렬 텍스트 확인
- 정렬 일치성 검증: 버튼 텍스트와 실제 선택된 옵션의 일치성 확인

검증 프로세스:
1. 정렬 버튼 클릭하여 드롭다운 메뉴 열기
2. 현재 표시된 정렬 버튼의 텍스트 추출
3. 정렬 옵션 리스트의 기본 정렬값 확인
4. 선택된 라디오 버튼의 정렬 텍스트 추출
5. 세 값 간의 일치성 검증 및 결과 반환
"""

from typing import Dict, Optional, List
from playwright.async_api import Page, ElementHandle
from utility.orangelogger import log


async def extract_sort_opener_text(page: Page) -> Optional[str]:
    """
    정렬 버튼의 현재 표시 텍스트를 추출합니다.
    
    동작 방식:
    - pd21-sort__opener-name 클래스를 가진 요소에서 텍스트 추출
    - 정렬 버튼을 클릭하기 전의 현재 표시된 정렬 옵션 텍스트를 확인
    - 요소가 존재하지 않거나 텍스트가 없는 경우 None 반환
    
    파라미터:
        page (Page): Playwright 페이지 객체
        
    반환값:
        Optional[str]: 정렬 버튼의 텍스트, 추출 실패 시 None
        
    예외 처리:
    - 요소를 찾을 수 없는 경우: None 반환
    - 텍스트가 비어있는 경우: None 반환
    """
    try:
        log.info("[extract_sort_opener_text] Extracting sort opener text")
        
        # 정렬 버튼의 텍스트 요소 찾기
        opener_element = await page.query_selector('.pd21-sort__opener-name')
        
        if not opener_element:
            log.warning("[extract_sort_opener_text] Sort opener element not found")
            return None
        
        # 텍스트 추출
        text = await opener_element.inner_text()
        text = text.strip() if text else None
        
        if text:
            log.info(f"[extract_sort_opener_text] Extracted text: '{text}'")
        else:
            log.warning("[extract_sort_opener_text] No text found in sort opener")
            
        return text
        
    except Exception as e:
        log.error(f"[extract_sort_opener_text] Error extracting sort opener text: {e}")
        return None


async def extract_sort_list_default(page: Page) -> Optional[str]:
    """
    정렬 옵션 리스트의 기본 정렬값을 추출합니다.
    
    동작 방식:
    - pd21-sort__opener 버튼을 클릭하여 정렬 옵션 드롭다운 열기
    - js-pfv2-sortby-wrap 클래스의 data-default-sort 속성값 추출
    - 드롭다운이 열린 후 기본 정렬값 확인
    
    파라미터:
        page (Page): Playwright 페이지 객체
        
    반환값:
        Optional[str]: 기본 정렬값, 추출 실패 시 None
        
    예외 처리:
    - 정렬 버튼을 찾을 수 없는 경우: None 반환
    - 드롭다운을 열 수 없는 경우: None 반환
    - data-default-sort 속성이 없는 경우: None 반환
    """
    try:
        log.info("[extract_sort_list_default] Extracting sort list default value")
        
        # 정렬 버튼 찾기
        sort_opener = await page.query_selector('.pd21-sort__opener')
        
        if not sort_opener:
            log.warning("[extract_sort_list_default] Sort opener button not found")
            return None
        
        # 정렬 버튼 클릭하여 드롭다운 열기
        await sort_opener.click()
        log.info("[extract_sort_list_default] Sort opener clicked")
        
        # 잠시 대기하여 드롭다운이 완전히 열리도록 함
        await page.wait_for_timeout(500)
        
        # 정렬 옵션 리스트 컨테이너 찾기
        sort_wrap = await page.query_selector('.js-pfv2-sortby-wrap')
        
        if not sort_wrap:
            log.warning("[extract_sort_list_default] Sort wrap element not found")
            return None
        
        # data-default-sort 속성값 추출
        default_sort = await sort_wrap.get_attribute('data-default-sort')
        
        if default_sort:
            log.info(f"[extract_sort_list_default] Extracted default sort: '{default_sort}'")
        else:
            log.warning("[extract_sort_list_default] No data-default-sort attribute found")
            
        return default_sort
        
    except Exception as e:
        log.error(f"[extract_sort_list_default] Error extracting sort list default: {e}")
        return None


async def extract_selected_sort_text(page: Page) -> Optional[str]:
    """
    선택된 정렬 옵션의 텍스트를 추출합니다.
    
    동작 방식:
    - 정렬 드롭다운이 열린 상태에서 checked 속성이 있는 라디오 버튼 찾기
    - 해당 라디오 버튼의 data-sort-text 속성값 추출
    - 실제로 선택된 정렬 옵션의 텍스트를 확인
    
    파라미터:
        page (Page): Playwright 페이지 객체
        
    반환값:
        Optional[str]: 선택된 정렬 옵션의 텍스트, 추출 실패 시 None
        
    예외 처리:
    - checked 속성이 있는 라디오 버튼을 찾을 수 없는 경우: None 반환
    - data-sort-text 속성이 없는 경우: None 반환
    """
    try:
        log.info("[extract_selected_sort_text] Extracting selected sort text")
        
        # checked 속성이 있는 라디오 버튼 찾기
        checked_radio = await page.query_selector('.radio-v3__input[checked]')
        
        if not checked_radio:
            log.warning("[extract_selected_sort_text] No checked radio button found")
            return None
        
        # data-sort-text 속성값 추출
        sort_text = await checked_radio.get_attribute('data-sort-text')
        
        if sort_text:
            log.info(f"[extract_selected_sort_text] Extracted selected sort text: '{sort_text}'")
        else:
            log.warning("[extract_selected_sort_text] No data-sort-text attribute found")
            
        return sort_text
        
    except Exception as e:
        log.error(f"[extract_selected_sort_text] Error extracting selected sort text: {e}")
        return None


async def extract_all_sort_options(page: Page) -> List[Dict[str, str]]:
    """
    정렬 드롭다운의 모든 옵션을 추출합니다.
    
    동작 방식:
    - 정렬 드롭다운이 열린 상태에서 모든 라디오 버튼 찾기
    - 각 라디오 버튼의 data-sort-text 속성값과 checked 상태 확인
    - 모든 정렬 옵션의 정보를 리스트로 반환
    
    파라미터:
        page (Page): Playwright 페이지 객체
        
    반환값:
        List[Dict[str, str]]: 모든 정렬 옵션 정보
        [{"text": "정렬 텍스트", "checked": "true/false"}, ...]
        
    예외 처리:
    - 라디오 버튼을 찾을 수 없는 경우: 빈 리스트 반환
    - 개별 옵션에서 오류가 발생하는 경우: 해당 옵션만 제외하고 계속 진행
    """
    try:
        log.info("[extract_all_sort_options] Extracting all sort options")
        
        # 모든 라디오 버튼 찾기
        radio_buttons = await page.query_selector_all('.radio-v3__input')
        
        if not radio_buttons:
            log.warning("[extract_all_sort_options] No radio buttons found")
            return []
        
        options = []
        for idx, radio in enumerate(radio_buttons):
            try:
                # data-sort-text 속성값 추출
                sort_text = await radio.get_attribute('data-sort-text')
                
                # checked 상태 확인
                is_checked = await radio.get_attribute('checked') is not None
                
                if sort_text:
                    option_info = {
                        "text": sort_text,
                        "checked": str(is_checked).lower()
                    }
                    options.append(option_info)
                    
                    log.info(f"[extract_all_sort_options] Option {idx + 1}: '{sort_text}' (checked: {is_checked})")
                    
            except Exception as e:
                log.warning(f"[extract_all_sort_options] Error processing option {idx + 1}: {e}")
                continue
        
        log.info(f"[extract_all_sort_options] Extracted {len(options)} sort options")
        return options
        
    except Exception as e:
        log.error(f"[extract_all_sort_options] Error extracting all sort options: {e}")
        return []


async def validate_sort(page: Page) -> Dict[str, any]:
    """
    정렬 기능의 일치성을 검증합니다.
    
    동작 방식:
    - 정렬 버튼의 현재 표시 텍스트 추출
    - 정렬 드롭다운의 기본 정렬값 추출
    - 선택된 정렬 옵션의 텍스트 추출
    - 세 값 간의 일치성 검증
    - 검증 결과와 상세 정보를 반환
    
    파라미터:
        page (Page): Playwright 페이지 객체
        
    반환값:
        Dict[str, any]: 검증 결과
        {
            "validate": bool,
            "description": str,
            "details": {
                "opener_text": str,
                "default_sort": str,
                "selected_text": str,
                "all_options": List[Dict],
                "matches": {
                    "opener_vs_default": bool,
                    "opener_vs_selected": bool,
                    "default_vs_selected": bool
                }
            }
        }
        
    예외 처리:
    - 각 단계에서 오류가 발생하는 경우: 해당 값은 None으로 설정하고 검증 계속
    - 모든 값이 None인 경우: 검증 실패로 처리
    """
    try:
        log.info("[validate_sort] Starting sort consistency validation")
        
        # 1. 정렬 버튼의 현재 표시 텍스트 추출
        opener_text = await extract_sort_opener_text(page)
        
        # 2. 정렬 드롭다운 열기 및 기본 정렬값 추출
        default_sort = await extract_sort_list_default(page)
        
        # 3. 선택된 정렬 옵션의 텍스트 추출
        selected_text = await extract_selected_sort_text(page)
        
        # 4. 모든 정렬 옵션 추출 (선택사항)
        all_options = await extract_all_sort_options(page)
        
        # 5. 일치성 검증
        opener_vs_default = opener_text == default_sort if opener_text and default_sort else False
        opener_vs_selected = opener_text == selected_text if opener_text and selected_text else False
        default_vs_selected = default_sort == selected_text if default_sort and selected_text else False
        
        # 6. 전체 검증 결과 결정
        # 모든 값이 일치해야 검증 통과
        validate_result = opener_vs_default and opener_vs_selected and default_vs_selected
        
        # 7. 검증 실패 시 상세 설명 생성
        if not validate_result:
            mismatch_details = []
            if not opener_vs_default:
                mismatch_details.append(f"opener_text('{opener_text}') != default_sort('{default_sort}')")
            if not opener_vs_selected:
                mismatch_details.append(f"opener_text('{opener_text}') != selected_text('{selected_text}')")
            if not default_vs_selected:
                mismatch_details.append(f"default_sort('{default_sort}') != selected_text('{selected_text}')")
            
            description = "; ".join(mismatch_details)
        else:
            description = ""
        
        result = {
            "validate": validate_result,
            "description": description,
            "details": {
                "opener_text": opener_text,
                "default_sort": default_sort,
                "selected_text": selected_text,
                "all_options": all_options,
                "matches": {
                    "opener_vs_default": opener_vs_default,
                    "opener_vs_selected": opener_vs_selected,
                    "default_vs_selected": default_vs_selected
                }
            }
        }
        
        log.info(f"[validate_sort] Validation result: {validate_result}")
        if description:
            log.info(f"[validate_sort] Mismatch details: {description}")
        
        return result
        
    except Exception as e:
        log.error(f"[validate_sort] Error during sort consistency validation: {e}")
        
        # 오류 발생 시 기본 결과 반환
        return {
            "validate": False,
            "description": f"Validation error: {str(e)}",
            "details": {
                "opener_text": None,
                "default_sort": None,
                "selected_text": None,
                "all_options": [],
                "matches": {
                    "opener_vs_default": False,
                    "opener_vs_selected": False,
                    "default_vs_selected": False
                }
            }
        }
