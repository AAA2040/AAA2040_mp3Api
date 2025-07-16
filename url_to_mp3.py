import yt_dlp

def url_to_mp3(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'mp3Raw/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'quiet': False,
        'noplaylist': True,
    }
    ydl_opts['ffmpeg_location'] = "ffmpeg-master-latest-win64-gpl-shared\\bin" # ffmpeg 경로

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])