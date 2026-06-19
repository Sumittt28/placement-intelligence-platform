import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base


class Weakness(Base):
    __tablename__ = "weaknesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)           # technical, behavioral, communication
    occurrence_count = Column(Integer, default=1)
    severity = Column(String(20), nullable=True)           # low, medium, high
    sources = Column(JSONB, default=list)                  # list of interview IDs where detected
    recommended_actions = Column(JSONB, default=list)
    is_resolved = Column(Boolean, default=False)
    first_detected = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_detected = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="weaknesses")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)              # topic, practice_plan, mock_interview
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=0)
    metadata_ = Column("metadata", JSONB, default=dict)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="recommendations")


class ResumeData(Base):
    __tablename__ = "resume_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    raw_text = Column(Text, nullable=True)
    skills = Column(JSONB, default=list)
    projects = Column(JSONB, default=list)
    experience = Column(JSONB, default=list)
    technologies = Column(JSONB, default=list)
    domains = Column(JSONB, default=list)
    insights = Column(JSONB, default=dict)
    # embedding = Column(Vector(768), nullable=True)       # pgvector — enabled via migration
    parsed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="resume_data")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="activity_logs")
