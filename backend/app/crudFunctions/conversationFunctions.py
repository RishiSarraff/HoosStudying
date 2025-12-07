from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from sqlalchemy.sql import text
from .pipelineFunctions import get_general_pipeline_id


## CREATE CONVERSATION
def create_conversation(db: Session, user_id: int, pipeline_id=None) -> Optional[Dict[str, Any]]:
    try:
        result = db.execute(
            text("""
                INSERT INTO Conversation (user_id, pipeline_id)
                VALUES (:user_id, :pipeline_id)
            """),
            {
                'user_id': user_id,
                'pipeline_id': pipeline_id
            }
        )
        
        db.commit()
        
        conversation_id = result.lastrowid
        
        created_conversation = db.execute(
            text("""
                SELECT * 
                FROM Conversation 
                WHERE conversation_id = :conversation_id
            """),
            {'conversation_id': conversation_id}
        )
        
        return created_conversation.mappings().first()
        
    except Exception as e:
        db.rollback()
        raise e
  

def create_general_conversation(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    return create_conversation(db, user_id, pipeline_id=None)

## READ/QUERY CONVERSATIONS
def get_conversation_by_id(db: Session, conversation_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * 
                FROM Conversation 
                WHERE conversation_id = :conversation_id
            """
        ),{
            'conversation_id': conversation_id
        }
    )

    return result.mappings().first()

def get_conversations_by_user(db: Session, user_id: int) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * 
                FROM Conversation 
                WHERE user_id = :user_id
            """
        ),{
            'user_id': user_id
        }
    )

    return result.mappings().all()

def get_conversations_by_pipeline(db: Session, pipeline_id: int) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * 
                FROM Conversation 
                WHERE pipeline_id = :pipeline_id 
                ORDER BY 
                    CASE WHEN last_message_at IS NULL THEN 1 ELSE 0 END,
                    last_message_at DESC
            """
        ),{
            'pipeline_id': pipeline_id
        }
    )

    return result.mappings().all()
    

def get_general_conversations_for_user(db: Session, user_id: int) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * 
                FROM Conversation 
                WHERE user_id = :user_id AND pipeline_id IS NULL;
            """
        ),{
            'user_id': user_id
        }
    )

    return result.mappings().all()

def get_recent_conversations(db: Session, user_id: int, limit=10) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * 
                FROM Conversation 
                WHERE user_id = :user_id 
                ORDER BY last_message_at DESC
                LIMIT :limit
            """
        ),{
            'user_id': user_id,
            'limit': limit
        }
    )

    return result.mappings().all()

def get_conversation_count_by_user(db: Session, user_id: int) -> int:
    result = db.execute(
        text(
            """
                SELECT COUNT(*) as count 
                FROM Conversation 
                WHERE user_id = :user_id 
            """
        ),{
            'user_id': user_id,
        }
    )

    return result.mappings().first()['count']

def get_conversation_count_by_user_pipeline(db: Session, user_id: int, pipeline_id: int) -> int:
    result = db.execute(
        text(
            """
                SELECT COUNT(*) as count
                FROM Conversation 
                WHERE user_id = :user_id AND pipeline_id = :pipeline_id
            """
        ),{
            'user_id': user_id,
            'pipeline_id': pipeline_id
        }
    )

    return result.mappings().first()['count']


## UPDATE CONVERSATIONS

def update_conversation_timestamp(db: Session, conversation_id: int):
    try:
        current_conversation = get_conversation_by_id(db, conversation_id)
        if not current_conversation:
            return False

        result = db.execute(
            text(
                """
                    UPDATE Conversation
                    SET last_message_at = NOW()
                    WHERE conversation_id = :conversation_id
                """
            ),
            {
                'conversation_id': conversation_id
            }
        )

        db.commit()

        return result.rowcount > 0
    except Exception as e:
        db.rollback()
        raise e

## DELETE CONVERSATIONS

def delete_conversation(db, conversation_id) -> bool: 
    try:
        result = db.execute(
            text(
                """
                    DELETE FROM Conversation WHERE conversation_id = :conversation_id
                """
            ),
            {
                'conversation_id': conversation_id
            }
        )
        
        db.commit()

        return result.mappings().first() is not None

    except Exception as e:
        db.rollback()
        raise e
    
def delete_all_conversations_for_user(db, user_id) -> int:
    try:
        result = db.execute(
            text(
                """
                    DELETE FROM Conversation WHERE user_id = :user_id
                """
            ),
            {
                'user_id': user_id
            }
        )
        
        db.commit()

        return result.rowcount

    except Exception as e:
        db.rollback()
        raise e