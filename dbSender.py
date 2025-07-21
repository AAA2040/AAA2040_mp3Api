import firebase_admin
from firebase_admin import credentials, firestore, storage
from firebase_admin.exceptions import FirebaseError
from dotenv import load_dotenv
import os
from logging_config import get_logger

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logger = get_logger(__name__)

# 환경 변수 가져오기
FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'repository/aaa2040-c4b67-firebase-adminsdk-fbsvc-0761cb3ce4.json')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', 'aaa2040-c4b67.firebasestorage.app')

# Firebase 초기화
try:
    # 인증 파일 존재 확인
    if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
        raise FileNotFoundError(f"Firebase 인증 파일이 존재하지 않습니다: {FIREBASE_CREDENTIALS_PATH}")
    
    # Firebase 앱이 이미 초기화되어 있는지 확인
    try:
        firebase_admin.get_app()
        logger.info("Firebase 앱이 이미 초기화되어 있습니다.")
    except ValueError:
        # 앱이 초기화되지 않은 경우 초기화
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': FIREBASE_STORAGE_BUCKET
        })
        logger.info("Firebase 앱 초기화 완료")
    
    db = firestore.client()
    bucket = storage.bucket()
    
except Exception as e:
    logger.error(f"Firebase 초기화 실패: {e}")
    db = None
    bucket = None

class SongDBUpload:
    def __init__(self, vocal_mp3_url=None, mr_mp3_url=None, lyrics_url=None):
        self.vocal_mp3_url = vocal_mp3_url
        self.mr_mp3_url = mr_mp3_url
        self.lyrics_url = lyrics_url

    def to_dict(self):
        return {
            "vocal_mp3_url": self.vocal_mp3_url,
            "mr_mp3_url": self.mr_mp3_url,
            "lyrics_url": self.lyrics_url
        }

def save_songDB_upload(song_id, song_data: SongDBUpload):
    """Firestore에 노래 데이터를 저장합니다."""
    
    if not song_id:
        raise ValueError("song_id가 필요합니다.")
    
    if not song_data:
        raise ValueError("song_data가 필요합니다.")
    
    if db is None:
        raise Exception("Firebase가 초기화되지 않았습니다.")
    
    try:
        logger.info(f"Firestore 저장 시작: {song_id}")
        
        doc_ref = db.collection('files').document(song_id)
        data_dict = song_data.to_dict()
        
        # 필수 필드 검증
        if not data_dict.get('vocal_mp3_url') or not data_dict.get('mr_mp3_url'):
            raise ValueError("vocal_mp3_url과 mr_mp3_url은 필수입니다.")
        
        doc_ref.set(data_dict)
        logger.info(f"Firestore 저장 완료: files/{song_id}")
        
    except FirebaseError as e:
        logger.error(f"Firebase 오류: {e}")
        raise Exception(f"Firestore 저장에 실패했습니다: {str(e)}")
    
    except Exception as e:
        logger.error(f"Firestore 저장 중 오류: {e}")
        raise

def fileUpload_to_firebase(result_path, local_path):
    """로컬 파일을 Firebase Storage에 업로드합니다."""
    
    if not result_path:
        raise ValueError("result_path가 필요합니다.")
    
    if not local_path:
        raise ValueError("local_path가 필요합니다.")
    
    if bucket is None:
        raise Exception("Firebase Storage가 초기화되지 않았습니다.")
    
    # 로컬 파일 존재 확인
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"업로드할 파일이 존재하지 않습니다: {local_path}")
    
    # 파일 크기 확인
    file_size = os.path.getsize(local_path)
    if file_size == 0:
        raise ValueError(f"파일이 비어있습니다: {local_path}")
    
    try:
        logger.info(f"Firebase Storage 업로드 시작: {local_path} -> {result_path}")
        
        blob = bucket.blob(result_path)
        
        # 메타데이터 설정
        blob.metadata = {
            'originalName': os.path.basename(local_path),
            'uploadTime': str(os.path.getmtime(local_path)),
            'fileSize': str(file_size)
        }
        
        # 파일 업로드
        blob.upload_from_filename(local_path)
        
        # 공개 URL 생성 (필요한 경우)
        # blob.make_public()
        public_url = blob.public_url
        
        logger.info(f"Firebase Storage 업로드 완료: {result_path} ({file_size} bytes)")
        return public_url
        
    except FirebaseError as e:
        logger.error(f"Firebase Storage 업로드 오류: {e}")
        raise Exception(f"파일 업로드에 실패했습니다: {str(e)}")
    
    except Exception as e:
        logger.error(f"파일 업로드 중 오류: {e}")
        raise