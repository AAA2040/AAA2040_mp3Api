import os
import requests
from dotenv import load_dotenv
from logging_config import get_logger

# 환경 변수 로드
load_dotenv()

# 환경 변수 가져오기
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '300'))

# 로깅 설정
logger = get_logger(__name__)

def get_lyrics_server_url():
    try:
        with open("whisper_server_url.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logger.warning(f"whisper_server_url.txt 파일을 읽을 수 없습니다: {e}")
        return None

def req_lyrics(vocals_url):
    """외부 Whisper 서버를 통해 가사를 추출합니다."""
    LYRICS_SERVER_URL = get_lyrics_server_url()
    
    if not vocals_url:
        logger.warning("vocals_url이 제공되지 않았습니다.")
        return None
    
    if not LYRICS_SERVER_URL:
        logger.warning("LYRICS_SERVER_URL이 설정되지 않았습니다.")
        return None
    
    try:
        logger.info(f"가사 추출 요청 시작: {vocals_url}")
        
        # 요청 헤더 설정
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MP3API/1.0'
        }
        
        # 요청 데이터 준비
        request_data = {"vocal_url": vocals_url}
        
        # Whisper 서버에 가사 추출 요청
        response = requests.post(
            f"{LYRICS_SERVER_URL}/lyrics",
            json=request_data,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        
        # 응답 상태 코드 확인
        if response.status_code == 200:
            try:
                response_data = response.json()
                lyrics_text = response_data.get("lyrics")
                
                if lyrics_text:
                    logger.info(f"가사 추출 성공: {len(lyrics_text)} 문자")
                    return lyrics_text
                else:
                    logger.warning("응답에서 가사를 찾을 수 없습니다.")
                    return None
                    
            except ValueError as e:
                logger.error(f"JSON 파싱 실패: {e}")
                logger.error(f"응답 내용: {response.text[:200]}...")
                return None
                
        elif response.status_code == 404:
            logger.error("Whisper 서버의 /lyrics 엔드포인트를 찾을 수 없습니다.")
            return None
            
        elif response.status_code == 500:
            logger.error("Whisper 서버 내부 오류 발생")
            return None
            
        else:
            logger.error(f"Whisper 서버 오류 {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"가사 추출 요청 타임아웃 ({REQUEST_TIMEOUT}초)")
        return None
        
    except requests.exceptions.ConnectionError:
        logger.error(f"Whisper 서버 연결 실패: {LYRICS_SERVER_URL}")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"가사 추출 요청 실패: {e}")
        return None
        
    except Exception as e:
        logger.error(f"가사 추출 중 예상치 못한 오류: {e}")
        return None