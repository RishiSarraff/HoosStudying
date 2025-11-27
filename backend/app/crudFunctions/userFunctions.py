from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from sqlalchemy.sql import text

## CREATE A USER:
def create_user(db: Session, firebase_uid: str, first_name: str, last_name: str, email: str) -> Optional[Dict[str, Any]]:
    try:
        does_user_exist = find_user(db, firebase_uid)
        if does_user_exist:
            return None
        result = db.execute(
            text("""
                INSERT INTO User (firebase_uid, first_name, last_name, email)
                VALUES (:firebase_uid, :first_name, :last_name, :email)
            """),
            {
                'firebase_uid': firebase_uid,
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }
        )
        
        db.commit()
        
        user_id = result.lastrowid
        
        created_user = db.execute(
            text("""
                SELECT * 
                FROM User 
                WHERE user_id = :user_id
            """),
            {'user_id': user_id}
        )
        
        return created_user.mappings().first()
        
    except Exception as e:
        db.rollback()
        raise e

def find_user(db: Session, firebase_uid: str) -> bool:
    user_exists = db.execute(
        text("""
            SELECT 1 FROM User
            WHERE firebase_uid = :firebase_uid
            LIMIT 1
        """),
        {
            'firebase_uid': firebase_uid,
        }
    )

    return user_exists.first() is not None # if the user's row is greater than 0 then our user exists, which we don't want when creating a user

def get_user_by_firebase_uid(db: Session, firebase_uid: str) -> Optional[Dict[str, Any]]:
    user = db.execute(
        text(
            """
                SELECT * FROM User
                WHERE firebase_uid = :firebase_uid
            """
        ),
        {'firebase_uid': firebase_uid}
    )

    return user.mappings().first()

def get_or_create_user_from_firebase(db: Session, firebase_uid: str, email: str) -> Dict[str, Any]:
    try:
        existing_user = get_user_by_firebase_uid(db, firebase_uid)
        if existing_user:
            if not existing_user["first_name"]:
                return {
                    "user": existing_user,
                    "created_user": False,
                    "needs_name": True
                }
            
            return {
                'user': dict(existing_user),
                'created_user': False,
                'needs_name': False
            }
    
        new_user = create_user(
            db,
            firebase_uid,
            "",
            "",
            email
        )

        return {
            'user': dict(new_user),
            'created_user': True,
            'needs_name': True,
        }
    except Exception as e:
        db.rollback()
        raise e

## READ/QUERY USERS:

# Get All User:
def get_all_users(db: Session) -> List[Dict[str, Any]]:
    result = db.execute(
        text("""
             SELECT *
             FROM User 
             """)
    )
    users = result.mappings().all()
    return users


# Get User by ID:
def get_user_by_id(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text("""
             SELECT * 
             FROM User 
             WHERE user_id = :user_id
             """), 
        {'user_id': user_id}
    )
    user_by_id = result.mappings().first()
    return user_by_id

# Get User by Email:
def get_user_by_email(db: Session, email: str) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text("""
             SELECT *
             FROM User
             WHERE email = :email
             """), 
        {'email': email}
    )
    user_by_email = result.mappings().first()
    return user_by_email

# Get User by First or Last Name:
def get_user_by_name(db: Session, name: str) -> Optional[Dict[str, Any]]:
    search_pattern = f"%{name}%"
    result = db.execute(
        text("""
             SELECT * 
             FROM User 
             WHERE first_name LIKE :pattern 
                OR last_name LIKE :pattern 
                OR CONCAT(first_name, ' ', last_name) LIKE :pattern
             """),
        {'pattern': search_pattern}
    )
    return result.mappings().all()

def get_users_name(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    result = db.execute(
        text("""
            SELECT first_name, last_name
            FROM User
            WHERE user_id = :user_id
        """),
        {'user_id': user_id}
    )
    return result.mappings().first()

def get_pipeline_count_by_user(db: Session, user_id: int) -> int:
    result = db.execute(
        text("""
            SELECT COUNT(*) AS pipeline_count
            FROM Pipeline 
            WHERE user_id = :user_id
        """),
        {'user_id': user_id}
    )

    return result.mappings().first()['pipeline_count']

## UPDATE A USER:

# Update a user by user_id:
def update_user(db: Session, user_id: int, 
                first_name: Optional[str] = None, 
                last_name: Optional[str] = None, 
                email: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        db_user = get_user_by_id(db, user_id)

        if not db_user:
            return None
        
        update_fields = []
        params = {'user_id': user_id}
        
        if first_name is not None:
            update_fields.append("first_name = :first_name")
            params['first_name'] = first_name
        if last_name is not None:
            update_fields.append("last_name = :last_name")
            params['last_name'] = last_name
        if email is not None:
            update_fields.append("email = :email")
            params['email'] = email
            
        if not update_fields:
            return db_user

        db.execute(
            text(f"""
                 UPDATE User 
                 SET {', '.join(update_fields)}
                 WHERE user_id = :user_id
            """),
            params
        )
        
        db.commit()
        

        return get_user_by_id(db, user_id)

    except Exception as e:
        db.rollback()
        raise e

## DELETE A USER:
def delete_user_by_id(db: Session, user_id: int) -> bool:
    try:

        db_user = get_user_by_id(db, user_id)
        if not db_user:
            return False


        result = db.execute(
            text("""
                DELETE FROM User 
                WHERE user_id = :user_id
            """),
            {'user_id': user_id}
        )
        
        db.commit()
  
        return result.rowcount > 0

    except Exception as e:
        db.rollback()
        raise e
    
## CUSTOM QUERIES: 

# Get the total number of users:
def get_user_count(db: Session) -> int:
    try:
        result = db.execute(
            text("""
                SELECT COUNT(*) AS user_count 
                FROM User
            """)
        )
        count = result.mappings().first()['user_count']
        return count

    except Exception as e:
        db.rollback()
        raise e