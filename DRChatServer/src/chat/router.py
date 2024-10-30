from fastapi import APIRouter, Query

from src.chat.services.openai_utils import OpenAIService
from src.chat.schemas import MessageRequest

router = APIRouter()
openai_service = OpenAIService()


@router.post("/get_chat_response")
def get_chat_response(payload: MessageRequest):
    return openai_service.get_openai_response(content=payload.content, thread_id=payload.thread_id)


@router.get("/get_chat_history")
def get_chat_history(thread_id: str = Query(...)):
    return {"messages": openai_service.get_thread_messages(thread_id=thread_id)}

@router.get("/get_chat_history")
def get_chat_history(thread_id: str = Query(...)):
    return openai_service.get_thread_messages(thread_id)