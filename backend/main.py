from fastapi import FastAPI, Depends
from routes.auth import router as auth_router
from routes.chat import router as chat_router 

app = FastAPI(title="MindMate - Mental Health Chatbot")

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
