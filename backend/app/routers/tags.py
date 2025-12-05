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

class CustomTagRequest(BaseModel):
    token: str
    name: str
    color: str
    user_id: int
    pipeline_id: int


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
    
@router.post("/create-custom-tag", response_model=TagResponse)
async def createCustomTag(
    request: CustomTagRequest,
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

        if not user or user["user_id"] != request.user_id:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        custom_tag = tagFunctions.create_custom_tag(db, user_id=request.user_id, name=request.name, color=request.color)
        if not custom_tag or custom_tag['tag_type'] != 'custom':
            raise HTTPException(
                status_code=400, 
                detail="Invalid custom tag"
            )
        
        tag_id = custom_tag["tag_id"]
        
        try:
            pipelineTagFunctions.add_tag_to_pipeline(
                db=db,
                pipeline_id=request.pipeline_id,
                tag_id=tag_id
            )
        except Exception as tag_error:
            print(f"Failed to add custom tag, rolling back custom tag creation: {tag_error}")
            tagFunctions.delete_tag(db, tag_id)
            raise HTTPException(
                status_code=500,
                detail="Failed to assign custom tag to pipeline"
            )

        return custom_tag

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))