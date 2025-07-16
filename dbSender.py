import firebase_admin
from firebase_admin import credentials, firestore, storage

cred = credentials.Certificate("repository/aaa2040-c4b67-firebase-adminsdk-fbsvc-0761cb3cee.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'aaa2040-c4b67.firebasestorage.app'  # 자신의 Firebase Storage 버킷 주소로 변경
})

db = firestore.client()
bucket = storage.bucket()

class SongUpload:
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

def upload_to_firebase(local_path, remote_path):
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(local_path)
    # blob.make_public()
    public_url = blob.public_url
    print(f"Uploaded {local_path} to Firebase Storage as {remote_path}. Public URL: {public_url}")
    return public_url

# song_id(예: uriId)로 SongUpload 객체를 저장

def save_song_upload(song_id, song_upload: SongUpload):
    doc_ref = db.collection('files').document(song_id)
    doc_ref.set(song_upload.to_dict())
    print(f"Saved SongUpload to Firestore: files/{song_id} -> {song_upload.to_dict()}")