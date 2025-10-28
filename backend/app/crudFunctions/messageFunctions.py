from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from sqlalchemy.sql import text
from models import SenderType

## CREATE MESSAGE:
def create_message(db: Session, conversation_id: int, sender_type: SenderType, message_text: str) -> Optional[Dict[str, Any]]:
    try:
        result = db.execute(
            text("""
                INSERT INTO Message (conversation_id, sender_type, message_text)
                VALUES (:conversation_id, :sender_type, :message_text)
            """),
            {
                'conversation_id': conversation_id,
                'sender_type': sender_type,
                'message_text': message_text
            }
        )
        
        db.commit()
        
        message_id = result.lastrowid
        
        created_message = db.execute(
            text("""
                SELECT * 
                FROM Message 
                WHERE message_id = :message_id
            """),
            {'message_id': message_id}
        )
        
        return created_message.mappings().first()
        
    except Exception as e:
        db.rollback()
        raise e

def create_user_message(db: Session, conversation_id: int, message_text: str) -> Optional[Dict[str, Any]]:
    return create_message(db, conversation_id, SenderType.USER, message_text)

def create_bot_message(db: Session, conversation_id: int, message_text: str) -> Optional[Dict[str, Any]]:
    return create_message(db, conversation_id, SenderType.BOT, message_text)

## READ/QUERY MESSAGES

def get_all_messages_in_conversation(db: Session, conversation_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * FROM Message WHERE conversation_id = :conversation_id;
            """
        ),
        {
            'conversation_id': conversation_id
        }
    )

    return result.mappings().all()

def get_all_messages(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT m.*
                FROM Message m
                JOIN Conversation c ON c.conversation_id = m.conversation_id
                WHERE c.user_id = :user_id;
            """
        ),
        {
            'user_id': user_id
        }
    )

    return result.mappings().all()

def get_all_pipeline_messages(db: Session, pipeline_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT m.*
                FROM Message m
                JOIN Conversation c ON c.conversation_id = m.conversation_id
                WHERE c.pipeline_id = :pipeline_id;
            """
        ),
        {
            'pipeline_id': pipeline_id
        }
    )

    return result.mappings().all()

def get_message_by_id(db: Session, message_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * 
                FROM Message
                WHERE message_id = :message_id
            """
        ),
        {
            'message_id': message_id
        }
    )

    return result.mappings().first()

def get_recent_messages(db: Session, conversation_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * 
                FROM Message
                WHERE conversation_id = :conversation_id
                ORDER BY timestamp DESC
                LIMIT :limit;
            """
        ),
        {
            'conversation_id': conversation_id,
            'limit': limit
        }
    )

    return result.mappings().all()

def get_last_message_in_conversation(db: Session, conversation_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * 
                FROM Message
                WHERE conversation_id = :conversation_id
                ORDER BY timestamp DESC
                LIMIT 1;
            """
        ),
        {
            'conversation_id': conversation_id
        }
    )

    return result.mappings().first()

## DELETE MESSAGE

def delete_message(db: Session, message_id: int) -> bool:
    try:
        result = db.execute(
            text(
                """
                    DELETE FROM Message WHERE message_id = :message_id
                """
            ),{
                'message_id': message_id
            }
        )

        db.commit()

        return result.mappings().first() is not None
    except Exception as e:
        raise e
    
def delete_all_messages_in_conversation(db: Session, conversation_id: int) -> int:
    try:
        result = db.execute(
            text("DELETE FROM Message WHERE conversation_id = :conversation_id"),
            {'conversation_id': conversation_id}
        )
        db.commit()
        return result.rowcount
    except Exception as e:
        db.rollback()
        raise e