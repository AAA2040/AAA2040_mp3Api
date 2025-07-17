import subprocess
import os

def convert_to_192kbps(uriId):
    
    if not os.path.exists('cvt'):
        os.makedirs('cvt')

    command = [
        'ffmpeg',
        '-i', f'separated/htdemucs/{uriId}/no_vocals.mp3',         # 입력 파일
        '-b:a', '128k',          # 오디오 비트레이트 192kbps
        '-y',                    # 덮어쓰기 허용
        f'cvt/{uriId}_no_vocals.mp3'
    ]
    subprocess.run(command, check=True)

    command = [
        'ffmpeg',
        '-i', f'separated/htdemucs/{uriId}/vocals.mp3',         # 입력 파일
        '-b:a', '128k',          # 오디오 비트레이트 192kbps
        '-y',                    # 덮어쓰기 허용
        f'cvt/{uriId}_vocals.mp3'
    ]
    subprocess.run(command, check=True)

    os.remove(f'separated/htdemucs/{uriId}/no_vocals.mp3')
    os.remove(f'separated/htdemucs/{uriId}/vocals.mp3')