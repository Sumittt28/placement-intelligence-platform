"""initial_schema

Revision ID: 001
Revises: 
Create Date: 2026-06-19 11:00:00.295319
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # --- roles ---
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- permissions ---
    op.create_table(
        'permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id'), nullable=False),
        sa.Column('resource', sa.String(100), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.UniqueConstraint('role_id', 'resource', 'action'),
    )

    # --- users ---
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('auth_provider', sa.String(50), server_default='email'),
        sa.Column('supabase_uid', sa.String(255), unique=True, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- user_roles ---
    op.create_table(
        'user_roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id'), nullable=False),
        sa.UniqueConstraint('user_id', 'role_id'),
    )

    # --- profiles ---
    op.create_table(
        'profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('kalvium_id', sa.String(100), unique=True, nullable=True),
        sa.Column('batch', sa.String(50), nullable=True),
        sa.Column('graduation_year', sa.Integer, nullable=True),
        sa.Column('resume_url', sa.Text, nullable=True),
        sa.Column('linkedin_url', sa.Text, nullable=True),
        sa.Column('github_url', sa.Text, nullable=True),
        sa.Column('target_companies', postgresql.JSONB, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- companies ---
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('website', sa.Text, nullable=True),
        sa.Column('logo_url', sa.Text, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- company_analytics ---
    op.create_table(
        'company_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('total_experiences', sa.Integer, server_default='0'),
        sa.Column('total_questions', sa.Integer, server_default='0'),
        sa.Column('top_topics', postgresql.JSONB, server_default='[]'),
        sa.Column('difficulty_dist', postgresql.JSONB, server_default='{}'),
        sa.Column('round_dist', postgresql.JSONB, server_default='{}'),
        sa.Column('success_rate', sa.Float, server_default='0'),
        sa.Column('common_weaknesses', postgresql.JSONB, server_default='[]'),
        sa.Column('recent_90d_weight', sa.Float, server_default='1.0'),
        sa.Column('last_computed', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- interview_experiences ---
    op.create_table(
        'interview_experiences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('role', sa.String(255), nullable=False),
        sa.Column('interview_date', sa.Date, nullable=False),
        sa.Column('round_type', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False),
        sa.Column('outcome', sa.String(20), nullable=False),
        sa.Column('student_notes', sa.Text, nullable=True),
        sa.Column('ai_extracted', postgresql.JSONB, nullable=True),
        sa.Column('is_approved', sa.Boolean, server_default=sa.text('false')),
        sa.Column('is_flagged', sa.Boolean, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_interview_experiences_company', 'interview_experiences', ['company_id'])
    op.create_index('idx_interview_experiences_date', 'interview_experiences', [sa.text('interview_date DESC')])

    # --- interview_questions ---
    op.create_table(
        'interview_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('experience_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('interview_experiences.id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic', sa.String(100), nullable=False),
        sa.Column('question_text', sa.Text, nullable=False),
        sa.Column('could_answer', sa.String(20), nullable=False),
        sa.Column('ai_tags', postgresql.JSONB, nullable=True),
        # embedding vector(768) added separately after pgvector extension
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # Add vector column for embeddings
    op.execute('ALTER TABLE interview_questions ADD COLUMN embedding vector(768)')

    # --- interview_outcomes ---
    op.create_table(
        'interview_outcomes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('experience_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('interview_experiences.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=True),
        sa.Column('success', sa.Boolean, nullable=True),
        sa.Column('topics', postgresql.JSONB, nullable=True),
        sa.Column('skills_tested', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- mock_interviews ---
    op.create_table(
        'mock_interviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=True),
        sa.Column('interview_type', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False),
        sa.Column('mode', sa.String(20), server_default='text'),
        sa.Column('status', sa.String(20), server_default='in_progress'),
        sa.Column('context', postgresql.JSONB, nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_mock_interviews_user', 'mock_interviews', ['user_id'])

    # --- mock_interview_questions ---
    op.create_table(
        'mock_interview_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('interview_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('mock_interviews.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sequence_num', sa.Integer, nullable=False),
        sa.Column('question_text', sa.Text, nullable=False),
        sa.Column('question_type', sa.String(50), nullable=True),
        sa.Column('topic', sa.String(100), nullable=True),
        sa.Column('student_answer', sa.Text, nullable=True),
        sa.Column('ideal_answer', sa.Text, nullable=True),
        sa.Column('audio_url', sa.Text, nullable=True),
        sa.Column('evaluation', postgresql.JSONB, nullable=True),
        sa.Column('feedback', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- evaluations ---
    op.create_table(
        'evaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('interview_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('mock_interviews.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('communication_score', sa.Float, nullable=False),
        sa.Column('communication_reason', sa.Text, nullable=False),
        sa.Column('technical_score', sa.Float, nullable=False),
        sa.Column('technical_reason', sa.Text, nullable=False),
        sa.Column('confidence_score', sa.Float, nullable=False),
        sa.Column('confidence_reason', sa.Text, nullable=False),
        sa.Column('problem_solving_score', sa.Float, nullable=False),
        sa.Column('problem_solving_reason', sa.Text, nullable=False),
        sa.Column('behavioral_score', sa.Float, nullable=False),
        sa.Column('behavioral_reason', sa.Text, nullable=False),
        sa.Column('project_score', sa.Float, nullable=False),
        sa.Column('project_reason', sa.Text, nullable=False),
        sa.Column('overall_score', sa.Float, nullable=False),
        sa.Column('overall_feedback', sa.Text, nullable=False),
        sa.Column('strengths', postgresql.JSONB, server_default='[]'),
        sa.Column('improvements', postgresql.JSONB, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- weaknesses ---
    op.create_table(
        'weaknesses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('occurrence_count', sa.Integer, server_default='1'),
        sa.Column('severity', sa.String(20), nullable=True),
        sa.Column('sources', postgresql.JSONB, server_default='[]'),
        sa.Column('recommended_actions', postgresql.JSONB, server_default='[]'),
        sa.Column('is_resolved', sa.Boolean, server_default=sa.text('false')),
        sa.Column('first_detected', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_detected', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_weaknesses_user', 'weaknesses', ['user_id'])

    # --- recommendations ---
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('priority', sa.Integer, server_default='0'),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('is_completed', sa.Boolean, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- resume_data ---
    op.create_table(
        'resume_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('raw_text', sa.Text, nullable=True),
        sa.Column('skills', postgresql.JSONB, server_default='[]'),
        sa.Column('projects', postgresql.JSONB, server_default='[]'),
        sa.Column('experience', postgresql.JSONB, server_default='[]'),
        sa.Column('technologies', postgresql.JSONB, server_default='[]'),
        sa.Column('domains', postgresql.JSONB, server_default='[]'),
        sa.Column('insights', postgresql.JSONB, server_default='{}'),
        sa.Column('parsed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # Add vector column for resume embeddings
    op.execute('ALTER TABLE resume_data ADD COLUMN embedding vector(768)')

    # --- activity_logs ---
    op.create_table(
        'activity_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource', sa.String(100), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_activity_logs_user', 'activity_logs', ['user_id'])
    op.create_index('idx_activity_logs_created', 'activity_logs', [sa.text('created_at DESC')])

    # --- pgvector indexes ---
    op.execute("""
        CREATE INDEX idx_interview_questions_embedding 
        ON interview_questions USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)

    # --- Seed default roles ---
    op.execute("INSERT INTO roles (name, description) VALUES ('student', 'Student user role')")
    op.execute("INSERT INTO roles (name, description) VALUES ('admin', 'Administrator role')")
    op.execute("INSERT INTO roles (name, description) VALUES ('mentor', 'Mentor role (future)')")


def downgrade() -> None:
    op.drop_table('activity_logs')
    op.drop_table('resume_data')
    op.drop_table('recommendations')
    op.drop_table('weaknesses')
    op.drop_table('evaluations')
    op.drop_table('mock_interview_questions')
    op.drop_table('mock_interviews')
    op.drop_table('interview_outcomes')
    op.drop_table('interview_questions')
    op.drop_table('interview_experiences')
    op.drop_table('company_analytics')
    op.drop_table('companies')
    op.drop_table('profiles')
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.execute('DROP EXTENSION IF EXISTS vector')
