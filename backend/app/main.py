from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import upload, auth, pipelines

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(pipelines.router, prefix="/api/pipeline", tags="pipeline")

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}