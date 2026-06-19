"""
Tests for AI service interfaces and base classes.
"""
import pytest
from app.services.ai.base import BaseAIService, BaseQuestionGenerator, BaseEvaluator, BaseParser, BaseRecommender
from app.services.ai.interview_generator import InterviewGenerator
from app.services.ai.followup_generator import FollowUpGenerator
from app.services.ai.evaluator import Evaluator
from app.services.ai.knowledge_extractor import KnowledgeExtractor
from app.services.ai.resume_parser import ResumeParser
from app.services.ai.recommendation_engine import RecommendationEngine
from app.services.ai.voice_engine import VoiceEngine
from app.services.ai.gemini_client import GeminiClient


class TestAIServiceInheritance:
    """Verify all AI services extend BaseAIService as required by the blueprint."""

    def test_gemini_client_extends_base(self):
        assert issubclass(GeminiClient, BaseAIService)

    def test_interview_generator_extends_base(self):
        assert issubclass(InterviewGenerator, BaseAIService)
        assert issubclass(InterviewGenerator, BaseQuestionGenerator)

    def test_followup_generator_extends_base(self):
        assert issubclass(FollowUpGenerator, BaseAIService)
        assert issubclass(FollowUpGenerator, BaseQuestionGenerator)

    def test_evaluator_extends_base(self):
        assert issubclass(Evaluator, BaseAIService)
        assert issubclass(Evaluator, BaseEvaluator)

    def test_knowledge_extractor_extends_base(self):
        assert issubclass(KnowledgeExtractor, BaseAIService)
        assert issubclass(KnowledgeExtractor, BaseParser)

    def test_resume_parser_extends_base(self):
        assert issubclass(ResumeParser, BaseAIService)
        assert issubclass(ResumeParser, BaseParser)

    def test_recommendation_engine_extends_base(self):
        assert issubclass(RecommendationEngine, BaseAIService)
        assert issubclass(RecommendationEngine, BaseRecommender)

    def test_voice_engine_extends_base(self):
        assert issubclass(VoiceEngine, BaseAIService)


class TestEvaluatorWeaknessDetection:
    """Test the weakness detection logic in the Evaluator."""

    @pytest.mark.asyncio
    async def test_detect_weaknesses_with_low_scores(self):
        evaluator = Evaluator.__new__(Evaluator)  # Skip __init__ to avoid Gemini
        evaluation = {
            "communication": {"score": 3, "reason": "Unclear"},
            "technical": {"score": 2, "reason": "Wrong answers"},
            "confidence": {"score": 7, "reason": "Good"},
            "problem_solving": {"score": 4, "reason": "Struggled"},
            "behavioral": {"score": 8, "reason": "Great stories"},
            "project": {"score": 6, "reason": "Decent"},
        }
        weaknesses = await evaluator.detect_weaknesses(evaluation, "technical")
        topics = [w["topic"] for w in weaknesses]
        assert "communication" in topics
        assert "technical" in topics
        assert "problem_solving" in topics
        assert "confidence" not in topics
        assert "behavioral" not in topics

    @pytest.mark.asyncio
    async def test_detect_no_weaknesses(self):
        evaluator = Evaluator.__new__(Evaluator)
        evaluation = {
            "communication": {"score": 8, "reason": "Clear"},
            "technical": {"score": 7, "reason": "Good"},
            "confidence": {"score": 9, "reason": "Confident"},
            "problem_solving": {"score": 7, "reason": "Logical"},
            "behavioral": {"score": 8, "reason": "Great"},
            "project": {"score": 7, "reason": "Solid"},
        }
        weaknesses = await evaluator.detect_weaknesses(evaluation, "general")
        assert len(weaknesses) == 0
