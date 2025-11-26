# scripts/create_stored_procedures.py (Alternative)
from app.database import engine

GET_PIPELINE_STATS = """
CREATE PROCEDURE IF NOT EXISTS get_pipeline_stats(IN p_pipeline_id INT)
BEGIN
    SELECT 
        p.pipeline_id, 
        p.pipeline_name, 
        COUNT(DISTINCT pd.document_id) AS total_documents,
        SUM(CASE WHEN pd.is_active = TRUE THEN 1 ELSE 0 END) AS active_documents, 
        SUM(CASE WHEN pd.is_active = FALSE THEN 1 ELSE 0 END) AS inactive_documents, 
        COALESCE(SUM(dm.word_count), 0) AS total_word_count,
        COALESCE(AVG(dm.word_count), 0) AS average_word_count,
        COALESCE(AVG(dm.file_size), 0) AS average_file_size, 
        MAX(d.upload_date) AS most_recent_upload_date 
    FROM Pipeline p 
    JOIN Pipeline_Documents pd ON pd.pipeline_id = p.pipeline_id 
    JOIN Document_Metadata dm ON dm.document_id = pd.document_id 
    JOIN Document d ON d.document_id = pd.document_id 
    WHERE p.pipeline_id = p_pipeline_id 
    GROUP BY p.pipeline_id, p.pipeline_name;
END
"""

INSERT_DOCUMENT = """
CREATE PROCEDURE IF NOT EXISTS Insert_Document(
    IN p_user_id INT,
    IN p_file_name VARCHAR(50),
    IN p_file_type VARCHAR(5),
    IN p_pipeline_id INT,
    IN p_file_size INT,
    IN p_page_count INT,
    IN p_word_count INT,
    IN p_language VARCHAR(10),
    IN p_encoding VARCHAR(50),
    IN p_firebase_storage_path VARCHAR(500),
    IN p_checksum VARCHAR(255),
    IN p_mime_type VARCHAR(100),
    IN p_chunks JSON,
    OUT p_new_document_id INT
)
BEGIN 
    DECLARE v_chunk_index INT DEFAULT 0;
    DECLARE v_chunk_text TEXT;
    DECLARE v_chunks_count INT;

    START TRANSACTION;

    INSERT INTO Document(user_id, file_name, file_type) 
    VALUES (p_user_id, p_file_name, p_file_type);

    SET p_new_document_id = LAST_INSERT_ID();

    INSERT INTO Pipeline_Documents(pipeline_id, document_id) 
    VALUES (p_pipeline_id, p_new_document_id);

    INSERT INTO Document_Metadata (
        document_id, file_size, page_count, word_count, language, 
        encoding, firebase_storage_path, checksum, mime_type
    )
    VALUES (
        p_new_document_id, p_file_size, p_page_count, p_word_count, 
        p_language, p_encoding, p_firebase_storage_path, p_checksum, p_mime_type
    );

    SET v_chunks_count = JSON_LENGTH(p_chunks);

    WHILE v_chunk_index < v_chunks_count DO
        SET v_chunk_text = JSON_UNQUOTE(JSON_EXTRACT(p_chunks, CONCAT('$[', v_chunk_index, ']')));

        INSERT INTO Document_Chunk (document_id, chunk_text, chunk_index) 
        VALUES (p_new_document_id, v_chunk_text, v_chunk_index); 

        SET v_chunk_index = v_chunk_index + 1;
    END WHILE;

    COMMIT;
END
"""

DELETE_PIPELINE = """
CREATE PROCEDURE IF NOT EXISTS Delete_Pipeline(IN p_pipeline_id INT)
BEGIN 
    START TRANSACTION;
    
    DELETE FROM Conversation WHERE pipeline_id = p_pipeline_id;
    DELETE FROM Pipeline WHERE pipeline_id = p_pipeline_id;

    COMMIT;
END
"""

ALL_STORED_PROCEDURES = [
    ("get_pipeline_stats", GET_PIPELINE_STATS),
    ("Insert_Document", INSERT_DOCUMENT),
    ("Delete_Pipeline", DELETE_PIPELINE)
]

def create_all_stored_procedures():
    """Create stored procedures using SQLAlchemy"""
    connection = engine.raw_connection()
    
    try:
        cursor = connection.cursor()
        
        for i, (proc_name, proc_sql) in enumerate(ALL_STORED_PROCEDURES, 1):
            try:
                print(f"\n[{i}/{len(ALL_STORED_PROCEDURES)}] Creating: {proc_name}")
                
                # Drop if exists
                cursor.execute(f"DROP PROCEDURE IF EXISTS {proc_name}")
                print(f"Dropped existing (if any)")
                
                # Create procedure
                cursor.execute(proc_sql)
                connection.commit()
                print(f"Created successfully")
                
            except Exception as e:
                print(f"Error: {e}")
                connection.rollback()
                continue
        
        cursor.close()
        print("\n✅ All stored procedures processed!")
        
    finally:
        connection.close()

if __name__ == "__main__":
    create_all_stored_procedures()