"""Tests for Pydantic schema validation."""
import pytest
from pydantic import ValidationError
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.interview_experience import ExperienceCreate, QuestionCreate
from app.schemas.mock_interview import StartInterviewRequest


def test_register_request_valid():
    req = RegisterRequest(
        email="test@example.com",
        password="password123",
        full_name="John Doe",
    )
    assert req.email == "test@example.com"
    assert req.full_name == "John Doe"


def test_register_request_short_password():
    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(email="test@example.com", password="short", full_name="John")
    assert "min_length" in str(exc_info.value) or "at least" in str(exc_info.value).lower()


def test_register_request_invalid_email():
    with pytest.raises(ValidationError):
        RegisterRequest(email="not-an-email", password="password123", full_name="John")


def test_register_request_short_name():
    with pytest.raises(ValidationError):
        RegisterRequest(email="test@example.com", password="password123", full_name="J")


def test_login_request_valid():
    req = LoginRequest(email="test@example.com", password="mypassword")
    assert req.email == "test@example.com"


def test_question_create_valid():
    q = QuestionCreate(topic="Arrays", question_text="Reverse an array", could_answer="Yes")
    assert q.topic == "Arrays"
    assert q.could_answer.value == "Yes"


def test_question_create_invalid_could_answer():
    with pytest.raises(ValidationError):
        QuestionCreate(topic="Arrays", question_text="test", could_answer="Maybe")


def test_start_interview_valid():
    req = StartInterviewRequest(
        interview_type="technical",
        difficulty="Medium",
    )
    assert req.interview_type.value == "technical"
    assert req.difficulty == "Medium"


def test_start_interview_invalid_difficulty():
    with pytest.raises(ValidationError):
        StartInterviewRequest(interview_type="technical", difficulty="Extreme")


def test_start_interview_invalid_type():
    with pytest.raises(ValidationError):
        StartInterviewRequest(interview_type="unknown_type", difficulty="Easy")
