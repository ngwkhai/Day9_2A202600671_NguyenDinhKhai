"""Shared LLM factory for all agents.

Prefers the official OpenAI API when OPENAI_API_KEY is configured, while
keeping OpenRouter as a fallback for the original lab setup.
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def get_llm(temperature: float = 0.3) -> ChatOpenAI:
    """Return a ChatOpenAI client for OpenAI, or OpenRouter as fallback."""
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=openai_api_key,
            temperature=temperature,
        )

    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-5"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        temperature=temperature,
    )
