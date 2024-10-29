from dotenv import load_dotenv
from openai import OpenAI


load_dotenv('.env')

def get_openai_client() -> OpenAI:
    return OpenAI()
