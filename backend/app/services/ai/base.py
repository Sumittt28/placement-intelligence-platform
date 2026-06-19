from abc import ABC, abstractmethod
from typing import Any


class BaseAIService(ABC):
    """Base interface for all AI services. Swap Gemini for Ollama/OpenAI without touching business logic."""

    @abstractmethod
    async def generate(self, prompt: str, context: dict = None) -> Any:
        pass
