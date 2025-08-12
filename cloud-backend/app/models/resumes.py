"""
Resume and document generation models
"""

from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Float
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, UUIDMixin


class GeneratedResume(Base, UUIDMixin, TimestampMixin):
    """Generated resume versions"""
    __tablename__ = "generated_resumes"
    
    user_id = Column(String(36), nullable=False, index=True)
    job_posting_id = Column(String(36), index=True)  # Null for generic resumes
    
    # Resume metadata
    name = Column(String(200), nullable=False)
    template_used = Column(String(50))
    version_number = Column(Integer, default=1)
    
    # Tailoring information
    is_tailored = Column(Boolean, default=False)
    match_score = Column(Integer)  # 0-100, if tailored
    ats_score = Column(Integer)    # ATS compatibility score
    
    # Content structure
    summary = Column(Text)
    skills_section = Column(JSON)
    experience_sections = Column(JSON)  # Array of experience sections
    education_section = Column(JSON)
    additional_sections = Column(JSON)  # Projects, certifications, etc.
    
    # RS (Reasonable Synthesis) tracking
    rs_bullets_count = Column(Integer, default=0)
    rs_bullets = Column(JSON)  # Array of RS bullet metadata
    rs_risk_level = Column(String(20), default="low")
    
    # Document files
    pdf_url = Column(String(500))   # URL to PDF version
    docx_url = Column(String(500))  # URL to DOCX version
    html_content = Column(Text)     # HTML version for preview
    
    # Usage tracking
    download_count = Column(Integer, default=0)
    application_count = Column(Integer, default=0)  # How many times used in applications
    last_used = Column(DateTime)
    
    # Quality metrics
    readability_score = Column(Float)
    keyword_density = Column(Float)
    length_words = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    diff_reports = relationship("ResumeDiffReport", back_populates="resume")


class ResumeDiffReport(Base, UUIDMixin, TimestampMixin):
    """Diff report showing changes made during tailoring"""
    __tablename__ = "resume_diff_reports"
    
    resume_id = Column(String(36), nullable=False, index=True)
    
    # Change tracking
    changes = Column(JSON)  # Array of change objects
    total_changes = Column(Integer)
    rs_changes = Column(Integer)
    ats_changes = Column(Integer)
    
    # Change categories
    summary_changes = Column(JSON)
    skills_changes = Column(JSON)
    experience_changes = Column(JSON)
    
    # Risk assessment
    overall_risk_level = Column(String(20))
    high_risk_changes = Column(JSON)
    
    # Rollback capability
    original_content = Column(JSON)  # Original resume content for rollback
    can_rollback = Column(Boolean, default=True)
    
    # Relationship
    resume = relationship("GeneratedResume", back_populates="diff_reports")


class ResumeTemplate(Base, UUIDMixin, TimestampMixin):
    """Resume templates and formatting options"""
    __tablename__ = "resume_templates"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    # Template structure
    layout_type = Column(String(50))  # classic, modern, creative, ats_optimized
    color_scheme = Column(String(50))
    font_family = Column(String(50))
    
    # Section configuration
    section_order = Column(JSON)       # Ordered list of sections
    section_styles = Column(JSON)      # Styling for each section
    header_style = Column(JSON)        # Header configuration
    
    # ATS compatibility
    ats_friendly = Column(Boolean, default=True)
    ats_score = Column(Integer)        # Template's baseline ATS score
    
    # Usage and effectiveness
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float)       # Based on application success rates
    
    # Template files
    html_template = Column(Text)       # Jinja2 HTML template
    css_styles = Column(Text)          # CSS styles
    preview_image_url = Column(String(500))
    
    # Availability
    is_public = Column(Boolean, default=True)
    premium_only = Column(Boolean, default=False)


class EvidenceItem(Base, UUIDMixin, TimestampMixin):
    """Evidence vault items for RS"""
    __tablename__ = "evidence_items"
    
    user_id = Column(String(36), nullable=False, index=True)
    
    # Evidence classification
    evidence_type = Column(String(50), nullable=False)  # project, achievement, responsibility, etc.
    category = Column(String(50))  # technical, leadership, process_improvement, etc.
    
    # Content
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    
    # Context information
    company = Column(String(200))
    role = Column(String(200))
    start_date = Column(String(10))
    end_date = Column(String(10))
    
    # Skills and technologies
    skills = Column(JSON)
    technologies = Column(JSON)
    
    # Quantitative data
    metrics = Column(JSON)  # Structured metrics data
    impact_metrics = Column(JSON)  # Business impact metrics
    
    # Verification and confidence
    verification_status = Column(String(20), default="unverified")  # unverified, verified, disputed
    confidence = Column(Float, default=1.0)  # 0.0 to 1.0
    source_documents = Column(JSON)  # References to supporting documents
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Search and retrieval
    tags = Column(JSON)
    search_keywords = Column(Text)  # Preprocessed keywords for search


class CoverLetter(Base, UUIDMixin, TimestampMixin):
    """Generated cover letters"""
    __tablename__ = "cover_letters"
    
    user_id = Column(String(36), nullable=False, index=True)
    job_posting_id = Column(String(36), index=True)
    
    # Content
    content = Column(Text, nullable=False)
    personalized_content = Column(Text)  # Job-specific version
    
    # Generation metadata
    template_used = Column(String(50))
    ai_generated = Column(Boolean, default=True)
    personalization_score = Column(Integer)  # 0-100
    
    # Structure
    opening_paragraph = Column(Text)
    body_paragraphs = Column(JSON)
    closing_paragraph = Column(Text)
    
    # Quality metrics
    word_count = Column(Integer)
    readability_score = Column(Float)
    enthusiasm_score = Column(Float)  # AI-assessed enthusiasm level
    
    # Usage
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)


class DocumentGeneration(Base, UUIDMixin, TimestampMixin):
    """Document generation job tracking"""
    __tablename__ = "document_generations"
    
    user_id = Column(String(36), nullable=False, index=True)
    
    # Job details
    generation_type = Column(String(50), nullable=False)  # resume, cover_letter, portfolio
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    
    # Input parameters
    input_data = Column(JSON)  # Parameters used for generation
    template_id = Column(String(36))
    
    # Output
    generated_files = Column(JSON)  # URLs to generated files
    preview_url = Column(String(500))
    
    # Processing details
    processing_time_ms = Column(Integer)
    error_message = Column(Text)
    
    # Quality assessment
    quality_score = Column(Float)
    ats_compatibility = Column(Integer)
    
    # File metadata
    file_sizes = Column(JSON)  # File sizes in bytes
    formats_generated = Column(JSON)  # [pdf, docx, html]