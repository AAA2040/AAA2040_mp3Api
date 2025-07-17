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
