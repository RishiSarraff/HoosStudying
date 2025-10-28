from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from sqlalchemy.sql import text


## CREATE PIPELINE TAG
def add_tag_to_pipeline(db, pipeline_id, tag_id) -> Optional[Dict[str, Any]]:
    try:
        is_tag_in_pipeline = does_tag_in_pipeline_exist(db, pipeline_id, tag_id)
        
        if not is_tag_in_pipeline:
            result = db.execute(
                text(
                    """
                        INSERT INTO Pipeline_Tag (pipeline_id, tag_id)
                        VALUES (:pipeline_id, :tag_id)
                    """
                ),
                {
                    'pipeline_id': pipeline_id,
                    'tag_id': tag_id
                }
            )

            db.commit()

            return result
        
        return None
    except Exception as e:
        db.rollback()
        raise e

def add_multiple_tags_to_pipeline(db, pipeline_id, tag_ids: List[int]) -> List[Dict[str, Any]]:
    listOfTags = []
    try:
        for tag_id in tag_ids:
            if not does_tag_in_pipeline_exist(db, pipeline_id, tag_id):
                
                result = db.execute(
                    text(
                        """
                            INSERT INTO Pipeline_Tag (pipeline_id, tag_id)
                            VALUES (:pipeline_id, :tag_id)
                        """
                    ),
                    {
                        'pipeline_id': pipeline_id,
                        'tag_id': tag_id
                    }
                )

                listOfTags.append({'pipeline_id': pipeline_id, 'tag_id': tag_id})

        db.commit()
        return listOfTags

    except Exception as e:
        db.rollback()
        raise e

## READ/QUERY PIPELINE TAGS
def get_tags_for_pipeline(db, pipeline_id) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT t.* 
                FROM Tag t
                WHERE t.tag_id IN(
                    SELECT pt.tag_id 
                    FROM Pipeline_Tag pt
                    WHERE pt.pipeline_id = :pipeline_id
                )
            """
        ),
        {
            'pipeline_id': pipeline_id
        }
    )

    return result.mappings().all()

def get_pipelines_with_tag(db, tag_id) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT p.* 
                FROM Pipeline p
                WHERE p.pipeline_id IN(
                    SELECT pt.pipeline_id 
                    FROM Pipeline_Tag pt
                    WHERE pt.tag_id = :tag_id
                )
            """
        ),
        {
            'tag_id': tag_id
        }
    )

    return result.mappings().all()

def does_tag_in_pipeline_exist(db: Session, pipeline_id: int, tag_id: int) -> bool:
    result = db.execute(
        text("""
            SELECT 1
            FROM Pipeline_Tag
            WHERE pipeline_id = :pipeline_id AND tag_id = :tag_id
            LIMIT 1
        """),
        {'pipeline_id': pipeline_id, 'tag_id': tag_id}
    )
    return result.first() is not None

## DELETE PIPELINE TAGS

def remove_tag_from_pipeline(db, pipeline_id, tag_id) -> bool: 
    try:
        is_tag_in_pipeline = does_tag_in_pipeline_exist(db, pipeline_id, tag_id)

        if is_tag_in_pipeline:
            result = db.execute(
                text(
                    """
                        DELETE FROM Pipeline_Tag WHERE pipeline_id = :pipeline_id AND tag_id = :tag_id
                    """
                ),
                {
                    'pipeline_id': pipeline_id,
                    'tag_id': tag_id
                }
            )

            db.commit()

            return result.mappings().first() is not None
        
        return False

    except Exception as e:
        db.rollback()
        raise e
    
def remove_all_tags_from_pipeline(db, pipeline_id) -> int:
    try:
        result = db.execute(
            text(
                """
                    DELETE FROM Pipeline_Tag WHERE pipeline_id = :pipeline_id
                """
            ),
            {
                'pipeline_id': pipeline_id,
            }
        )

        db.commit()
        return result.rowcount

    except Exception as e:
        db.rollback()
        raise e