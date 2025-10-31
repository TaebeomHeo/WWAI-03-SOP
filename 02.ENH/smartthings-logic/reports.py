#!/usr/bin/env python3
"""보고서 생성 모듈 - 간소화된 함수 기반"""

import os
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd


def generate_story_reasoning(results: List[Dict[str, Any]], output_dir: str = "output") -> str:
    """스토리 추천 reasoning MD 파일 생성"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"story_reasoning_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    content = []
    content.append("# 스토리 추천 상세 분석")
    content.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("")
    content.append("---")
    content.append("")
    
    for i, result in enumerate(results, 1):
        account_id = result['account_id']
        success = result['success']
        
        content.append(f"## {i}. {account_id}")
        content.append("")
        
        if success:
            content.append(f"**최종 결과**: {result['final_result']}")
            content.append(f"**스토리 ID**: {', '.join(result['story_ids'])}")
            content.append(f"**결과 타입**: {result['result_type']}")
            content.append(f"**처리 시간**: {result['processing_time']:.2f}초")
            content.append("")
            
            # 적용된 규칙
            if result.get('applied_rules'):
                content.append("**적용된 규칙**:")
                for rule in result['applied_rules']:
                    content.append(f"- {rule}")
                content.append("")
            
            # 추론 단계
            if result.get('reasoning_steps'):
                content.append("**추론 과정**:")
                for step in result['reasoning_steps']:
                    content.append(f"{step}")
                    content.append("")
            
            # 전체 응답 (접힌 형태로)
            if result.get('full_response'):
                content.append("<details>")
                content.append("<summary>전체 LLM 응답 보기</summary>")
                content.append("")
                content.append("```")
                content.append(result['full_response'])
                content.append("```")
                content.append("</details>")
                content.append("")
        else:
            content.append(f"**❌ 처리 실패**: {result.get('error_message', '알 수 없는 오류')}")
            content.append(f"**처리 시간**: {result['processing_time']:.2f}초")
            content.append("")
        
        content.append("---")
        content.append("")
    
    # 파일 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return filepath


def generate_product_reasoning(product_results: List[Dict[str, Any]], output_dir: str = "output") -> str:
    """제품 추천 reasoning MD 파일 생성"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"product_reasoning_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    content = []
    content.append("# 제품 추천 상세 분석")
    content.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("")
    content.append("---")
    content.append("")
    
    for i, result in enumerate(product_results, 1):
        account_id = result['account_id']
        
        content.append(f"## {i}. {account_id}")
        content.append("")
        
        if result.get('success') and result.get('products'):
            content.append(f"**추천 제품**: {', '.join(result['products'])}")
            content.append(f"**추천 개수**: {len(result['products'])}개")
            content.append("")
            
            # 전체 응답 (접힌 형태로)
            if result.get('full_response'):
                content.append("<details>")
                content.append("<summary>전체 LLM 응답 보기</summary>")
                content.append("")
                content.append("```")
                content.append(result['full_response'])
                content.append("```")
                content.append("</details>")
                content.append("")
        else:
            content.append("**❌ 제품 추천 실패**")
            if result.get('error'):
                content.append(f"오류: {result['error']}")
            content.append("")
        
        content.append("---")
        content.append("")
    
    # 파일 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return filepath


def generate_excel_report(story_results: List[Dict[str, Any]], 
                         product_results: List[Dict[str, Any]], 
                         output_dir: str = "output") -> str:
    """최종 통합 Excel 보고서 생성"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"final_results_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    # 데이터 준비
    excel_data = []
    
    for story_result in story_results:
        account_id = story_result['account_id']
        
        # 해당 계정의 제품 추천 결과 찾기
        product_result = next(
            (pr for pr in product_results if pr['account_id'] == account_id), 
            None
        )
        
        row = {
            'Account': account_id,
            'Success': story_result['success'],
            'Story1': '',
            'Story2': '',
            'Product1': '',
            'Product2': '',
            'Product3': '',
            'Product4': '',
            'Product5': '',
            'Processing_Time': f"{story_result['processing_time']:.2f}s",
            'Error': story_result.get('error_message', '')
        }
        
        # 스토리 결과 추가
        if story_result['success']:
            # 특례 조건 확인 (랜덤 출력인 경우)
            if story_result.get('result_type') == 'special_random' or '중 랜덤' in story_result.get('final_result', ''):
                # 특례 조건: Story1에 전체 랜덤 문구, Story2는 비움
                row['Story1'] = story_result.get('final_result', '')
                row['Story2'] = ''
            elif story_result.get('story_ids'):
                # 일반적인 경우: 개별 스토리 ID들
                story_ids = story_result['story_ids']
                if len(story_ids) >= 1:
                    row['Story1'] = story_ids[0]
                if len(story_ids) >= 2:
                    row['Story2'] = story_ids[1]
        
        # 제품 추천 결과 추가
        if product_result and product_result.get('success') and product_result.get('products'):
            products = product_result['products']
            for i, product in enumerate(products[:5], 1):
                row[f'Product{i}'] = product
        
        excel_data.append(row)
    
    # DataFrame 생성 및 Excel 저장
    df = pd.DataFrame(excel_data)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # 메인 결과 시트
        df.to_excel(writer, sheet_name='Results', index=False)
        
        # 요약 통계 시트
        successful_stories = sum(1 for r in story_results if r['success'])
        successful_products = sum(1 for r in product_results if r.get('success'))
        
        summary_data = {
            '항목': [
                '총 계정 수',
                '스토리 추천 성공',
                '스토리 추천 실패', 
                '스토리 성공률 (%)',
                '제품 추천 성공',
                '제품 추천 실패',
                '제품 성공률 (%)',
                '평균 처리 시간 (초)'
            ],
            '값': [
                len(story_results),
                successful_stories,
                len(story_results) - successful_stories,
                f"{successful_stories / len(story_results) * 100:.1f}" if story_results else "0.0",
                successful_products,
                len(product_results) - successful_products,
                f"{successful_products / len(product_results) * 100:.1f}" if product_results else "0.0",
                f"{sum(r['processing_time'] for r in story_results) / len(story_results):.2f}" if story_results else "0.00"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    return filepath


def generate_summary_report(story_results: List[Dict[str, Any]], 
                           product_results: List[Dict[str, Any]], 
                           output_dir: str = "output") -> str:
    """간단한 요약 보고서 생성"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"summary_report_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    successful_stories = sum(1 for r in story_results if r['success'])
    successful_products = sum(1 for r in product_results if r.get('success'))
    total_time = sum(r['processing_time'] for r in story_results)
    
    content = [
        "=" * 60,
        "SmartThings 추천 시스템 실행 결과 요약",
        "=" * 60,
        f"실행 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "📊 처리 결과:",
        f"  - 총 계정 수: {len(story_results)}개",
        f"  - 스토리 추천 성공: {successful_stories}개 ({successful_stories/len(story_results)*100:.1f}%)",
        f"  - 제품 추천 성공: {successful_products}개 ({successful_products/len(product_results)*100:.1f}%)",
        "",
        "⏱️ 성능 정보:",
        f"  - 총 처리 시간: {total_time:.1f}초",
        f"  - 평균 처리 시간: {total_time/len(story_results):.2f}초/계정",
        "",
        "=" * 60
    ]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return filepath