from fastapi import FastAPI
from src.chat.router import router as chat_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],   # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],   # Allows all headers
)

app.include_router(chat_router, prefix="/api")
