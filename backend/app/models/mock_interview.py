import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base


class MockInterview(Base):
    __tablename__ = "mock_interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    interview_type = Column(String(50), nullable=False)    # behavioral, technical, hm, project, company, custom
    difficulty = Column(String(20), nullable=False)        # Easy, Medium, Hard
    mode = Column(String(20), default="text")              # text, voice
    status = Column(String(20), default="in_progress")     # in_progress, completed, abandoned
    context = Column(JSONB, nullable=True)                 # resume data + company data used
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="mock_interviews")
    company = relationship("Company", back_populates="mock_interviews")
    questions = relationship("MockInterviewQuestion", back_populates="interview", cascade="all, delete-orphan", order_by="MockInterviewQuestion.sequence_num")
    evaluation = relationship("Evaluation", back_populates="interview", uselist=False, cascade="all, delete-orphan")


class MockInterviewQuestion(Base):
    __tablename__ = "mock_interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("mock_interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence_num = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=True)      # main, follow_up
    topic = Column(String(100), nullable=True)
    student_answer = Column(Text, nullable=True)
    ideal_answer = Column(Text, nullable=True)
    audio_url = Column(Text, nullable=True)
    evaluation = Column(JSONB, nullable=True)               # per-question evaluation
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    interview = relationship("MockInterview", back_populates="questions")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("mock_interviews.id", ondelete="CASCADE"), nullable=False, unique=True)

    communication_score = Column(Float, nullable=False)
    communication_reason = Column(Text, nullable=False)
    technical_score = Column(Float, nullable=False)
    technical_reason = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    confidence_reason = Column(Text, nullable=False)
    problem_solving_score = Column(Float, nullable=False)
    problem_solving_reason = Column(Text, nullable=False)
    behavioral_score = Column(Float, nullable=False)
    behavioral_reason = Column(Text, nullable=False)
    project_score = Column(Float, nullable=False)
    project_reason = Column(Text, nullable=False)

    overall_score = Column(Float, nullable=False)
    overall_feedback = Column(Text, nullable=False)
    strengths = Column(JSONB, default=list)
    improvements = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    interview = relationship("MockInterview", back_populates="evaluation")
