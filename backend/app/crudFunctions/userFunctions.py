from sqlalchemy.orm import Session
from typing import Optional, List
from app.models import User
from datetime import datetime

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
    return db.query(User).all()

# Get User by ID:
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()

# Get User by Email:
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

# Get User by First or Last Name:
def get_user_by_name(db: Session, name: str) -> List[User]:
    search_pattern = f"%{name}%"
    return db.query(User).filter(
        (User.first_name.ilike(search_pattern)) | (User.last_name.ilike(search_pattern))
    ).all()

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
    
# CUSTOM QUERIES: 
def get_user_count(db: Session) -> int:
    """Get total number of users"""
    return db.query(User).count()