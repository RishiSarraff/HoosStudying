from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from sqlalchemy.sql import text
from documentFunctions import get_document_by_document_id

## ADD DOCUMENT TO PIPELINE:
def add_document_to_pipeline(db: Session, pipeline_id: int, document_id: int, is_active: bool) -> Optional[Dict[str, Any]]:
    try:

        result = db.execute(
            text("""
                INSERT INTO Pipeline_Documents (pipeline_id, document_id, is_active)
                VALUES (:pipeline_id, :document_id, :is_active)
            """),
            {
                'pipeline_id': pipeline_id,
                'document_id': document_id,
                'is_active': is_active
            }
        )

        db.commit()

        return result

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
    listOfDocuments = []
    try:
        for document_id in document_ids:
            added_document = add_document_to_pipeline(db, pipeline_id, document_id, True)
            listOfDocuments.append(added_document)

        return listOfDocuments

    except Exception as e:
        db.rollback()
        raise e

def get_documents_in_pipeline(db: Session, pipeline_id: int, is_active: bool = None) -> List[Dict[str, Any]]:
    if is_active is None:
        result = db.execute(
            text("""
                SELECT * FROM Pipeline_Documents WHERE pipeline_id = :pipeline_id;
                """
            ),
            {'pipeline_id': pipeline_id}
        )
    else:
        result = db.execute(
            text("""
                SELECT * FROM Pipeline_Documents WHERE pipeline_id = :pipeline_id AND is_active = :is_active;
                """
            ),
            {'pipeline_id': pipeline_id,
            'is_active': is_active}
        )

    return result.mappings().all()

def get_active_documents_in_pipeline(db: Session, pipeline_id: int) -> List[Dict[str, Any]]:
    result = db.execute(
        text("""
            SELECT * FROM Pipeline_Documents WHERE pipeline_id = :pipeline_id AND is_active = True;
            """
        ),
        {'pipeline_id': pipeline_id}
    )

    return result.mappings().all()

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
                UPDATE Pipeline_Documents SET is_active = :is_active WHERE pipeline_id = :pipeline_id AND document_id = :document_id;
                """
            ),
            {
                'is_active': is_active,
                'pipeline_id': pipeline_id,
                'document_id': document_id    
            }
        )

        db.commit()

        return get_document_by_document_id(db, document_id)
    
    except Exception as e:
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
            {'pipeline_id': pipeline_id,
             'document_id': document_id}
        )
        
        db.commit()
  
        return result.mappings().first() is not None

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
