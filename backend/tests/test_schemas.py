"""
Tests for Pydantic schema validation.
"""
import pytest
from pydantic import ValidationError
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.mock_interview import StartInterviewRequest


class TestAuthSchemas:
    def test_register_valid(self):
        req = RegisterRequest(
            email="test@example.com",
            password="StrongPass123!",
            full_name="Test User",
        )
        assert req.email == "test@example.com"
        assert req.full_name == "Test User"

    def test_register_missing_email(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                password="StrongPass123!",
                full_name="Test User",
            )

    def test_register_missing_password(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@example.com",
                full_name="Test User",
            )

    def test_login_valid(self):
        req = LoginRequest(
            email="test@example.com",
            password="StrongPass123!",
        )
        assert req.email == "test@example.com"


class TestInterviewSchemas:
    def test_start_interview_valid(self):
        req = StartInterviewRequest(
            interview_type="technical",
            difficulty="Medium",
        )
        assert req.interview_type == "technical"
        assert req.difficulty == "Medium"

    def test_start_interview_with_company(self):
        req = StartInterviewRequest(
            interview_type="company",
            difficulty="Hard",
            company_id="company-123",
            mode="voice",
        )
        assert req.company_id == "company-123"
        assert req.mode == "voice"
