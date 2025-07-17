import os
import requests

add = "https://71f5d29b1c09.ngrok-free.app"

def req_lyrics(vocals_url):

    # 가사 추출 요청
    try:
        whisper_response = requests.post(
            f"{add}/lyrics",  # ← 당신이 만든 Whisper 서버 주소
            json={"vocal_url": vocals_url},
            timeout=300 # 5분
        )
        if whisper_response.status_code == 200:
            lyrics_text = whisper_response.json().get("lyrics")
            print(f"[디버그] Whisper 서버에서 받은 lyrics_text: {lyrics_text}")
        else:
            print(f"[Whisper 오류] {whisper_response.status_code}: {whisper_response.text}")
            return None
    except Exception as e:
        print(f"[Whisper 호출 실패] {e}")
        return None
        
    return lyrics_text