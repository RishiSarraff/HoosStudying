import firebase_admin
from firebase_admin import credentials, storage
import os
import uuid
from datetime import timedelta
from typing import Tuple
from dotenv import load_dotenv

load_dotenv()

class FirebaseStorageService:
    
    def __init__(self):
        firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        if not firebase_credentials_path:
            raise ValueError("FIREBASE_CREDENTIALS_PATH environment variable is not set")
        
        firebase_storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET', 'hoosstudying-ab036.firebasestorage.app')
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_credentials_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': firebase_storage_bucket
            })
        
        self.bucket = storage.bucket(firebase_storage_bucket)
    
    def upload_file(
        self, 
        file_path: str, 
        firebase_uid: str, 
        file_name: str,
        folder: str = "documents"
    ) -> Tuple[str, str]:
        try:
            document_uuid = str(uuid.uuid4())
            storage_path = f"users/{firebase_uid}/{folder}/{document_uuid}/{file_name}"
            
            blob = self.bucket.blob(storage_path)
            blob.upload_from_filename(file_path)
            
            download_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=1),
                method="GET"
            )
            
            return storage_path, download_url
            
        except Exception as e:
            raise Exception(f"Error uploading to Firebase Storage: {str(e)}")
    
    def upload_file_from_bytes(
        self,
        file_content: bytes,
        firebase_uid: str,
        file_name: str,
        folder: str = "documents"
    ) -> Tuple[str, str]:
        try:
            document_uuid = str(uuid.uuid4())
            storage_path = f"users/{firebase_uid}/{folder}/{document_uuid}/{file_name}"
            
            blob = self.bucket.blob(storage_path)
            blob.upload_from_string(file_content)
            
            download_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=1),
                method="GET"
            )
            
            return storage_path, download_url
            
        except Exception as e:
            raise Exception(f"Error uploading to Firebase Storage: {str(e)}")

