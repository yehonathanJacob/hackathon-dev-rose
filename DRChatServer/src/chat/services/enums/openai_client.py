from enum import Enum


class OpenAIClientRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"

class OpenAIClientThreadStatus(Enum):
    COMPLETED = 'completed'
