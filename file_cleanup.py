"""
임시 파일 정리 모듈
처리 과정에서 생성된 임시 파일들을 안전하게 정리합니다.
"""

import os
import shutil
import time
from datetime import datetime, timedelta
from typing import List, Optional
from logging_config import get_logger

logger = get_logger(__name__)

class FileCleanup:
    """파일 정리를 담당하는 클래스"""
    
    def __init__(self):
        self.temp_dirs = ['mp3Raw', 'separated', 'cvt']
        self.max_age_hours = 24  # 24시간 이상된 파일 삭제
    
    def cleanup_old_files(self, max_age_hours: Optional[int] = None) -> int:
        """지정된 시간보다 오래된 파일들을 정리합니다."""
        
        if max_age_hours is None:
            max_age_hours = self.max_age_hours
        
        cutoff_time = time.time() - (max_age_hours * 3600)
        deleted_count = 0
        
        logger.info(f"파일 정리 시작: {max_age_hours}시간 이상된 파일 삭제")
        
        for temp_dir in self.temp_dirs:
            if not os.path.exists(temp_dir):
                continue
                
            try:
                deleted_count += self._cleanup_directory(temp_dir, cutoff_time)
            except Exception as e:
                logger.error(f"디렉토리 정리 실패 {temp_dir}: {e}")
        
        logger.info(f"파일 정리 완료: {deleted_count}개 파일 삭제됨")
        return deleted_count
    
    def _cleanup_directory(self, directory: str, cutoff_time: float) -> int:
        """디렉토리 내의 오래된 파일들을 정리합니다."""
        
        deleted_count = 0
        
        for root, dirs, files in os.walk(directory):
            # 파일 정리
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.debug(f"파일 삭제: {file_path}")
                except Exception as e:
                    logger.warning(f"파일 삭제 실패 {file_path}: {e}")
            
            # 빈 디렉토리 정리
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if self._is_directory_empty(dir_path) and os.path.getmtime(dir_path) < cutoff_time:
                        os.rmdir(dir_path)
                        logger.debug(f"빈 디렉토리 삭제: {dir_path}")
                except Exception as e:
                    logger.warning(f"디렉토리 삭제 실패 {dir_path}: {e}")
        
        return deleted_count
    
    def _is_directory_empty(self, directory: str) -> bool:
        """디렉토리가 비어있는지 확인합니다."""
        try:
            return len(os.listdir(directory)) == 0
        except:
            return False
    
    def cleanup_by_uri_id(self, uri_id: str, keep_final_files: bool = True) -> bool:
        """특정 URI ID와 관련된 임시 파일들을 정리합니다."""
        
        if not uri_id:
            logger.warning("URI ID가 제공되지 않았습니다.")
            return False
        
        logger.info(f"URI ID별 파일 정리 시작: {uri_id}")
        
        try:
            # mp3Raw 파일 정리
            raw_file = f'mp3Raw/{uri_id}.mp3'
            if os.path.exists(raw_file):
                os.remove(raw_file)
                logger.debug(f"원본 파일 삭제: {raw_file}")
            
            # separated 디렉토리 정리
            separated_dir = f'separated/htdemucs/{uri_id}'
            if os.path.exists(separated_dir):
                shutil.rmtree(separated_dir)
                logger.debug(f"분리 디렉토리 삭제: {separated_dir}")
            
            # cvt 파일들은 최종 결과물이므로 keep_final_files에 따라 결정
            if not keep_final_files:
                cvt_vocals = f'cvt/{uri_id}_vocals.mp3'
                cvt_no_vocals = f'cvt/{uri_id}_no_vocals.mp3'
                
                for file_path in [cvt_vocals, cvt_no_vocals]:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.debug(f"최종 파일 삭제: {file_path}")
            
            logger.info(f"URI ID별 파일 정리 완료: {uri_id}")
            return True
            
        except Exception as e:
            logger.error(f"URI ID별 파일 정리 실패 {uri_id}: {e}")
            return False
    
    def cleanup_failed_processing(self, uri_id: str) -> bool:
        """실패한 처리 과정의 파일들을 정리합니다."""
        
        logger.info(f"실패한 처리 파일 정리: {uri_id}")
        
        try:
            # 모든 관련 파일 삭제 (최종 파일 포함)
            return self.cleanup_by_uri_id(uri_id, keep_final_files=False)
        except Exception as e:
            logger.error(f"실패한 처리 파일 정리 실패 {uri_id}: {e}")
            return False
    
    def get_disk_usage(self) -> dict:
        """임시 디렉토리들의 디스크 사용량을 반환합니다."""
        
        usage = {}
        
        for temp_dir in self.temp_dirs:
            if not os.path.exists(temp_dir):
                usage[temp_dir] = {'size': 0, 'files': 0}
                continue
            
            total_size = 0
            file_count = 0
            
            try:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except:
                            continue
                
                usage[temp_dir] = {
                    'size': total_size,
                    'size_mb': round(total_size / (1024 * 1024), 2),
                    'files': file_count
                }
            except Exception as e:
                logger.error(f"디스크 사용량 확인 실패 {temp_dir}: {e}")
                usage[temp_dir] = {'size': 0, 'files': 0}
        
        return usage

# 전역 정리 함수들
cleanup_manager = FileCleanup()

def cleanup_old_files(max_age_hours: int = 24) -> int:
    """오래된 파일들을 정리합니다."""
    return cleanup_manager.cleanup_old_files(max_age_hours)

def cleanup_uri_files(uri_id: str, keep_final: bool = True) -> bool:
    """특정 URI의 파일들을 정리합니다."""
    return cleanup_manager.cleanup_by_uri_id(uri_id, keep_final)

def cleanup_failed_files(uri_id: str) -> bool:
    """실패한 처리의 파일들을 정리합니다."""
    return cleanup_manager.cleanup_failed_processing(uri_id)

def get_disk_usage() -> dict:
    """디스크 사용량을 반환합니다."""
    return cleanup_manager.get_disk_usage()

if __name__ == "__main__":
    # 테스트 실행
    print("디스크 사용량:", get_disk_usage())
    print("오래된 파일 정리:", cleanup_old_files(1))  # 1시간 이상된 파일 정리