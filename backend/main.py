from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models.emotionModel import EmotionModel
from models.responseModel import ResponseModel
from database.dbConnection import chat_collection
from datetime import datetime

app = FastAPI(title="MindMate - Mental Health Chatbot")

emotion_model = EmotionModel()
response_model = ResponseModel()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        emotion = emotion_model.predict(request.message)
        reply = response_model.generate_reply(request.message, emotion)
        
        chat_log = {
            "user_id": request.user_id,
            "message": request.message,
            "bot_reply": reply,
            "emotion": emotion,
            "timestamp": datetime.utcnow()
        }
        chat_collection.insert_one(chat_log)
        return {"emotion": emotion, "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-history/{user_id}")
def get_history(user_id: str):
    chats = list(chat_collection.find({"user_id": user_id}, {"_id": 0}))
    return {"history": chats}

@app.delete("/clear-chat/{user_id}")
def clear_chat(user_id: str):
    chat_collection.delete_many({"user_id": user_id})
    return {"message": "Chat history cleared."}