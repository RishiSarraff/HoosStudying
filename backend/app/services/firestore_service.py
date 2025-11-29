import firebase_admin
from firebase_admin import credentials, firestore
import os
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
if not firebase_credentials_path:
    raise ValueError("FIREBASE_CREDENTIALS_PATH environment variable is not set")

class FirestoreService:
    
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_credentials_path)
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
    
    def get_collection(self, collection_name: str):
        return self.db.collection(collection_name)
    
    def add_document(self, collection_name: str, document_id: str, data: Dict[str, Any]) -> str:
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc_ref.set(data)
        return doc_ref.id
    
    def get_document(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def update_document(self, collection_name: str, document_id: str, data: Dict[str, Any]):
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc_ref.update(data)
    
    def delete_document(self, collection_name: str, document_id: str):
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc_ref.delete()
    
    def query_collection(self, collection_name: str, filters: List[tuple] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = self.db.collection(collection_name)
        
        if filters:
            for field, operator, value in filters:
                query = query.where(field, operator, value)
        
        if limit:
            query = query.limit(limit)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def add_embedding(self, document_id: str, embedding: List[float], text: str, metadata: Dict[str, Any] = None) -> str:
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        data = {
            'embedding': embedding,
            'text': text
        }
        if metadata:
            data.update(metadata)
        return self.add_document('embeddings', document_id, data)
    
    def add_embeddings_batch(self, embeddings: List[np.ndarray], chunk_ids: List[str], texts: List[str], metadata_list: List[Dict[str, Any]] = None) -> int:
        batch = self.db.batch()
        count = 0
        
        for i, (embedding, chunk_id, text) in enumerate(zip(embeddings, chunk_ids, texts)):
            if isinstance(embedding, np.ndarray):
                embedding_list = embedding.tolist()
            else:
                embedding_list = embedding
            
            data = {
                'embedding': embedding_list,
                'text': text
            }
            
            if metadata_list and i < len(metadata_list):
                data.update(metadata_list[i])
            
            doc_ref = self.db.collection('embeddings').document(chunk_id)
            batch.set(doc_ref, data)
            count += 1
        
        batch.commit()
        return count
    
    def get_embedding(self, document_id: str) -> Optional[Dict[str, Any]]:
        return self.get_document('embeddings', document_id)
    
    def get_all_embeddings(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.query_collection('embeddings', limit=limit)
    
    def get_all_documents_with_ids(self, collection_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = self.db.collection(collection_name)
        if limit:
            query = query.limit(limit)
        docs = query.stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]

if __name__ == "__main__":
    service = FirestoreService()
    
    print("=" * 60)
    print("FIRESTORE DATABASE CONTENTS")
    print("=" * 60)
    
    print("\n--- Embeddings Collection ---")
    embeddings = service.get_all_documents_with_ids('embeddings')
    
    if not embeddings:
        print("No documents found in 'embeddings' collection")
    else:
        print(f"Found {len(embeddings)} document(s):\n")
        for i, doc in enumerate(embeddings, 1):
            doc_id = doc.pop('id')
            print(f"Document {i}: {doc_id}")
            for key, value in doc.items():
                if key == 'embedding' and isinstance(value, (list, dict)):
                    if isinstance(value, list):
                        print(f"  {key}: [{len(value)} values] {value[:5]}..." if len(value) > 5 else f"  {key}: {value}")
                    else:
                        print(f"  {key}: [dict with {len(value)} keys]")
                else:
                    print(f"  {key}: {value}")
            print()
    
    print("\n--- All Collections ---")
    collections = service.db.collections()
    for collection in collections:
        count = len(list(collection.stream()))
        print(f"  {collection.id}: {count} document(s)")
    
    print("\n" + "=" * 60)

