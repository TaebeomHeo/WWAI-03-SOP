#!/usr/bin/env python3
"""프롬프트 관리 모듈 - 간소화된 함수 기반"""

import json
import logging
from typing import Dict, List, Any, Optional


def load_system_prompts(config: Dict[str, Any]) -> tuple[str, str]:
    """시스템 프롬프트 파일들을 로드"""
    story_prompt_path = config.get('story_prompt_path', 'story_prompt.md')
    product_prompt_path = config.get('product_prompt_path', 'product_prompt.md')
    
    try:
        with open(story_prompt_path, "r", encoding="utf-8") as f:
            story_system_prompt = f.read()
    except FileNotFoundError:
        logging.error(f"❌ 스토리 프롬프트 파일을 찾을 수 없습니다: {story_prompt_path}")
        raise
    
    try:
        with open(product_prompt_path, "r", encoding="utf-8") as f:
            product_system_prompt = f.read()
    except FileNotFoundError:
        logging.error(f"❌ 제품 프롬프트 파일을 찾을 수 없습니다: {product_prompt_path}")
        raise
    
    return story_system_prompt, product_system_prompt


def _get_candidate_stories(account: Dict[str, Any], data_loader) -> List[Dict[str, Any]]:
    """후보 스토리들을 가져오는 함수 - 새로운 단계별 로직에 따라 데이터 선별"""
    keyword = account.get('관심사키워드', '').strip()
    owned_products_str = account.get('보유제품', '').strip()
    owned_products = [] if owned_products_str == '-' or not owned_products_str else [p.strip() for p in owned_products_str.split(',') if p.strip()]
    
    # 특례 조건 (Ease of use + Mobile,TV)
    if keyword == "Ease of use" and set(owned_products) == {"Mobile", "TV"}:
        # 특례 조건: 35-1, 35-2, 35-3, 42-3만 전달
        special_story_ids = ['35-1', '35-2', '35-3', '42-3']
        special_stories = []
        for story_id in special_story_ids:
            story = data_loader.get_story_by_id(story_id)
            if story:
                special_stories.append(story)
        return special_stories
    
    # 1-1. 둘 다 없음
    if (keyword == '-' or not keyword) and not owned_products:
        story_38_2 = data_loader.get_story_by_id('38-2')
        story_38_1 = data_loader.get_story_by_id('38-1')
        return [story for story in [story_38_2, story_38_1] if story is not None]
    
    # 1-2. 관심사가 없음 (제품은 있음)
    if keyword == '-' or not keyword:
        # 전체 스토리에서 보유제품으로 1등, 1등의 관심사키워드로 2등 선정
        return data_loader.get_all_stories()
    
    # 1-3. 제품이 없음 (관심사는 있음)
    if not owned_products:
        # 해당 관심사키워드 스토리들에서만 1,2등 선정
        matched_stories = data_loader.get_stories_by_keyword(keyword)
        return matched_stories if matched_stories else []
    
    # 1-4. 둘 다 있음 → 2단계로 진행
    # 2-1, 2-2, 2-3 모든 경우에 대비해 전체 스토리 전달
    # (관심사키워드 스토리 개수와 완전일치 여부에 따라 LLM이 판단)
    return data_loader.get_all_stories()


def _calculate_match_mismatch(account: Dict[str, Any], stories: List[Dict[str, Any]], data_loader) -> Dict[str, Dict[str, Any]]:
    """매치/미스매치 계산"""
    owned_products_str = account.get('보유제품', '').strip()
    owned_products = [] if owned_products_str == '-' or not owned_products_str else [p.strip() for p in owned_products_str.split(',') if p.strip()]
    
    result = {}
    product_columns = data_loader.get_product_columns()
    
    for story in stories:
        story_id = story.get('스토리ID', '')
        
        matched_products = []
        story_product_names = []
        
        # 각 제품 컬럼을 확인하여 정확한 매칭 수행
        for col in product_columns:
            story_product_value = story.get(col, '').strip()
            if story_product_value:
                # 스토리의 실제 제품값과 보유제품을 직접 비교
                if story_product_value in owned_products:
                    matched_products.append(story_product_value)
                
                # mismatch 계산을 위해 스토리 제품 이름 수집
                story_product_names.append(story_product_value)
        
        # mismatch 계산: 스토리와 보유제품 간의 불일치
        # 1. 보유제품 중 스토리에 없는 것들
        unmatched_owned = [owned for owned in owned_products if owned not in matched_products]
        
        # 2. 스토리 제품 중 보유하지 않은 것들
        unmatched_story = [sp_name for sp_name in story_product_names if sp_name not in owned_products]
        
        # 3. 두 가지를 합쳐서 mismatch
        mismatch_products = unmatched_owned + unmatched_story
        
        result[story_id] = {
            'match_items': matched_products,
            'mismatch_items': mismatch_products,
            'match_cnt': len(matched_products),
            'mismatch_cnt': len(mismatch_products)
        }
    
    return result


def _check_special_condition(precalc_json: Dict[str, Any]) -> str:
    """특례 조건을 확인하고 힌트를 생성"""
    if not precalc_json:
        return ""
    
    # 완벽 매칭 스토리 찾기 (mismatch_cnt = 0)
    perfect_matches = []
    for story_id, data in precalc_json.items():
        if data.get('mismatch_cnt', 0) == 0:
            perfect_matches.append(story_id)
    
    # 특례 조건 확인: [35-1, 35-2, 35-3, 42-3] 모두 완벽 매칭인지
    special_stories = ['35-1', '35-2', '35-3', '42-3']
    special_perfect = [sid for sid in special_stories if sid in perfect_matches]
    
    if len(special_perfect) == 4:
        return f"""
⚠️ **특례 조건 알림**: 
스토리 {special_stories}가 모두 완벽 매칭(mismatch_cnt=0)입니다.
이 경우 "최종 스토리 도출: 35-1, 35-3, 42-3, 35-2 중 랜덤"을 출력해야 합니다.
반드시 모든 스토리를 1단계 분석에 포함시키고 특례 조건을 적용하세요.
"""
    
    return ""


def _build_special_case_prompt(account: Dict[str, Any]) -> str:
    """특별 케이스용 프롬프트 생성"""
    account_name = account.get('Account', account.get('계정명', ''))
    
    return f"""
<account_info>
- Account: {account_name}
- 관심사키워드: -
- 보유제품: -
</account_info>

특별 케이스: 관심사키워드와 보유제품이 모두 '-'인 경우입니다.

최종 스토리 도출: 38-2, 38-1
"""


def _assemble_story_prompt(account: Dict[str, Any], story_json: Dict, precalc_json: Dict, 
                          fixed_story_id: Optional[str] = None, special_hint: str = "") -> str:
    """스토리 프롬프트를 조립"""
    # 계정 정보 블록
    owned_products_str = account.get('보유제품', '').strip()
    if owned_products_str == '-' or not owned_products_str:
        owned_products = []
    else:
        owned_products = [p.strip() for p in owned_products_str.split(',') if p.strip()]
    
    account_block = f"""<account_info>
- Account: {account.get('Account', account.get('계정명', ''))}
- 관심사키워드: {account.get('관심사키워드', '')}
- 보유제품: {json.dumps(owned_products, ensure_ascii=False)}
</account_info>

"""
    
    # 통합 스토리 JSON 블록 (story_json + precalc_json 합침)
    integrated_stories = {}
    for story_id in story_json:
        integrated_stories[story_id] = {
            **story_json[story_id],  # 스토리 기본 정보
            **precalc_json.get(story_id, {})  # 매칭 계산 결과
        }
    
    integrated_block = f"""<integrated_story_data>
{json.dumps(integrated_stories, ensure_ascii=False, indent=2)}
</integrated_story_data>

"""
    
    # 특례 조건 힌트 블록
    hint_block = ""
    if special_hint:
        hint_block = f"""{special_hint}

"""
    
    # 고정 스토리 블록 (선택사항)
    fixed_block = ""
    if fixed_story_id:
        fixed_block = f"""<fixed_story_id>{fixed_story_id}</fixed_story_id>

"""
    
    return account_block + integrated_block + hint_block + fixed_block


def _build_integrated_stories(account: Dict[str, Any], candidate_stories: List[Dict[str, Any]], data_loader) -> Dict[str, Any]:
    """통합된 스토리 데이터 생성 (제품 정보 + 매칭 계산을 한 번에 처리)"""
    product_columns = data_loader.get_product_columns()
    
    # 보유제품 파싱
    owned_products_str = account.get('보유제품', '').strip()
    owned_products = [] if owned_products_str == '-' or not owned_products_str else [p.strip() for p in owned_products_str.split(',') if p.strip()]
    
    integrated_stories = {}
    
    for story in candidate_stories:
        story_id = story.get('스토리ID', '')
        
        # 1. 스토리 제품 정보 수집
        story_products = {}
        story_product_names = []
        
        for col in product_columns:
            story_product_value = story.get(col, '').strip()
            if story_product_value:
                story_products[col] = story_product_value
                story_product_names.append(story_product_value)
        
        # 2. 매칭 계산
        matched_products = []
        for product_name in story_product_names:
            if product_name in owned_products:
                matched_products.append(product_name)
        
        # 3. 미스매치 계산
        unmatched_owned = [owned for owned in owned_products if owned not in matched_products]
        unmatched_story = [sp_name for sp_name in story_product_names if sp_name not in owned_products]
        mismatch_products = unmatched_owned + unmatched_story
        
        # 4. 통합된 데이터 생성
        integrated_stories[story_id] = {
            **story_products,  # 스토리 제품 정보
            'match_items': matched_products,
            'mismatch_items': mismatch_products,
            'match_cnt': len(matched_products),
            'mismatch_cnt': len(mismatch_products)
        }
    
    return integrated_stories


def _check_special_condition_integrated(integrated_stories: Dict[str, Any]) -> str:
    """통합된 스토리 데이터에서 특례 조건을 확인하고 힌트를 생성"""
    if not integrated_stories:
        return ""
    
    # 완벽 매칭 스토리 찾기 (mismatch_cnt = 0)
    perfect_matches = []
    for story_id, data in integrated_stories.items():
        if data.get('mismatch_cnt', 0) == 0:
            perfect_matches.append(story_id)
    
    # 특례 조건 확인: [35-1, 35-2, 35-3, 42-3] 모두 완벽 매칭인지
    special_stories = ['35-1', '35-2', '35-3', '42-3']
    special_perfect = [sid for sid in special_stories if sid in perfect_matches]
    
    if len(special_perfect) == 4:
        return f"""
⚠️ **특례 조건 알림**: 
스토리 {special_stories}가 모두 완벽 매칭(mismatch_cnt=0)입니다.
이 경우 "최종 스토리 도출: 35-1, 35-3, 42-3, 35-2 중 랜덤"을 출력해야 합니다.
반드시 모든 스토리를 1단계 분석에 포함시키고 특례 조건을 적용하세요.
"""
    
    return ""


def _assemble_integrated_prompt(account: Dict[str, Any], integrated_stories: Dict[str, Any], 
                               fixed_story_id: Optional[str] = None, special_hint: str = "") -> str:
    """통합된 스토리 데이터로 프롬프트를 조립"""
    # 계정 정보 블록
    owned_products_str = account.get('보유제품', '').strip()
    if owned_products_str == '-' or not owned_products_str:
        owned_products = []
    else:
        owned_products = [p.strip() for p in owned_products_str.split(',') if p.strip()]
    
    account_block = f"""<account_info>
- Account: {account.get('Account', account.get('계정명', ''))}
- 관심사키워드: {account.get('관심사키워드', '')}
- 보유제품: {json.dumps(owned_products, ensure_ascii=False)}
</account_info>

"""
    
    # 통합 스토리 JSON 블록
    integrated_block = f"""<integrated_story_data>
{json.dumps(integrated_stories, ensure_ascii=False, indent=2)}
</integrated_story_data>

"""
    
    # 특례 조건 힌트 블록
    hint_block = ""
    if special_hint:
        hint_block = f"""{special_hint}

"""
    
    # 고정 스토리 블록 (선택사항)
    fixed_block = ""
    if fixed_story_id:
        fixed_block = f"""<fixed_story_id>{fixed_story_id}</fixed_story_id>

"""
    
    return account_block + integrated_block + hint_block + fixed_block


def build_story_prompt(account_id: str, data_loader, fixed_story_id: Optional[str] = None) -> tuple[str, Dict[str, Any]]:
    """스토리 추천 프롬프트 생성 - 케이스별 사전 분류"""
    logging.info(f"프롬프트 생성 시작: {account_id}")
    
    account = data_loader.get_account_by_id(account_id)
    if not account:
        raise ValueError(f"계정 ID '{account_id}'를 찾을 수 없습니다.")
    
    keyword = account.get('관심사키워드', '').strip()
    owned_products_str = account.get('보유제품', '').strip()
    owned_products = [] if owned_products_str == '-' or not owned_products_str else [p.strip() for p in owned_products_str.split(',') if p.strip()]
    
    # 1-1. 특례 조건 체크 (즉시 반환)
    if keyword == "Ease of use" and set(owned_products) == {"Mobile", "TV"}:
        return _build_special_result_prompt(account, "35-1, 35-3, 42-3, 35-2 중 랜덤"), {}
    
    # 1-2. 관심사/제품 모두 없음 (즉시 반환)
    if (keyword == '-' or not keyword) and not owned_products:
        return _build_special_result_prompt(account, "38-2, 38-1"), {}
    
    # 1-3. 관심사 없고 제품만 있음
    if keyword == '-' or not keyword:
        return _handle_no_keyword_case(account, data_loader)
    
    # 1-6. 관심사 있고 제품 없음
    if not owned_products:
        return _handle_no_products_case(account, data_loader)
    
    # 1-4. 단일 키워드 매칭 특별 처리
    matched_stories = data_loader.get_stories_by_keyword(keyword)
    if len(matched_stories) == 1:
        return _handle_single_keyword_case(account, matched_stories[0], data_loader)
    
    # 1-5. 혼합 키워드 전략 (확장 조건)
    if len(matched_stories) >= 2:
        perfect_match_story = _find_perfect_match_story(account, matched_stories, data_loader)
        if perfect_match_story:
            return _handle_expansion_case(account, perfect_match_story, data_loader)
    
    # 일반 등수제 로직 (기존 방식)
    candidate_stories = _get_candidate_stories(account, data_loader)
    integrated_stories = _build_integrated_stories(account, candidate_stories, data_loader)
    prompt = _assemble_integrated_prompt(account, integrated_stories, fixed_story_id)
    
    return prompt, integrated_stories


def _build_special_result_prompt(account: Dict[str, Any], result: str) -> str:
    """특별 결과용 프롬프트 생성 (즉시 결과 반환)"""
    account_name = account.get('Account', account.get('계정명', ''))
    owned_products_str = account.get('보유제품', '').strip()
    owned_products = [] if owned_products_str == '-' or not owned_products_str else [p.strip() for p in owned_products_str.split(',') if p.strip()]
    
    return f"""<account_info>
- Account: {account_name}
- 관심사키워드: {account.get('관심사키워드', '')}
- 보유제품: {json.dumps(owned_products, ensure_ascii=False)}
</account_info>

최종 스토리 도출: {result}
"""


def _handle_no_keyword_case(account: Dict[str, Any], data_loader) -> tuple[str, Dict[str, Any]]:
    """1-3. 관심사 없고 제품만 있음 처리"""
    # 모든 스토리에서 제품 매칭도 계산하여 1등, 2등 선정
    all_stories = data_loader.get_all_stories()
    integrated_stories = _build_integrated_stories(account, all_stories, data_loader)
    
    # 제품 매칭도 기준으로 정렬
    sorted_stories = sorted(integrated_stories.items(), 
                           key=lambda x: (-x[1]['match_cnt'], x[0]))  # match_cnt 내림차순, story_id 오름차순
    
    if len(sorted_stories) >= 2:
        rank1_id = sorted_stories[0][0]
        rank2_id = sorted_stories[1][0]
        result = f"{rank1_id}, {rank2_id}"
    else:
        result = "38-2, 38-1"  # 기본값
    
    return _build_special_result_prompt(account, result), {}


def _handle_no_products_case(account: Dict[str, Any], data_loader) -> tuple[str, Dict[str, Any]]:
    """1-6. 관심사 있고 제품 없음 처리"""
    keyword = account.get('관심사키워드', '').strip()
    matched_stories = data_loader.get_stories_by_keyword(keyword)
    
    if len(matched_stories) >= 2:
        # 스토리 ID 순서로 정렬하여 첫 2개 선택
        sorted_stories = sorted(matched_stories, key=lambda x: x.get('스토리ID', ''))
        result = f"{sorted_stories[0]['스토리ID']}, {sorted_stories[1]['스토리ID']}"
    elif len(matched_stories) == 1:
        result = f"{matched_stories[0]['스토리ID']}, 38-1"  # 기본 스토리와 조합
    else:
        result = "38-2, 38-1"  # 기본값
    
    return _build_special_result_prompt(account, result), {}


def _handle_single_keyword_case(account: Dict[str, Any], keyword_story: Dict[str, Any], data_loader) -> tuple[str, Dict[str, Any]]:
    """1-4. 단일 키워드 매칭 특별 처리"""
    rank1_id = keyword_story['스토리ID']
    
    # 전체 스토리에서 보유제품 매칭도 최고 스토리 선택 (키워드 스토리 제외)
    all_stories = data_loader.get_all_stories()
    other_stories = [s for s in all_stories if s['스토리ID'] != rank1_id]
    
    if other_stories:
        integrated_stories = _build_integrated_stories(account, other_stories, data_loader)
        sorted_stories = sorted(integrated_stories.items(), 
                               key=lambda x: (-x[1]['match_cnt'], x[0]))
        rank2_id = sorted_stories[0][0]
    else:
        rank2_id = "38-1"  # 기본값
    
    result = f"{rank1_id}, {rank2_id}"
    return _build_special_result_prompt(account, result), {}


def _find_perfect_match_story(account: Dict[str, Any], matched_stories: List[Dict[str, Any]], data_loader) -> Optional[Dict[str, Any]]:
    """해당 키워드 스토리 중 완벽 매칭 스토리 찾기"""
    integrated_stories = _build_integrated_stories(account, matched_stories, data_loader)
    
    perfect_matches = []
    for story_id, data in integrated_stories.items():
        if data.get('mismatch_cnt', 0) == 0:
            perfect_matches.append(story_id)
    
    # 완벽 매칭이 정확히 1개인 경우만 반환
    if len(perfect_matches) == 1:
        return next(s for s in matched_stories if s['스토리ID'] == perfect_matches[0])
    
    return None


def _handle_expansion_case(account: Dict[str, Any], perfect_match_story: Dict[str, Any], data_loader) -> tuple[str, Dict[str, Any]]:
    """1-5. 혼합 키워드 전략 (확장 조건) 처리"""
    rank1_id = perfect_match_story['스토리ID']
    
    # 다른 관심사키워드에서 보유제품 매칭도 최고 스토리 선택
    all_stories = data_loader.get_all_stories()
    other_keyword_stories = [s for s in all_stories 
                            if s.get('관심사키워드', '') != perfect_match_story.get('관심사키워드', '')]
    
    if other_keyword_stories:
        integrated_stories = _build_integrated_stories(account, other_keyword_stories, data_loader)
        sorted_stories = sorted(integrated_stories.items(), 
                               key=lambda x: (-x[1]['match_cnt'], x[0]))
        rank2_id = sorted_stories[0][0]
    else:
        rank2_id = "38-1"  # 기본값
    
    result = f"{rank1_id}, {rank2_id}"
    return _build_special_result_prompt(account, result), {}


def build_product_prompt(account: Dict[str, Any], story_ids: List[str], data_loader) -> str:
    """제품 추천 프롬프트 생성"""
    # 보유제품 파싱
    owned_products_str = account.get('보유제품', '').strip()
    if owned_products_str == '-' or not owned_products_str:
        owned_products = []
    else:
        owned_products = [p.strip() for p in owned_products_str.split(',') if p.strip()]
    
    # 스토리별 제품 구성 분석
    story_products = {}
    product_columns = data_loader.get_product_columns()
    
    for story_id in story_ids:
        story = data_loader.get_story_by_id(story_id)
        if story:
            products = {}
            for col in product_columns:
                product_value = story.get(col, '').strip()
                if product_value:
                    products[col] = product_value
            story_products[story_id] = products
    
    # 프롬프트 조립
    user_prompt = f"""<account_info>
- Account: {account.get('Account', '')}
- 관심사키워드: {account.get('관심사키워드', '')}
- 보유제품: {json.dumps(owned_products, ensure_ascii=False)}
</account_info>

<story_info>
- 추천된 스토리: {json.dumps(story_ids, ensure_ascii=False)}
- 스토리별 제품 구성:
"""
    
    for story_id, products in story_products.items():
        user_prompt += f"  - {story_id}: {json.dumps(products, ensure_ascii=False)}\n"
    
    user_prompt += "</story_info>"
    
    return user_prompt