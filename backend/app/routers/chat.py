from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.firebase_auth import verify_firebase_token
from app.services.rag_service import RAGService
from app.crudFunctions import userFunctions, conversationFunctions, messageFunctions
from app.database import get_db

router = APIRouter()

def get_rag_service():
    try:
        return RAGService()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize RAG service: {str(e)}")

class ChatMessageRequest(BaseModel):
    message_text: str
    conversation_id: Optional[int] = None
    pipeline_id: Optional[int] = None

class SourceInfo(BaseModel):
    file_name: str
    chunk_index: int
    similarity_score: float
    text_preview: str

class ChatMessageResponse(BaseModel):
    message_id: int
    conversation_id: int
    response: str
    sources: List[SourceInfo]
    has_context: bool

@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")
        
        token = authorization.replace("Bearer ", "")
        firebase_user = verify_firebase_token(token)
        firebase_uid = firebase_user.get("uid")

        user = userFunctions.get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_id = user["user_id"]

        if request.conversation_id:
            conversation = conversationFunctions.get_conversation_by_id(db, request.conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            if conversation["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="Unauthorized")
            conversation_id = request.conversation_id
            pipeline_id = conversation["pipeline_id"]
        else:
            new_conversation = conversationFunctions.create_conversation(
                db=db,
                user_id=user_id,
                pipeline_id=request.pipeline_id
            )
            conversation_id = new_conversation["conversation_id"]
            pipeline_id = request.pipeline_id

        user_message = messageFunctions.create_user_message(
            db=db,
            conversation_id=conversation_id,
            message_text=request.message_text
        )

        conversation_history = []
        if request.conversation_id:
            messages = messageFunctions.get_all_messages_in_conversation(db, conversation_id)
            for msg in messages:
                role = "user" if msg["sender_type"] == "user" else "bot"
                conversation_history.append({
                    "role": role,
                    "content": msg["message_text"]
                })

        rag_service = get_rag_service()
        rag_response = rag_service.chat(
            query=request.message_text,
            pipeline_id=pipeline_id,
            conversation_history=conversation_history,
            top_k=5
        )

        bot_message = messageFunctions.create_bot_message(
            db=db,
            conversation_id=conversation_id,
            message_text=rag_response["response"]
        )

        conversationFunctions.update_conversation_timestamp(db, conversation_id)

        return ChatMessageResponse(
            message_id=bot_message["message_id"],
            conversation_id=conversation_id,
            response=rag_response["response"],
            sources=rag_response.get("sources", []),
            has_context=rag_response.get("has_context", False)
        )

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR IN send_chat_message: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/conversation/{pipeline_id}/new")
async def create_new_conversation(
    pipeline_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")
        
        token = authorization.replace("Bearer ", "")
        firebase_user = verify_firebase_token(token)
        firebase_uid = firebase_user.get("uid")

        user = userFunctions.get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_conversation = conversationFunctions.create_conversation(
            db=db,
            user_id=user["user_id"],
            pipeline_id=pipeline_id
        )

        return {
            "conversation_id": new_conversation["conversation_id"],
            "pipeline_id": pipeline_id,
            "created_at": new_conversation["created_at"]
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        print("ERROR IN create_new_conversation:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")
        
        token = authorization.replace("Bearer ", "")
        firebase_user = verify_firebase_token(token)
        firebase_uid = firebase_user.get("uid")

        user = userFunctions.get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        conversation = conversationFunctions.get_conversation_by_id(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation["user_id"] != user["user_id"]:
            raise HTTPException(status_code=403, detail="Unauthorized")

        result = conversationFunctions.delete_conversation(db, conversation_id)
        
        if result:
            return {"message": "Conversation deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete conversation")

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print("ERROR IN delete_conversation:", e)
        raise HTTPException(status_code=500, detail=str(e))