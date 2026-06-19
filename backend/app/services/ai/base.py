from abc import ABC, abstractmethod
from typing import Any


class BaseAIService(ABC):
    """Base interface for all AI services. Swap Gemini for Ollama/OpenAI without touching business logic."""

    @abstractmethod
    async def generate(self, prompt: str, context: dict = None) -> Any:
        pass


class BaseQuestionGenerator(BaseAIService):
    """Interface for services that generate interview questions."""

    @abstractmethod
    async def generate_question(self, context: dict, **kwargs) -> dict:
        pass

    async def generate(self, prompt: str, context: dict = None) -> Any:
        return await self.generate_question(context or {})


class BaseEvaluator(BaseAIService):
    """Interface for services that evaluate interview performance."""

    @abstractmethod
    async def evaluate(self, transcript: list, interview_type: str) -> dict:
        pass

    async def generate(self, prompt: str, context: dict = None) -> Any:
        return await self.evaluate([], "general")


class BaseParser(BaseAIService):
    """Interface for services that parse/extract structured data."""

    @abstractmethod
    async def parse(self, raw_input: str) -> dict:
        pass

    async def generate(self, prompt: str, context: dict = None) -> Any:
        return await self.parse(prompt)


class BaseRecommender(BaseAIService):
    """Interface for services that generate recommendations."""

    @abstractmethod
    async def recommend(self, **kwargs) -> list:
        pass

    async def generate(self, prompt: str, context: dict = None) -> Any:
        return await self.recommend()
