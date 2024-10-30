from fastapi import APIRouter, Query, HTTPException

from src.chat.services.openai_utils import OpenAIService
from src.chat.schemas import MessageRequest
from pydantic import BaseModel

router = APIRouter()
openai_service = OpenAIService()

class QueryRequest(BaseModel):
    query: str

@router.post("/get_chat_response")
def get_chat_response(payload: MessageRequest):
    return openai_service.get_openai_response(content=payload.content, thread_id=payload.thread_id)


@router.get("/get_chat_history")
def get_chat_history(thread_id: str = Query(...)):
    return {"messages": openai_service.get_thread_messages(thread_id=thread_id)}

@router.post("/get_completion_with_confluence")
def get_completion_with_confluence(request: QueryRequest):
    try:
        response = openai_service.get_completion(request.query)
        return {"results": response}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}"
        )