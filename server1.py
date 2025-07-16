#pip install fastapi uvicorn

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
import re
import os
from url_to_mp3 import url_to_mp3
from mp3Separate import mp3_separate
from mp3Convert import convert_to_192kbps

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
    if not os.path.exists(result_path):
        url_to_mp3(url)
        mp3_separate(uriId)
        convert_to_192kbps(uriId)

    # 파일이 생성되었는지 확인
    if os.path.exists(result_path):
        return {"result": "success"} #200
    raise HTTPException(status_code=500, detail="파일 생성에 실패했습니다.")

@app.get("/download/{uri_id}/no_vocals")
def down_no_vocals(uri_id: str):

    # 파일 다운로드 응답
    return FileResponse(f'cvt/{uri_id}_no_vocals.mp3', media_type='audio/mpeg', filename=f"{uri_id}_no_vocals.mp3")

@app.get("/download/{uri_id}/vocals")
def down_vocals(uri_id: str):

    # 파일 다운로드 응답
    return FileResponse(f'cvt/{uri_id}_vocals.mp3', media_type='audio/mpeg', filename=f"{uri_id}_vocals.mp3")