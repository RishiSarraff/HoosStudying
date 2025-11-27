from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.firebase_auth import verify_firebase_token
from app.crudFunctions import userFunctions, pipelineFunctions
from app.database import get_db
from sqlalchemy import text

router = APIRouter()

class TokenRequest(BaseModel):
    token: str

class UpdateNameRequest(BaseModel):
    first_name: str
    last_name: str | None = ""

class UserResponse(BaseModel):
    user_id: int
    firebase_uid: str
    first_name: str
    last_name: str
    email: str
    created_user: bool #did we create user or does it exist already.
    needs_name: bool

@router.post("/verify", response_model=UserResponse)
async def verify_and_sync_user(
    request: TokenRequest,
    db: Session = Depends(get_db)
):
    try:
        firebase_user = verify_firebase_token(request.token)

        firebase_uid = firebase_user.get("uid")
        email = firebase_user.get("email")
        display_name = firebase_user.get("displayName", "")
        

        if not firebase_uid or not email:
            raise HTTPException(
                status_code=401, 
                detail="Invalid token: missing uid or email"
            )

        create_user = userFunctions.get_or_create_user_from_firebase(
            db,
            firebase_uid,
            email
        )

        user = create_user['user']
        user_was_created = create_user['created_user']

        needs_name = user['first_name'].strip() == "" 


        return UserResponse(
            user_id = user['user_id'],
            firebase_uid = user['firebase_uid'],
            first_name = user['first_name'],
            last_name = user['last_name'],
            email = user['email'],  
            created_user = user_was_created,
            needs_name = needs_name
        )

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing user: {str(e)}")
    
@router.post("/me")
async def get_current_user(
    request: TokenRequest,
    db: Session = Depends(get_db)
):
    try:
        firebase_user = verify_firebase_token(request.token)
        firebase_uid = firebase_user.get("uid")

        user = userFunctions.get_user_by_firebase_uid(
            db,
            firebase_uid
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        return dict(user)

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/user/update-name")
async def update_name(
    update: UpdateNameRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = authorization.replace("Bearer ", "")
        firebase_user = verify_firebase_token(token)
        firebase_uid = firebase_user.get("uid")

        user = userFunctions.get_user_by_firebase_uid(
            db,
            firebase_uid
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        db.execute(
            text("""
                UPDATE User
                SET first_name = :first,
                    last_name = :last
                WHERE firebase_uid = :uid
            """),
            {"first": update.first_name, "last": update.last_name, "uid": firebase_uid}
        )
        db.commit()

        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except:
        raise HTTPException(status_code=500, detail=str(e))
    


