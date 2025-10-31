#!/usr/bin/env python3
"""SmartThings 통합 추천 시스템 - 메인 실행 파일"""

import os
import sys
import logging
from dotenv import load_dotenv
from processor import SmartThingsProcessor

# 로거 설정
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# HTTP 요청 로그 숨기기
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


def load_config() -> dict:
    """env.user 파일에서 설정을 로드"""
    # env.user 파일 로드
    if not os.path.exists("env.user"):
        logger.error("❌ 오류: env.user 파일이 없습니다.")
        sys.exit(1)
    
    try:
        load_dotenv("env.user")
    except Exception as e:
        logger.error(f"❌ 오류: env.user 파일을 읽을 수 없습니다: {e}")
        sys.exit(1)
    
    # 설정 값들을 딕셔너리로 구성
    config = {
        'openai_api_key': os.getenv("OPENAI_API_KEY"),
        'model_name': os.getenv("MODEL_NAME", "gpt-4o-mini"),
        'account_csv_path': os.getenv("ACCOUNT_CSV_PATH", "data/account.csv"),
        'story_csv_path': os.getenv("STORY_CSV_PATH", "data/story.csv"),
        'story_prompt_path': os.getenv("STORY_PROMPT_PATH", "prompt/story_prompt.md"),
        'product_prompt_path': os.getenv("PRODUCT_PROMPT_PATH", "prompt/product_prompt.md"),
        'output_directory': os.getenv("OUTPUT_DIRECTORY", "output")
    }
    
    return config


def validate_config(config: dict) -> bool:
    """설정 값들을 검증"""
    # API 키 확인
    if not config['openai_api_key'] or config['openai_api_key'] == "your_openai_api_key_here":
        logger.error("❌ 오류: OpenAI API 키가 설정되지 않았습니다.")
        logger.error("env.user 파일에서 OPENAI_API_KEY를 설정해주세요.")
        return False
    
    logger.info("✅ API 키 확인됨")
    
    # 필수 파일들 확인
    required_files = [
        ('account_csv_path', '계정 CSV 파일'),
        ('story_csv_path', '스토리 CSV 파일'),
        ('story_prompt_path', '스토리 프롬프트 파일'),
        ('product_prompt_path', '제품 프롬프트 파일')
    ]
    
    for config_key, description in required_files:
        file_path = config[config_key]
        if not os.path.exists(file_path):
            logger.error(f"❌ 오류: {description}을 찾을 수 없습니다: {file_path}")
            logger.error(f"env.user 파일에서 {config_key.upper()}를 확인해주세요.")
            return False
        logger.info(f"✅ {description} 확인됨: {file_path}")
    return True


def main():
    """메인 실행 함수"""
    try:
        # 설정 로드 및 검증
        config = load_config()
        
        if not validate_config(config):
            input("\n아무 키나 눌러서 종료...")
            sys.exit(1)
        
        # 처리기 실행
        processor = SmartThingsProcessor(config)
        processor.run()
        
    except KeyboardInterrupt:
        logger.warning("⚠️ 사용자 중단")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ 시스템 오류: {e}")
        input("\n아무 키나 눌러서 종료...")
        sys.exit(1)


if __name__ == "__main__":
    main()