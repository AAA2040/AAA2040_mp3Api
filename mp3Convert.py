import subprocess
import os
from dotenv import load_dotenv
from logging_config import get_logger

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logger = get_logger(__name__)

def convert_to_192kbps(uriId):
    """비트레이트를 128kbps로 변환하고 임시 파일을 정리합니다."""
    
    if not uriId:
        raise ValueError("uriId가 필요합니다.")
    
    # 디렉토리 생성
    if not os.path.exists('cvt'):
        os.makedirs('cvt')
    
    # 입력 파일 경로
    input_no_vocals = f'separated/htdemucs/{uriId}/no_vocals.mp3'
    input_vocals = f'separated/htdemucs/{uriId}/vocals.mp3'
    
    # 출력 파일 경로
    output_no_vocals = f'cvt/{uriId}_no_vocals.mp3'
    output_vocals = f'cvt/{uriId}_vocals.mp3'
    
    # 입력 파일 존재 확인
    if not os.path.exists(input_no_vocals):
        raise FileNotFoundError(f"입력 파일이 존재하지 않습니다: {input_no_vocals}")
    
    if not os.path.exists(input_vocals):
        raise FileNotFoundError(f"입력 파일이 존재하지 않습니다: {input_vocals}")
    
    try:
        # no_vocals 변환
        logger.info(f"no_vocals 변환 시작: {uriId}")
        command_no_vocals = [
            'ffmpeg',
            '-i', input_no_vocals,
            '-b:a', '128k',
            '-y',
            output_no_vocals
        ]
        result = subprocess.run(command_no_vocals, check=True, capture_output=True, text=True)
        logger.info(f"no_vocals 변환 완료: {uriId}")
        
        # vocals 변환
        logger.info(f"vocals 변환 시작: {uriId}")
        command_vocals = [
            'ffmpeg',
            '-i', input_vocals,
            '-b:a', '128k',
            '-y',
            output_vocals
        ]
        result = subprocess.run(command_vocals, check=True, capture_output=True, text=True)
        logger.info(f"vocals 변환 완료: {uriId}")
        
        # 출력 파일 존재 확인
        if not os.path.exists(output_no_vocals):
            raise FileNotFoundError(f"변환된 파일이 생성되지 않았습니다: {output_no_vocals}")
        
        if not os.path.exists(output_vocals):
            raise FileNotFoundError(f"변환된 파일이 생성되지 않았습니다: {output_vocals}")
        
        # 임시 파일 정리
        try:
            if os.path.exists(input_no_vocals):
                os.remove(input_no_vocals)
                logger.info(f"임시 파일 삭제: {input_no_vocals}")
            
            if os.path.exists(input_vocals):
                os.remove(input_vocals)
                logger.info(f"임시 파일 삭제: {input_vocals}")
        except Exception as e:
            logger.warning(f"임시 파일 삭제 실패 (계속 진행): {e}")
        
        logger.info(f"비트레이트 변환 완료: {uriId}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg 변환 실패: {e.stderr if e.stderr else str(e)}")
        raise Exception(f"비트레이트 변환에 실패했습니다: {e.stderr if e.stderr else str(e)}")
    
    except Exception as e:
        logger.error(f"비트레이트 변환 중 오류: {e}")
        raise