"""
Job-related models
"""

from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Float
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, UUIDMixin


class JobPosting(Base, UUIDMixin, TimestampMixin):
    """Job posting information"""
    __tablename__ = "job_postings"
    
    # External identifiers
    source = Column(String(50), nullable=False)  # indeed, linkedin, greenhouse, etc.
    external_id = Column(String(200))  # ID from source system
    url = Column(String(1000))
    
    # Basic job information
    title = Column(String(300), nullable=False, index=True)
    company = Column(String(200), nullable=False, index=True)
    location = Column(String(200))
    salary_range = Column(String(100))
    employment_type = Column(String(50))  # full_time, part_time, contract
    remote_policy = Column(String(50))   # remote, hybrid, on_site
    
    # Job details
    description = Column(Text)
    requirements = Column(Text)
    responsibilities = Column(Text)
    benefits = Column(Text)
    
    # Parsed information (from AI analysis)
    required_skills = Column(JSON)
    nice_to_have_skills = Column(JSON)
    experience_level = Column(String(50))  # entry, mid, senior, executive
    education_requirements = Column(JSON)
    
    # Metadata
    posted_date = Column(DateTime)
    expires_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Analysis results
    ats_complexity = Column(String(20))  # simple, medium, complex
    application_process = Column(JSON)   # Steps in application process
    
    # Relationships
    applications = relationship("JobApplication", back_populates="job_posting")
    analyses = relationship("JobAnalysis", back_populates="job_posting")


class JobAnalysis(Base, UUIDMixin, TimestampMixin):
    """AI analysis results for job postings"""
    __tablename__ = "job_analyses"
    
    job_posting_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)  # Analysis is user-specific
    
    # Match analysis
    overall_match_score = Column(Integer)  # 0-100
    skills_match_score = Column(Float)
    experience_match_score = Column(Float)
    education_match_score = Column(Float)
    location_match_score = Column(Float)
    
    # Detailed breakdown
    matching_skills = Column(JSON)
    skill_gaps = Column(JSON)
    experience_analysis = Column(JSON)
    
    # Recommendations
    recommendations = Column(JSON)
    improvement_suggestions = Column(JSON)
    
    # Analysis metadata
    analysis_method = Column(String(50))  # ai_enhanced, rule_based, hybrid
    confidence_score = Column(Float)
    processing_time_ms = Column(Integer)
    
    # Relationship
    job_posting = relationship("JobPosting", back_populates="analyses")


class JobApplication(Base, UUIDMixin, TimestampMixin):
    """Job application tracking"""
    __tablename__ = "job_applications"
    
    user_id = Column(String(36), nullable=False, index=True)
    job_posting_id = Column(String(36), nullable=False, index=True)
    
    # Application details
    status = Column(String(50), default="draft")  # draft, submitted, interviewing, rejected, offered
    applied_date = Column(DateTime)
    
    # Documents used
    resume_version_id = Column(String(36))
    cover_letter_id = Column(String(36))
    
    # Application data
    form_responses = Column(JSON)  # Q&A responses submitted
    custom_fields = Column(JSON)   # Additional fields filled
    
    # Automation details
    auto_filled = Column(Boolean, default=False)
    auto_submitted = Column(Boolean, default=False)
    automation_notes = Column(Text)
    
    # Follow-up tracking
    follow_up_date = Column(DateTime)
    follow_up_status = Column(String(50))
    
    # Communication log
    communications = Column(JSON)  # Array of communication entries
    
    # Relationships
    user = relationship("User", back_populates="applications")
    job_posting = relationship("JobPosting", back_populates="applications")
    resume_version = relationship("GeneratedResume", foreign_keys=[resume_version_id])


class CompanyProfile(Base, UUIDMixin, TimestampMixin):
    """Company information and insights"""
    __tablename__ = "company_profiles"
    
    name = Column(String(200), unique=True, nullable=False, index=True)
    domain = Column(String(100))  # company.com
    
    # Basic information
    industry = Column(String(100))
    size = Column(String(50))      # startup, small, medium, large, enterprise
    location = Column(String(200))  # HQ location
    
    # Culture and values
    culture_keywords = Column(JSON)
    values = Column(JSON)
    work_environment = Column(String(50))  # fast_paced, collaborative, innovative, etc.
    
    # Hiring patterns
    hiring_frequency = Column(String(20))  # high, medium, low
    typical_process = Column(JSON)         # Typical interview process
    response_time_days = Column(Integer)   # Average response time
    
    # Application success insights
    successful_applicant_patterns = Column(JSON)
    common_rejection_reasons = Column(JSON)
    
    # Social presence
    linkedin_url = Column(String(300))
    careers_page_url = Column(String(300))
    
    # Analysis metadata
    last_analyzed = Column(DateTime)
    data_completeness_score = Column(Float)  # 0.0 to 1.0


class JobApplicationTemplate(Base, UUIDMixin, TimestampMixin):
    """Templates for common application questions"""
    __tablename__ = "job_application_templates"
    
    user_id = Column(String(36), nullable=False, index=True)
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Question-answer pairs
    qa_pairs = Column(JSON)  # Array of {question, answer, category} objects
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Template metadata
    categories = Column(JSON)  # Tags for organization
    is_public = Column(Boolean, default=False)  # Can be shared with other users
    effectiveness_score = Column(Float)  # Based on application success rates