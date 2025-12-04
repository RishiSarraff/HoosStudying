import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
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
                'embedding': Vector(embedding_list),
                'text': text
            }
            
            if metadata_list and i < len(metadata_list):
                metadata = metadata_list[i].copy()
                if 'pipeline_id' in metadata and metadata['pipeline_id'] is not None:
                    metadata['pipeline_id'] = int(metadata['pipeline_id'])
                data.update(metadata)
            
            doc_ref = self.db.collection('embeddings').document(chunk_id)
            batch.set(doc_ref, data)
            count += 1
        
        batch.commit()
        print(f"Stored {count} embeddings with metadata: {metadata_list[0] if metadata_list else 'None'}")
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

    def find_nearest_embeddings(
        self,
        query_vector: List[float],
        pipeline_id: Optional[int] = None,
        top_k: int = 5,
        distance_measure: str = "COSINE"
    ) -> List[Dict[str, Any]]:
        try:
            collection = self.db.collection('embeddings')
            
            measure_map = {
                "COSINE": DistanceMeasure.COSINE,
                "EUCLIDEAN": DistanceMeasure.EUCLIDEAN,
                "DOT_PRODUCT": DistanceMeasure.DOT_PRODUCT
            }
            measure = measure_map.get(distance_measure.upper(), DistanceMeasure.COSINE)
            
            limit = top_k * 3 if pipeline_id else top_k
            
            print(f"Searching for embeddings with pipeline_id={pipeline_id}, top_k={top_k}, limit={limit}")
            
            vector_query = collection.find_nearest(
                vector_field="embedding",
                query_vector=Vector(query_vector),
                distance_measure=measure,
                limit=limit,
                distance_result_field="vector_distance"
            )
            
            docs = vector_query.stream()
            
            results = []
            checked = 0
            for doc in docs:
                checked += 1
                data = doc.to_dict()
                doc_pipeline_id = data.get('pipeline_id')
                
                if pipeline_id is not None:
                    if doc_pipeline_id is None:
                        continue
                    if int(doc_pipeline_id) != int(pipeline_id):
                        continue
                
                distance = data.pop('vector_distance', None)
                
                if measure == DistanceMeasure.COSINE:
                    similarity_score = 1 - distance if distance is not None else 0
                else:
                    similarity_score = 1 / (1 + distance) if distance is not None else 0
                
                results.append({
                    'id': doc.id,
                    'text': data.get('text', ''),
                    'file_name': data.get('file_name', 'Unknown'),
                    'chunk_index': data.get('chunk_index', 0),
                    'document_id': data.get('document_id'),
                    'pipeline_id': int(doc_pipeline_id) if doc_pipeline_id is not None else None,
                    'similarity_score': similarity_score,
                    'distance': distance
                })
                
                if len(results) >= top_k:
                    break
            
            print(f"Checked {checked} embeddings, found {len(results)} matching pipeline_id={pipeline_id}")
            return results
        except Exception as e:
            print(f"Error in find_nearest_embeddings: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

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

