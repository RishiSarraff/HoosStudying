from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from sqlalchemy.sql import text
from .documentFunctions import get_document_by_document_id

## ADD DOCUMENT TO PIPELINE:
def add_document_to_pipeline(db: Session, pipeline_id: int, document_id: int, is_active: bool) -> Optional[Dict[str, Any]]:
    try:

        insert_query = text("""
            INSERT INTO Pipeline_Documents (pipeline_id, document_id, is_active)
            VALUES (:pipeline_id, :document_id, :is_active)
        """)

        db.execute(insert_query, {
            'pipeline_id': pipeline_id,
            'document_id': document_id,
            'is_active': is_active
        })

        db.commit()
        
        select_query = text("""
            SELECT pipeline_id, document_id, is_active, added_at
            FROM Pipeline_Documents
            WHERE pipeline_id = :pipeline_id AND document_id = :document_id
        """)

        result = db.execute(select_query, {
            'pipeline_id': pipeline_id,
            'document_id': document_id
        })
        
        row = result.fetchone()
        
        if row:
            return {
                'pipeline_id': row[0],
                'document_id': row[1],
                'is_active': row[2],
                'added_at': row[3]
            }
        
        return None

    except Exception as e:
        db.rollback()
        raise e
    
def get_count_of_documents_by_pipeline(db: Session, pipeline_id: int) -> int:
    result = db.execute(
        text("""
            SELECT COUNT(*) as count
            FROM Pipeline_Documents
            WHERE pipeline_id = :pipeline_id;
            """
        ),
        {'pipeline_id': pipeline_id}
    )

    return result.mappings().first()['count']

def add_multiple_documents_to_pipeline(db: Session, pipeline_id: int, document_ids: List[int]) -> List[Dict[str, Any]]:
    try:
        listOfDocuments = []

        for document_id in document_ids:
            added_document = add_document_to_pipeline(db, pipeline_id, document_id, True)
            if added_document:
                listOfDocuments.append(added_document)

        return listOfDocuments

    except Exception as e:
        db.rollback()
        raise e

def get_documents_in_pipeline(db: Session, pipeline_id: int, is_active: bool = None) -> List[Dict[str, Any]]:
    if is_active is None:
        result = db.execute(
            text("""
                SELECT 
                    d.document_id,
                    d.file_name,
                    d.file_type,
                    d.upload_date,
                    pd.is_active,
                    pd.added_at
                FROM Pipeline_Documents pd
                JOIN Document d ON pd.document_id = d.document_id
                WHERE pd.pipeline_id = :pipeline_id
                ORDER BY pd.added_at DESC
            """),
            {'pipeline_id': pipeline_id}
        )
    else:
        result = db.execute(
            text("""
                SELECT 
                    d.document_id,
                    d.file_name,
                    d.file_type,
                    d.upload_date,
                    pd.is_active,
                    pd.added_at
                FROM Pipeline_Documents pd
                JOIN Document d ON pd.document_id = d.document_id
                WHERE pd.pipeline_id = :pipeline_id AND pd.is_active = :is_active
                ORDER BY pd.added_at DESC
            """),
            {'pipeline_id': pipeline_id, 'is_active': is_active}
        )

    return [dict(row) for row in result.mappings().all()]

def get_active_documents_in_pipeline(db: Session, pipeline_id: int) -> List[Dict[str, Any]]:
    """Get only active documents in pipeline with their details"""
    result = db.execute(
        text("""
            SELECT 
                d.document_id,
                d.file_name,
                d.file_type,
                d.upload_date,
                pd.is_active,
                pd.added_at
            FROM Pipeline_Documents pd
            JOIN Document d ON pd.document_id = d.document_id
            WHERE pd.pipeline_id = :pipeline_id AND pd.is_active = TRUE
            ORDER BY pd.added_at DESC
        """),
        {'pipeline_id': pipeline_id}
    )

    return [dict(row) for row in result.mappings().all()]

def is_document_in_pipeline(db: Session, pipeline_id: int, document_id: int) -> bool:
    result = db.execute(
        text("""
            SELECT * FROM Pipeline_Documents WHERE pipeline_id = :pipeline_id AND document_id = :document_id;
            """
        ),
        {'pipeline_id': pipeline_id,
         'document_id': document_id}
    )

    return result.first() is not None

## UPDATE PIPELINE DOCUMENTS:
def toggle_document_active_status(db: Session, pipeline_id: int, document_id: int, is_active: bool) -> Optional[Dict[str, Any]]:
    try:
        result = db.execute(
            text("""
                UPDATE Pipeline_Documents 
                SET is_active = :is_active 
                WHERE pipeline_id = :pipeline_id AND document_id = :document_id
            """),
            {
                'is_active': is_active,
                'pipeline_id': pipeline_id,
                'document_id': document_id    
            }
        )

        db.commit()

        select_result = db.execute(
            text("""
                SELECT pipeline_id, document_id, is_active, added_at
                FROM Pipeline_Documents
                WHERE pipeline_id = :pipeline_id AND document_id = :document_id
            """),
            {'pipeline_id': pipeline_id, 'document_id': document_id}
        )
        
        row = select_result.fetchone()
        
        if row:
            return {
                'pipeline_id': row[0],
                'document_id': row[1],
                'is_active': row[2],
                'added_at': row[3]
            }
        
        return None
    
    except Exception as e:
        db.rollback()
        raise e
    
def activate_document_in_pipeline(db: Session, pipeline_id: int, document_id: int) -> Optional[Dict[str, Any]]:
    try:
        return toggle_document_active_status(db, pipeline_id, document_id, True)
    except Exception as e:
        raise e

def deactivate_document_in_pipeline(db: Session, pipeline_id: int, document_id: int) -> Optional[Dict[str, Any]]:
    try:
        return toggle_document_active_status(db, pipeline_id, document_id, False)
    except Exception as e:
        raise e

## DELETE PIPELINE DOCUMENTS:
def remove_document_from_pipeline(db: Session, pipeline_id: int, document_id: int) -> bool:
    try:
        is_doc_in_pipeline = is_document_in_pipeline(db, pipeline_id, document_id)
        if not is_doc_in_pipeline:
            return False

        result = db.execute(
            text("""
                DELETE FROM Pipeline_Documents
                WHERE pipeline_id = :pipeline_id AND document_id = :document_id
            """),
            {'pipeline_id': pipeline_id, 'document_id': document_id}
        )
        
        db.commit()
  
        # Use rowcount instead of mappings()
        return result.rowcount > 0

    except Exception as e:
        db.rollback()
        raise e

def remove_all_documents_from_pipeline(db: Session, pipeline_id: int) -> int:
    try:
        result = db.execute(
            text("""
                DELETE FROM Pipeline_Documents 
                WHERE pipeline_id = :pipeline_id
            """),
            {'pipeline_id': pipeline_id}
        )
        
        db.commit()
  
        return result.rowcount

    except Exception as e:
        db.rollback()
        raise e

def remove_inactive_documents_from_pipeline(db: Session, pipeline_id: int) -> int:
    try:
        result = db.execute(
            text(
                """
                    DELETE FROM Pipeline_Documents WHERE pipeline_id = :pipeline_id AND is_active = FALSE;
                """
            ),
            {'pipeline_id': pipeline_id}
        )

        db.commit()

        return result.rowcount
    except Exception as e:
        raise e

