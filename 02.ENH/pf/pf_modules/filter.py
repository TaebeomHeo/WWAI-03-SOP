"""
pf_modules/filter.py - 필터 추출 및 검증 모듈

Samsung Product Family 페이지의 필터 시스템을 종합적으로 분석하고 검증하는
핵심 모듈입니다. 사용자가 제품을 필터링할 때의 기능적 정확성을 보장합니다.

주요 검증 대상:
- 필터 구조 분석 및 추출
- 개별 필터 옵션의 기능성 검증
- 다중 필터 조합의 정확성 검증
- 랜덤 필터 조합을 통한 스트레스 테스트

핵심 기능:
- 필터 구조 추출: 페이지의 모든 필터 카테고리와 옵션을 체계적으로 분석
- 개별 필터 테스트: 각 필터 옵션의 단독 적용 시 정확성 검증
- 조합 필터 테스트: 여러 필터를 동시에 적용했을 때의 결과 검증
- 랜덤 조합 테스트: 예측 불가능한 필터 조합으로 시스템 안정성 검증
- 필터 상태 관리: 체크/언체크 상태의 정확한 추적 및 검증

검증 프로세스:
1. 페이지 로드 후 필터 컨테이너 구조 분석
2. 각 필터 카테고리별 옵션 목록 추출
3. 개별 필터 옵션에 대한 단독 테스트 수행
4. 랜덤 필터 조합 생성 및 적용
5. 필터 적용 후 결과 페이지의 정확성 검증
"""

import asyncio
import random
from typing import Dict, List, Any, Optional
from playwright.async_api import Page, ElementHandle
from utility.orangelogger import log
from utility.aem import scroll_for_lazyload
from pf_modules.sort import validate_sort


########################################################################################
# 필터 정보 추출 함수
########################################################################################
async def _extract_filter_info(
    filter_item: ElementHandle, filter_index: int, page: Page
) -> Optional[dict]:
    """
    개별 필터 아이템에서 필터 정보를 추출합니다.

    동작 방식:
    - 필터 타입을 CSS 클래스와 구조로 판단 (단일 체크박스 vs 다중 체크박스)
    - 단일 체크박스 필터: 체크박스에서 이름과 정보를 한 번에 추출
    - 다중 체크박스 필터: CTA에서 이름 추출, 펼친 후 체크박스 추출

    파라미터:
        filter_item: 필터 아이템 ElementHandle
        filter_index (int): 필터 인덱스
        page: Playwright Page 객체

    반환값:
        dict: 필터 정보
    """
    try:
        # 필터 타입을 CSS 클래스와 구조로 판단
        class_list = await filter_item.get_attribute("class")
        has_menu_class = class_list and "pd21-filter__selector-item--menu" in class_list
        has_cta_button = await filter_item.query_selector(
            ".pd21-filter__selector-item-cta"
        )

        if has_menu_class and has_cta_button:
            # 다중 체크박스 필터: CTA에서 이름 추출, 펼친 후 체크박스 추출
            return await _extract_multi_checkbox_filter(filter_item, filter_index, page)
        else:
            # 단일 체크박스 필터: 체크박스에서 이름과 정보를 한 번에 추출
            return await _extract_single_checkbox_filter(filter_item, filter_index)

    except Exception as e:
        log.error(
            f"[_extract_filter_info] Error extracting filter info for index {filter_index}: {e}"
        )
        return None


async def _extract_single_checkbox_filter(
    filter_item: ElementHandle, filter_index: int
) -> Optional[dict]:
    """
    단일 체크박스 필터 정보를 추출합니다.

    동작 방식:
    - 체크박스 요소에서 직접 필터 이름과 정보를 추출
    - disabled 상태 확인하여 유효한 체크박스만 포함
    - 단일 체크박스이므로 펼치기 작업 불필요

    파라미터:
        filter_item: 필터 아이템 ElementHandle
        filter_index (int): 필터 인덱스

    반환값:
        dict: 필터 정보 (name, index, checkboxes, filter_type)

    예외 처리:
    - 체크박스 요소를 찾을 수 없는 경우 None 반환
    - 라벨 텍스트를 찾을 수 없는 경우 None 반환
    """
    try:
        # 체크박스 요소 조회
        checkbox_element = await filter_item.query_selector(".checkbox-v3")
        if not checkbox_element:
            log.warning(
                f"[_extract_single_checkbox_filter] Could not find checkbox element for filter at index {filter_index}"
            )
            return None

        # 체크박스에서 필터 이름과 an-la 속성 추출
        label_text = await checkbox_element.query_selector(".checkbox-v3__label-text")
        if not label_text:
            log.warning(
                f"[_extract_single_checkbox_filter] Could not find label text for filter at index {filter_index}"
            )
            return None

        filter_name = await label_text.inner_text()
        filter_name = filter_name.strip()

        # an-la 속성 추출 (단일 체크박스: filter:단일필터:단일필터)
        # input 요소에서 an-la 속성 찾기
        input_element = await checkbox_element.query_selector(".checkbox-v3__input")
        if not input_element:
            log.warning(
                f"[_extract_single_checkbox_filter] Could not find input element for filter '{filter_name}' at index {filter_index}"
            )
            return None

        filter_an_la = await input_element.get_attribute("an-la")
        if not filter_an_la:
            log.warning(
                f"[_extract_single_checkbox_filter] Could not find an-la attribute in input element for filter '{filter_name}' at index {filter_index}"
            )
            return None

        log.info(
            f"[_extract_single_checkbox_filter] Successfully extracted filter: '{filter_name}' (an-la: '{filter_an_la}') at index {filter_index}"
        )

        # disabled 체크박스 확인
        input_element = await checkbox_element.query_selector(".checkbox-v3__input")
        is_disabled = (
            input_element and await input_element.get_attribute("disabled") is not None
        )

        checkboxes = []
        if not is_disabled:
            checkboxes.append({"text": filter_name, "an_la": filter_an_la, "index": 0})

        log.info(
            f"[_extract_single_checkbox_filter] Extracted {len(checkboxes)} valid checkboxes for filter '{filter_name}'"
        )

        return {
            "name": filter_name,
            "an_la": filter_an_la,
            "index": filter_index,
            "checkboxes": checkboxes,
            "filter_type": "single_checkbox",
        }

    except Exception as e:
        log.error(
            f"[_extract_single_checkbox_filter] Error extracting single checkbox filter info for index {filter_index}: {e}"
        )
        return None


async def _extract_multi_checkbox_filter(
    filter_item: ElementHandle, filter_index: int, page: Page
) -> Optional[dict]:
    """
    다중 체크박스 필터 정보를 추출합니다.

    동작 방식:
    - CTA 버튼에서 필터 이름 추출
    - 필터를 펼친 후 모든 체크박스 정보 추출
    - disabled 체크박스는 제외
    - 필터 접기 작업 수행

    파라미터:
        filter_item: 필터 아이템 ElementHandle
        filter_index (int): 필터 인덱스
        page: Playwright Page 객체

    반환값:
        dict: 필터 정보 (name, index, checkboxes, filter_type)

    예외 처리:
    - CTA 버튼을 찾을 수 없는 경우 None 반환
    - 필터 펼치기 실패 시 None 반환
    - 체크박스 추출 실패 시 빈 리스트로 처리
    """
    try:
        # CTA 버튼에서 필터 이름과 an-la 속성 추출
        cta_button = await filter_item.query_selector(".pd21-filter__selector-item-cta")
        if not cta_button:
            log.warning(
                f"[_extract_multi_checkbox_filter] Could not find CTA button for filter at index {filter_index}"
            )
            return None

        filter_name = await cta_button.inner_text()
        filter_name = filter_name.strip()

        # an-la 속성 추출 (다중 체크박스: filter:필터)
        filter_an_la = await cta_button.get_attribute("an-la")
        if not filter_an_la:
            log.warning(
                f"[_extract_multi_checkbox_filter] Could not find an-la attribute for filter '{filter_name}' at index {filter_index}"
            )
            return None

        log.info(
            f"[_extract_multi_checkbox_filter] Found multi-checkbox filter: '{filter_name}' (an-la: '{filter_an_la}') at index {filter_index}"
        )

        # 필터 펼치기 전에 스크롤을 최상단으로 이동
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)  # 스크롤 완료 대기

        # CTA 버튼이 화면에 보이도록 스크롤
        await cta_button.scroll_into_view_if_needed()
        await page.wait_for_timeout(300)  # 스크롤 안정화 대기

        # 필터 펼치기
        await cta_button.click()
        await page.wait_for_timeout(1000)  # 펼치기 완료 대기

        # 펼쳐진 필터에서 체크박스 정보 추출
        checkboxes = []
        checkbox_elements = await filter_item.query_selector_all(".checkbox-v3")

        for i, checkbox in enumerate(checkbox_elements):
            try:
                # 체크박스 텍스트 추출
                label_text = await checkbox.query_selector(".checkbox-v3__label-text")
                if not label_text:
                    continue

                text = await label_text.inner_text()
                text = text.strip()

                if not text:  # 빈 텍스트는 건너뛰기
                    continue

                # an-la 속성 추출 (다중 체크박스: filter:필터:체크박스)
                # input 요소에서 an-la 속성 찾기
                input_element = await checkbox.query_selector(".checkbox-v3__input")
                if not input_element:
                    log.warning(
                        f"[_extract_multi_checkbox_filter] Could not find input element for checkbox '{text}' in filter '{filter_name}'"
                    )
                    continue

                an_la = await input_element.get_attribute("an-la")
                if not an_la:
                    log.warning(
                        f"[_extract_multi_checkbox_filter] Could not find an-la attribute in input element for checkbox '{text}' in filter '{filter_name}'"
                    )
                    continue

                log.info(
                    f"[_extract_multi_checkbox_filter] Successfully extracted checkbox: '{text}' (an-la: '{an_la}')"
                )

                # disabled 체크박스 확인
                input_element = await checkbox.query_selector(".checkbox-v3__input")
                if (
                    input_element
                    and await input_element.get_attribute("disabled") is not None
                ):
                    continue

                checkboxes.append({"text": text, "an_la": an_la, "index": i})

            except Exception as e:
                log.warning(
                    f"[_extract_multi_checkbox_filter] Error extracting checkbox {i} for filter '{filter_name}': {e}"
                )
                continue

        # 필터 접기
        try:
            # 필터 접기 전에 스크롤을 최상단으로 이동
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(300)  # 스크롤 완료 대기

            close_button = await filter_item.query_selector(
                ".pd21-filter__selector-item-cta"
            )
            if close_button:
                # 버튼이 화면에 보이도록 스크롤
                await close_button.scroll_into_view_if_needed()
                await page.wait_for_timeout(200)  # 스크롤 안정화 대기

                await close_button.click()
                await page.wait_for_timeout(500)  # 접기 완료 대기
        except Exception as e:
            log.warning(
                f"[_extract_multi_checkbox_filter] Error closing filter '{filter_name}': {e}"
            )

        log.info(
            f"[_extract_multi_checkbox_filter] Extracted {len(checkboxes)} valid checkboxes for filter '{filter_name}'"
        )

        return {
            "name": filter_name,
            "an_la": filter_an_la,
            "index": filter_index,
            "checkboxes": checkboxes,
            "filter_type": "multi_checkbox",
        }

    except Exception as e:
        log.error(
            f"[_extract_multi_checkbox_filter] Error extracting multi-checkbox filter info for index {filter_index}: {e}"
        )
        return None


async def _ensure_filter_area_visible(page: Page) -> bool:
    """
    필터 영역이 숨겨져 있는지 확인하고 필요시 복구합니다.

    동작 방식:
    - 필터 컨테이너의 클래스에서 pd21-filter--hide 확인
    - 숨겨져 있으면 최상단으로 스크롤하여 복구 시도
    - 복구 성공 여부를 반환

    파라미터:
        page (Page): Playwright Page 객체

    반환값:
        bool: 필터 영역이 보이는 상태이면 True

    예외 처리:
    - 필터 컨테이너를 찾을 수 없는 경우: True 반환 (기본값)
    - 복구 실패: False 반환
    """
    try:
        filter_container = await page.query_selector(".pd21-filter")
        if not filter_container:
            return True  # 필터 컨테이너가 없으면 기본적으로 보이는 것으로 간주

        # 필터 영역이 숨겨져 있는지 확인
        class_list = await filter_container.get_attribute("class")
        if class_list and "pd21-filter--hide" in class_list:
            log.info(
                "[_ensure_filter_area_visible] Filter area is hidden, attempting to show it"
            )

            # 필터 영역을 다시 보이게 하기 위해 스크롤
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(500)

            # 필터 영역이 다시 보이는지 확인
            updated_class_list = await filter_container.get_attribute("class")
            if updated_class_list and "pd21-filter--hide" not in updated_class_list:
                log.info("[_ensure_filter_area_visible] Filter area is now visible")
                return True
            else:
                log.warning(
                    "[_ensure_filter_area_visible] Filter area is still hidden after scroll"
                )
                return False

        return True  # 이미 보이는 상태

    except Exception as e:
        log.error(
            f"[_ensure_filter_area_visible] Error ensuring filter area visibility: {e}"
        )
        return False


########################################################################################
# 필터 조합 생성 함수
########################################################################################
def _generate_individual_test_combinations(filter_info: dict) -> List[List[dict]]:
    """
    개별 테스트용 조합을 생성합니다.

    동작 방식:
    - 필터의 각 체크박스를 개별 테스트 조합으로 생성
    - 각 체크박스에 필터 이름과 타입 정보 추가
    - 모든 체크박스가 별도의 조합으로 생성됨

    파라미터:
        filter_info (dict): 필터 정보 (name, checkboxes, filter_type 포함)

    반환값:
        List[List[dict]]: 개별 테스트 조합 리스트

    예외 처리:
    - checkboxes가 비어있는 경우 빈 리스트 반환
    - filter_info가 None인 경우 빈 리스트 반환
    """
    combinations = []
    for checkbox in filter_info["checkboxes"]:
        checkbox_with_filter = {
            **checkbox,
            "filter_name": filter_info["name"],
            "filter_an_la": filter_info.get("an_la"),
            "filter_type": filter_info.get("filter_type", "unknown"),
        }
        combinations.append([checkbox_with_filter])
    return combinations


def _generate_random_combinations(
    random_filters: List[dict], max_combinations: int = 3
) -> List[List[dict]]:
    """
    랜덤 체크박스 조합을 생성합니다 (체크박스 기준 비복원 방식).

    규칙:
    - 1개 또는 2개 체크박스 조합만 생성
    - 2개 체크박스인 경우 서로 다른 필터에서 선택
    - 체크박스 중복 방지 (이미 선택된 체크박스는 재선택 불가)
    - 가능한 조합이 max_combinations보다 적어도 그대로 사용
    - 1개, 2개 체크박스 조합의 비중이 랜덤하게 결정됨
    - 체크박스 기준으로 비복원 방식 적용

    동작 방식:
    1. 모든 체크박스를 수집하여 사용 가능한 체크박스 풀 생성
    2. 1개 또는 2개 체크박스 조합을 랜덤하게 생성
    3. 2개 조합 시 서로 다른 필터에서만 선택
    4. 이미 사용된 체크박스는 제외하고 선택
    5. 선택된 체크박스를 사용된 목록에 추가
    6. 최종 체크박스 조합 생성 (필터 정보 포함)

    파라미터:
        random_filters (List[dict]): 랜덤 조합용 필터 리스트
        max_combinations (int): 생성할 최대 조합 수 (기본값: 3)

    반환값:
        List[List[dict]]: 랜덤 조합 리스트
        - 각 조합은 List[dict] 형태 (체크박스 리스트)
        - 각 체크박스는 원본 정보 + "filter_name" 키 포함
        - 체크박스 기준으로 비복원 방식 적용

    예외 처리:
    - random_filters가 비어있는 경우 빈 리스트 반환
    - 체크박스가 없는 필터는 해당 조합에서 제외됨
    """
    combinations = []
    used_checkboxes = set()  # 사용된 체크박스 추적 (체크박스 기준 비복원)

    try:
        if len(random_filters) < 1:
            log.warning("[_generate_random_combinations] No random filters available")
            return combinations

        # 모든 체크박스를 수집하여 사용 가능한 체크박스 풀 생성
        all_checkboxes = []
        for filter_info in random_filters:
            filter_checkboxes = filter_info.get("checkboxes", [])
            for checkbox in filter_checkboxes:
                checkbox_with_filter = {
                    **checkbox,
                    "filter_name": filter_info.get('name', ''),
                    "filter_an_la": filter_info.get('an_la'),  # an-la 속성 추가
                    "filter_type": filter_info.get('filter_type', 'unknown')
                }
                all_checkboxes.append(checkbox_with_filter)

        if not all_checkboxes:
            log.warning("[_generate_random_combinations] No checkboxes available")
            return combinations

        log.info(
            f"[_generate_random_combinations] Total available checkboxes: {len(all_checkboxes)}"
        )

        # 충분한 조합을 생성하기 위해 더 많은 시도
        max_attempts = max_combinations * 3  # 충분한 시도 횟수

        for attempt in range(max_attempts):
            # 충분한 조합을 찾았으면 중단
            if len(combinations) >= max_combinations:
                break

            # 사용 가능한 체크박스만 필터링 (비복원 방식)
            available_checkboxes = []
            for checkbox in all_checkboxes:
                checkbox_key = f"{checkbox['filter_name']}:{checkbox['text']}"
                if checkbox_key not in used_checkboxes:
                    available_checkboxes.append(checkbox)

            if not available_checkboxes:
                log.info("[_generate_random_combinations] No more available checkboxes")
                break

            # 1개, 2개 체크박스 조합 랜덤 선택
            max_possible_size = min(2, len(available_checkboxes))
            combination_size = random.randint(1, max_possible_size)

            if combination_size == 1:
                # 1개 체크박스 조합
                selected_checkbox = random.choice(available_checkboxes)
                checkbox_combination = [selected_checkbox]
            else:
                # 2개 체크박스 조합 (서로 다른 필터에서 선택)
                # 서로 다른 필터의 체크박스만 선택 가능하도록 필터링
                different_filter_checkboxes = []
                used_filters_in_combination = set()

                for checkbox in available_checkboxes:
                    # 이미 사용된 필터가 아닌 경우만 추가
                    if checkbox["filter_name"] not in used_filters_in_combination:
                        different_filter_checkboxes.append(checkbox)
                        used_filters_in_combination.add(checkbox["filter_name"])

                if len(different_filter_checkboxes) >= 2:
                    # 2개 체크박스 랜덤 선택 (서로 다른 필터에서)
                    selected_checkboxes = random.sample(different_filter_checkboxes, 2)
                    checkbox_combination = selected_checkboxes
                else:
                    # 다른 필터의 체크박스가 부족한 경우 1개만 선택
                    selected_checkbox = random.choice(available_checkboxes)
                    checkbox_combination = [selected_checkbox]

            # 선택된 체크박스들을 사용된 목록에 추가
            for checkbox in checkbox_combination:
                checkbox_key = f"{checkbox['filter_name']}:{checkbox['text']}"
                used_checkboxes.add(checkbox_key)

            # 조합 추가
            combinations.append(checkbox_combination)
            combination_info = [
                f"{cb['filter_name']}:{cb['text']}" for cb in checkbox_combination
            ]
            log.info(
                f"[_generate_random_combinations] Added combination {len(combinations)}: {combination_info}"
            )

        log.info(
            f"[_generate_random_combinations] Generated {len(combinations)} unique combinations (target: {max_combinations})"
        )

    except Exception as e:
        log.error(
            f"[_generate_random_combinations] Error generating random combinations: {e}"
        )

    return combinations


async def _generate_all_combinations(filter_structure: dict) -> List[List[dict]]:
    """
    모든 테스트 조합을 생성합니다.

    동작 방식:
    1. individual_test_filters의 각 필터를 개별 테스트 (두 번째 필터, size 필터)
       - 각 필터의 모든 체크박스를 개별 조합으로 생성
    2. random_combination_filters로 랜덤 조합 생성
       - 최대 3개 조합 생성 (가능한 조합이 3개 미만이면 그대로 사용)
    3. 모든 조합을 하나의 리스트로 통합
    4. disabled 체크박스는 이미 추출 시점에서 제외됨

    파라미터:
        filter_structure (dict): 추출된 필터 구조
            - individual_test_filters: 개별 테스트용 필터 리스트
            - random_combination_filters: 랜덤 조합용 필터 리스트

    반환값:
        List[List[dict]]: 모든 테스트 조합 리스트
        - 각 조합은 List[dict] 형태 (체크박스 리스트)
        - 개별 테스트 조합 + 랜덤 조합이 순서대로 포함됨

    예외 처리:
    - 필터가 없는 경우 빈 리스트 반환
    - 체크박스가 없는 필터는 해당 조합에서 제외됨
    """
    all_combinations = []

    # 1. 개별 테스트 필터들 처리 (두 번째 필터, size 필터)
    individual_filters = filter_structure.get("individual_test_filters", [])
    if individual_filters:
        log.info(
            f"[_generate_all_combinations] Processing {len(individual_filters)} individual test filters"
        )

        for filter_info in individual_filters:
            if filter_info["checkboxes"]:
                combinations = _generate_individual_test_combinations(filter_info)
                all_combinations.extend(combinations)
                log.info(
                    f"[_generate_all_combinations] Added {len(combinations)} individual tests for '{filter_info['name']}'"
                )
            else:
                log.warning(
                    f"[_generate_all_combinations] Filter '{filter_info['name']}' has no checkboxes, skipping"
                )
    else:
        log.info("[_generate_all_combinations] No individual test filters found")

    # 2. 랜덤 조합 필터들 처리
    random_filters = filter_structure.get("random_combination_filters", [])
    if random_filters:
        log.info(
            f"[_generate_all_combinations] Processing {len(random_filters)} random combination filters"
        )

        random_combinations = _generate_random_combinations(
            random_filters, max_combinations=3
        )
        all_combinations.extend(random_combinations)
        log.info(
            f"[_generate_all_combinations] Added {len(random_combinations)} random combinations"
        )
    else:
        log.info("[_generate_all_combinations] No random combination filters found")

    log.info(
        f"[_generate_all_combinations] Generated {len(all_combinations)} total test combinations"
    )
    return all_combinations


########################################################################################
# 필터 조합 테스트 실행 함수
########################################################################################
async def _verify_filter_applied(page: Page, test_combination: List[dict]) -> dict:
    """
    선택된 체크박스 텍스트가 필터 적용 목록에 표시되는지 확인합니다.

    동작 방식:
    - 선택된 필터가 나타날 때까지 대기
    - 모든 체크박스 텍스트가 선택된 필터 목록에 포함되어 있는지 확인
    - 검증 결과를 딕셔너리로 반환

    파라미터:
        page (Page): Playwright Page 객체
        test_combination (List[dict]): 테스트한 체크박스 조합

    반환값:
        dict: 텍스트 일치 검증 결과
        {
            "validate": bool,  # 모든 텍스트가 일치하면 True
            "description": str  # 검증 결과 설명
        }

    예외 처리:
    - 선택된 필터가 나타나지 않는 경우: validate=False로 반환
    - 텍스트 추출 실패: validate=False로 반환
    """
    try:
        # 필터 적용 후 페이지 업데이트 대기
        await page.wait_for_timeout(3000)

        # 선택된 필터 목록에서 텍스트 추출 (div.pd21-filter__selected-list 내의 button 태그들)
        selected_items = await page.query_selector_all(
            "div.pd21-filter__selected-list button.pd21-filter__selected-item"
        )
        if not selected_items:
            return {
                "validate": False,
                "description": "Text match FAILED: No selected filter items found",
            }

        # 텍스트 추출 및 정규화 (한 번에 처리)
        selected_texts = set()
        for item in selected_items:
            text = await item.inner_text()
            if text:
                selected_texts.add(text.strip())

        # selected text가 없으면 에러로 처리
        if not selected_texts:
            return {
                "validate": False,
                "description": "Text match FAILED: No selected filter text found",
                "selected_texts": "No text found",
            }

        # 예상 텍스트 준비 (한 번에 처리)
        expected_texts = [checkbox["text"] for checkbox in test_combination]
        expected_set = set(expected_texts)
        total_expected = len(expected_texts)

        # 효율적인 비교 (집합 연산 사용)
        matched_texts = expected_set & selected_texts
        matched_count = len(matched_texts)

        # 검증 결과 생성
        if matched_count == total_expected:
            validate_result = True
            description = f"Text match PASSED: All {total_expected} expected texts found in selected filters"
        else:
            validate_result = False
            missing_texts = list(expected_set - selected_texts)
            description = f"Text match FAILED: Found {matched_count}/{total_expected} texts. Missing: {missing_texts}"
            log.warning(f"[_verify_filter_applied] {description}")

        # 실제 선택된 필터 텍스트만 반환 (selected 정보용)
        selected_texts_list = list(selected_texts)
        selected_info = (
            ", ".join(selected_texts_list)
            if selected_texts_list
            else "No selected filters found"
        )

        return {
            "validate": validate_result,
            "description": description,
            "selected_texts": selected_info,
        }

    except Exception as e:
        log.error(f"[_verify_filter_applied] Error verifying filter application: {e}")
        return {"validate": False, "description": f"Text match failed: {str(e)}"}


async def _check_visible_products_without_scroll(page: Page) -> dict:
    """
    현재 페이지에 로드된 제품들의 구매 가능성을 검증합니다.

    동작 방식:
    - No result 상태 확인: pd21-product-finder__no-result 클래스가 있으면 정상으로 처리
    - AEM lazyload 스크롤 후 모든 제품이 로드된 상태에서 제품 카드 확인
    - 제품 카드가 4개 이상이면 상위 4개만, 4개 미만이면 전체를 대상으로 구매 가능 검증
    - pf.py의 validate_purchase_capability 함수를 활용하여 실제 구매 가능성 검증

    파라미터:
        page: Playwright Page 객체

    반환값:
        dict: 구매 가능성 검증 결과
        {
            "validate": bool,  # 구매 가능한 제품이 있거나 no result 상태면 True
            "description": str  # "Sorry, no results were found." 또는 구매 검증 결과
        }
    """
    try:
        # 페이지 상태 확인
        current_url = page.url
        log.info(f"[Purchase Validation] Current page URL: {current_url}")

        # 제품 카드 로딩 완료 대기 (Playwright 내장 기능 활용)
        product_cards_found = False
        try:
            # 제품 카드가 나타날 때까지 대기 (최대 5초) - 일반 선택자 사용
            await page.wait_for_selector("div.pd21-product-card__item", timeout=5000)
            await page.wait_for_timeout(1000)  # 추가 안정화 대기
            product_cards_found = True
            log.info(f"[Purchase Validation] Product cards found and page stabilized")
        except Exception as e:
            log.warning(
                f"[Purchase Validation] No product cards found within timeout: {e}"
            )
            # 제품이 없는 경우, no_result 요소 확인

        # 제품 카드가 없는 경우에만 No result 상태 확인
        if not product_cards_found:
            no_result_element = await page.query_selector(
                ".pd21-product-finder__no-result"
            )
            if no_result_element:
                log.info(
                    f"[Purchase Validation] No results found - pd21-product-finder__no-result element detected"
                )
                return {
                    "validate": True,  # 정상적인 상태로 처리
                    "description": "Sorry, no results were found.",
                }
            else:
                log.warning(
                    f"[Purchase Validation] No product cards and no 'no-result' element found"
                )
                # 계속 진행하여 빈 목록 반환

        # 일반 셀렉터로 모든 상품 카드 찾기 (배너 포함)
        all_products = await page.query_selector_all("div.pd21-product-card__item")
        log.info(
            f"[Purchase Validation] Found {len(all_products)} total product card candidates with general selector"
        )

        # 디버깅: 각 상품 카드의 정보 출력 및 배너 제외
        valid_products = []
        banner_count = 0

        for i, product in enumerate(all_products):
            try:
                productidx = await product.get_attribute("data-productidx")
                itemidx = await product.get_attribute("data-item-idx")
                class_attr = await product.get_attribute("class")
                is_visible = await product.is_visible()
                log.debug(
                    f"[Purchase Validation] Product {i}: data-productidx='{productidx}', data-item-idx='{itemidx}', class='{class_attr}', visible={is_visible}"
                )

                # 배너 제품 제외
                if is_visible and "pd21-product-card__banner" not in (class_attr or ""):
                    valid_products.append(product)
                    log.debug(
                        f"[Purchase Validation] Valid product found: {class_attr}"
                    )
                elif "pd21-product-card__banner" in (class_attr or ""):
                    banner_count += 1
                    log.debug(
                        f"[Purchase Validation] Excluded banner product: {class_attr}"
                    )
            except Exception as e:
                log.debug(f"[Purchase Validation] Error getting product {i} info: {e}")

        visible_count = len(valid_products)
        log.info(
            f"[Purchase Validation] Valid products: {visible_count}, Banner products: {banner_count}"
        )

        # 제품이 없는 경우
        if visible_count == 0:
            return {
                "validate": True,
                "description": "Purchase validation PASSED: No products found (filter working correctly - no matching products)",
            }

        # 검증할 제품 수 결정 (4개 이상이면 4개만, 4개 미만이면 전체)
        products_to_validate = (
            valid_products[:4] if visible_count >= 4 else valid_products
        )
        validation_count = len(products_to_validate)

        # 제품 정보 추출 (pf.py의 extract_product 함수 활용)
        from pf import extract_product

        # 현재 페이지에서 제품 정보 추출 (스크롤 없이)
        all_products = await extract_product(page)

        # 추출된 제품 중 검증 대상 제품만 선택
        # valid_products의 순서와 extract_product의 결과 순서가 일치한다고 가정
        products_to_validate_info = (
            all_products[:validation_count]
            if len(all_products) >= validation_count
            else all_products
        )

        # 구매 가능성 검증 (pf_modules의 validate_purchase_capability 함수 활용)
        from pf_modules.purchase import validate_purchase_capability

        purchase_result = await validate_purchase_capability(products_to_validate_info, page)
        
        # 구매 불가능한 제품의 위치와 CTA 정보 구성
        unpurchasable_positions = []
        if "details" in purchase_result and "products" in purchase_result["details"]:
            total_products = purchase_result["details"].get("total_checked", 0)
            for idx, product in enumerate(purchase_result["details"]["products"], 1):
                purchasable = product.get("purchasable", False)
                if not purchasable:
                    cta_an_la = product.get("cta_an_la", "")
                    # CTA 값 처리: "pf product card:" 접두사가 있으면 제거, 없으면 그대로 표시
                    if cta_an_la.startswith("pf product card:"):
                        cta_display = cta_an_la.removeprefix("pf product card:")
                    else:
                        cta_display = cta_an_la if cta_an_la else "empty"
                    unpurchasable_positions.append(f"[{idx}/{total_products}]({cta_display})")
        
        # 구매 불가능한 제품이 있으면 해당 위치들만 표시, 없으면 성공 메시지
        if unpurchasable_positions:
            purchase_desc = ", ".join(unpurchasable_positions)
        else:
            purchase_desc = "All visible products are purchasable"

        return {"validate": purchase_result["validate"], "description": purchase_desc}

    except Exception as e:
        log.error(
            f"[_check_visible_products_without_scroll] Error checking purchase availability: {e}"
        )
        return {
            "validate": False,
            "description": f"Purchase validation failed: {str(e)}",
        }


async def _test_filter_combination(page: Page, test_combination: List[dict]) -> dict:
    """
    단일 테스트 조합을 실행합니다.

    동작 방식:
    1. 각 체크박스에 대해:
       - Energy Efficient 필터: 체크박스만 클릭
       - Menu 타입 필터: 필터 펼치기 + 체크박스 선택 → 필터 접기
    2. 페이지 로딩 대기
    3. 텍스트 일치 검증 (선택된 텍스트 vs 표시된 텍스트)
    4. 구매 가능 검증 (현재 화면에 보이는 상위 4개의 PICK 제품)
       - PICK 제품은 구현중이므로 클래스명 변경될 가능성이 있음

    파라미터:
        page (Page): Playwright Page 객체
        test_combination (List[dict]): 테스트할 체크박스 조합 (필터 정보 포함)

    반환값:
        dict: 테스트 결과
        {
            "text_match": bool,  # 텍스트 일치 결과
            "purchase_available": bool  # 구매 가능 결과
        }
    """
    try:
        # 조합 정보 상세 로그
        combo_info = []
        for cb in test_combination:
            combo_info.append(f"{cb['filter_name']}:{cb['text']} (type:{cb.get('filter_type', 'unknown')})")
        log.info(f"[_test_filter_combination] ========== START TEST COMBINATION ==========")
        log.info(f"[_test_filter_combination] Total checkboxes to click: {len(test_combination)}")
        log.info(f"[_test_filter_combination] Combination details: {combo_info}")
        
        # 1. 모든 체크박스 클릭 (필터 타입에 따라 다르게 처리)
        for idx, checkbox in enumerate(test_combination, 1):
            log.info(f"[_test_filter_combination] --- Processing checkbox {idx}/{len(test_combination)} ---")
            log.info(f"[_test_filter_combination] Filter: '{checkbox['filter_name']}', Checkbox: '{checkbox['text']}', Type: '{checkbox.get('filter_type')}'")
            
            try:
                # 필터 타입에 따라 다른 처리 방식 적용
                if checkbox.get('filter_type') == 'single_checkbox':
                    log.info(f"[_test_filter_combination] Single checkbox type - directly selecting checkbox")
                    # 단일 체크박스 필터: 체크박스 선택 + 대기
                    await _select_checkbox(page, checkbox)
                    log.info(f"[_test_filter_combination] Waiting 1s after single checkbox selection")
                    await page.wait_for_timeout(1000)  # 체크박스 클릭 후 대기
                    log.info(f"[_test_filter_combination] Single checkbox selection completed")
                else:
                    log.info(f"[_test_filter_combination] Multi checkbox type - expand -> select -> close")
                    # 다중 체크박스 필터: 펼치기 + 체크박스 선택 + 대기 + 접기
                    # an-la 속성을 우선 사용하고, 없으면 filter_name 사용
                    filter_identifier = checkbox.get('filter_an_la', checkbox['filter_name'])
                    log.info(f"[_test_filter_combination] Using filter identifier: '{filter_identifier}'")
                    
                    filter_item = await _expand_filter(page, filter_identifier)
                    if filter_item:
                        log.info(f"[_test_filter_combination] Filter expanded successfully")
                        await _select_checkbox(page, checkbox)
                        log.info(f"[_test_filter_combination] Checkbox selected successfully")
                        
                        # 체크박스 선택 후 대기
                        log.info(f"[_test_filter_combination] Waiting 1s after checkbox selection")
                        await page.wait_for_timeout(1000)

                        # 필터 닫기 시도 (실패 시 한 번 더 재시도)
                        log.info(f"[_test_filter_combination] Attempting to close filter")
                        close_success = await _close_filter(page, checkbox, filter_item)
                        if not close_success:
                            log.warning(
                                f"[_test_filter_combination] First close attempt failed for '{checkbox['filter_name']}', retrying..."
                            )
                            close_success = await _close_filter(
                                page, checkbox, filter_item
                            )
                            if not close_success:
                                log.error(f"[_test_filter_combination] Both close attempts failed for '{checkbox['filter_name']}', continuing...")
                        else:
                            log.info(f"[_test_filter_combination] Filter closed successfully")
                        
                        log.info(f"[_test_filter_combination] Waiting 1s after filter close")
                        await page.wait_for_timeout(1000)  # 필터 조작 후 1초 대기
                    else:
                        log.error(f"[_test_filter_combination] Failed to expand filter '{filter_identifier}'")
                        raise Exception(f"Failed to expand filter '{filter_identifier}'")
                
            except Exception as checkbox_error:
                log.error(
                    f"[_test_filter_combination] Failed to click checkbox '{checkbox['text']}' in filter '{checkbox['filter_name']}': {checkbox_error}"
                )
                # 체크박스 클릭 실패 시 테스트 중단하고 실패 결과 반환
                return {
                    "text_match": False,
                    "purchase_available": False,
                    "validate_desc": f"Checkbox click failed: {checkbox['text']} in {checkbox['filter_name']} - {str(checkbox_error)}",
                }
        
        log.info(f"[_test_filter_combination] ========== ALL CHECKBOXES CLICKED ==========")
        log.info(f"[_test_filter_combination] Successfully clicked all {len(test_combination)} checkboxes")
        
        # 2. 페이지 로딩 대기 (필터 적용 후 충분한 대기)
        log.info(f"[_test_filter_combination] Waiting 3s for filter application to complete")
        await page.wait_for_timeout(3000)  # 필터 적용 후 3초 대기
        log.info(f"[_test_filter_combination] Filter application wait completed")
        
        # 화면 상태 확인 (스크롤 전)
        scroll_pos_before_lazyload = await page.evaluate("window.pageYOffset")
        log.info(f"[_test_filter_combination] Screen position before lazyload scroll: {scroll_pos_before_lazyload}px")
        
        # 2.5. AEM lazyload 스크롤 적용 (필터 적용 후 모든 상품이 로드되도록)
        log.info(
            f"[_test_filter_combination] Applying AEM lazyload scroll after filter application"
        )
        try:
            await scroll_for_lazyload(page)
            log.info(f"[_test_filter_combination] AEM lazyload scroll completed successfully")
            
            # 스크롤 후 화면 상태 확인
            scroll_pos_after_lazyload = await page.evaluate("window.pageYOffset")
            log.info(f"[_test_filter_combination] Screen position after lazyload scroll: {scroll_pos_after_lazyload}px")
            
            # 스크롤 완료 후 DOM 안정화를 위한 추가 대기
            log.info(f"[_test_filter_combination] Waiting 1s for DOM stabilization")
            await page.wait_for_timeout(1000)
        except Exception as scroll_error:
            log.warning(
                f"[_test_filter_combination] AEM lazyload scroll failed: {scroll_error}"
            )
            # 스크롤 실패해도 테스트 계속 진행

        # 3. 텍스트 일치 검증
        log.info(f"[_test_filter_combination] Starting text match validation")
        text_match_result = await _verify_filter_applied(page, test_combination)
        log.info(f"[_test_filter_combination] Text match validation result: {text_match_result['validate']}")
        
        # 4. 구매 가능 검증 (lazyload 스크롤 후 모든 상품 확인)
        log.info(f"[_test_filter_combination] Starting purchase validation")
        purchase_available_result = await _check_visible_products_without_scroll(page)
        log.info(f"[_test_filter_combination] Purchase validation result: {purchase_available_result['validate']}")
        
        # 5. 가격 정보 확인 후 최상단으로 스크롤
        log.info(f"[_test_filter_combination] Scrolling back to top")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        
        scroll_pos_final = await page.evaluate("window.pageYOffset")
        log.info(f"[_test_filter_combination] Final screen position: {scroll_pos_final}px")
        
        # validate_desc 생성 (개별 필터 검증용)
        validate_desc = ""
        checkbox_items = [
            (checkbox["filter_name"], checkbox["text"]) for checkbox in test_combination
        ]
        if text_match_result["validate"] and purchase_available_result["validate"]:
            # 성공 시: ((필터:체크박스), (필터:체크박스)) 형태로 표시
            checkbox_info = ", ".join(
                [f"({filter_name}:{text})" for filter_name, text in checkbox_items]
            )
            validate_desc = f"({checkbox_info})"
        else:
            # 실패 시: filter와 selected 정보 표시
            checkbox_info = ", ".join(
                [f"({filter_name}:{text})" for filter_name, text in checkbox_items]
            )
            filter_info = f"filter: ({checkbox_info})"

            if not text_match_result["validate"]:
                selected_info = (
                    f"selected: {text_match_result.get('selected_texts', 'Unknown')}"
                )
                validate_desc = f"{filter_info} | {selected_info}"
            elif not purchase_available_result["validate"]:
                # 구매 가능성 검증 실패 시에도 선택된 필터 텍스트는 text_match_result에서 가져옴
                selected_info = (
                    f"selected: {text_match_result.get('selected_texts', 'Unknown')}"
                )
                purchase_info = f"purchase: {purchase_available_result.get('description', 'Unknown')}"
                validate_desc = f"{filter_info} | {selected_info} | {purchase_info}"

        # text 검증 결과 설명 생성
        text_validate_desc = ""
        checkbox_items = [
            (checkbox["filter_name"], checkbox["text"]) for checkbox in test_combination
        ]
        if not text_match_result["validate"]:
            # text_validate가 false일 경우: 에러 description 또는 ((필터:체크박스), (필터:체크박스)) | selected: 선택된텍스트
            error_desc = text_match_result.get("description", "")
            if (
                "No selected filter text found" in error_desc
                or "No selected filter items found" in error_desc
            ):
                # selected text가 없는 에러인 경우 에러 description 사용
                text_validate_desc = error_desc
            else:
                # 일반적인 텍스트 불일치인 경우: ((필터:체크박스), (필터:체크박스)) | selected: 선택된텍스트
                selected_texts = text_match_result.get("selected_texts", "Unknown")
                if isinstance(selected_texts, set):
                    selected_texts = ", ".join(sorted(selected_texts))
                checkbox_info = ", ".join(
                    [f"({filter_name}:{text})" for filter_name, text in checkbox_items]
                )
                text_validate_desc = f"({checkbox_info}) | selected: {selected_texts}"
        else:
            # text_validate가 true일 경우: ((필터:체크박스), (필터:체크박스))
            checkbox_info = ", ".join(
                [f"({filter_name}:{text})" for filter_name, text in checkbox_items]
            )
            text_validate_desc = f"({checkbox_info})"

        # 구매 검증 결과 설명 생성
        purchase_validate_desc = ""
        if not purchase_available_result["validate"]:
            # purchase_validate가 false일 경우: Failed combinations 정보 포함
            # 필터 조합 정보 구성: [필터명: 값 | 필터명: 값]
            filter_combination_parts = []
            for checkbox in test_combination:
                filter_combination_parts.append(
                    f"{checkbox['filter_name']}: {checkbox['text']}"
                )
            filter_combination_str = " | ".join(filter_combination_parts)
            
            # 구매 불가능한 상품의 위치 및 CTA 정보
            purchase_info = purchase_available_result.get("description", "Purchase validation failed")
            
            # 최종 형식: Failed combinations: [필터조합], Purchase: [위치](CTA값), ...
            purchase_validate_desc = f"Failed combinations: [{filter_combination_str}], Purchase: {purchase_info}"
        else:
            # purchase_validate가 true일 경우 성공 메시지
            purchase_validate_desc = purchase_available_result.get(
                "description", "Purchase validation passed"
            )

        result = {
            "text_validate": text_match_result["validate"],
            "text_validate_desc": text_validate_desc,
            "purchase_validate": purchase_available_result["validate"],
            "purchase_validate_desc": purchase_validate_desc,
        }

        # 분리된 검증 결과 로그 출력
        log.info(
            f"[_test_filter_combination] Text validation: {text_match_result['validate']} - {text_validate_desc}"
        )
        log.info(
            f"[_test_filter_combination] Purchase validation: {purchase_available_result['validate']} - {purchase_validate_desc}"
        )

        # 테스트 완료 후 필터 지우기
        log.info(f"[_test_filter_combination] Clearing filters after test completion")
        try:
            clear_success = await _clear_filters_and_wait(page)
            if not clear_success:
                log.warning(
                    f"[_test_filter_combination] Failed to clear filters after test"
                )
                # 필터 지우기 실패는 테스트 결과에 영향을 주지 않음
            else:
                log.info(f"[_test_filter_combination] Filters cleared successfully")
        except Exception as clear_error:
            log.error(
                f"[_test_filter_combination] Error clearing filters: {clear_error}"
            )

        return result

    except Exception as e:
        log.error(f"[_test_filter_combination] Error testing combination: {e}")

        # 에러 발생 시에도 필터 지우기 시도
        try:
            await _clear_filters_and_wait(page)
        except:
            pass

        return {
            "text_match": False,
            "purchase_available": False,
            "validate_desc": f"Test execution error: {str(e)}",
        }


########################################################################################
# 필터 헬퍼 함수
########################################################################################
async def _expand_filter(page: Page, filter_name: str) -> ElementHandle:
    """
    지정된 이름의 필터를 찾아서 펼칩니다.

    동작 방식:
    - 모든 필터 아이템을 순회하며 이름 매칭
    - 매칭되는 필터의 CTA 버튼을 클릭하여 펼치기
    - 펼쳐진 필터 아이템을 반환

    파라미터:
        page (Page): Playwright Page 객체
        filter_name (str): 펼칠 필터의 이름

    반환값:
        ElementHandle: 펼쳐진 필터 아이템 (닫기용으로 사용)

    예외 처리:
    - 필터를 찾지 못한 경우: None 반환
    - 펼치기 실패 시: None 반환
    """
    try:
        # filter_name에서 "filter:" 접두사 제거 (통일된 비교를 위해)
        filter_name_clean = filter_name.replace("filter:", "") if filter_name.startswith("filter:") else filter_name
        log.info(f"[_expand_filter] START - Looking for filter: '{filter_name_clean}'")
        
        # 스크롤 전 화면 상태 확인
        scroll_pos_before = await page.evaluate("window.pageYOffset")
        log.info(f"[_expand_filter] Screen scroll position before scroll: {scroll_pos_before}px")
        
        # 최상단으로 스크롤
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        
        # 스크롤 후 화면 상태 확인
        scroll_pos_after = await page.evaluate("window.pageYOffset")
        log.info(f"[_expand_filter] Screen scroll position after scroll to top: {scroll_pos_after}px")
        
        # 모든 필터 타입을 찾아서 펼치기
        filter_items = await page.query_selector_all(".pd21-filter__selector-item")
        log.debug(f"[_expand_filter] Found {len(filter_items)} filter items on page")

        available_filter_names = []
        available_filter_an_las = []
        for filter_item in filter_items:
            # 필터 이름과 an-la 속성 확인
            cta_button = await filter_item.query_selector(
                ".pd21-filter__selector-item-cta"
            )
            if cta_button:
                name_span = await cta_button.query_selector("span")
                if name_span:
                    name_text = await name_span.inner_text()
                    if name_text:
                        name_text = name_text.strip()
                        available_filter_names.append(name_text)

                        # an-la 속성 추출
                        an_la_attr = await cta_button.get_attribute("an-la")
                        if an_la_attr:
                            available_filter_an_las.append(an_la_attr)

                            # an-la 속성으로 필터 찾기 (우선순위)
                            # an-la 속성에서 "filter:" 접두사 제거 후 비교
                            an_la_clean = (
                                an_la_attr.replace("filter:", "")
                                if an_la_attr.startswith("filter:")
                                else an_la_attr
                            )
                            if an_la_clean.lower() == filter_name_clean.lower():
                                log.info(f"[_expand_filter] MATCHED filter by an-la: '{an_la_attr}' (looking for: '{filter_name_clean}')")
                                
                                # 필터가 이미 펼쳐진 상태인지 확인 (CSS 클래스로 확인)
                                filter_item_classes = await filter_item.get_attribute("class")
                                is_open = "pd21-filter__selector-item--open" in (filter_item_classes or "")
                                log.info(f"[_expand_filter] Filter state - is_open: {is_open}, classes: {filter_item_classes}")
                                
                                if is_open:
                                    log.info(f"[_expand_filter] Filter '{filter_name}' is already expanded - skipping click")
                                    return filter_item
                                
                                # 필터의 가시성 및 위치 확인
                                is_visible = await cta_button.is_visible()
                                bbox = await cta_button.bounding_box()
                                log.info(f"[_expand_filter] Filter button state - visible: {is_visible}, position: {bbox}")
                                
                                # 필터 펼치기
                                try:
                                    log.info(f"[_expand_filter] Attempting to click filter button for '{filter_name}'")
                                    await cta_button.click(timeout=5000)
                                    log.info(f"[_expand_filter] Click executed, waiting 1s for expansion")
                                    await page.wait_for_timeout(1000)  # 펼쳐지는 시간 대기
                                    
                                    # 펼침 후 상태 확인
                                    updated_classes = await filter_item.get_attribute("class")
                                    is_now_open = "pd21-filter__selector-item--open" in (updated_classes or "")
                                    log.info(f"[_expand_filter] After click - is_open: {is_now_open}, classes: {updated_classes}")
                                    
                                    log.info(f"[_expand_filter] Successfully expanded filter '{filter_name}'")
                                    return filter_item
                                except Exception as click_error:
                                    log.error(f"[_expand_filter] Failed to expand filter '{filter_name}': {click_error}")
                                    continue

                        # 텍스트로 필터 찾기 (fallback)
                        elif name_text.lower() == filter_name_clean.lower():
                            # 필터가 이미 펼쳐진 상태인지 확인 (CSS 클래스로 확인)
                            filter_item_classes = await filter_item.get_attribute(
                                "class"
                            )
                            is_open = "pd21-filter__selector-item--open" in (
                                filter_item_classes or ""
                            )

                            if is_open:
                                log.info(
                                    f"[_expand_filter] Filter '{filter_name}' is already expanded (text fallback)"
                                )
                                return filter_item

                            # 필터 펼치기
                            try:
                                await cta_button.click(timeout=5000)
                                await page.wait_for_timeout(1000)  # 펼쳐지는 시간 대기
                                log.info(
                                    f"[_expand_filter] Successfully expanded filter '{filter_name}' (text fallback)"
                                )
                                return filter_item
                            except Exception as click_error:
                                log.warning(
                                    f"[_expand_filter] Failed to expand filter '{filter_name}': {click_error}"
                                )
                                continue

        log.warning(f"[_expand_filter] Could not find filter: {filter_name}")
        log.info(f"[_expand_filter] Available filter names: {available_filter_names}")
        log.info(
            f"[_expand_filter] Available an-la attributes: {available_filter_an_las}"
        )
        return None

    except Exception as e:
        log.error(
            f"[_expand_filter] Error finding and expanding filter '{filter_name}': {e}"
        )
        return None


async def _select_checkbox(page: Page, checkbox: dict) -> None:
    """
    체크박스를 선택합니다.

    동작 방식:
    - 텍스트 기반으로 체크박스 찾아서 클릭
    - label 요소를 클릭하여 연결된 input 체크박스 선택
    - 클릭 후 체크박스가 실제로 체크되었는지 검증
    - 체크되지 않았다면 다른 방법 시도
    """
    try:
        log.info(f"[_select_checkbox] START - Looking for checkbox: '{checkbox['text']}' in filter '{checkbox['filter_name']}'")
        
        # 스크롤 전 화면 상태 확인
        scroll_pos_before = await page.evaluate("window.pageYOffset")
        log.info(f"[_select_checkbox] Screen scroll position before scroll: {scroll_pos_before}px")
        
        # 최상단으로 스크롤
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        
        # 스크롤 후 화면 상태 확인
        scroll_pos_after = await page.evaluate("window.pageYOffset")
        log.info(f"[_select_checkbox] Screen scroll position after scroll to top: {scroll_pos_after}px")
        
        # 현재 활성화된 필터 내에서만 체크박스 찾기
        active_filter = await page.query_selector(".pd21-filter__selector-item--open")
        if not active_filter:
            # 펼쳐진 필터가 없으면 모든 필터에서 찾기
            log.info(f"[_select_checkbox] No open filter found, searching all checkboxes")
            checkbox_elements = await page.query_selector_all(".checkbox-v3")
        else:
            # 펼쳐진 필터 내에서만 찾기
            log.info(f"[_select_checkbox] Open filter found, searching within active filter")
            checkbox_elements = await active_filter.query_selector_all(".checkbox-v3")
        
        log.info(f"[_select_checkbox] Found {len(checkbox_elements)} checkbox elements")
        
        
        # an-la 속성으로 체크박스 찾기 (우선순위)
        for i, element in enumerate(checkbox_elements):
            # input 요소에서 an-la 속성 찾기
            input_element = await element.query_selector(".checkbox-v3__input")
            if input_element:
                an_la_attr = await input_element.get_attribute("an-la")
                if an_la_attr and an_la_attr == checkbox['an_la']:
                    log.info(f"[_select_checkbox] MATCHED checkbox by an-la: '{an_la_attr}' (looking for: '{checkbox['an_la']}')")
                    
                    # 체크박스 현재 상태 확인 (다양한 방법으로 확인)
                    is_checked_attr = await input_element.get_attribute("checked") is not None
                    is_checked_prop = await input_element.evaluate("el => el.checked")
                    aria_checked = await input_element.get_attribute("aria-checked")
                    element_class = await element.get_attribute("class")
                    is_disabled = await input_element.get_attribute("disabled") is not None
                    is_visible = await element.is_visible()
                    bbox = await element.bounding_box()
                    
                    log.info(f"[_select_checkbox] Checkbox state:")
                    log.info(f"  - checked attribute: {is_checked_attr}")
                    log.info(f"  - checked property: {is_checked_prop}")
                    log.info(f"  - aria-checked: {aria_checked}")
                    log.info(f"  - element class: {element_class}")
                    log.info(f"  - disabled: {is_disabled}, visible: {is_visible}, position: {bbox}")
                    
                    # 체크 상태는 property로 확인
                    is_checked = is_checked_prop
                    
                    # 이미 체크된 상태인지 확인
                    if is_checked:
                        log.info(f"[_select_checkbox] Checkbox '{checkbox['text']}' is already checked - skipping click")
                        return  # 이미 체크된 상태면 클릭하지 않고 종료
                    
                    # 체크박스가 화면에 보이지 않는 경우 처리
                    if not is_visible or not bbox:
                        log.warning(f"[_select_checkbox] Checkbox '{checkbox['text']}' is not visible or has no bounding box")
                        raise Exception(f"Filter exists but checkbox is not visible on screen - cannot be clicked")
                    
                    # 체크박스를 화면 중앙으로 스크롤
                    log.info(f"[_select_checkbox] Scrolling checkbox to center of viewport")
                    try:
                        # 요소를 화면 중앙으로 스크롤
                        await element.evaluate("el => el.scrollIntoView({ behavior: 'instant', block: 'center', inline: 'center' })")
                        await page.wait_for_timeout(300)
                        
                        # 스크롤 후 위치 재확인
                        bbox_after = await element.bounding_box()
                        scroll_pos_after = await page.evaluate("window.pageYOffset")
                        log.info(f"[_select_checkbox] After scroll - position: {bbox_after}, page scroll: {scroll_pos_after}px")
                    except Exception as e:
                        log.warning(f"[_select_checkbox] Failed to scroll element to center: {e}")
                    
                    # 체크박스 클릭 시도
                    # 방법 1: label 요소 클릭 (가장 확실한 방법)
                    try:
                        log.info(f"[_select_checkbox] Method 1: Clicking label element")
                        label_element = await element.query_selector(".checkbox-v3__label")
                        if label_element:
                            await label_element.click(timeout=10000)
                            
                            # 클릭 후 체크 상태 확인
                            await page.wait_for_timeout(500)
                            is_checked_after = await input_element.evaluate("el => el.checked")
                            log.info(f"[_select_checkbox] After click (method 1) - checked state changed from {is_checked} to {is_checked_after}")
                            
                            if is_checked != is_checked_after:
                                log.info(f"[_select_checkbox] Successfully clicked checkbox '{checkbox['text']}' (method 1)")
                                # 클릭 후 최상단으로 스크롤
                                await page.evaluate("window.scrollTo(0, 0)")
                                await page.wait_for_timeout(300)
                                log.info(f"[_select_checkbox] Scrolled back to top after successful click")
                                return
                            else:
                                log.warning(f"[_select_checkbox] Method 1 failed: state did not change")
                        else:
                            log.warning(f"[_select_checkbox] Method 1 failed: label element not found")
                    except Exception as e:
                        log.debug(f"[_select_checkbox] Method 1 failed: {e}")
                    
                    # 방법 2: JavaScript로 label 클릭
                    try:
                        log.info(f"[_select_checkbox] Method 2: Using JavaScript to click label")
                        label_element = await element.query_selector(".checkbox-v3__label")
                        if label_element:
                            await label_element.evaluate("el => el.click()")
                            
                            # 클릭 후 체크 상태 확인
                            await page.wait_for_timeout(500)
                            is_checked_after = await input_element.evaluate("el => el.checked")
                            log.info(f"[_select_checkbox] After click (method 2) - checked state changed from {is_checked} to {is_checked_after}")
                            
                            if is_checked != is_checked_after:
                                log.info(f"[_select_checkbox] Successfully clicked checkbox '{checkbox['text']}' (method 2)")
                                # 클릭 후 최상단으로 스크롤
                                await page.evaluate("window.scrollTo(0, 0)")
                                await page.wait_for_timeout(300)
                                log.info(f"[_select_checkbox] Scrolled back to top after successful click")
                                return
                            else:
                                log.warning(f"[_select_checkbox] Method 2 failed: state did not change")
                        else:
                            log.warning(f"[_select_checkbox] Method 2 failed: label element not found")
                    except Exception as e:
                        log.debug(f"[_select_checkbox] Method 2 failed: {e}")
                    
                    # 방법 3: input 요소를 직접 클릭 (force)
                    try:
                        log.info(f"[_select_checkbox] Method 3: Force clicking input element")
                        await input_element.click(timeout=10000, force=True)
                        
                        # 클릭 후 체크 상태 확인
                        await page.wait_for_timeout(500)
                        is_checked_after = await input_element.evaluate("el => el.checked")
                        log.info(f"[_select_checkbox] After click (method 3) - checked state changed from {is_checked} to {is_checked_after}")
                        
                        if is_checked != is_checked_after:
                            log.info(f"[_select_checkbox] Successfully clicked checkbox '{checkbox['text']}' (method 3)")
                            # 클릭 후 최상단으로 스크롤
                            await page.evaluate("window.scrollTo(0, 0)")
                            await page.wait_for_timeout(300)
                            log.info(f"[_select_checkbox] Scrolled back to top after successful click")
                            return
                        else:
                            log.warning(f"[_select_checkbox] Method 3 failed: state did not change")
                    except Exception as e:
                        log.debug(f"[_select_checkbox] Method 3 failed: {e}")
                    
                    # 모든 방법이 실패한 경우
                    log.error(f"[_select_checkbox] All click methods failed for checkbox '{checkbox['text']}'")
                    raise Exception(f"Checkbox '{checkbox['text']}' was clicked but state did not change")
        
        # an-la로 찾지 못한 경우 텍스트 기반 fallback
        for element in checkbox_elements:
            label_text = await element.query_selector(".checkbox-v3__label-text")
            if label_text:
                element_text = await label_text.inner_text()
                element_text = element_text.strip()

                # 텍스트 매칭 (fallback)
                if element_text == checkbox['text']:
                    log.info(f"[_select_checkbox] MATCHED checkbox by text: '{element_text}' (looking for: '{checkbox['text']}')")
                    
                    # 체크박스 현재 상태 확인 (text fallback)
                    input_element_fallback = await element.query_selector(".checkbox-v3__input")
                    if input_element_fallback:
                        is_checked = await input_element_fallback.evaluate("el => el.checked")
                        is_disabled = await input_element_fallback.get_attribute("disabled") is not None
                    else:
                        is_checked = False
                        is_disabled = False
                    is_visible = await element.is_visible()
                    bbox = await element.bounding_box()
                    log.info(f"[_select_checkbox] Checkbox state (text fallback) - checked: {is_checked}, disabled: {is_disabled}, visible: {is_visible}, position: {bbox}")
                    
                    # 체크박스가 화면에 보이지 않는 경우 처리
                    if not is_visible or not bbox:
                        log.warning(f"[_select_checkbox] Checkbox '{checkbox['text']}' is not visible or has no bounding box (text fallback)")
                        raise Exception(f"Filter exists but checkbox is not visible on screen - cannot be clicked")
                    
                    # 체크박스를 화면 중앙으로 스크롤 (text fallback)
                    log.info(f"[_select_checkbox] Scrolling checkbox to center of viewport (text fallback)")
                    try:
                        # 요소를 화면 중앙으로 스크롤
                        await element.evaluate("el => el.scrollIntoView({ behavior: 'instant', block: 'center', inline: 'center' })")
                        await page.wait_for_timeout(300)
                        
                        # 스크롤 후 위치 재확인
                        bbox_after = await element.bounding_box()
                        scroll_pos_after = await page.evaluate("window.pageYOffset")
                        log.info(f"[_select_checkbox] After scroll (text fallback) - position: {bbox_after}, page scroll: {scroll_pos_after}px")
                    except Exception as e:
                        log.warning(f"[_select_checkbox] Failed to scroll element to center (text fallback): {e}")
                    
                    # 체크박스 클릭 시도 (text fallback)
                    if input_element_fallback:
                        # 방법 1: label 요소 클릭
                        try:
                            log.info(f"[_select_checkbox] Method 1 (text fallback): Clicking label element")
                            label_element = await element.query_selector(".checkbox-v3__label")
                            if label_element:
                                await label_element.click(timeout=10000)
                                
                                # 클릭 후 체크 상태 확인
                                await page.wait_for_timeout(500)
                                is_checked_after = await input_element_fallback.evaluate("el => el.checked")
                                log.info(f"[_select_checkbox] After click (text fallback method 1) - checked state changed from {is_checked} to {is_checked_after}")
                                
                                if is_checked != is_checked_after:
                                    log.info(f"[_select_checkbox] Successfully clicked checkbox '{checkbox['text']}' (text fallback method 1)")
                                    # 클릭 후 최상단으로 스크롤
                                    await page.evaluate("window.scrollTo(0, 0)")
                                    await page.wait_for_timeout(300)
                                    log.info(f"[_select_checkbox] Scrolled back to top after successful click (text fallback)")
                                    return
                                else:
                                    log.warning(f"[_select_checkbox] Method 1 (text fallback) failed: state did not change")
                            else:
                                log.warning(f"[_select_checkbox] Method 1 (text fallback) failed: label element not found")
                        except Exception as e:
                            log.debug(f"[_select_checkbox] Method 1 (text fallback) failed: {e}")
                        
                        # 방법 2: JavaScript로 label 클릭
                        try:
                            log.info(f"[_select_checkbox] Method 2 (text fallback): Using JavaScript to click label")
                            label_element = await element.query_selector(".checkbox-v3__label")
                            if label_element:
                                await label_element.evaluate("el => el.click()")
                                
                                # 클릭 후 체크 상태 확인
                                await page.wait_for_timeout(500)
                                is_checked_after = await input_element_fallback.evaluate("el => el.checked")
                                log.info(f"[_select_checkbox] After click (text fallback method 2) - checked state changed from {is_checked} to {is_checked_after}")
                                
                                if is_checked != is_checked_after:
                                    log.info(f"[_select_checkbox] Successfully clicked checkbox '{checkbox['text']}' (text fallback method 2)")
                                    # 클릭 후 최상단으로 스크롤
                                    await page.evaluate("window.scrollTo(0, 0)")
                                    await page.wait_for_timeout(300)
                                    log.info(f"[_select_checkbox] Scrolled back to top after successful click (text fallback)")
                                    return
                                else:
                                    log.warning(f"[_select_checkbox] Method 2 (text fallback) failed: state did not change")
                            else:
                                log.warning(f"[_select_checkbox] Method 2 (text fallback) failed: label element not found")
                        except Exception as e:
                            log.debug(f"[_select_checkbox] Method 2 (text fallback) failed: {e}")
                        
                        # 방법 3: input 요소를 직접 클릭 (force)
                        try:
                            log.info(f"[_select_checkbox] Method 3 (text fallback): Force clicking input element")
                            await input_element_fallback.click(timeout=10000, force=True)
                            
                            # 클릭 후 체크 상태 확인
                            await page.wait_for_timeout(500)
                            is_checked_after = await input_element_fallback.evaluate("el => el.checked")
                            log.info(f"[_select_checkbox] After click (text fallback method 3) - checked state changed from {is_checked} to {is_checked_after}")
                            
                            if is_checked != is_checked_after:
                                log.info(f"[_select_checkbox] Successfully clicked checkbox '{checkbox['text']}' (text fallback method 3)")
                                # 클릭 후 최상단으로 스크롤
                                await page.evaluate("window.scrollTo(0, 0)")
                                await page.wait_for_timeout(300)
                                log.info(f"[_select_checkbox] Scrolled back to top after successful click (text fallback)")
                                return
                            else:
                                log.warning(f"[_select_checkbox] Method 3 (text fallback) failed: state did not change")
                        except Exception as e:
                            log.debug(f"[_select_checkbox] Method 3 (text fallback) failed: {e}")
                        
                        # 모든 방법이 실패한 경우
                        log.error(f"[_select_checkbox] All click methods failed for checkbox '{checkbox['text']}' (text fallback)")
                        raise Exception(f"Checkbox '{checkbox['text']}' was clicked but state did not change")
                    else:
                        log.warning(f"[_select_checkbox] No input element found for text '{checkbox['text']}'")
                        continue
        
        # 매칭되는 체크박스를 찾지 못한 경우
        log.warning(f"[_select_checkbox] No exact match found for '{checkbox['text']}'")
        error_msg = f"Checkbox click failed for '{checkbox['text']}' - not found or not checked after all attempts"
        log.error(f"[_select_checkbox] {error_msg}")
        raise Exception(error_msg)

    except Exception as e:
        log.error(
            f"[_select_checkbox] Error selecting checkbox '{checkbox['text']}' in filter '{checkbox['filter_name']}': {e}"
        )
        raise


async def _close_filter(page: Page, checkbox: dict, filter_item: ElementHandle) -> bool:
    """
    필터를 접습니다.

    동작 방식:
    - single_checkbox 필터: 즉시 True 반환 (펼치지 않아도 되는 필터)
    - multi_checkbox 필터: 필터가 열려있는지 확인 후 닫기 시도
    - 필터 영역이 숨겨지는 것을 방지하기 위한 복구 작업
    - 최종 실패 시 페이지 재로드 후 재시도

    파라미터:
        page (Page): Playwright Page 객체
        checkbox (dict): 체크박스 정보 (filter_type 포함)
        filter_item (ElementHandle): 접을 필터 아이템

    반환값:
        bool: 필터 닫기 성공 여부

    예외 처리:
    - 접기 실패 시: 페이지 재로드 후 재시도
    - 재시도 실패 시: False 반환
    """
    # single_checkbox 필터는 즉시 True 반환 (펼치지 않아도 되는 필터)
    if checkbox.get('filter_type') == 'single_checkbox':
        log.info(f"[_close_filter] Single checkbox filter - no need to close")
        return True

    try:
        log.info(f"[_close_filter] START - Closing filter '{checkbox['filter_name']}'")
        
        # 스크롤 전 화면 상태 확인
        scroll_pos_before = await page.evaluate("window.pageYOffset")
        log.info(f"[_close_filter] Screen scroll position before scroll: {scroll_pos_before}px")
        
        # 최상단으로 스크롤
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        
        # 스크롤 후 화면 상태 확인
        scroll_pos_after = await page.evaluate("window.pageYOffset")
        log.info(f"[_close_filter] Screen scroll position after scroll to top: {scroll_pos_after}px")
        
        # multi_checkbox 필터인지 확인 (펼쳐야 하는 필터)
        if checkbox.get("filter_type") != "multi_checkbox":
            return True  # 알 수 없는 필터 타입은 안전하게 True 반환

        cta_button = await filter_item.query_selector(".pd21-filter__selector-item-cta")
        if not cta_button:
            log.warning(f"[_close_filter] CTA button not found for filter '{checkbox['filter_name']}'")
            return False

        # 필터가 열려있는지 확인 (pd21-filter__selector-item--open 클래스 확인)
        filter_class = await filter_item.get_attribute("class")
        is_filter_open = filter_class and "pd21-filter__selector-item--open" in filter_class
        log.info(f"[_close_filter] Filter state - is_open: {is_filter_open}, classes: {filter_class}")
        
        if not is_filter_open:
            log.info(f"[_close_filter] Filter '{checkbox['filter_name']}' is already closed, skipping close operation")
            return True

        # 필터 닫기 시도
        try:
            # 필터를 닫기 전에 필터 박스가 활성화된 상태인지 확인
            filter_container = await page.query_selector(".pd21-filter")
            if filter_container:
                class_list = await filter_container.get_attribute("class")
                if class_list and "pd21-filter--close" in class_list:
                    # 필터 박스가 비활성화된 상태라면 페이지 재로드
                    log.warning(
                        f"[_close_filter] Filter area is closed before closing '{checkbox['filter_name']}'"
                    )
                    await page.reload()
                    await page.wait_for_timeout(5000)  # 페이지 재로드 대기

            # CTA 버튼의 가시성 및 위치 확인
            is_visible = await cta_button.is_visible()
            bbox = await cta_button.bounding_box()
            log.info(f"[_close_filter] CTA button state - visible: {is_visible}, position: {bbox}")
            
            log.info(f"[_close_filter] Attempting to click CTA button to close filter")
            await cta_button.click(timeout=5000)
            log.info(f"[_close_filter] Click executed, waiting 1s for filter to close")
            await page.wait_for_timeout(1000)  # 접히는 시간 대기
            
            # 닫힘 후 상태 확인
            updated_classes = await filter_item.get_attribute("class")
            is_now_closed = "pd21-filter__selector-item--open" not in (updated_classes or "")
            log.info(f"[_close_filter] After click - is_closed: {is_now_closed}, classes: {updated_classes}")
            
            # 필터를 닫은 후 필터 영역이 숨겨져 있는지 확인하고 복구
            await _ensure_filter_area_visible(page)
            
            log.info(f"[_close_filter] Successfully closed filter '{checkbox['filter_name']}'")
            return True

        except Exception as click_error:
            log.warning(
                f"[_close_filter] Failed to close filter '{checkbox['filter_name']}': {click_error}"
            )
            # 페이지 재로드 후 재시도
            try:
                log.info(
                    f"[_close_filter] Retrying filter close for '{checkbox['filter_name']}' after page reload"
                )
                await page.reload()
                await page.wait_for_timeout(5000)  # 페이지 재로드 대기

                # 재로드 후 필터 닫기 재시도
                cta_button = await filter_item.query_selector(
                    ".pd21-filter__selector-item-cta"
                )
                if cta_button:
                    await cta_button.click(timeout=5000)
                    await page.wait_for_timeout(1000)

                    # 필터 영역 복구
                    await _ensure_filter_area_visible(page)

                    log.debug(
                        f"[_close_filter] Successfully closed filter '{checkbox['filter_name']}' after retry"
                    )
                    return True
                else:
                    log.warning(
                        f"[_close_filter] CTA button not found for filter '{checkbox['filter_name']}' after reload"
                    )
                    return False

            except Exception as retry_error:
                log.error(
                    f"[_close_filter] Retry failed for filter '{checkbox['filter_name']}': {retry_error}"
                )
                return False

    except Exception as close_error:
        log.warning(
            f"[_close_filter] Error during filter close process for '{checkbox['filter_name']}': {close_error}"
        )
        return False


async def _clear_filters_and_wait(page: Page) -> bool:
    """
    모든 적용된 필터를 지우고 페이지 로딩을 기다립니다.

    동작 방식:
    1. 필터 영역이 숨겨져 있는지 확인하고 다시 보이게 하기
    2. Clear 버튼으로 한 번에 지우기 시도
    3. 실패 시 개별 필터 제거 시도
    4. 최후의 수단으로 페이지 새로고침

    파라미터:
        page (Page): Playwright Page 객체

    반환값:
        bool: 필터 지우기 성공 여부
    """
    try:
        log.info(f"[_clear_filters_and_wait] START - Clearing all applied filters")
        
        # 최상단으로 스크롤
        try:
            scroll_pos_before = await page.evaluate("window.pageYOffset")
            log.info(f"[_clear_filters_and_wait] Screen position before scroll: {scroll_pos_before}px")
            
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(500)
            
            scroll_pos_after = await page.evaluate("window.pageYOffset")
            log.info(f"[_clear_filters_and_wait] Screen position after scroll to top: {scroll_pos_after}px")
        except Exception as scroll_error:
            log.warning(f"[_clear_filters_and_wait] Scroll to top failed: {scroll_error}")
            pass  # 스크롤 실패해도 계속 진행

        # 현재 선택된 필터 확인
        selected_items = await page.query_selector_all(".pd21-filter__selected-item")
        log.info(f"[_clear_filters_and_wait] Found {len(selected_items)} selected filter items")
        
        if not selected_items:
            log.info(f"[_clear_filters_and_wait] No selected filters found - nothing to clear")
            return True

        # 방법 1: Clear 버튼으로 한 번에 지우기
        log.info(f"[_clear_filters_and_wait] Method 1: Attempting to use Clear button")
        clear_button = await page.query_selector(".cta.cta--underline-v2.cta--black.pd21-filter__clear--pc")
        if clear_button:
            try:
                is_visible = await clear_button.is_visible()
                bbox = await clear_button.bounding_box()
                log.info(f"[_clear_filters_and_wait] Clear button found - visible: {is_visible}, position: {bbox}")
                
                log.info(f"[_clear_filters_and_wait] Scrolling Clear button into view")
                await clear_button.scroll_into_view_if_needed()
                await page.wait_for_timeout(500)
                
                log.info(f"[_clear_filters_and_wait] Clicking Clear button")
                await clear_button.click(timeout=10000)
                log.info(f"[_clear_filters_and_wait] Waiting 3s after Clear button click")
                await page.wait_for_timeout(3000)

                # 확인
                remaining_items = await page.query_selector_all(".pd21-filter__selected-item")
                log.info(f"[_clear_filters_and_wait] After Clear button - remaining items: {len(remaining_items)}")
                
                if not remaining_items:
                    log.info(f"[_clear_filters_and_wait] Method 1 SUCCESS - All filters cleared")
                    return True
                else:
                    log.warning(f"[_clear_filters_and_wait] Method 1 FAILED - {len(remaining_items)} items remaining")
                    
            except Exception as clear_error:
                log.warning(f"[_clear_filters_and_wait] Method 1 FAILED with exception: {clear_error}")
                pass  # Clear 버튼 실패 시 다음 방법 시도
        else:
            log.warning(f"[_clear_filters_and_wait] Method 1 SKIPPED - Clear button not found")
        
        # 방법 2: 개별 필터 제거
        try:
            for item in selected_items:
                try:
                    # X 버튼 찾기 (여러 선택자 시도)
                    remove_button = await item.query_selector(
                        "svg.icon"
                    ) or await item.query_selector(".pd21-filter__selected-item-remove")

                    if remove_button:
                        await item.scroll_into_view_if_needed()
                        await page.wait_for_timeout(500)
                        await remove_button.click(timeout=5000)
                        await page.wait_for_timeout(1000)

                except Exception:
                    continue  # 개별 필터 제거 실패 시 다음 필터로

            # 확인
            await page.wait_for_timeout(2000)
            if not await page.query_selector_all(".pd21-filter__selected-item"):
                return True

        except Exception:
            pass  # 개별 제거 실패 시 다음 방법 시도

        # 방법 3: JavaScript로 직접 필터 상태 초기화
        try:
            log.info(f"[_clear_filters_and_wait] Method 3: Attempting JavaScript filter reset")
            
            # JavaScript로 모든 체크박스 언체크
            await page.evaluate("""
                // 모든 체크박스 찾아서 언체크
                const checkboxes = document.querySelectorAll('.checkbox-v3__input');
                checkboxes.forEach(checkbox => {
                    if (checkbox.checked) {
                        checkbox.checked = false;
                        // change 이벤트 발생시키기
                        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });
                
                // 선택된 필터 아이템들 제거
                const selectedItems = document.querySelectorAll('.pd21-filter__selected-item');
                selectedItems.forEach(item => {
                    const closeButton = item.querySelector('.pd21-filter__selected-item-close');
                    if (closeButton) {
                        closeButton.click();
                    }
                });
            """)
            
            await page.wait_for_timeout(2000)
            
            # 확인
            remaining_items = await page.query_selector_all(".pd21-filter__selected-item")
            log.info(f"[_clear_filters_and_wait] After JavaScript reset - remaining items: {len(remaining_items)}")
            
            if not remaining_items:
                log.info(f"[_clear_filters_and_wait] Method 3 SUCCESS - All filters cleared via JavaScript")
                return True
            else:
                log.warning(f"[_clear_filters_and_wait] Method 3 FAILED - {len(remaining_items)} items remaining")
                
        except Exception as js_error:
            log.warning(f"[_clear_filters_and_wait] Method 3 FAILED with exception: {js_error}")
            pass  # JavaScript 실패 시 다음 방법 시도

        # 방법 4: URL 초기화 후 페이지 새로고침
        try:
            log.info(f"[_clear_filters_and_wait] Method 4: Attempting URL reset/reload")
            # 현재 URL에서 필터 관련 파라미터 제거
            current_url = page.url
            if "?" in current_url:
                base_url = current_url.split("?")[0]
                log.info(
                    f"[_clear_filters_and_wait] Resetting URL from {current_url} to {base_url}"
                )
                await page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
            else:
                await page.reload(wait_until="domcontentloaded", timeout=30000)

            await page.wait_for_timeout(3000)

            final_check = await page.query_selector_all(".pd21-filter__selected-item")
            log.info(f"[_clear_filters_and_wait] After URL reset - remaining items: {len(final_check)}")
            
            if not final_check:
                log.info(f"[_clear_filters_and_wait] Method 4 SUCCESS - All filters cleared via URL reset")
                return True
            else:
                log.warning(f"[_clear_filters_and_wait] Method 4 FAILED - {len(final_check)} items still remaining")
                return False

        except Exception as reload_error:
            log.error(
                f"[_clear_filters_and_wait] Method 4 FAILED with exception: {reload_error}"
            )
            return False

    except Exception as e:
        log.error(f"[_clear_filters_and_wait] Error clearing filters: {e}")
        return False


########################################################################################
# 필터 구조 추출
########################################################################################
async def extract_filter_structure(page: Page) -> dict:
    """
    현재 페이지에서 필터 구조 정보를 추출합니다.

    동작 방식:
    - 모든 필터 아이템을 찾아서 순서대로 처리
    - 두 번째 필터와 size로 끝나는 필터들은 개별 테스트용으로 분류
    - 나머지 필터들은 랜덤 조합 테스트용으로 분류

    파라미터:
        page (Page): Playwright Page 객체

    반환값:
        dict: 필터 구조 정보
            - filters: 모든 필터 정보 리스트
            - individual_test_filters: 개별 테스트용 필터 리스트
            - random_combination_filters: 랜덤 조합용 필터 리스트
            - total_filters: 전체 필터 개수
    """
    log.info("[extract_filter_structure] Starting filter structure extraction")

    result = {
        "filters": [],
        "individual_test_filters": [],  # 개별 테스트용 필터들 (두 번째 필터 + size 필터)
        "random_combination_filters": [],  # 랜덤 조합용 필터들
        "total_filters": 0,
    }

    try:
        # 0. 이미 적용된 필터가 있는 경우 먼저 지우기
        log.info("[extract_filter_structure] Checking for pre-applied filters")
        selected_items = await page.query_selector_all(".pd21-filter__selected-item")
        if selected_items:
            log.info(f"[extract_filter_structure] Found {len(selected_items)} pre-applied filters, clearing them")
            clear_success = await _clear_filters_and_wait(page)
            if clear_success:
                log.info("[extract_filter_structure] Pre-applied filters cleared successfully")
            else:
                log.warning("[extract_filter_structure] Failed to clear pre-applied filters, continuing with extraction")
        else:
            log.info("[extract_filter_structure] No pre-applied filters found")

        # 1. 스크롤을 최상단으로 이동하여 필터 영역이 보이도록 보장
        try:
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(500)  # 스크롤 완료 대기
            log.info("[extract_filter_structure] Scrolled to top of page")
        except Exception as scroll_error:
            log.warning(
                f"[extract_filter_structure] Failed to scroll to top: {scroll_error}"
            )

        # 1. 필터 컨테이너 찾기
        filter_container = await page.query_selector(".pd21-filter__selector-list")
        if not filter_container:
            log.error("[extract_filter_structure] Filter container not found")
            return result

        # 2. 모든 필터 아이템 찾기 (checkbox 타입 + menu 타입)
        filter_items = await filter_container.query_selector_all(
            ".pd21-filter__selector-item--checkbox, .pd21-filter__selector-item--menu"
        )
        result["total_filters"] = len(filter_items)

        log.info(
            f"[extract_filter_structure] Found {result['total_filters']} filter items"
        )

        # 3. 각 필터 처리
        for filter_index, filter_item in enumerate(filter_items):
            try:
                # 각 필터 처리 전에 스크롤을 최상단으로 이동 (안정성 보장)
                try:
                    await page.evaluate("window.scrollTo(0, 0)")
                    await page.wait_for_timeout(300)  # 스크롤 완료 대기
                except Exception:
                    pass  # 스크롤 실패해도 계속 진행

                # 3-1. 필터 정보 추출 (이름 + 체크박스) - 펼치기도 자동으로 처리하고 추출 후 접기
                filter_info = await _extract_filter_info(
                    filter_item, filter_index, page
                )

                # filter_info가 None인 경우 건너뛰기
                if filter_info is None:
                    log.warning(
                        f"[extract_filter_structure] Skipping filter {filter_index} due to extraction failure"
                    )
                    continue

                # 모든 필터를 filters 리스트에 추가
                result["filters"].append(filter_info)

                # 3-2. 필터 타입별 분류
                if filter_info["index"] == 1:
                    # 개별 테스트용 필터 (무조건 2번째 필터만)
                    result["individual_test_filters"].append(filter_info)
                    log.info(
                        f"[extract_filter_structure] Individual test filter: {filter_info['name']} ({len(filter_info['checkboxes'])} checkboxes)"
                    )
                else:
                    # 랜덤 조합용 필터
                    result["random_combination_filters"].append(filter_info)
                    log.info(
                        f"[extract_filter_structure] Random combination filter: {filter_info['name']} ({len(filter_info['checkboxes'])} checkboxes)"
                    )

            except Exception as filter_error:
                log.error(
                    f"[extract_filter_structure] Error processing filter {filter_index}: {filter_error}"
                )
                continue

        # 4. 최종 결과 로깅
        log.info(f"[extract_filter_structure] Filter extraction completed")
        log.info(
            f"[extract_filter_structure] - Total filters: {len(result['filters'])}"
        )
        log.info(
            f"[extract_filter_structure] - Individual test filters: {len(result['individual_test_filters'])} filters"
        )
        log.info(
            f"[extract_filter_structure] - Random combination filters: {len(result['random_combination_filters'])} filters"
        )

    except Exception as e:
        log.error(f"[extract_filter_structure] Error during filter extraction: {e}")

    return result


########################################################################################
# 필터 검증
########################################################################################
async def validate_filter(shop_result, original_page) -> None:
    """
    필터 검증을 수행합니다.

    동작 방식:
    1. 필터 테스트 가능한 서브카테고리 노드 찾기
    2. 필터 구조 추출
    3. 모든 테스트 조합 생성
    4. 각 조합에 대해 테스트 실행
    5. 결과를 노드에 저장

    파라미터:
        shop_result (List[SubCategoryNode]): 서브카테고리 노드 리스트
        original_page (Page): 원본 페이지 객체

    예외 처리:
    - 필터 테스트 가능한 노드가 없는 경우: 조기 종료
    - 필터 정보가 없는 경우: 조기 종료
    - 테스트 조합 생성 실패: 조기 종료
    - 개별 테스트 실패: 해당 조합 실패로 기록하고 계속 진행

    사용 예시:
        await validate_filter(shop_result, page)
        # 검증 결과는 노드의 filter_validate 속성에 저장됨

    데이터 구조:
    - 노드에 저장되는 결과:
        * filter_validate: 전체 검증 성공 여부 (bool)
        * filter_validate_desc: 실패 시 상세 설명 (str)
        * filter_validate_info: 상세 검증 정보 (dict)
            - total_tests: 전체 테스트 수
            - successful_tests: 성공한 테스트 수
            - failed_tests: 실패한 테스트 수
            - test_details: 각 테스트의 상세 결과
    """
    try:
        # 필터 테스트 가능한 노드 찾기
        current_url = original_page.url
        target_node = None
        for node in shop_result:
            if node.url == current_url and node.is_filter_testable:
                target_node = node
                break

        if not target_node:
            log.info(
                f"[validate_filter] No filter testable node found for current URL: {current_url}"
            )
            return

        # 필터 구조가 이미 추출되어 있는지 확인
        if not target_node.filter_info:
            log.warning("[validate_filter] No filter info found in target node")
            return

        log.info(
            f"[validate_filter] Starting filter validation for node: {target_node.name}"
        )

        # 모든 테스트 조합 생성
        all_combinations = await _generate_all_combinations(target_node.filter_info)

        if not all_combinations:
            log.warning("[validate_filter] No test combinations generated")
            return

        # 각 조합에 대해 테스트 실행
        failed_combinations = []
        test_details = []
        total_tests = len(all_combinations)

        for i, combination in enumerate(all_combinations):
            try:
                # 조합 정보 미리 구성
                filter_groups = {}
                for checkbox in combination:
                    filter_name = checkbox.get("filter_name", "Unknown")
                    if filter_name not in filter_groups:
                        filter_groups[filter_name] = []
                    filter_groups[filter_name].append(checkbox["text"])
                combo_details = []
                for filter_name, texts in filter_groups.items():
                    combo_details.append(f"{filter_name}: {', '.join(texts)}")
                base_combo = f"[{' | '.join(combo_details)}]"

                log.info(
                    f"[validate_filter] Testing combination {i+1}/{total_tests}: {base_combo}"
                )

                # 테스트 실행
                result = await _test_filter_combination(original_page, combination)

                passed = result["text_validate"] and result["purchase_validate"]

                # 분리된 검증 결과 정보 추출
                text_validation = {
                    "passed": result["text_validate"],
                    "desc": result["text_validate_desc"],
                }
                purchase_validation = {
                    "passed": result["purchase_validate"],
                    "desc": result["purchase_validate_desc"],
                }

                # 검증 결과 상세 로그
                log.info(f"[validate_filter] Combination {i+1} results:")
                log.info(
                    f"  Text validation: {result['text_validate']} - {result['text_validate_desc']}"
                )
                log.info(
                    f"  Purchase validation: {result['purchase_validate']} - {result['purchase_validate_desc']}"
                )
                log.info(f"  Overall result: {'PASSED' if passed else 'FAILED'}")

                # 실패 조합 모음 (기존 호환성 유지)
                if not passed:
                    # text 검증과 구매 검증 중 실패한 것의 설명을 사용
                    failed_desc = ""
                    if not result["text_validate"]:
                        failed_desc = result["text_validate_desc"]
                    elif not result["purchase_validate"]:
                        failed_desc = result["purchase_validate_desc"]

                    combo_str = (
                        f"{base_combo} | {failed_desc}" if failed_desc else base_combo
                    )
                    failed_combinations.append(combo_str)

                # 테스트 상세 누적 (성공/실패 모두) - 분리된 검증 결과 포함
                test_details.append(
                    {
                        "combo": base_combo,
                        "passed": passed,
                        "desc": result.get(
                            "validate_desc", ""
                        ),  # 기존 호환성을 위해 유지
                        "text_validation": text_validation,
                        "purchase_validation": purchase_validation,
                    }
                )

            except Exception as test_error:
                log.error(
                    f"[validate_filter] Error testing combination {i+1}: {test_error}"
                )
                # 필터 이름과 체크박스 텍스트를 함께 표시
                filter_groups = {}
                for checkbox in combination:
                    filter_name = checkbox.get("filter_name", "Unknown")
                    if filter_name not in filter_groups:
                        filter_groups[filter_name] = []
                    filter_groups[filter_name].append(checkbox["text"])

                combo_details = []
                for filter_name, texts in filter_groups.items():
                    combo_details.append(f"{filter_name}: {', '.join(texts)}")
                combo_str = f"[{' | '.join(combo_details)}]"
                failed_combinations.append(combo_str)

        # 최종 결과 계산
        successful_tests = sum(1 for t in test_details if t.get("passed"))
        overall_success = (
            all(t.get("passed") for t in test_details) if test_details else True
        )

        # 결과를 노드에 저장
        target_node.filter_validate = overall_success
        target_node.filter_validate_info = {
            "total_tests": total_tests,
            "failed_tests": len([t for t in test_details if not t.get("passed")]),
            "test_details": test_details,
        }

        if not overall_success:
            # 실패 조합 상세를 그대로 desc에 포함 (체크박스 텍스트 + 검증 설명)
            target_node.filter_validate_desc = (
                f"Failed combinations: {'; '.join(failed_combinations)}"
            )

        log.info(
            f"[validate_filter] Filter validation completed: {successful_tests}/{total_tests} tests successful"
        )

        # 정렬 기능 검증 (필터 검증 완료 후)
        try:
            log.info("[validate_filter] Starting sort validation")
            sort_result = await validate_sort(original_page)
            target_node.sort_validate = sort_result["validate"]
            target_node.sort_validate_info = sort_result["details"]
            if not sort_result["validate"]:
                target_node.sort_validate_desc = sort_result["description"]
                log.info(f"Sort validation: {target_node.sort_validate_desc}")
            else:
                log.info("Sort validation: PASSED")
        except Exception as sort_error:
            log.error(f"[validate_filter] Error during sort validation: {sort_error}")
            target_node.sort_validate = False
            target_node.sort_validate_desc = (
                f"Sort validation failed due to error: {str(sort_error)}"
            )
            target_node.sort_validate_info = {}

    except Exception as e:
        log.error(f"[validate_filter] Error during filter validation: {e}")
        # 에러 발생 시에도 노드에 실패 결과 저장
        try:
            if target_node:
                target_node.filter_validate = False
                target_node.filter_validate_desc = (
                    f"Filter validation failed due to error: {str(e)}"
                )
                target_node.filter_validate_info = {"total_tests": 0}
        except:
            pass
