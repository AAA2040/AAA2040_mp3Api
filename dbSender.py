import firebase_admin
from firebase_admin import credentials, firestore, storage

cred = credentials.Certificate("repository/aaa2040-c4b67-firebase-adminsdk-fbsvc-0761cb3ce4.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'aaa2040-c4b67.firebasestorage.app'  # 자신의 Firebase Storage 버킷 주소로 변경
})

db = firestore.client()
bucket = storage.bucket()

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
# song_id(예: uriId)로 SongUpload 객체를 저장
def save_songDB_upload(song_id, SongDBUpload: SongDBUpload):
    doc_ref = db.collection('files').document(song_id)
    doc_ref.set(SongDBUpload.to_dict())
    print(f"Saved SongDBUpload to Firestore: files/{song_id} -> {SongDBUpload.to_dict()}")

def fileUpload_to_firebase(result_path, local_path): # 파일 스토리지에 저장
    blob = bucket.blob(result_path)
    blob.upload_from_filename(local_path)
    # blob.make_public()
    public_url = blob.public_url
    print(f"Uploaded {local_path} to Firebase Storage as {result_path}. Public URL: {public_url}")
    return public_url