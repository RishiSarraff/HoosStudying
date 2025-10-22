from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import Pipeline

## CREATE A PIPELINE:
def create_pipeline(db: Session, user_id: int, pipeline_name: str, description: str) -> Pipeline:
    try:
        db_pipeline = Pipeline(
            user_id=user_id,
            pipeline_name=pipeline_name,
            description=description
        )

        db.add(db_pipeline)

        db.commit()
        db.refresh(db_pipeline)

        return db_pipeline
    except Exception as e:
        db.rollback()
        raise e
    
## READ/QUERY PIPELINES:

# Get All Pipelines:
def get_all_pipelines(db: Session) -> List[Pipeline]:
    return db.query(Pipeline).all()

# Get Pipeline by pipeline ID:
def get_pipeline_by_id(db: Session, pipeline_id: int) -> Optional[Pipeline]:
    return db.query(Pipeline).filter(Pipeline.pipeline_id == pipeline_id).all()

# Get Pipelines by User ID:
def get_pipelines_by_user_id(db: Session, user_id: int) -> List[Pipeline]:
    return db.query(Pipeline).filter(Pipeline.user_id == user_id).all()


## UPDATE A PIPELINE:

# Update a pipeline using pipeline_id:
def update_pipeline(db: Session, pipeline_id: int, pipeline_name: Optional[str], description: Optional[str]) -> Optional[Pipeline]:
    try:
        db_pipeline = get_pipeline_by_id(db, pipeline_id)

        if pipeline_name is not None:
            db_pipeline.pipeline_name = pipeline_name

        if description is not None:
            db_pipeline.description = description

        if pipeline_name is None and description is None:
            return db_pipeline
        
        db.commit()
        db.refresh(db_pipeline)
        return db_pipeline
    except Exception as e:
        db.rollback()
        raise e