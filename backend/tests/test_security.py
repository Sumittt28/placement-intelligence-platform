"""
Tests for security utilities (JWT, password hashing).
"""
import pytest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from jose import jwt
from app.core.config import settings


class TestPasswordHashing:
    def test_hash_password(self):
        hashed = hash_password("testpassword")
        assert hashed != "testpassword"
        assert len(hashed) > 20

    def test_verify_password_correct(self):
        hashed = hash_password("testpassword")
        assert verify_password("testpassword", hashed) is True

    def test_verify_password_wrong(self):
        hashed = hash_password("testpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("testpassword")
        h2 = hash_password("testpassword")
        assert h1 != h2  # bcrypt uses random salt


class TestJWT:
    def test_create_token(self):
        token = create_access_token({"sub": "user-123", "email": "test@test.com", "role": "student"})
        assert isinstance(token, str)
        assert len(token) > 50

    def test_decode_token(self):
        payload = {"sub": "user-123", "email": "test@test.com", "role": "student"}
        token = create_access_token(payload)
        decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert decoded["sub"] == "user-123"
        assert decoded["email"] == "test@test.com"
        assert decoded["role"] == "student"
        assert "exp" in decoded

    def test_token_has_expiry(self):
        token = create_access_token({"sub": "user-123"})
        decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert "exp" in decoded
