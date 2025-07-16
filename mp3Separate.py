import os
import demucs.separate
import shlex

def mp3_separate(uriId):

    ffmpeg_dir = r'ffmpeg-master-latest-win64-gpl-shared\bin'
    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')

    if os.path.exists(f'separated/htdemucs/{uriId}/no_vocals.mp3'):
        print('already separated')
        return

    demucs.separate.main(shlex.split(f'--mp3 --two-stems vocals "mp3Raw/{uriId}.mp3"'))