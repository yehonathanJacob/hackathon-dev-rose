from fastapi import HTTPException
from typing import Optional

from src.chat.services.enums.openai_client import OpenAIClientRole, OpenAIClientThreadStatus
from src.chat.dependencies import get_openai_client
from src.settings import settings


class OpenAIService:
    def __init__(self):
        self.client = get_openai_client()

    def _create_thread(self) -> str:
        return self.client.beta.threads.create().id

    def _send_message(self, thread_id: str, content: str) -> None:
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            content=content,
            role=OpenAIClientRole.USER.value
        )

    def _get_latest_message(self, thread_id: str) -> str:
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=1
        )
        return messages.data[0].content[0].text.value

    def _run_thread(self, thread_id: str) -> str:
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=settings.assistant_id
        )

        return run.status

    def get_openai_response(self, content: str, thread_id: Optional[int] = None) -> dict:
        try:
            thread_id = thread_id or self._create_thread()

            self._send_message(thread_id, content)
            status = self._run_thread(thread_id)

            # TODO implement polling
            data = self._get_latest_message(thread_id) if status == OpenAIClientThreadStatus.COMPLETED.value else status
            return dict(data=data, thread_id=thread_id)

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error communicating with OpenAI: {str(e)}"
            ) from e
            
    def get_thread_messages(self, thread_id: str):
        try:
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            return [message.content[0].text.value for message in messages.data]
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error retrieving chat history: {str(e)}"
            ) from e
