from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.firebase_auth import verify_firebase_token
from app.crudFunctions import userFunctions, pipelineFunctions, tagFunctions, pipelineTagFunctions
from app.database import get_db
from sqlalchemy import text


router = APIRouter()

class TokenRequest(BaseModel):
    token: str

class UserResponse(BaseModel):
    user_id: int
    firebase_uid: str
    first_name: str
    last_name: str
    email: str

class TagResponse(BaseModel):
    tag_id: int
    user_id: Optional[int]
    name: str
    color: str
    tag_type: str
    created_at: datetime


@router.post("/get-system-tags", response_model=List[TagResponse])
async def getNonDefaultPipelines(
    request: TokenRequest,
    db: Session = Depends(get_db)
):
    try:
        firebase_user = verify_firebase_token(request.token)
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


        list_of_systemTags = tagFunctions.get_all_system_tags(
            db
        )

        if not list_of_systemTags:
            return []
        
        return list_of_systemTags

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        print("ERROR IN getNonDefaultPipelines:", e)
        raise HTTPException(status_code=500, detail=str(e))
    
