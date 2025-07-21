import yt_dlp
import os
import re
from dotenv import load_dotenv
from logging_config import get_logger
import platform

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logger = get_logger(__name__)

def url_to_mp3(url):
    """YouTube URL에서 MP3 파일을 다운로드합니다."""
    
    if not url:
        raise ValueError("URL이 필요합니다.")
    
    # YouTube URL 유효성 검사
    youtube_pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
    if not re.search(youtube_pattern, url):
        raise ValueError("유효하지 않은 YouTube URL입니다.")
    
    # 출력 디렉토리 생성
    if not os.path.exists('mp3Raw'):
        os.makedirs('mp3Raw')
    
    # YouTube ID 추출
    uriId_match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', url)
    if not uriId_match:
        raise ValueError("YouTube ID를 추출할 수 없습니다.")
    
    uriId = uriId_match.group(1)
    output_file = f'mp3Raw/{uriId}.mp3'
    
    # 이미 다운로드된 파일이 있는지 확인
    if os.path.exists(output_file):
        logger.info(f"이미 다운로드된 파일 존재: {uriId}")
        return
    
    try:
        logger.info(f"YouTube 다운로드 시작: {url}")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'mp3Raw/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': os.getenv('DEFAULT_BITRATE', '128').replace('k', ''),
            }],
            'quiet': True,  # 에러 로깅을 위해 quiet 모드 활성화
            'noplaylist': True,
            'extractaudio': True,
            'audioformat': 'mp3',
        }
        
        # ffmpeg 경로 설정 (도커/리눅스에서는 /usr/bin/ffmpeg로 고정)
        if platform.system() == "Linux":
            ffmpeg_path = "/usr/bin/ffmpeg"
        else:
            ffmpeg_path = os.getenv('FFMPEG_PATH', "ffmpeg")
        ydl_opts['ffmpeg_location'] = ffmpeg_path
        
        # FFmpeg 경로 확인
        if not os.path.exists(ffmpeg_path):
            logger.warning(f"FFmpeg 경로가 존재하지 않습니다: {ffmpeg_path}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # 다운로드 결과 확인
        if not os.path.exists(output_file):
            raise FileNotFoundError(f"다운로드된 파일이 생성되지 않았습니다: {output_file}")
        
        # 파일 크기 확인
        file_size = os.path.getsize(output_file)
        if file_size == 0:
            os.remove(output_file)
            raise Exception("다운로드된 파일이 비어있습니다.")
        
        logger.info(f"YouTube 다운로드 완료: {uriId} ({file_size} bytes)")
        
    except yt_dlp.DownloadError as e:
        logger.error(f"yt-dlp 다운로드 오류: {e}")
        raise Exception(f"YouTube 다운로드에 실패했습니다: {str(e)}")
    
    except Exception as e:
        logger.error(f"YouTube 다운로드 중 오류: {e}")
        # 실패한 파일이 있다면 정리
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except:
                pass
        raise Exception(f"YouTube 다운로드에 실패했습니다: {str(e)}")