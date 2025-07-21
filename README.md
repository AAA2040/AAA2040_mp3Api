# YouTube MP3 Processing & Separation Service

> FastAPI 기반의 YouTube URL 입력으로 MP3 다운로드, 분리, 변환, Firebase 업로드, 가사 요청 및 외부 서버 연동을 제공하는 REST API

---

## 🚀 프로젝트 개요

`mp3Api`는 YouTube 영상 URL을 받아:

1. **MP3 다운로드** (`yt-dlp`)
2. **음원 분리** (`demucs`)으로 보컬/반주 트랙 생성
3. **오디오 변환** (`ffmpeg`)으로 192kbps로 인코딩
4. **Firebase Storage 업로드** 및 Firestore 저장
5. **가사 요청** (`lyrics_Sender`)
6. **외부 서버 전송**
7. **결과 응답** (트랙 URL, 가사)

를 순차적으로 처리하는 FastAPI 서비스입니다.

---

## 📦 기술 스택

* **언어**: Python 3.9+
* **웹 프레임워크**: FastAPI
* **ASGI 서버**: Uvicorn
* **MP3 다운로드**: yt-dlp (`url_to_mp3.py`)
* **음원 분리**: Demucs (`mp3Separate.py`)
* **오디오 변환**: ffmpeg (`mp3Convert.py` 포함된 바이너리 사용)
* **클라우드 스토리지**: Firebase Storage & Firestore (`dbSender.py`)
* **가사 요청**: 커스텀 서비스 (`lyrics_Sender.py`)
* **HTTP 요청**: requests

---

## 📁 디렉터리 구조

```
AAA2040_mp3Api-main/
├─ .gitignore
├─ README.md                  # 현재 파일
├─ server1.py                 # FastAPI 앱 엔트리포인트
├─ url_to_mp3.py              # YouTube → MP3 변환 유틸
├─ mp3Separate.py             # Demucs를 이용한 트랙 분리 유틸
├─ mp3Convert.py              # ffmpeg 기반 오디오 재인코딩 유틸
├─ lyrics_Sender.py           # 가사 요청 모듈
├─ dbSender.py                # Firebase Storage/Firestore 업로드 모듈
├─ requirements.txt           # Python 의존성
└─ ffmpeg-master-latest-win64-gpl-shared/  # Windows용 ffmpeg 바이너리
```

---

## 🔧 설치 및 실행

### 1. 클론

```bash
git clone <repo-url>
cd AAA2040_mp3Api-main
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
# 추가 설치
pip install -U demucs
pip install -U --pre "yt-dlp[default]"
```

### 3. Firebase 설정

* `repository/` 폴더에 Firebase 서비스 계정 키(JSON) 저장
* `dbSender.py` 내 `firebase_admin.initialize_app()` 호출 시 키 경로 설정

### 4. FastAPI 서버 실행

```bash
uvicorn server1:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 API 명세

### POST `/process`

* **Request Body** (JSON)

  ```json
  { "url": "https://www.youtube.com/watch?v=XYZ" }
  ```
* **Response** (JSON)

  ```json
  {
    "result": "success",
    "uriId": "XYZ",
    "no_vocals_url": "https://.../no_vocals/XYZ.mp3",
    "vocals_url": "https://.../vocals/XYZ.mp3",
    "lyrics": "[0.00 ~ 10.00] 가사..."
  }
  ```

### GET `/download/{uri_id}/no_vocals`

* **Response**: `FileResponse`로 `cvt/{uri_id}_no_vocals.mp3` 반환

### GET `/download/{uri_id}/vocals`

* **Response**: `FileResponse`로 `cvt/{uri_id}_vocals.mp3` 반환

---

## ⚙️ 환경 변수 & 설정

* Firebase 키 파일 경로
* Firestore 컬렉션 이름
* 외부 서버 전송 URL (server1.py 내 `requests.post` 대상)

---

## 🚀 향후 개선 포인트

* **Cross‑Platform**: ffmpeg 바이너리 자동 설치 (Linux, macOS 지원)
* **Docker화**: 컨테이너 이미지로 패키징
* **비동기 처리 최적화**: FastAPI 비동기 기능 활용 및 작업 큐 도입 (Celery)
* **에러 처리 강화**: 예외 핸들링 및 로깅
* **멀티미디어 지원**: 다른 오디오 포맷(WAV, FLAC) 지원

---










[설치해야되는거]

https://github.com/facebookresearch/demucs
pip install -U demucs

https://github.com/yt-dlp/yt-dlp
pip install -U --pre "yt-dlp[default]"

pip install fastapi uvicorn

pip install firebase-admin

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118


[해야할거]

repository 폴더 안에 firebase키 넣어야함


[실행법 (터미널에 입력)]
uvicorn server1:app --reload


  POST /process
  {
    "url": "https://www.youtube.com/watch?v=QW_TSknSbWM"
  }
