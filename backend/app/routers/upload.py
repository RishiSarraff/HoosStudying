from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.firebase_auth import verify_firebase_token
from app.services.document_processor import DocumentProcessor
from app.services.firebase_storage import FirebaseStorageService
from app.services.embedding_service import EmbeddingService
from app.services.vector_db_service import VectorDBService
import tempfile
import os
import uuid

router = APIRouter()

@router.post("/upload-simple")
async def upload_document_simple(
    file: UploadFile = File(...),
    token: str = Form(...)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        firebase_user = verify_firebase_token(token)
        firebase_uid = firebase_user.get("uid")
        
        if not firebase_uid:
            raise HTTPException(status_code=401, detail="Invalid token: no UID found")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            storage_service = FirebaseStorageService()
            storage_path, download_url = storage_service.upload_file(
                file_path=tmp_file_path,
                firebase_uid=firebase_uid,
                file_name=file.filename
            )
            
            processor = DocumentProcessor()
            file_type = processor.get_file_type_from_path(file.filename)
            text, _ = processor.extract_text(tmp_file_path, file_type)
            chunks = processor.chunk_text(text)
            
            embedding_service = EmbeddingService()
            embeddings = embedding_service.generate_embeddings(chunks)
            
            chunk_ids = [f"{firebase_uid}_{uuid.uuid4()}_{i}" for i in range(len(chunks))]
            
            vector_db_service = VectorDBService()
            if len(embeddings) > 0:
                embedding_dimension = len(embeddings[0])
                vector_db_service.create_index_if_not_exists(dimensions=embedding_dimension)
                
                metadata = [{"storage_path": storage_path, "chunk_index": i, "file_name": file.filename} for i in range(len(chunks))]
                vector_db_service.upsert_embeddings(embeddings, chunk_ids, metadata)
            
            print(f"\n{'=' * 50}")
            print(f"EMBEDDINGS GENERATED AND STORED FOR: {file.filename}")
            print(f"{'=' * 50}")
            print(f"Total chunks: {len(chunks)}")
            print(f"Total embeddings: {len(embeddings)}")
            print(f"Embeddings stored in Vertex AI Vector Search")
            for i, embedding in enumerate(embeddings):
                print(f"\n--- Embedding {i} (ID: {chunk_ids[i]}) ---")
                print(f"Shape: {embedding.shape}")
                print(f"Min: {embedding.min():.4f}, Max: {embedding.max():.4f}, Mean: {embedding.mean():.4f}")
            print(f"{'=' * 50}\n")
            
            return {
                "success": True,
                "message": "Document uploaded to Firebase Storage and embeddings stored in Vector DB",
                "file_name": file.filename,
                "storage_path": storage_path,
                "download_url": download_url,
                "chunk_count": len(chunks),
                "embedding_count": len(embeddings),
                "vector_db_stored": True
            }
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

