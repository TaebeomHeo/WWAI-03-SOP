#!/usr/bin/env python3
"""SmartThings 추천 시스템 - 핵심 처리 로직"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class DataLoader:
    """pandas 기반 CSV 데이터 로더"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.accounts_df = None
        self.stories_df = None
        self.load_data()
    
    def load_data(self):
        """탭 구분자 CSV 파일들을 pandas로 로드 (모든 값을 문자열로)"""
        account_path = self.config.get('account_csv_path', 'account.csv')
        story_path = self.config.get('story_csv_path', 'story.csv')
        
        # 계정 데이터 로드 (탭 구분자, 모든 컬럼을 문자열로, NaN 처리 방지)
        self.accounts_df = pd.read_csv(account_path, sep='\t', encoding='utf-8', dtype=str, keep_default_na=False, na_values=[])
        
        # 스토리 데이터 로드 (탭 구분자, 모든 컬럼을 문자열로, NaN 처리 방지)
        self.stories_df = pd.read_csv(story_path, sep='\t', encoding='utf-8', dtype=str, keep_default_na=False, na_values=[])
        
        logging.info(f"계정 데이터 로드: {len(self.accounts_df)}개")
        logging.info(f"스토리 데이터 로드: {len(self.stories_df)}개")
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        return self.accounts_df.to_dict('records')
    
    def get_account_by_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        account_row = self.accounts_df[self.accounts_df['Account'] == account_id]
        if not account_row.empty:
            return account_row.iloc[0].to_dict()
        return None
    
    def get_all_stories(self) -> List[Dict[str, Any]]:
        return self.stories_df.to_dict('records')
    
    def get_story_by_id(self, story_id: str) -> Optional[Dict[str, Any]]:
        story_row = self.stories_df[self.stories_df['스토리ID'] == story_id]
        if not story_row.empty:
            return story_row.iloc[0].to_dict()
        return None
    
    def get_stories_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        matched_stories = self.stories_df[self.stories_df['관심사키워드'] == keyword]
        return matched_stories.to_dict('records')
    
    def get_product_columns(self) -> List[str]:
        """제품 컬럼 목록 반환"""
        if self.stories_df is None or self.stories_df.empty:
            return []
        
        exclude_cols = ['스토리ID', '관심사키워드', '스토리명', '스토리설명']
        return [col for col in self.stories_df.columns if col not in exclude_cols]


def call_llm(system_prompt: str, user_prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """LLM API 호출"""
    model_name = config.get('model_name', 'gpt-4o-mini')
    
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.1,
        max_tokens=4000
    )
    
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        
        return {
            'success': True,
            'content': response.content,
            'estimated_tokens': 0
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'content': '',
            'estimated_tokens': 0
        }


def _extract_applied_rules(response_content: str) -> List[str]:
    """적용된 특별 규칙들을 추출"""
    import re
    applied_rules = []
    
    # 특별 처리 규칙 패턴들
    rule_patterns = [
        (r'특례 조건|특별.*랜덤', '1-1. 특례 조건'),
        (r'관심사.*없음.*제품.*없음|38-2.*38-1', '1-2. 관심사/제품 모두 없음'),
        (r'관심사.*없고.*제품.*있음', '1-3. 관심사 없고 제품만 있음'),
        (r'단일.*키워드.*매칭|키워드.*스토리.*1개', '1-4. 단일 키워드 매칭 특별 처리'),
        (r'혼합.*키워드.*전략', '1-5. 혼합 키워드 전략'),
        (r'관심사.*있고.*제품.*없음', '1-6. 관심사 있고 제품 없음'),
        (r'등수제.*로직|1단계|2단계|3단계|4단계|5단계', '등수제 핵심 로직')
    ]
    
    for pattern, rule_name in rule_patterns:
        if re.search(pattern, response_content, re.IGNORECASE):
            applied_rules.append(rule_name)
    
    return applied_rules


def _extract_reasoning_steps(response_content: str) -> List[str]:
    """추론 단계들을 추출"""
    import re
    reasoning_steps = []
    
    # 단계별 결과 패턴 추출
    step_patterns = re.findall(r'(\d+단계 결과:.*?)(?=\d+단계 결과:|최종 스토리 도출:|$)', 
                             response_content, re.DOTALL | re.IGNORECASE)
    
    for step in step_patterns:
        reasoning_steps.append(step.strip())
    
    # 특별 처리 메시지들 추출
    special_messages = re.findall(r'(⚠️.*?특별.*?처리.*?)(?=\n|$)', 
                                response_content, re.IGNORECASE)
    
    for msg in special_messages:
        reasoning_steps.append(msg.strip())
    
    return reasoning_steps


def parse_story_result(response_content: str) -> Dict[str, Any]:
    """LLM 응답에서 최종 결과 파싱"""
    import re
    
    result = {
        'success': False,
        'final_line': None,
        'story_ids': [],
        'result_type': 'unknown',
        'full_response': response_content,
        'applied_rules': [],
        'reasoning_steps': []
    }
    
    if not response_content:
        return result
    
    # 적용된 특별 규칙 감지
    result['applied_rules'] = _extract_applied_rules(response_content)
    
    # 추론 단계 추출
    result['reasoning_steps'] = _extract_reasoning_steps(response_content)
    
    # "최종 스토리 도출:" 패턴 검색
    final_match = re.search(r'최종 스토리 도출:\s*([^\n]+)', response_content, re.IGNORECASE)
    
    if not final_match:
        return result
    
    final_line = final_match.group(1).strip()
    result['final_line'] = final_line
    result['success'] = True
    
    # 스토리 ID 추출
    story_ids = re.findall(r'\b(\d{1,2}-\d{1,2})\b', final_line)
    result['story_ids'] = story_ids
    
    # 결과 타입 분석
    if '중 랜덤' in final_line:
        result['result_type'] = 'special_random'
    elif len(story_ids) == 2:
        result['result_type'] = 'normal_recommendation'
    elif len(story_ids) == 1:
        result['result_type'] = 'single_recommendation'
    else:
        result['result_type'] = 'unknown'
    
    return result


def process_single_account_story(account_id: str, data_loader: DataLoader, story_system_prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """단일 계정 스토리 추천 처리"""
    start_time = time.time()
    
    try:
        logging.info(f"계정 처리 시작: {account_id}")
        
        # 프롬프트 생성
        from prompts import build_story_prompt
        user_prompt, precalc_json = build_story_prompt(account_id, data_loader)
        
        # LLM 호출
        llm_result = call_llm(story_system_prompt, user_prompt, config)
        
        if not llm_result['success']:
            raise Exception(f"LLM API 호출 실패: {llm_result['error']}")
        
        # 결과 파싱
        parsed_result = parse_story_result(llm_result['content'])
        
        if not parsed_result['success']:
            raise Exception("결과 파싱 실패")
        
        processing_time = time.time() - start_time
        
        logging.info(f"계정 처리 완료: {account_id} -> {parsed_result['final_line']} ({processing_time:.2f}초)")
        
        return {
            'account_id': account_id,
            'success': True,
            'result_type': parsed_result['result_type'],
            'story_ids': parsed_result['story_ids'],
            'final_result': parsed_result['final_line'],
            'processing_time': processing_time,
            'error_message': None,
            'applied_rules': parsed_result['applied_rules'],
            'reasoning_steps': parsed_result['reasoning_steps'],
            'full_response': parsed_result['full_response']
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_message = str(e)
        
        logging.error(f"❌ 계정 처리 실패: {account_id} - {error_message} ({processing_time:.2f}초)")
        
        return {
            'account_id': account_id,
            'success': False,
            'result_type': 'error',
            'story_ids': [],
            'final_result': '',
            'processing_time': processing_time,
            'error_message': error_message
        }


# 제품 추천 헬퍼 함수들
def filter_owned_products(story_products: List[str], owned_products: List[str]) -> List[str]:
    """크로스셀링 필터링 로직 - 보유 제품 제외
    
    엑셀 공식 IF(COUNTIFS(보유제품, 스토리제품)>0, 제외, 포함)을 구현
    
    Args:
        story_products: 스토리에서 추출된 제품 목록
        owned_products: 사용자가 보유한 제품 목록
    
    Returns:
        보유하지 않은 제품들만 포함된 필터링된 목록
    """
    filtered = []
    for product in story_products:
        # COUNTIFS 로직: 보유제품에서 해당 제품 개수 확인
        count = owned_products.count(product)
        if count == 0:  # 보유하지 않은 제품만 포함
            filtered.append(product)
    return filtered


def should_add_mobile(recommended_products: List[str], owned_products: List[str]) -> bool:
    """Mobile 추가 자격 확인
    
    엑셀 공식 IF(AND(제품<>"Mobile", 사용자보유<>"Mobile"), 자격있음, 자격없음)을 구현
    
    Args:
        recommended_products: 현재 추천된 제품 목록
        owned_products: 사용자가 보유한 제품 목록
    
    Returns:
        Mobile 추가 자격이 있으면 True, 없으면 False
    """
    # 추천 제품에 Mobile이 없고, 사용자가 Mobile을 보유하지 않은 경우
    has_mobile_in_recommendations = 'Mobile' in recommended_products
    user_owns_mobile = 'Mobile' in owned_products
    
    return not has_mobile_in_recommendations and not user_owns_mobile


def get_business_unit(product: str) -> Optional[str]:
    """제품의 사업부 분류
    
    Args:
        product: 제품명
    
    Returns:
        사업부 코드 (MX, VD, DA) 또는 None (분류되지 않은 경우)
    """
    # 사업부별 제품 분류 정의
    BUSINESS_UNITS = {
        'MX': ['Mobile', 'Tab', 'Watch', 'Buds', 'SmartTag'],
        'VD': ['TV', 'Speaker'], 
        'DA': ['Refrigerator', 'Washer', 'Dryer', 'Air Conditioner', 
               'Robot Cleaner', 'Dish Washer', 'Oven', 'Cooktop']
    }
    
    for business_unit, products in BUSINESS_UNITS.items():
        if product in products:
            return business_unit
    
    return None

def process_single_account_product(account: Dict[str, Any], story_ids: List[str], 
                                     data_loader: DataLoader, product_system_prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """단일 계정 제품 추천 처리 (규칙 기반 프롬프트 사용)"""
    try:
        # 제품 추천 프롬프트 생성
        from prompts import build_product_prompt
        product_user_prompt = build_product_prompt(account, story_ids, data_loader)
        
        # LLM 호출 (규칙 기반 프롬프트 사용)
        llm_result = call_llm(product_system_prompt, product_user_prompt, config)
        
        if not llm_result['success']:
            raise Exception(f"제품 추천 LLM 호출 실패: {llm_result['error']}")
        
        # 결과 파싱 (규칙 기반 출력에 맞게 조정)
        import re
        response_content = llm_result['content']
        
        # "최종 제품 추천:" 패턴 검색
        final_match = re.search(r'최종 제품 추천:\s*([^\n]+)', response_content, re.IGNORECASE)
        
        if final_match:
            final_line = final_match.group(1).strip()
            
            # 규칙 기반 출력 파싱: "제품1 (Cross), 제품2 (Cross), ..." 또는 "제품1 (Up), 제품2 (Up), ..." 형식
            # (Cross), (Up), (추가) 태그를 제거하고 제품명만 추출
            products = []
            product_parts = [p.strip() for p in final_line.split(',') if p.strip()]
            
            for part in product_parts:
                # "(Cross)", "(Up)", "(Best)", "(추가)" 등의 태그와 대괄호 제거
                clean_product = re.sub(r'\s*\([^)]+\)\s*[\[\]]*\s*$', '', part).strip()
                # 남은 대괄호나 특수문자 제거
                clean_product = re.sub(r'[\[\]]+', '', clean_product).strip()
                if clean_product and clean_product != '```':
                    products.append(clean_product)
            
            return {
                'account_id': account['Account'],
                'success': True,
                'products': products,
                'full_response': response_content,
                'error': None
            }
        else:
            raise Exception("제품 추천 결과 파싱 실패")
        
    except Exception as e:
        logging.error(f"❌ 제품 추천 실패 (v2): {account['Account']} - {str(e)}")
        
        return {
            'account_id': account['Account'],
            'success': False,
            'products': [],
            'full_response': '',
            'error': str(e)
        }


class SmartThingsProcessor:
    """SmartThings 추천 시스템 핵심 처리기"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_loader = None
        self.story_system_prompt = None
        self.product_system_prompt = None
    
    def run(self) -> None:
        """전체 실행 흐름"""
        start_time = time.time()
        success = False
        errors_count = 0
        
        try:
            logging.info("🚀 시스템 실행 시작")
            
            # 컴포넌트 초기화
            from prompts import load_system_prompts
            from reports import generate_story_reasoning, generate_product_reasoning, generate_excel_report
            
            self.data_loader = DataLoader(self.config)
            self.story_system_prompt, self.product_system_prompt = load_system_prompts(self.config)
            
            # 모든 계정 처리
            story_results, product_results = self._process_accounts()
            
            # 결과 파일 생성
            self._generate_reports(story_results, product_results)
            
            # 통계 계산 및 출력
            successful_stories = sum(1 for r in story_results if r['success'])
            successful_products = sum(1 for r in product_results if r['success'])
            story_success_rate = successful_stories / len(story_results) * 100 if story_results else 0
            product_success_rate = successful_products / len(product_results) * 100 if product_results else 0
            total_time = time.time() - start_time
            
            logging.info("=" * 60)
            logging.info("📊 최종 결과 요약")
            logging.info(f"✅ 스토리 추천: {successful_stories}/{len(story_results)} ({story_success_rate:.1f}%)")
            logging.info(f"✅ 제품 추천: {successful_products}/{len(product_results)} ({product_success_rate:.1f}%)")
            logging.info(f"⏱️ 총 처리 시간: {total_time:.1f}초")
            logging.info("=" * 60)
            
            if errors_count > 0:
                logging.warning(f"⚠️ 실패: {errors_count}건")
            
            success = True
            
        except KeyboardInterrupt:
            logging.warning("⚠️ 사용자 중단")
            success = False
            
        except Exception as e:
            logging.error(f"❌ 오류 발생: {e}")
            success = False
        
        total_time = time.time() - start_time
        
        logging.info(f"🎯 최종 결과: {'성공' if success else '실패'} | {total_time:.1f}초")
        logging.info(f"⏰ 완료 시간: {datetime.now().strftime('%H:%M:%S')}")
        
        if not success:
            sys.exit(1)
    
    def _process_accounts(self) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """모든 계정 처리"""
        accounts = self.data_loader.get_all_accounts()
        story_results = []
        product_results = []
        
        logging.info(f"📊 총 {len(accounts)}개 계정 처리 시작")
        
        for i, account in enumerate(accounts, 1):
            account_id = account['Account']
            logging.info("📖 Phase 1: 스토리 추천 처리")
            logging.info(f"⏳ 추천 진행률: {i}/{len(accounts)} ({i/len(accounts)*100:.1f}%)")
            
            story_result = process_single_account_story(account_id, self.data_loader, self.story_system_prompt, self.config)
            story_results.append(story_result)
        
            # Phase 2: 제품 추천 (규칙 기반 프롬프트 사용)
            logging.info("🛍️ Phase 2: 제품 추천 처리 (규칙 기반)")
            if story_result['success'] and story_result.get('story_ids'):
                product_result = process_single_account_product(account, story_result['story_ids'], 
                                                                 self.data_loader, self.product_system_prompt, self.config)
            else:
                # 스토리 추천 실패 시 제품 추천도 실패 처리
                product_result = {
                    'account_id': account_id,
                    'success': False,
                    'products': [],
                    'full_response': '',
                    'error': '스토리 추천 실패로 인한 제품 추천 불가'
                }
            
            product_results.append(product_result)
        
        return story_results, product_results
    
    def _generate_reports(self, story_results: List[Dict[str, Any]], product_results: List[Dict[str, Any]]) -> None:
        """결과 파일 생성"""
        from reports import generate_story_reasoning, generate_product_reasoning, generate_excel_report
        
        logging.info("📄 Phase 3: 결과 파일 생성")
        
        output_dir = self.config.get('output_directory', 'output')
        
        # 1. 스토리 추천 상세 reasoning
        story_reasoning_file = generate_story_reasoning(story_results, output_dir)
        logging.info(f"📋 스토리 reasoning 파일: {story_reasoning_file}")
        
        # 2. 제품 추천 상세 reasoning  
        product_reasoning_file = generate_product_reasoning(product_results, output_dir)
        logging.info(f"🛍️ 제품 reasoning 파일: {product_reasoning_file}")
        
        # 3. 최종 통합 Excel 보고서
        excel_file = generate_excel_report(story_results, product_results, output_dir)
        logging.info(f"📊 최종 Excel 보고서: {excel_file}")