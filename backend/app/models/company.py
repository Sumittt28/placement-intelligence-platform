import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    industry = Column(String(100), nullable=True)
    website = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    analytics = relationship("CompanyAnalytics", back_populates="company", uselist=False, cascade="all, delete-orphan")
    interview_experiences = relationship("InterviewExperience", back_populates="company")
    mock_interviews = relationship("MockInterview", back_populates="company")


class CompanyAnalytics(Base):
    __tablename__ = "company_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_experiences = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    top_topics = Column(JSONB, default=list)
    difficulty_dist = Column(JSONB, default=dict)
    round_dist = Column(JSONB, default=dict)
    success_rate = Column(Float, default=0.0)
    common_weaknesses = Column(JSONB, default=list)
    recent_90d_weight = Column(Float, default=1.0)
    last_computed = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    company = relationship("Company", back_populates="analytics", foreign_keys=[company_id])

    __table_args__ = (
        {"comment": "Aggregated analytics per company, recomputed after each experience submission"},
    )
