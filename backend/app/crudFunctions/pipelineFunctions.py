from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from sqlalchemy.sql import text
from .pipelineDocumentFunctions import get_count_of_documents_by_pipeline
from .pipelineTagFunctions import get_tags_for_pipeline

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
def get_pipeline_by_id(db: Session, pipeline_id: int, include_tags: bool = True) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text("""
            SELECT * 
            FROM Pipeline 
            WHERE pipeline_id = :pipeline_id
        """),
        {'pipeline_id': pipeline_id})

    pipeline_by_pipeline_id = result.mappings().first()

    if pipeline_by_pipeline_id:
        pipeline_dict = dict(pipeline_by_pipeline_id)

        if include_tags and pipeline_dict.get('pipeline_name') != 'general':
            tags = get_tags_for_pipeline(db, pipeline_id)
            pipeline_dict['pipeline_tags'] = [dict(tag) for tag in tags]
        else:
            pipeline_dict['pipeline_tags'] = []
        
        return pipeline_dict

    return None

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

def get_non_general_pipelines_by_user_id(db: Session, user_id: int) -> List[Dict[str, Any]]:
    try:
        result = db.execute(
            text("""
                SELECT 
                    p.pipeline_id,
                    p.user_id,
                    p.pipeline_name,
                    p.description,
                    p.created_at,
                    COUNT(DISTINCT pd.document_id) as number_of_documents
                FROM Pipeline p
                LEFT JOIN Pipeline_Documents pd ON p.pipeline_id = pd.pipeline_id AND pd.is_active = TRUE
                WHERE p.user_id = :user_id AND p.pipeline_name != 'general'
                GROUP BY p.pipeline_id, p.user_id, p.pipeline_name, p.description, p.created_at
                ORDER BY p.created_at DESC
            """),
            {'user_id': user_id}
        )
        
        pipelines_list = []
        
        all_pipelines = result.mappings().all()
        
        for pipeline in all_pipelines:
            pipeline_dict = dict(pipeline)
            
            try:
                tags_result = db.execute(
                    text("""
                        SELECT t.tag_id, t.user_id, t.name, t.color, t.tag_type, t.created_at
                        FROM Tag t
                        JOIN Pipeline_Tag pt ON t.tag_id = pt.tag_id
                        WHERE pt.pipeline_id = :pipeline_id
                    """),
                    {'pipeline_id': pipeline_dict['pipeline_id']}
                )
                
                tags = tags_result.mappings().all()
                pipeline_dict['pipeline_tags'] = [dict(tag) for tag in tags]
                
            except Exception as tag_error:
                print(f"Error fetching tags for pipeline {pipeline_dict['pipeline_id']}: {tag_error}")
                pipeline_dict['pipeline_tags'] = []
            
            pipelines_list.append(pipeline_dict)
        
        return pipelines_list
        
    except Exception as e:
        print(f"Error in get_non_general_pipelines_by_user_id: {e}")
        import traceback
        traceback.print_exc()
        raise e


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
        db_pipeline = get_pipeline_by_id(db, pipeline_id, False)

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
        return get_pipeline_by_id(db, pipeline_id, True)
    
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