import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, auth, pipelines, documents, conversations, tags, chat

app = FastAPI()

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://hoosstudying-478421.web.app",
        "https://hoosstudying-478421.firebaseapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(pipelines.router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(documents.router, prefix="/api/document", tags=["document"])
app.include_router(conversations.router, prefix="/api/conversation", tags=["conversation"])
app.include_router(tags.router, prefix="/api/tag", tags=["tag"] )
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}
