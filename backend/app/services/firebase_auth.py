import firebase_admin
from firebase_admin import auth, credentials
from firebase_admin.exceptions import FirebaseError
import os
from dotenv import load_dotenv

load_dotenv()

def get_firebase_app():
    firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if not firebase_credentials_path:
        raise ValueError("FIREBASE_CREDENTIALS_PATH environment variable is not set")
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credentials_path)
        firebase_admin.initialize_app(cred)
    return firebase_admin.get_app()

def verify_firebase_token(token: str) -> dict:

    if not token or not isinstance(token, str):
        raise ValueError("Token must be a non-empty string")
    
    token_segments = token.split('.')
    if len(token_segments) != 3:
        raise ValueError(
            f"Invalid token format. Firebase ID tokens must be JWTs with 3 segments "
            f"(header.payload.signature), but received {len(token_segments)} segment(s). "
            f"Please provide a valid Firebase ID token."
        )
    
    try:
        get_firebase_app()
        decoded_token = auth.verify_id_token(token)

        uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        name = decoded_token.get("name")

        return {
            "uid": uid,
            "email": email,
            "name": name or "",
        }
    except ValueError as e:
        raise
    except FirebaseError as e:
        raise Exception(f"Firebase authentication error: {str(e)}")
    except Exception as e:
        raise Exception(f"Token verification failed: {str(e)}")

