#pip install fastapi uvicorn
#uvicorn server1:app --reload

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
import re
import os
from url_to_mp3 import url_to_mp3
from mp3Separate import mp3_separate
from mp3Convert import convert_to_192kbps
from dbSender import fileUpload_to_firebase, SongDBUpload, save_songDB_upload
import requests

add = "https://71f5d29b1c09.ngrok-free.app"

app = FastAPI()

@app.post("/process")
async def process_youtube(request: Request):
    data = await request.json()
    url = data.get("url")
    
    if not url:
        raise HTTPException(status_code=400, detail="url이 필요합니다.")

    # 유튜브 ID 추출
    uriId = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
    if uriId:
        uriId = uriId.group(1)
    else:
        raise HTTPException(status_code=400, detail="유효한 유튜브 ID를 찾을 수 없습니다.")

    # 이미 파일이 있으면 바로 반환
    result_path = f'cvt/{uriId}_no_vocals.mp3'
    if not os.path.exists(result_path): # [수정] db에서 찾아야함
        url_to_mp3(url)
        mp3_separate(uriId)
        convert_to_192kbps(uriId)

    # 파일이 생성되었는지 확인
    if os.path.exists(result_path):

        # Firebase Storage에 업로드
        vocals_path = f'cvt/{uriId}_vocals.mp3'
        if os.path.exists(vocals_path):
            vocals_url = fileUpload_to_firebase(f"vocals/{uriId}_vocals.mp3",f'cvt/{uriId}_vocals.mp3')
            # 가사 추출 요청
            try:
                whisper_response = requests.post(
                    f"{add}/lyrics",  # ← 당신이 만든 Whisper 서버 주소
                    json={"vocal_url": vocals_url},
                    timeout=300
                )
                if whisper_response.status_code == 200:
                    lyrics_text = whisper_response.json().get("lyrics")
                    print(f"[디버그] Whisper 서버에서 받은 lyrics_text: {lyrics_text}")
                else:
                    print(f"[Whisper 오류] {whisper_response.status_code}: {whisper_response.text}")
            except Exception as e:
                print(f"[Whisper 호출 실패] {e}")
            no_vocals_url = fileUpload_to_firebase(f"no_vocals/{uriId}_no_vocals.mp3",f'cvt/{uriId}_no_vocals.mp3')

        # Firestore에 SongUpload 객체로 저장
        song_DBDict = SongDBUpload(
            vocal_mp3_url=vocals_url,
            mr_mp3_url=no_vocals_url,
            lyrics_url=lyrics_text if 'lyrics_text' in locals() else None
        )
        save_songDB_upload(uriId, song_DBDict)

        return {
            "result": "success",
            "uriId": uriId,
            "no_vocals_url": no_vocals_url,
            "vocals_url": vocals_url,
            "lyrics": lyrics_text if 'lyrics_text' in locals() else None
        }

    raise HTTPException(status_code=500, detail="파일 생성에 실패했습니다.")


@app.get("/download/{uri_id}/no_vocals")
def down_no_vocals(uri_id: str):

    # 파일 다운로드 응답
    return FileResponse(f'cvt/{uri_id}_no_vocals.mp3', media_type='audio/mpeg', filename=f"{uri_id}_no_vocals.mp3")

@app.get("/download/{uri_id}/vocals")
def down_vocals(uri_id: str):

    # 파일 다운로드 응답
    return FileResponse(f'cvt/{uri_id}_vocals.mp3', media_type='audio/mpeg', filename=f"{uri_id}_vocals.mp3")

    