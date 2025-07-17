import os
import demucs.separate
import shlex

def mp3_separate(uriId, device='cuda'):

    ffmpeg_dir = r'ffmpeg-master-latest-win64-gpl-shared\bin'
    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')

    if os.path.exists(f'separated/htdemucs/{uriId}/no_vocals.mp3'):
        print('already separated')
        return

    try:
        print("cuda분할")
        demucs.separate.main(shlex.split(f'--mp3 --two-stems vocals --device {device} "mp3Raw/{uriId}.mp3"'))
    except Exception:
        if device == 'cuda':
            print("cpu분할")
            demucs.separate.main(shlex.split(f'--mp3 --two-stems vocals --device cpu "mp3Raw/{uriId}.mp3"'))
        else:
            pass
