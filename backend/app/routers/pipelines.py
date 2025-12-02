from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.firebase_auth import verify_firebase_token
from app.crudFunctions import userFunctions, pipelineFunctions, pipelineDocumentFunctions
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
    number_of_documents: Optional[int]

class CreatePipelineRequest(BaseModel):
    pipeline_name: str
    pipeline_description: str

class EditPipelineRequest(BaseModel):
    pipeline_id: int
    pipeline_name: str
    pipeline_description: str

class DeletePipelineRequest(BaseModel):
    pipeline_id: int

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
        
        document_count = pipelineDocumentFunctions.get_count_of_documents_by_pipeline(db, general_pipeline_id)
        pipeline_dict = dict(general_pipeline)
        pipeline_dict["number_of_documents"] = document_count

        return pipeline_dict

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
            return []
        
        return list_of_non_general_pipelines


    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        print("ERROR IN getNonDefaultPipelines:", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/create-new-pipeline", response_model=PipelineResponse)
async def createNewPipeline(
    request: CreatePipelineRequest,
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

        user_id = user["user_id"]

        created_pipeline = pipelineFunctions.create_pipeline(
            db,
            user_id,
            request.pipeline_name,
            request.pipeline_description
        )

        if not created_pipeline:
            raise HTTPException(
                status_code=404,
                detail=f"Non General Pipelines for user {user_id} not found"
            )
        
        pipeline_dict = dict(created_pipeline)
        document_count = pipelineDocumentFunctions.get_count_of_documents_by_pipeline(
            db, 
            pipeline_dict["pipeline_id"]
        )
        pipeline_dict["number_of_documents"] = document_count
        
        return pipeline_dict

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-pipeline/{pipeline_id}")
async def deletePipeline(
    pipeline_id: int,
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
    
        pipeline = pipelineFunctions.get_pipeline_by_id(db, pipeline_id)

        if not pipeline:
            raise HTTPException(
                status_code=404,
                detail="Pipeline not found"
            )
        
        if pipeline["user_id"] != user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this pipeline"
            )

        resultOfDeletion = pipelineFunctions.delete_pipeline_with_procedure(
            db,
            pipeline["pipeline_id"]
        )

        ## WE get all active documents in the pipeline and toggler the

        if not resultOfDeletion:
            raise HTTPException(
                status_code=400,
                detail="Failed to delete pipeline"
            )

        return {"success": True, "message": "Pipeline deleted successfully"}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{pipeline_id}/documents")
async def get_pipeline_documents(
    pipeline_id: int,
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
    
        pipeline = pipelineFunctions.get_pipeline_by_id(db, pipeline_id)

        if not pipeline:
            raise HTTPException(
                status_code=404,
                detail="Pipeline not found"
            )
        
        if pipeline["user_id"] != user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this pipeline"
            )
        
        documents = pipelineDocumentFunctions.get_documents_in_pipeline(
            db,
            pipeline_id,
            is_active=True
        )

        return {
            "success": True,
            "pipeline_id": pipeline_id,
            "documents": documents
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit-pipeline", response_model=PipelineResponse)
async def editPipeline(
    request: EditPipelineRequest,
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
        pipeline = pipelineFunctions.get_pipeline_by_id(db, request.pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        if pipeline["user_id"] != user["user_id"]:
            raise HTTPException(status_code=403, detail="You don't have permission to edit this pipeline")


        edited_pipeline = pipelineFunctions.update_pipeline(
            db,
            request.pipeline_id,
            request.pipeline_name,
            request.pipeline_description
        )

        if not edited_pipeline:
            raise HTTPException(
                status_code=404,
                detail=f"Non General Pipelines not found"
            )
        
        pipeline_dict = dict(edited_pipeline)
        document_count = pipelineDocumentFunctions.get_count_of_documents_by_pipeline(
            db, 
            pipeline_dict["pipeline_id"]
        )
        pipeline_dict["number_of_documents"] = document_count
        
        return pipeline_dict

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))