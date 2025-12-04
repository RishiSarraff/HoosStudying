from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.firebase_auth import verify_firebase_token
from app.crudFunctions import userFunctions, pipelineFunctions, conversationFunctions, messageFunctions
from app.database import get_db

router = APIRouter()

class ConversationResponse(BaseModel):
    conversation_id: int
    pipeline_id: Optional[int]
    user_id: int
    created_at: datetime
    last_message_at: Optional[datetime]
    first_message_content: Optional[str]

class MessageResponse(BaseModel):
    message_id: int
    conversation_id: int
    sender_type: str
    message_text: str
    timestamp: datetime

@router.get("/pipeline/{pipeline_id}/conversations", response_model=List[ConversationResponse])
async def getConversations(
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

        pipeline = pipelineFunctions.get_pipeline_by_id(db, pipeline_id, False)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        if pipeline["user_id"] != user["user_id"]:
            raise HTTPException(status_code=403, detail="Unauthorized")

        list_of_conversations_unformatted = conversationFunctions.get_conversations_by_pipeline(
            db,
            pipeline_id=pipeline_id
        )

        list_of_conversations = []

        for eachConversation in list_of_conversations_unformatted:
            eachConversationDict = dict(eachConversation)
            first_message = messageFunctions.get_first_message_in_conversation(
                db, 
                eachConversation["conversation_id"]
            )
            eachConversationDict["first_message_content"] = (
                first_message["message_text"] if first_message else "No messages yet"
            )
            list_of_conversations.append(eachConversationDict)

        
        return list_of_conversations if list_of_conversations else []

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        print("ERROR IN getConversations:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{conversation_id}/messages", response_model=List[MessageResponse])
async def getMessagesFromConversation(
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

        list_of_messages = messageFunctions.get_all_messages_in_conversation(
            db,
            conversation_id=conversation_id
        )
        
        return list_of_messages if list_of_messages else []

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        print("ERROR IN getMessagesFromConversation:", e)
        raise HTTPException(status_code=500, detail=str(e))