FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# 필수 패키지 설치 및 Python 3.10 설치
RUN apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3.10-distutils python3-pip wget ffmpeg \
    python3-numpy python3-dev && \
    ln -sf /usr/bin/python3.10 /usr/bin/python3 && \
    python3 -m pip install --upgrade pip

# CUDA 환경 변수 설정
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Firebase 키 경로 설정 (repository 폴더 내 json 파일)
ENV FIREBASE_KEY_PATH=/app/repository/key.json

# ffmpeg 설치 및 확인
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN which ffmpeg
RUN which ffprobe

# ffmpeg 환경변수 등록
# ENV PATH="/usr/bin:$PATH"

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir numpy && \
    pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu118

# 소스 전체 복사
COPY . .

# 필요한 디렉토리 생성
RUN mkdir -p mp3Raw separated cvt

# 8000 포트 노출
EXPOSE 8000

# 기본 실행 명령
CMD ["uvicorn", "server1:app", "--host", "0.0.0.0", "--port", "8000"] 