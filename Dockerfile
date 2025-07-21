# Python 3.10 slim 이미지를 기반으로 사용
FROM python:3.10-slim

# ffmpeg 설치
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 생성 및 이동
WORKDIR /app

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#RUN pip install torch==2.3.0+cu118 torchvision==0.18.0+cu118 torchaudio==2.3.0 --extra-index-url https://download.pytorch.org/whl/cu118

# 소스 코드 복사
COPY . .

# uvicorn 실행 (포트 8000)
CMD ["uvicorn", "server1:app", "--host", "0.0.0.0", "--port", "8011"] 