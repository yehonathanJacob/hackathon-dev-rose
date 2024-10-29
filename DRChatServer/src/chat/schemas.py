from pydantic import BaseModel
from typing import Optional


class MessageRequest(BaseModel):
    content: str
    thread_id: Optional[str] = None
