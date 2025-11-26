from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from sqlalchemy.sql import text

## CREATE A PIPELINE:
def create_pipeline(db: Session, user_id: int, pipeline_name: str, description: str) -> Optional[Dict[str, Any]]:
    try:
        result = db.execute(
            text(""" 
                INSERT INTO Pipeline (user_id, pipeline_name, description)
                VALUES (:user_id, :pipeline_name, :description)
            """),
            {
                'user_id': user_id,
                'pipeline_name': pipeline_name,
                'description': description
            }
        )
        
        db.commit()
        pipeline_id = result.lastrowid

        created_pipeline = db.execute(
            text("""
                SELECT * 
                FROM Pipeline 
                WHERE pipeline_id = :pipeline_id
            """),
            {'pipeline_id': pipeline_id}
        )

        return created_pipeline.mappings().first()
    except Exception as e:
        db.rollback()
        raise e
    
## READ/QUERY PIPELINES:

# Get All Pipelines:
def get_all_pipelines(db: Session) -> List[Dict[str, Any]]:
    result = db.execute(
        text("""
            SELECT *  FROM Pipeline
        """)
    )
    pipelines = result.mappings().all()
    return pipelines

# Get Pipeline by pipeline ID:
def get_pipeline_by_id(db: Session, pipeline_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text("""
            SELECT * 
            FROM Pipeline 
            WHERE pipeline_id = :pipeline_id
        """),
        {'pipeline_id': pipeline_id})

    pipeline_by_pipeline_id = result.mappings().first()

    return pipeline_by_pipeline_id

# Get Pipelines by User ID:
def get_pipelines_by_user_id(db: Session, user_id: int) -> List[Dict[str, Any]]:
    result = db.execute(
        text("""
            SELECT * 
            FROM Pipeline 
            WHERE user_id = :user_id
        """),
        {'user_id': user_id})

    pipeline_by_user_id = result.mappings().all()

    return pipeline_by_user_id

def get_pipeline_name_description(db: Session, user_id: int) -> List[Dict[str, Any]]:
    result = db.execute(
        text("""
            SELECT pipeline_name, description
            FROM Pipeline
            WHERE user_id = :user_id
        """),
        {'user_id': user_id}
    )

    return result.mappings().first()

def get_general_pipeline_id(db: Session, user_id: int) -> Optional[int]:
    result = db.execute(
        text("""
            SELECT pipeline_id
            FROM Pipeline
            WHERE user_id = :user_id AND pipeline_name = 'general'
        """),
        {'user_id': user_id}
    )

    row = result.mappings().first()
    return row['pipeline_id'] if row else None

## UPDATE A PIPELINE:

# Update a pipeline using pipeline_id:
def update_pipeline(db: Session, pipeline_id: int, 
                    pipeline_name: Optional[str] = None, 
                    description: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        db_pipeline = get_pipeline_by_id(db, pipeline_id)

        if not db_pipeline:
            return None

        update_fields = []
        params = {'pipeline_id': pipeline_id}

        if pipeline_name is not None:
            update_fields.append("pipeline_name = :pipeline_name")
            params['pipeline_name'] = pipeline_name

        if description is not None:
            update_fields.append("description = :description")
            params['description'] = description

        if not update_fields:
            return db_pipeline
        
        db.execute(
            text(f"""
                 UPDATE Pipeline 
                 SET {', '.join(update_fields)}
                 WHERE pipeline_id = :pipeline_id
            """),
            params
        )
        
        db.commit()
        return get_pipeline_by_id(db, pipeline_id)
    
    except Exception as e:
        db.rollback()
        raise e

## DELETE A PIPELINE:
def delete_pipeline_with_procedure(db: Session, pipeline_id: int) -> bool:
    try:
        db_pipeline = get_pipeline_by_id(db, pipeline_id)

        if not db_pipeline:
            return False
        
        db.execute(
            text("CALL Delete_Pipeline(:pipeline_id)"),
            {'pipeline_id': pipeline_id}
        )

        db.commit()
        return True
    
    except Exception as e:
        db.rollback()
        raise e

## CUSTOM QUERIES:
def get_pipeline_stats(db: Session, pipeline_id: int) -> Optional[Dict[str, Any]]:
    try:
        result = db.execute(
            text("CALL get_pipeline_stats(:pipeline_id)"),
            {'pipeline_id': pipeline_id}
        )

        return result.mappings().first()

    except Exception as e:
        db.rollback()
        raise e