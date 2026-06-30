import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base


class InterviewExperience(Base):
    __tablename__ = "interview_experiences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    role = Column(String(255), nullable=False)
    interview_date = Column(Date, nullable=False)
    round_type = Column(String(50), nullable=False)       # OA, Technical, HM, HR, System Design, Other
    difficulty = Column(String(20), nullable=False)        # Easy, Medium, Hard
    outcome = Column(String(20), nullable=False)           # Selected, Rejected, Waiting, Unknown
    student_notes = Column(Text, nullable=True)
    ai_extracted = Column(JSONB, nullable=True)            # AI-generated structured metadata
    is_approved = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="interview_experiences")
    company = relationship("Company", back_populates="interview_experiences")
    questions = relationship("InterviewQuestion", back_populates="experience", cascade="all, delete-orphan")
    outcome_record = relationship("InterviewOutcome", back_populates="experience", uselist=False, cascade="all, delete-orphan")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experience_id = Column(UUID(as_uuid=True), ForeignKey("interview_experiences.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(100), nullable=False)
    question_text = Column(Text, nullable=False)
    could_answer = Column(String(20), nullable=False)      # Yes, Partially, No
    ai_tags = Column(JSONB, nullable=True)
    # embedding = Column(Vector(768), nullable=True)       # pgvector — enabled via migration
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    experience = relationship("InterviewExperience", back_populates="questions")


class InterviewOutcome(Base):
    __tablename__ = "interview_outcomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experience_id = Column(UUID(as_uuid=True), ForeignKey("interview_experiences.id", ondelete="CASCADE"), nullable=False, unique=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    success = Column(Boolean, nullable=True)
    topics = Column(JSONB, nullable=True)
    skills_tested = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    experience = relationship("InterviewExperience", back_populates="outcome_record")
