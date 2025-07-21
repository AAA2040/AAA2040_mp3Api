"""
로깅 설정 모듈
모든 모듈에서 통일된 로깅 설정을 사용할 수 있도록 합니다.
"""

import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def setup_logging():
    """프로젝트 전체의 로깅을 설정합니다."""
    
    # 로그 디렉토리 생성
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로그 레벨 설정 (환경 변수에서 가져오기)
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # 날짜별 로그 파일 이름
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'mp3api_{current_date}.log')
    
    # 로그 포맷 설정
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 루트 로거 설정
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # 파일 핸들러 (모든 로그)
            logging.FileHandler(log_file, encoding='utf-8'),
            # 콘솔 핸들러 (INFO 이상만)
            logging.StreamHandler()
        ]
    )
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('firebase_admin').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    
    # 로깅 설정 완료 메시지
    logger = logging.getLogger(__name__)
    logger.info(f"로깅 시스템 초기화 완료 - 레벨: {log_level}, 파일: {log_file}")
    
    return logger

def get_logger(name):
    """모듈별 로거를 반환합니다."""
    return logging.getLogger(name)

# 프로젝트 시작 시 자동으로 로깅 설정
if __name__ == "__main__":
    setup_logging()