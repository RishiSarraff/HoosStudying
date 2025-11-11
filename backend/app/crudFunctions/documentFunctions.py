from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from sqlalchemy.sql import text


## CREATE A DOCUMENT:
def create_document(db: Session, user_id: int, file_name: str, file_type: str) -> Optional[Dict[str, Any]]:
    try:
        result = db.execute(
            text("""
                INSERT INTO Document (user_id, file_name, file_type)
                VALUES (:user_id, :file_name, :file_type)
            """),
            {
               'user_id': user_id,
               'file_name': file_name,
               'file_type': file_type,
            })
        
        db.commit()

        return get_document_by_document_id(db, result.lastrowid)
            
    except Exception as e:
        db.rollback()
        raise e
    
def create_document_metadata(db: Session, 
                             document_id: int, 
                             file_size: int = None,
                             page_count: int = None,
                             word_count: int = None,
                             language: str = None,
                             encoding: str = None,
                             firebase_storage_path: str = None,
                             checksum: str = None,
                             mime_type: str = None) -> Optional[Dict[str, Any]]:
    try:
        result = db.execute(
            text("""
                INSERT INTO Document_Metadata (
                    document_id, 
                    file_size, 
                    page_count, 
                    word_count, 
                    language, 
                    encoding, 
                    firebase_storage_path, 
                    checksum, 
                    mime_type
                )
                VALUES (
                    :document_id, 
                    :file_size,
                    :page_count,
                    :word_count,
                    :language, 
                    :encoding, 
                    :firebase_storage_path, 
                    :checksum, 
                    :mime_type
                )
            """),
            {
               'document_id': document_id,
               'file_size': file_size,
               'page_count': page_count,
               'word_count': word_count,
               'language': language,
               'encoding': encoding,
               'firebase_storage_path': firebase_storage_path,
               'checksum': checksum,
               'mime_type': mime_type,
            })
        
        db.commit()

        return get_document_metadata_by_document_id(db, document_id)
    except Exception as e:
        db.rollback()
        raise e

def create_document_chunks_batch(db: Session, document_id: int, chunks: List[str]) -> Optional[Dict[str, Any]]:
    try:

        created_chunks = []

        ## we take the chunk text and make index based on the size of the arr
        for chunk_index, chunk_text in enumerate(chunks):
            currentResult = db.execute(
                text(
                    """
                    INSERT INTO Document_Chunk (document_id, chunk_text, chunk_index)
                    VALUES (:document_id, :chunk_text, :chunk_index)
                    """
                )
                ,{
                    'document_id': document_id,
                    'chunk_text': chunk_text,
                    'chunk_index': chunk_index
                })

            currentChunkId = currentResult.lastrowid

            chunk_value = db.execute(
                text(
                    """
                    SELECT * FROM Document_Chunk WHERE chunk_id = :chunk_id
                    """
                ),
                {'chunk_id': currentChunkId}
            )

            created_chunks.append(chunk_value.mappings().first())
        
        db.commit()

        return created_chunks
    except Exception as e:
        db.rollback()
        raise e
    
## READ/QUERY DOCUMENTS:

def get_document_by_document_id(db: Session, document_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text(
            """
            SELECT * FROM Document WHERE document_id = :document_id;
            """
        ),
        {'document_id': document_id}
    )

    return result.mappings().first()

def get_documents_by_user_id(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(text("""
        SELECT * FROM Document WHERE user_id = :user_id"""),
        {'user_id': user_id})
        
    return result.mappings().all()
 
def get_document_metadata_by_document_id(db: Session, document_id: int):
    result = db.execute(
        text(
            """
            SELECT * FROM Document_Metadata WHERE document_id = :document_id;
            """
        ),
        {'document_id': document_id}
    )

    return result.mappings().first()

def get_document_file_info(db: Session, document_id: int) -> Dict[str, Any]:
    result = db.execute(
        text("""
            SELECT file_name, file_type, upload_date FROM Document WHERE document_id = :document_id
        """),
        {'document_id': document_id}
    )

    return result.mappings().first()

def get_all_metadata_for_user(db: Session,  user_id: int) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT dm.* 
                FROM Document_Metadata dm
                JOIN Document d ON d.document_id = dm.document_id
                WHERE d.user_id = :user_id
            """
        ),
        {
            'user_id': user_id
        }
    )

    return result.mappings().all()

def get_user_document_averages(db: Session, user_id: int) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT 
                    d.user_id AS user_id,
                    u.first_name AS first_name,
                    u.last_name AS last_name,
                    AVG(dm.file_size) AS average_file_size, 
                    AVG(dm.page_count) AS average_page_count,
                    AVG(dm.word_count) AS average_word_count
                FROM Document_Metadata dm
                JOIN Document d ON dm.document_id = d.document_id
                JOIN User u ON d.user_id = u.user_id
                WHERE u.user_id = :user_id
                GROUP BY u.user_id
            """
        ),
        {
            'user_id': user_id
        }
    )

    return result.mappings().all()

def get_all_chunks_by_user(db: Session, user_id: int) -> List[str]:
    result = db.execute(
        text(
            """
                SELECT dc.chunk_text
                FROM Document_Chunk dc 
                JOIN Document d ON dc.document_id = d.document_id
                WHERE d.user_id = :user_id;
            """
        ),
        {
            'user_id': user_id
        }
    )

    return result.mappings().all()

def get_chunk_by_id(db: Session, chunk_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * FROM Document_Chunk WHERE chunk_id = :chunk_id
            """
        ),
        {
            'chunk_id': chunk_id
        }
    )

    return result.mappings().first()

def get_chunks_by_document(db: Session, document_id: int) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * FROM 
                Document_Chunk WHERE document_id = :document_id
            """
        ),
        {
            'document_id': document_id
        }
    )

    return result.mappings().all()

def get_chunks_by_document_and_user(db: Session, document_id: int, user_id: int) -> List[str]:
    result = db.execute(
        text(
            """
                SELECT dc.chunk_text
                FROM Document_Chunk dc 
                JOIN Document d ON dc.document_id = d.document_id
                WHERE d.user_id = :user_id AND dc.document_id = :document_id;
            """
        ),
        {
            'document_id': document_id,
            'user_id': user_id
        }
    )

    return result.mappings().all()

def get_chunks_from_list(db: Session, listOfChunkIds: List[int]) -> List[Dict[str, Any]]:
    if not listOfChunkIds:
        return []
    
    # Create placeholders for each ID
    placeholders = ', '.join([f':id{i}' for i in range(len(listOfChunkIds))])
    params = {f'id{i}': chunk_id for i, chunk_id in enumerate(listOfChunkIds)}
    
    result = db.execute(
        text(f"SELECT * FROM Document_Chunk WHERE chunk_id IN ({placeholders})"),
        params
    )
    
    return result.mappings().all()

### DELETE DOCUMENTS:

def delete_document_by_id(db: Session, document_id: int):
    try:
        result = db.execute(
            text(
                """
                    DELETE FROM Document WHERE document_id = :document_id
                """
            ),
            {
                'document_id': document_id
            }
        )

        db.commit()

        return result.mappings().first() is not None
    
    except Exception as e:
        db.rollback()
        raise e
    
def delete_all_documents_for_user(db: Session, user_id: int):
    try:
        result = db.execute(
            text(
                """
                    DELETE FROM Document WHERE user_id = :user_id
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