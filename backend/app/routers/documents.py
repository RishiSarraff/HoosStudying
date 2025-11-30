from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.firebase_auth import verify_firebase_token
from app.crudFunctions import userFunctions, documentFunctions, pipelineDocumentFunctions
from app.database import get_db
from sqlalchemy import text

from app.crudFunctions import userFunctions

router = APIRouter()

class TokenRequest(BaseModel):
    token: str

class DocumentMetadataResponse(BaseModel):
    metadata_id: int
    document_id: int
    file_size: int
    page_count: int
    word_count: int
    language: str
    encoding: str
    firebase_storage_path: str
    firebase_download_url: str
    checksum: str
    mime_type: str
    created_at: datetime

@router.get("/get-document-metadata/{document_id}")
async def get_document_metadata(
    document_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        firebase_user = verify_firebase_token(token)
        firebase_uid = firebase_user.get("uid")

        user = userFunctions.get_user_by_firebase_uid(
            db,
            firebase_uid
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        ## after we get the user we want to call a sql fucntion that gives us our dcoument metadata for us to get teh storage path 
        document_metadata = documentFunctions.get_document_metadata_by_document_id(
            db,
            document_id
        )

        if not document_metadata:
            raise HTTPException(
                status_code=404,
                detail="Document metadata not found"
            )

        return document_metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-document/{pipeline_id}/{document_id}")
async def deleteDocument(
    pipeline_id: int,
    document_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        firebase_user = verify_firebase_token(token)
        firebase_uid = firebase_user.get("uid")

        user = userFunctions.get_user_by_firebase_uid(
            db,
            firebase_uid
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
    
        success = pipelineDocumentFunctions.remove_document_from_pipeline(
            db,
            pipeline_id,
            document_id
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Pipeline not found"
            )

        return {"success": success, "message": f"Document {document_id} deleted successfully from pipeline {pipeline_id}"}

    except HTTPException as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))