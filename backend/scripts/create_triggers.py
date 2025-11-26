from sqlalchemy.sql import text

UPDATE_CONVERSATION_AFTER_MESSAGE = """
    CREATE TRIGGER Update_Conversation_After_Message
    AFTER INSERT ON Message
    FOR EACH ROW
    BEGIN
        UPDATE Conversation
        SET last_message_at = NOW()
        WHERE conversation_id = NEW.conversation_id;
    END;
"""

CREATE_GENERAL_PIPELINE = """
    CREATE TRIGGER Create_General_Pipeline
    AFTER INSERT ON User
    FOR EACH ROW
    BEGIN
        INSERT INTO Pipeline (user_id, pipeline_name, description, created_at) 
        VALUES (New.user_id, 'general', 'general pipeline for chatbot', New.created_at);
    END;
"""

ADD_DOCUMENT_TO_GENERAL_PIPELINE = """
    CREATE TRIGGER Add_Document_To_General_Pipeline
    AFTER INSERT ON Document 
    FOR EACH ROW BEGIN 
        INSERT INTO Pipeline_Documents (pipeline_id, document_id, is_active)
            SELECT p.pipeline_id, NEW.document_id, TRUE 
            FROM Pipeline p WHERE p.user_id = NEW.user_id AND p.pipeline_name = 'general' LIMIT 1; 
    END
"""

def create_triggers(engine):
    """Create all triggers using raw SQL and no ORM"""
    with engine.connect() as conn:
        triggers = [
            UPDATE_CONVERSATION_AFTER_MESSAGE,
            CREATE_GENERAL_PIPELINE,
            ADD_DOCUMENT_TO_GENERAL_PIPELINE
        ]
        
        for trigger in triggers:
            try:
                conn.execute(text(trigger))
                conn.commit()
            except Exception as e:
                print(f"Trigger error (may already exist): {e}")