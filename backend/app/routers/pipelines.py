from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.firebase_auth import verify_firebase_token
from app.crudFunctions import userFunctions, pipelineFunctions
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

class PipelineResponse(BaseModel):
    pipeline_id: int
    user_id: int
    pipeline_name: str
    description: str
    created_at: datetime

@router.post("/get-default-pipeline", response_model=PipelineResponse)
async def getDefaultPipeline(
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

        user_id = user["user_id"]

        general_pipeline_id = pipelineFunctions.get_general_pipeline_id(
            db,
            user_id
        )

        if not general_pipeline_id:
            raise HTTPException(
                status_code=404,
                detail=f"General Pipeline for user {user_id} not found"
            )

        general_pipeline = pipelineFunctions.get_pipeline_by_id(
            db,
            pipeline_id=general_pipeline_id
        )

        if not general_pipeline:
            raise HTTPException(
                status_code=404,
                detail=f"General Pipeline information not found and could not be retrieved"
            )
        
        return dict(general_pipeline)


    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/get-non-default-pipelines", response_model=List[PipelineResponse])
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

        user_id = user["user_id"]

        list_of_non_general_pipelines = pipelineFunctions.get_non_general_pipelines_by_user_id(
            db,
            user_id
        )

        if not list_of_non_general_pipelines:
            raise HTTPException(
                status_code=404,
                detail=f"Non General Pipelines for user {user_id} not found"
            )
        
        return list_of_non_general_pipelines


    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))