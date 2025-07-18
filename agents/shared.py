import os
from dotenv import load_dotenv
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel

load_dotenv()

def get_model():
    """Get the configured model for agents."""
    model_name = os.getenv('MAIN_MODEL', 'gpt-3.5-turbo')
    base_url = os.getenv('MAIN_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta/openai')
    api_key = os.getenv('OPENAI_API_KEY', 'no-api-key-provided')
    model = OpenAIModel(model_name, provider=OpenAIProvider(base_url=base_url, api_key=api_key))
    return model
