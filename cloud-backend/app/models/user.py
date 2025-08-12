"""
User and profile models
"""

from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User account model"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    subscription_tier = Column(String(50), default="free")  # free, professional, enterprise
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    applications = relationship("JobApplication", back_populates="user")
    resumes = relationship("GeneratedResume", back_populates="user")


class UserProfile(Base, UUIDMixin, TimestampMixin):
    """User profile and preferences"""
    __tablename__ = "user_profiles"
    
    user_id = Column(String(36), nullable=False, index=True)
    
    # Personal information
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    location = Column(String(200))
    
    # Professional information
    work_authorization = Column(String(50))  # citizen, permanent_resident, work_permit, etc.
    experience_years = Column(Integer)
    current_title = Column(String(200))
    target_roles = Column(JSON)  # List of target job titles
    skills = Column(JSON)  # List of skills
    
    # Preferences
    salary_expectation = Column(JSON)  # {"min": 50000, "max": 80000, "currency": "CAD"}
    preferred_locations = Column(JSON)
    remote_preference = Column(String(50))  # remote_only, hybrid, on_site, no_preference
    willing_to_relocate = Column(Boolean, default=False)
    notice_period = Column(String(50))  # immediate, 2_weeks, 1_month, etc.
    
    # Privacy settings
    share_analytics = Column(Boolean, default=True)
    marketing_consent = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", back_populates="profile")


class UserExperience(Base, UUIDMixin, TimestampMixin):
    """User work experience entries"""
    __tablename__ = "user_experience"
    
    user_id = Column(String(36), nullable=False, index=True)
    
    company = Column(String(200), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    start_date = Column(String(10))  # YYYY-MM-DD format
    end_date = Column(String(10))    # YYYY-MM-DD format or null for current
    is_current = Column(Boolean, default=False)
    
    responsibilities = Column(JSON)  # List of responsibility bullets
    technologies = Column(JSON)     # List of technologies used
    achievements = Column(JSON)     # List of achievements
    
    # Location and type
    location = Column(String(200))
    employment_type = Column(String(50))  # full_time, part_time, contract, internship
    
    # Order for display
    display_order = Column(Integer, default=0)


class UserEducation(Base, UUIDMixin, TimestampMixin):
    """User education entries"""
    __tablename__ = "user_education"
    
    user_id = Column(String(36), nullable=False, index=True)
    
    institution = Column(String(200), nullable=False)
    degree_type = Column(String(100))  # bachelor, master, phd, certificate, etc.
    field_of_study = Column(String(200))
    start_date = Column(String(10))
    end_date = Column(String(10))
    gpa = Column(String(10))
    
    honors = Column(JSON)  # List of honors/awards
    relevant_coursework = Column(JSON)
    
    display_order = Column(Integer, default=0)


class UserSettings(Base, UUIDMixin, TimestampMixin):
    """User application and automation settings"""
    __tablename__ = "user_settings"
    
    user_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # Automation preferences
    auto_submit_enabled = Column(Boolean, default=False)
    require_confirmation = Column(Boolean, default=True)
    max_applications_per_day = Column(Integer, default=10)
    
    # Resume preferences
    default_resume_template = Column(String(50), default="professional")
    include_photo = Column(Boolean, default=False)
    preferred_format = Column(String(10), default="pdf")  # pdf, docx
    
    # AI preferences
    ai_enhancement_level = Column(String(20), default="moderate")  # conservative, moderate, aggressive
    rs_confidence_threshold = Column(Float, default=0.7)
    max_rs_bullets = Column(Integer, default=5)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    application_confirmations = Column(Boolean, default=True)
    daily_summaries = Column(Boolean, default=False)
    
    # Privacy preferences
    data_retention_days = Column(Integer, default=365)
    share_anonymous_analytics = Column(Boolean, default=True)