from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from sqlalchemy.sql import text
from ..models import TagType

## CREATE TAG:
def create_system_tag(db: Session, name: str, color: str) ->  Optional[Dict[str, Any]]:
    try:
        result = db.execute(
            text("""
                INSERT INTO Tag (user_id, name, color, tag_type)
                VALUES (NULL, :name, :color, :tag_type)
            """),
            {
                'name': name,
                'color': color,
                'tag_type': TagType.SYSTEM.value
            }
        )
        
        db.commit()
        
        tag_id = result.lastrowid
        
        created_tag = db.execute(
            text("""
                SELECT * 
                FROM Tag 
                WHERE tag_id = :tag_id
            """),
            {'tag_id': tag_id}
        )
        
        return created_tag.mappings().first()
        
    except Exception as e:
        db.rollback()
        raise e

def create_custom_tag(db: Session, user_id: int, name: str, color: str) ->  Optional[Dict[str, Any]]:
    try:
        result = db.execute(
            text("""
                INSERT INTO Tag (user_id, name, color, tag_type)
                VALUES (:user_id, :name, :color, :tag_type)
            """),
            {
                'user_id': user_id,
                'name': name,
                'color': color,
                'tag_type': TagType.CUSTOM.value
            }
        )
        
        db.commit()
        
        tag_id = result.lastrowid
        
        created_tag = db.execute(
            text("""
                SELECT * 
                FROM Tag 
                WHERE tag_id = :tag_id
            """),
            {'tag_id': tag_id}
        )
        
        return created_tag.mappings().first()
        
    except Exception as e:
        db.rollback()
        raise e

## READ/QUERY TAG
def get_tag_by_id(db: Session, tag_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * 
                FROM Tag 
                WHERE tag_id = :tag_id
            """
        ),
        {
            'tag_id': tag_id
        }
    )

    return result.mappings().first()

def get_all_system_tags(db: Session) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * 
                FROM Tag 
                WHERE tag_type = :tag_type;
            """
        ),
        {
            'tag_type': TagType.SYSTEM.value
        }
    )

    return result.mappings().all()

def get_custom_tags_by_user(db: Session, user_id: int) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT * 
                FROM Tag 
                WHERE tag_type = :tag_type AND user_id = :user_id;
            """
        ),
        {
            'tag_type': TagType.CUSTOM.value,
            'user_id': user_id
        }
    )

    return result.mappings().all()

def get_all_tags_for_user(db: Session, user_id: int) -> List[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT t1.* 
                FROM Tag t1
                WHERE t1.user_id = :user_id

                UNION

                SELECT t2.*
                FROM Tag t2
                WHERE t2.tag_type = :tag_type
            """
        ),
        {
            'user_id': user_id,
            'tag_type': TagType.SYSTEM.value
        }
    )

    return result.mappings().all()

def get_tag_by_name_and_user(db: Session, user_id: int, name: str) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text(
            """
                SELECT *
                FROM Tag
                WHERE user_id = :user_id AND name = :name
            """
        ),
        {
            'user_id': user_id,
            'name': name
        }
    )

    return result.mappings().first()


## UPDATE TAG:

def update_tag(db: Session, 
               tag_id: int, 
               name:Optional[str]=None, 
               color:Optional[str]=None) -> Optional[Dict[str, Any]]:
    try:
        tag = get_tag_by_id(db, tag_id)

        if not tag:
            return None
        
        update_fields = []
        params = {'tag_id': tag_id}
        
        if name is not None:
            update_fields.append("name = :name")
            params['name'] = name
        if color is not None:
            update_fields.append("color = :color")
            params['color'] = color

        if not update_fields:
            return tag

        db.execute(
            text(f"""
                 UPDATE Tag 
                 SET {', '.join(update_fields)}
                 WHERE tag_id = :tag_id
            """),
            params
        )
        
        db.commit()
        

        return get_tag_by_id(db, tag_id)

    except Exception as e:
        db.rollback()
        raise e

## DELETE TAG:
def delete_tag(db: Session, tag_id: int) -> bool:
    try:
        tag = get_tag_by_id(db, tag_id)

        if not tag:
            return False
        
        result = db.execute(
            text(
                """
                    DELETE FROM Tag where tag_id = :tag_id
                """
            ),
            {
                'tag_id': tag_id
            }
        )

        db.commit()

        return result.mappings().first() is not None

    except Exception as e:
        db.rollback()
        raise e