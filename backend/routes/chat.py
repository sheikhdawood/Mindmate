from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from models.emotionModel import EmotionModel
from models.responseModel import ResponseModel
from database.dbConnection import chat_collection
from datetime import datetime
from routes.auth import get_current_user  # 🔐 import auth dependency

router = APIRouter()

emotion_model = EmotionModel()
response_model = ResponseModel()

class ChatRequest(BaseModel):
    message: str  # removed user_id (we’ll use from token)

# 💬 Chat Endpoint
@router.post("/")
def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):
    try:
        emotion = emotion_model.predict(request.message)
        reply = response_model.generate_reply(request.message, emotion)

        chat_log = {
            "user_id": user_id,
            "message": request.message,
            "bot_reply": reply,
            "emotion": emotion,
            "timestamp": datetime.utcnow()
        }
        chat_collection.insert_one(chat_log)

        return {"emotion": emotion, "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🕓 Get Chat History
@router.get("/history")
def get_history(user_id: str = Depends(get_current_user)):
    try:
        chats = list(chat_collection.find({"user_id": user_id}, {"_id": 0}))
        return {"history": chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🧹 Clear Chat History
@router.delete("/clear")
def clear_chat(user_id: str = Depends(get_current_user)):
    try:
        chat_collection.delete_many({"user_id": user_id})
        return {"message": "Chat history cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
