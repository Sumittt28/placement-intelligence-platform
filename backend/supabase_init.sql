-- ============================================================
-- Placement Intelligence Platform - Initial Database Schema
-- Run this in Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)
-- ============================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- roles
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- permissions
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID REFERENCES roles(id),
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    UNIQUE(role_id, resource, action)
);

-- users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    auth_provider VARCHAR(50) DEFAULT 'email',
    supabase_uid VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- user_roles
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id),
    UNIQUE(user_id, role_id)
);

-- profiles
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    kalvium_id VARCHAR(100) UNIQUE,
    batch VARCHAR(50),
    graduation_year INTEGER,
    resume_url TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    target_companies JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- companies
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    industry VARCHAR(100),
    website TEXT,
    logo_url TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);

-- company_analytics
CREATE TABLE IF NOT EXISTS company_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID UNIQUE REFERENCES companies(id) ON DELETE CASCADE,
    total_experiences INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    top_topics JSONB DEFAULT '[]',
    difficulty_dist JSONB DEFAULT '{}',
    round_dist JSONB DEFAULT '{}',
    success_rate FLOAT DEFAULT 0,
    common_weaknesses JSONB DEFAULT '[]',
    recent_90d_weight FLOAT DEFAULT 1.0,
    last_computed TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- interview_experiences
CREATE TABLE IF NOT EXISTS interview_experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id),
    role VARCHAR(255) NOT NULL,
    interview_date DATE NOT NULL,
    round_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    outcome VARCHAR(20) NOT NULL,
    student_notes TEXT,
    ai_extracted JSONB,
    is_approved BOOLEAN DEFAULT false,
    is_flagged BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_exp_company ON interview_experiences(company_id);
CREATE INDEX IF NOT EXISTS idx_exp_user ON interview_experiences(user_id);

-- interview_questions
CREATE TABLE IF NOT EXISTS interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experience_id UUID REFERENCES interview_experiences(id) ON DELETE CASCADE,
    topic VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    could_answer VARCHAR(20) NOT NULL,
    ai_tags JSONB,
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- interview_outcomes
CREATE TABLE IF NOT EXISTS interview_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experience_id UUID UNIQUE REFERENCES interview_experiences(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id),
    success BOOLEAN,
    topics JSONB,
    skills_tested JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- mock_interviews
CREATE TABLE IF NOT EXISTS mock_interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id),
    interview_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    mode VARCHAR(20) DEFAULT 'text',
    status VARCHAR(20) DEFAULT 'in_progress',
    context JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_mock_user ON mock_interviews(user_id);

-- mock_interview_questions
CREATE TABLE IF NOT EXISTS mock_interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_id UUID REFERENCES mock_interviews(id) ON DELETE CASCADE,
    sequence_num INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50),
    topic VARCHAR(100),
    student_answer TEXT,
    ideal_answer TEXT,
    audio_url TEXT,
    evaluation JSONB,
    feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- evaluations
CREATE TABLE IF NOT EXISTS evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_id UUID UNIQUE REFERENCES mock_interviews(id) ON DELETE CASCADE,
    communication_score FLOAT NOT NULL,
    communication_reason TEXT NOT NULL,
    technical_score FLOAT NOT NULL,
    technical_reason TEXT NOT NULL,
    confidence_score FLOAT NOT NULL,
    confidence_reason TEXT NOT NULL,
    problem_solving_score FLOAT NOT NULL,
    problem_solving_reason TEXT NOT NULL,
    behavioral_score FLOAT NOT NULL,
    behavioral_reason TEXT NOT NULL,
    project_score FLOAT NOT NULL,
    project_reason TEXT NOT NULL,
    overall_score FLOAT NOT NULL,
    overall_feedback TEXT NOT NULL,
    strengths JSONB DEFAULT '[]',
    improvements JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- weaknesses
CREATE TABLE IF NOT EXISTS weaknesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    topic VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    occurrence_count INTEGER DEFAULT 1,
    severity VARCHAR(20),
    sources JSONB DEFAULT '[]',
    recommended_actions JSONB DEFAULT '[]',
    is_resolved BOOLEAN DEFAULT false,
    first_detected TIMESTAMPTZ DEFAULT NOW(),
    last_detected TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_weaknesses_user ON weaknesses(user_id);

-- recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    is_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- resume_data
CREATE TABLE IF NOT EXISTS resume_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    raw_text TEXT,
    skills JSONB DEFAULT '[]',
    projects JSONB DEFAULT '[]',
    experience JSONB DEFAULT '[]',
    technologies JSONB DEFAULT '[]',
    domains JSONB DEFAULT '[]',
    insights JSONB DEFAULT '{}',
    embedding vector(768),
    parsed_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- activity_logs
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    resource_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_created ON activity_logs(created_at DESC);

-- Seed default roles
INSERT INTO roles (name, description) VALUES ('student', 'Student user role') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name, description) VALUES ('admin', 'Administrator role') ON CONFLICT (name) DO NOTHING;
INSERT INTO roles (name, description) VALUES ('mentor', 'Mentor role (future)') ON CONFLICT (name) DO NOTHING;

-- Seed sample companies
INSERT INTO companies (name, industry, description) VALUES
    ('Google', 'Technology', 'Global technology leader'),
    ('Amazon', 'E-Commerce/Cloud', 'E-commerce and cloud computing giant'),
    ('Microsoft', 'Technology', 'Software and cloud services leader'),
    ('Flipkart', 'E-Commerce', 'Indian e-commerce marketplace'),
    ('Zomato', 'Food Tech', 'Food delivery and restaurant discovery platform'),
    ('Razorpay', 'Fintech', 'Payment gateway and financial services'),
    ('Swiggy', 'Food Tech', 'Food and grocery delivery platform'),
    ('Paytm', 'Fintech', 'Digital payments and financial services'),
    ('PhonePe', 'Fintech', 'Digital payments platform'),
    ('Infosys', 'IT Services', 'Global IT consulting and services')
ON CONFLICT (name) DO NOTHING;

-- Done!
SELECT 'Database initialized successfully!' AS status;
