import firebase_admin
from firebase_admin import credentials, firestore, storage

cred = credentials.Certificate("repository/aaa2040-c4b67-firebase-adminsdk-fbsvc-0761cb3ce4.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

firebase_admin.initialize_app(cred, {
    'storageBucket': 'gs://aaa2040-c4b67.firebasestorage.app'  # 자신의 Firebase Storage 버킷 주소로 변경
})
bucket = storage.bucket()

app = FastAPI()

def upload_to_firebase(local_path, remote_path):
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(local_path)
    # 파일을 공개로 만들고 싶으면 아래 주석 해제
    # blob.make_public()
    return blob.public_url  # 또는 blob.generate_signed_url()로 임시 다운로드 링크 생성 가능