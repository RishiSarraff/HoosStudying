import hashlib
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Header
from sqlalchemy.orm import Session
from app.services.firebase_auth import verify_firebase_token
from app.services.document_processor import DocumentProcessor
from app.services.firebase_storage import FirebaseStorageService
from app.services.embedding_service import EmbeddingService
from app.services.vector_db_service import VectorDBService
import tempfile
import os
import uuid

from app.crudFunctions import userFunctions, pipelineFunctions, pipelineDocumentFunctions, documentFunctions

from app.database import get_db

router = APIRouter()

def calculate_checksum(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@router.post("/upload-simple")
async def upload_document_simple(
    file: UploadFile = File(...),
    pipeline_id: int = Form(...),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):  
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        firebase_user = verify_firebase_token(token)
        firebase_uid = firebase_user.get("uid")
        
        if not firebase_uid:
            raise HTTPException(status_code=401, detail="Invalid token: no UID found")
        
        user = userFunctions.get_user_by_firebase_uid(
            db,
            firebase_uid
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        user_id = user["user_id"]

        pipeline = pipelineFunctions.get_pipeline_by_id(
            db,
            pipeline_id
        )

        if not pipeline:
            raise HTTPException(
                status_code=404,
                detail="Pipeline not found"
            )
        
        if pipeline["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="You don't have permission to upload to this pipeline")

        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            file_size = os.path.getsize(tmp_file_path)
            checksum = calculate_checksum(tmp_file_path)

            storage_service = FirebaseStorageService()
            firebase_storage_path, download_url = storage_service.upload_file(
                file_path=tmp_file_path,
                firebase_uid=firebase_uid,
                file_name=file.filename
            )
            
            processor = DocumentProcessor()
            file_type = processor.get_file_type_from_path(file.filename)
            text, metadata = processor.extract_text(tmp_file_path, file_type)
            chunks = processor.chunk_text(text)

            word_count = len(text.split())
            page_count = metadata.get("page_count", 1) if metadata else 1
            
            embedding_service = EmbeddingService()
            embeddings = embedding_service.generate_embeddings(chunks)
            
            chunk_ids = [f"{firebase_uid}_{uuid.uuid4()}_{i}" for i in range(len(chunks))]
            
            vector_db_service = VectorDBService()
            if len(embeddings) > 0:
                embedding_dimension = len(embeddings[0])
                vector_db_service.create_index_if_not_exists(dimensions=embedding_dimension)
                
                vector_metadata = [
                    {
                        "storage_path": firebase_storage_path,
                        "chunk_index": i,
                        "file_name": file.filename,
                        "pipeline_id": pipeline_id,
                        "user_id": user_id,
                        "firebase_uid": firebase_uid
                    }
                    for i in range(len(chunks))
                ]
                vector_db_service.upsert_embeddings(embeddings, chunk_ids, vector_metadata)
            
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

            document_id = documentFunctions.insert_document_with_stored_procedure(
                db=db,
                user_id=user_id,
                file_name=file.filename,
                file_type=file_type,
                pipeline_id=pipeline_id,
                file_size=file_size,
                page_count=page_count,
                word_count=word_count,
                language="en",
                encoding="utf-8",
                firebase_storage_path=firebase_storage_path,
                checksum=checksum,
                mime_type=file.content_type or "application/pdf",
                chunks=chunks
            )

            document = documentFunctions.get_document_by_document_id(db, document_id)

            
            return {
                "success": True,
                "message": "Document uploaded to Firebase Storage and embeddings stored in Vector DB",
                "file_name": file.filename,
                "storage_path": firebase_storage_path,
                "document_id": document_id,
                "document": dict(document) if document else None,
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
    

