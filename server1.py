#uvicorn server1:app --reload

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
import re
import os
import requests
from logging_config import setup_logging, get_logger
from url_to_mp3 import url_to_mp3
from mp3Separate import mp3_separate
from mp3Convert import convert_to_192kbps
from dbSender import fileUpload_to_firebase, SongDBUpload, save_songDB_upload
from lyrics_Sender import req_lyrics
from file_cleanup import cleanup_uri_files, cleanup_failed_files
from scheduler import start_background_tasks
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 시스템 초기화
setup_logging()
logger = get_logger(__name__)

# 백그라운드 작업 시작
start_background_tasks()

# 환경 변수 가져오기
CALLBACK_SERVER_URL = os.getenv('CALLBACK_SERVER_URL', 'https://f2e082c5c354.ngrok-free.app')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '300'))

# 디렉토리 생성
os.makedirs('cvt', exist_ok=True)
os.makedirs('mp3Raw', exist_ok=True)
os.makedirs('separated', exist_ok=True)

app = FastAPI()

@app.post("/process")
async def process_youtube(request: Request):
    uriId = None
    try:
        # JSON 파싱 에러 핸들링
        try:
            data = await request.json()
        except Exception as e:
            logger.error(f"JSON 파싱 실패: {e}")
            raise HTTPException(status_code=400, detail="잘못된 JSON 형식입니다.")
        
        url = data.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="url이 필요합니다.")

        # 유튜브 ID 추출
        uriId_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
        if uriId_match:
            uriId = uriId_match.group(1)
            logger.info(f"유튜브 ID 추출 성공: {uriId}")
        else:
            logger.error(f"유효하지 않은 유튜브 URL: {url}")
            raise HTTPException(status_code=400, detail="유효한 유튜브 ID를 찾을 수 없습니다.")

        # 이미 파일이 있으면 바로 반환
        vocals_path = f'cvt/{uriId}_vocals.mp3'
        no_vocals_path = f'cvt/{uriId}_no_vocals.mp3'
        
        if os.path.exists(vocals_path) and os.path.exists(no_vocals_path):
            logger.info(f"로컬 파일 존재함 (과정 스킵): {uriId}")
        else:
            logger.info(f"로컬 파일 없음, 처리 시작: {uriId}")
            
            # YouTube 다운로드
            try:
                url_to_mp3(url)
                logger.info(f"YouTube 다운로드 완료: {uriId}")
            except Exception as e:
                logger.error(f"YouTube 다운로드 실패: {e}")
                raise HTTPException(status_code=500, detail=f"YouTube 다운로드에 실패했습니다: {str(e)}")
            
            # 음성 분리
            try:
                mp3_separate(uriId)
                logger.info(f"음성 분리 완료: {uriId}")
            except Exception as e:
                logger.error(f"음성 분리 실패: {e}")
                raise HTTPException(status_code=500, detail=f"음성 분리에 실패했습니다: {str(e)}")
            
            # 비트레이트 변환
            try:
                convert_to_192kbps(uriId)
                logger.info(f"비트레이트 변환 완료: {uriId}")
            except Exception as e:
                logger.error(f"비트레이트 변환 실패: {e}")
                raise HTTPException(status_code=500, detail=f"비트레이트 변환에 실패했습니다: {str(e)}")

        # 최종 파일 존재 확인
        if not (os.path.exists(vocals_path) and os.path.exists(no_vocals_path)):
            logger.error(f"처리 후 파일이 존재하지 않음: {uriId}")
            raise HTTPException(status_code=500, detail="파일 처리가 완료되지 않았습니다.")

        # Firebase 업로드
        vocals_url = None
        no_vocals_url = None
        try:
            vocals_url = fileUpload_to_firebase(f"vocals/{uriId}_vocals.mp3", vocals_path)
            no_vocals_url = fileUpload_to_firebase(f"no_vocals/{uriId}_no_vocals.mp3", no_vocals_path)
            logger.info(f"Firebase 업로드 완료: {uriId}")
        except Exception as e:
            logger.error(f"Firebase 업로드 실패: {e}")
            raise HTTPException(status_code=500, detail=f"파일 업로드에 실패했습니다: {str(e)}")
         
        # 가사 추출 (실패해도 계속 진행)
        lyrics_text = None
        try:
            lyrics_text = req_lyrics(vocals_url)
            logger.info(f"가사 추출 완료: {uriId}")
        except Exception as e:
            logger.warning(f"가사 추출 실패 (계속 진행): {e}")

        # Firestore 저장
        try:
            song_DBDict = SongDBUpload(
                vocal_mp3_url=vocals_url,
                mr_mp3_url=no_vocals_url,
                lyrics_url=lyrics_text
            )
            save_songDB_upload(uriId, song_DBDict)
            logger.info(f"Firestore 저장 완료: {uriId}")
        except Exception as e:
            logger.error(f"Firestore 저장 실패: {e}")
            # 저장 실패해도 결과는 반환

        # 콜백 전송 (실패해도 계속 진행)
        result_data = {
            "result": "success",
            "uriId": uriId,
            "no_vocals_url": no_vocals_url,
            "vocals_url": vocals_url,
            "lyrics": lyrics_text
        }
        
        try:
            response = requests.post(
                f"{CALLBACK_SERVER_URL}/",
                json=result_data,
                timeout=REQUEST_TIMEOUT
            )
            logger.info(f"콜백 전송 성공: {response.status_code}")
        except Exception as e:
            logger.warning(f"콜백 전송 실패 (계속 진행): {e}")

        # 처리 완료 후 임시 파일 정리
        try:
            cleanup_uri_files(uriId, keep_final=True)
            logger.info(f"임시 파일 정리 완료: {uriId}")
        except Exception as e:
            logger.warning(f"임시 파일 정리 실패: {e}")

        return result_data

    except HTTPException:
        # HTTP 예외는 그대로 전달
        # 실패 시 모든 파일 정리
        if uriId:
            try:
                cleanup_failed_files(uriId)
                logger.info(f"실패한 처리 파일 정리 완료: {uriId}")
            except Exception as cleanup_error:
                logger.error(f"실패한 처리 파일 정리 실패: {cleanup_error}")
        raise
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        # 실패 시 모든 파일 정리
        if uriId:
            try:
                cleanup_failed_files(uriId)
                logger.info(f"실패한 처리 파일 정리 완료: {uriId}")
            except Exception as cleanup_error:
                logger.error(f"실패한 처리 파일 정리 실패: {cleanup_error}")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류가 발생했습니다: {str(e)}")


@app.get("/download/{uri_id}/no_vocals")
def down_no_vocals(uri_id: str):
    file_path = f'cvt/{uri_id}_no_vocals.mp3'
    
    if not os.path.exists(file_path):
        logger.error(f"파일이 존재하지 않음: {file_path}")
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    try:
        return FileResponse(file_path, media_type='audio/mpeg', filename=f"{uri_id}_no_vocals.mp3")
    except Exception as e:
        logger.error(f"파일 다운로드 실패: {e}")
        raise HTTPException(status_code=500, detail="파일 다운로드에 실패했습니다.")

@app.get("/download/{uri_id}/vocals")
def down_vocals(uri_id: str):
    file_path = f'cvt/{uri_id}_vocals.mp3'
    
    if not os.path.exists(file_path):
        logger.error(f"파일이 존재하지 않음: {file_path}")
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    try:
        return FileResponse(file_path, media_type='audio/mpeg', filename=f"{uri_id}_vocals.mp3")
    except Exception as e:
        logger.error(f"파일 다운로드 실패: {e}")
        raise HTTPException(status_code=500, detail="파일 다운로드에 실패했습니다.")

    