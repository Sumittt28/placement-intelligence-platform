"""Tests for core security functions — JWT, password hashing."""
import pytest
from datetime import timedelta
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


def test_password_hashing():
    password = "securePassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongPassword", hashed) is False


def test_password_hash_uniqueness():
    password = "samePassword"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2  # bcrypt uses random salt


def test_create_and_decode_token():
    data = {"sub": "user-123", "email": "test@example.com", "role": "student"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert decoded["sub"] == "user-123"
    assert decoded["email"] == "test@example.com"
    assert decoded["role"] == "student"
    assert "exp" in decoded


def test_token_with_custom_expiry():
    data = {"sub": "user-456"}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    decoded = decode_token(token)
    assert decoded["sub"] == "user-456"


def test_invalid_token_raises():
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        decode_token("invalid.token.here")
    assert exc_info.value.status_code == 401
