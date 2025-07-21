import os
import demucs.separate
import shlex
from dotenv import load_dotenv
from logging_config import get_logger

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logger = get_logger(__name__)

def mp3_separate(uriId, device='cuda'):
    """음성을 vocals와 no_vocals로 분리합니다."""
    
    if not uriId:
        raise ValueError("uriId가 필요합니다.")
    
    # FFmpeg 경로 설정
    ffmpeg_dir = os.getenv('FFMPEG_PATH', r'ffmpeg-master-latest-win64-gpl-shared\bin')
    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
    
    # 입력 파일 경로
    input_file = f'mp3Raw/{uriId}.mp3'
    output_dir = f'separated/htdemucs/{uriId}'
    no_vocals_file = f'{output_dir}/no_vocals.mp3'
    vocals_file = f'{output_dir}/vocals.mp3'
    
    # 입력 파일 존재 확인
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"입력 파일이 존재하지 않습니다: {input_file}")
    
    # 이미 분리된 파일이 있는지 확인
    if os.path.exists(no_vocals_file) and os.path.exists(vocals_file):
        logger.info(f"이미 분리된 파일 존재: {uriId}")
        return
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # CUDA 기기로 시도
        logger.info(f"CUDA 기기로 음성 분리 시작: {uriId}")
        demucs.separate.main(shlex.split(f'--mp3 --two-stems vocals --device {device} "{input_file}"'))
        
        # 결과 파일 확인
        if os.path.exists(no_vocals_file) and os.path.exists(vocals_file):
            logger.info(f"CUDA 기기로 음성 분리 성공: {uriId}")
            return
        else:
            raise Exception("분리 후 파일이 생성되지 않았습니다.")
            
    except Exception as cuda_error:
        logger.warning(f"CUDA 기기 분리 실패: {cuda_error}")
        
        if device == 'cuda':
            try:
                # CPU로 다시 시도
                logger.info(f"CPU 기기로 음성 분리 시작: {uriId}")
                demucs.separate.main(shlex.split(f'--mp3 --two-stems vocals --device cpu "{input_file}"'))
                
                # 결과 파일 확인
                if os.path.exists(no_vocals_file) and os.path.exists(vocals_file):
                    logger.info(f"CPU 기기로 음성 분리 성공: {uriId}")
                    return
                else:
                    raise Exception("분리 후 파일이 생성되지 않았습니다.")
                    
            except Exception as cpu_error:
                logger.error(f"CPU 기기 분리도 실패: {cpu_error}")
                raise Exception(f"음성 분리에 실패했습니다. CUDA 오류: {cuda_error}, CPU 오류: {cpu_error}")
        else:
            # 다른 기기로 시도한 경우
            logger.error(f"{device} 기기 분리 실패: {cuda_error}")
            raise Exception(f"음성 분리에 실패했습니다: {cuda_error}")
