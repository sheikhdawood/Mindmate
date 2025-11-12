import time
import jwt
from decouple import config

JWT_SECRET = config("JWT_SECRET", default="supersecret")
JWT_ALGORITHM = "HS256"

def create_access_token(user_id: str):
    payload = {
        "user_id": user_id,
        "expires": time.time() + 3600  # 1 hour expiry
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_token(token: str):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if decoded["expires"] >= time.time():
            return decoded
        else:
            return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
