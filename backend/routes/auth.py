from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from models.user_model import User
from database.dbConnection import user_collection
from utils.jwt_handler import create_access_token, verify_token
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
import hashlib

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

import hashlib
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from models.user_model import User
from database.dbConnection import user_collection
from utils.jwt_handler import create_access_token

router = APIRouter()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Step 1: Full SHA256 hashing (no truncation)
    sha_hash = hashlib.sha256(password.encode()).hexdigest()
    # Step 2: Then bcrypt that fixed-size hash
    return bcrypt_context.hash(sha_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    sha_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return bcrypt_context.verify(sha_hash, hashed_password)

@router.post("/register")
def register(user: User):
    # Check if user already exists
    if user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Store user info
    user_data = {
        "name": user.name,
        "email": user.email,
        "password": user.password
    }
    result = user_collection.insert_one(user_data)

    # Generate JWT token
    token = create_access_token(str(result.inserted_id))
    return {"message": "User registered successfully", "token": token}


@router.post("/login")
def login(user: User):
    db_user = user_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not (user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token(str(db_user["_id"]))
    return {
    "access_token": token,
    "user": {
        "_id": str(db_user["_id"]),
        "username": db_user["name"]
    }
}

def get_current_user(token: str = Depends(oauth2_scheme)):
    decoded = verify_token(token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return decoded["user_id"]
