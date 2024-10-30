from fastapi import HTTPException
from typing import Optional

from src.chat.services.enums.openai_client import OpenAIClientRole, OpenAIClientThreadStatus
from src.chat.dependencies import get_openai_client
from src.settings import settings
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from atlassian import Confluence
from typing import List,Dict
import os

class OpenAIService:
    def __init__(self):
        self.client = get_openai_client()
        self.confluence = Confluence(
            url=os.getenv('CONFLUENCE_URL'),
            username=os.getenv('CONFLUENCE_USERNAME'),
            password=os.getenv('CONFLUENCE_API_TOKEN')
        )

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
            
    def get_confluence_contents(self, search_string: str):
        query = f'type=page AND text~"{search_string}"'
        results = self.confluence.cql(query, limit=3).get('results', [])
        content_dict = {}
        for page in results:
            title = page['title']
            page_id = page['id']
            content = self.confluence.get_page_by_id(page_id, expand='body.storage')['body']['storage']['value']
            content_dict[title] = content
        return content_dict

    def get_completion(self, query: str):
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
        
        tools: List[ChatCompletionToolParam] = [
            {
                "type": "function",
                "function": {
                    "name": "search_confluence",
                    "description": "Searches Confluence pages and returns top 3 page contents",
                    "parameters": {"query": {"type": "string"}}
                }
            }
        ]

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        choice = completion.choices[0]

        if choice.finish_reason == 'tool_calls':
            tool_call = choice.message.tool_calls[0]
            if tool_call.function.name == 'search_confluence':
                search_string = tool_call.function.arguments.get("query")
                confluence_results = self.get_confluence_contents(search_string)
                confluence_answer = "\n".join([f"{title}: {content}" for title, content in confluence_results.items()])

                return confluence_answer

        return choice.message.content