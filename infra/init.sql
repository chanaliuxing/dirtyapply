-- Apply-Copilot Database Initialization
-- This script creates the initial database structure

-- Create database (if not exists)
SELECT 'CREATE DATABASE apply_copilot'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'apply_copilot')\gexec

-- Connect to apply_copilot database
\c apply_copilot;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create basic tables (will be managed by Alembic migrations)
-- This is just for initial structure

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job postings table
CREATE TABLE IF NOT EXISTS job_postings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255) NOT NULL,
    source VARCHAR(100) NOT NULL,
    url TEXT,
    jd_html TEXT,
    jd_text TEXT,
    requirements JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    job_posting_id UUID REFERENCES job_postings(id),
    status VARCHAR(50) DEFAULT 'pending',
    match_score DECIMAL(3,2),
    tailored_resume_url VARCHAR(500),
    action_plan JSONB,
    submitted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Evidence vault table
CREATE TABLE IF NOT EXISTS evidence_vault (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    text TEXT NOT NULL,
    skills JSONB,
    achievement_year INTEGER,
    source_document VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume profiles table
CREATE TABLE IF NOT EXISTS resume_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_posting_id ON applications(job_posting_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_evidence_vault_user_id ON evidence_vault(user_id);
CREATE INDEX IF NOT EXISTS idx_job_postings_company ON job_postings(company);
CREATE INDEX IF NOT EXISTS idx_job_postings_source ON job_postings(source);
CREATE INDEX IF NOT EXISTS idx_resume_profiles_user_id ON resume_profiles(user_id);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_job_postings_text_search 
    ON job_postings USING gin(to_tsvector('english', jd_text));
CREATE INDEX IF NOT EXISTS idx_evidence_vault_text_search 
    ON evidence_vault USING gin(to_tsvector('english', text));

-- Insert sample data for development
INSERT INTO users (id, email, full_name) VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', 'dev@apply-copilot.com', 'Development User')
ON CONFLICT (email) DO NOTHING;

COMMENT ON DATABASE apply_copilot IS 'Apply-Copilot application database';
COMMENT ON TABLE users IS 'User accounts and profiles';
COMMENT ON TABLE job_postings IS 'Job postings scraped from various sources';
COMMENT ON TABLE applications IS 'Job applications submitted by users';
COMMENT ON TABLE evidence_vault IS 'User achievements and evidence for resume tailoring';
COMMENT ON TABLE resume_profiles IS 'User resume templates and profiles';