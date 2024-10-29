from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_model: str = "gpt-4o"
    assistant_id: str = "asst_6s9EOatpr9zyjLtBYXfUUDMV"

settings = Settings()
