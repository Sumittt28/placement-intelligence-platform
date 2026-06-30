from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    kalvium_id: Optional[str] = None
    batch: Optional[str] = None
    graduation_year: Optional[int] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    target_companies: Optional[List[str]] = None


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    full_name: str
    kalvium_id: Optional[str] = None
    batch: Optional[str] = None
    graduation_year: Optional[int] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    target_companies: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    auth_provider: str
    is_active: bool
    created_at: datetime
    profile: Optional[ProfileResponse] = None
