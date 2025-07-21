"""
백그라운드 스케줄러 모듈
주기적으로 오래된 파일들을 정리하고 시스템 상태를 모니터링합니다.
"""

import schedule
import time
import threading
from datetime import datetime
from file_cleanup import cleanup_old_files, get_disk_usage
from logging_config import get_logger

logger = get_logger(__name__)

class BackgroundScheduler:
    """백그라운드 작업을 관리하는 스케줄러"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """스케줄러를 시작합니다."""
        if self.running:
            logger.warning("스케줄러가 이미 실행 중입니다.")
            return
        
        self._setup_jobs()
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("백그라운드 스케줄러 시작됨")
    
    def stop(self):
        """스케줄러를 중지합니다."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("백그라운드 스케줄러 중지됨")
    
    def _setup_jobs(self):
        """스케줄 작업들을 설정합니다."""
        
        # 매시간마다 오래된 파일 정리 (24시간 이상)
        schedule.every().hour.do(self._cleanup_old_files_job)
        
        # 매일 자정에 디스크 사용량 로깅
        schedule.every().day.at("00:00").do(self._log_disk_usage_job)
        
        # 30분마다 시스템 상태 체크
        schedule.every(30).minutes.do(self._system_health_check_job)
        
        logger.info("스케줄 작업 설정 완료")
    
    def _run_scheduler(self):
        """스케줄러 메인 루프"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
            except Exception as e:
                logger.error(f"스케줄러 실행 중 오류: {e}")
                time.sleep(60)
    
    def _cleanup_old_files_job(self):
        """오래된 파일 정리 작업"""
        try:
            deleted_count = cleanup_old_files(24)  # 24시간 이상된 파일 삭제
            logger.info(f"정기 파일 정리 완료: {deleted_count}개 파일 삭제")
        except Exception as e:
            logger.error(f"정기 파일 정리 실패: {e}")
    
    def _log_disk_usage_job(self):
        """디스크 사용량 로깅 작업"""
        try:
            usage = get_disk_usage()
            total_size_mb = sum(dir_info.get('size_mb', 0) for dir_info in usage.values())
            total_files = sum(dir_info.get('files', 0) for dir_info in usage.values())
            
            logger.info(f"디스크 사용량 - 총 {total_size_mb:.2f}MB, {total_files}개 파일")
            
            for dir_name, info in usage.items():
                logger.info(f"  {dir_name}: {info.get('size_mb', 0):.2f}MB, {info.get('files', 0)}개 파일")
                
        except Exception as e:
            logger.error(f"디스크 사용량 로깅 실패: {e}")
    
    def _system_health_check_job(self):
        """시스템 상태 체크 작업"""
        try:
            usage = get_disk_usage()
            total_size_mb = sum(dir_info.get('size_mb', 0) for dir_info in usage.values())
            
            # 임시 파일이 1GB 이상이면 경고
            if total_size_mb > 1024:
                logger.warning(f"임시 파일 사용량 과다: {total_size_mb:.2f}MB")
                
                # 강제 정리 (12시간 이상된 파일)
                deleted_count = cleanup_old_files(12)
                logger.info(f"강제 파일 정리 실행: {deleted_count}개 파일 삭제")
            
        except Exception as e:
            logger.error(f"시스템 상태 체크 실패: {e}")

# 전역 스케줄러 인스턴스
background_scheduler = BackgroundScheduler()

def start_background_tasks():
    """백그라운드 작업을 시작합니다."""
    background_scheduler.start()

def stop_background_tasks():
    """백그라운드 작업을 중지합니다."""
    background_scheduler.stop()

if __name__ == "__main__":
    # 테스트 실행
    print("백그라운드 스케줄러 테스트 시작...")
    start_background_tasks()
    
    try:
        # 테스트를 위해 잠시 대기
        time.sleep(65)  # 1분 조금 넘게 대기
    except KeyboardInterrupt:
        print("테스트 중단됨")
    
    stop_background_tasks()
    print("테스트 완료")