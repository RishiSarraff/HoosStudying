from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import User
from sqlalchemy.sql import text

## CREATE A USER:
def create_user(db: Session, first_name: str, last_name: str, email: str) -> User:
    try:
        db_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        db.add(db_user)

        db.commit()
        db.refresh(db_user)

        return db_user
    except Exception as e:
        db.rollback()
        raise e

## READ/QUERY USERS:

# Get All User:
def get_all_users(db: Session) -> List[User]:
    result = db.execute(
        text("""
             SELECT *
             FROM User 
             """)
    )
    users = result.mappings().all()
    return users


# Get User by ID:
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
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
def get_user_by_email(db: Session, email: str) -> Optional[User]:
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
def get_user_by_name(db: Session, name: str) -> List[User]:
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

## UPDATE A USER:

# Update a user by user_id:
def update_user(db: Session, user_id: int, first_name: Optional[str], last_name: Optional[str], email: Optional[str]) -> Optional[User]:
    try:
        db_user = get_user_by_id(db, user_id)

        if not db_user:
            return None
        
        if first_name is not None:
            db_user.first_name = first_name
        if last_name is not None:
            db_user.last_name = last_name
        if email is not None:
            db_user.email = email
        if first_name is None and last_name is None and email is None:
            return db_user
        
        db.commit()
        db.refresh(db_user)

        return db_user

    except Exception as e:
        db.rollback()
        raise e

## DELETE A USER:

# Delete User by Id
def delete_user_by_id(db: Session, user_id: int) -> bool:
    try:
        db_user = get_user_by_id(db, user_id)

        if not db_user:
            return False

        db.delete(db_user)
        db.commit()

        return True

    except Exception as e:
        db.rollback()
        raise e
    
## CUSTOM QUERIES: 

# Get the total number of users:
def get_user_count(db: Session) -> int:
    return db.query(User).count()