import os
from typing import Optional

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_mistralai import ChatMistralAI

load_dotenv()

def create_llm(model: Optional[str] = None, temperature: float = 0.0) -> BaseChatModel:
    """
    Create a chat model using Mistral when an API key is available.
    Fall back to Gemini only when that key is present.
    """
    mistral_api_key = os.getenv("MISTRAL_API_KEY") or os.getenv("MISTRAL_KEY")
    if mistral_api_key:
        return ChatMistralAI(
            model=model or os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
            api_key=mistral_api_key,
            temperature=temperature,
        )

    raise RuntimeError(
        "No LLM API key configured. Set MISTRAL_API_KEY (preferred) or GOOGLE_API_KEY."
    )
