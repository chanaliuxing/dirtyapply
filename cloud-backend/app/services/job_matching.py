"""
Job Matching Service - AI-powered job compatibility analysis
Calculates match scores, identifies skill gaps, and provides recommendations
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
import math
from dataclasses import dataclass, asdict
from collections import defaultdict
import structlog

# ML/AI imports for advanced matching
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import pandas as pd
except ImportError:
    print("Warning: ML libraries not installed. Using fallback matching.")
    TfidfVectorizer = None
    SentenceTransformer = None

from app.core.config import settings
from app.ai.orchestrator import get_ai_orchestrator, AITask, TaskType

logger = structlog.get_logger(__name__)


@dataclass
class SkillMatch:
    """Individual skill match result"""
    skill: str
    user_has: bool
    proficiency_level: Optional[str] = None  # beginner, intermediate, advanced, expert
    importance: str = "medium"  # low, medium, high, critical
    match_confidence: float = 1.0
    synonyms_matched: List[str] = None
    
    def __post_init__(self):
        if self.synonyms_matched is None:
            self.synonyms_matched = []


@dataclass
class JobMatchAnalysis:
    """Complete job match analysis result"""
    job_id: str
    user_id: str
    overall_match_score: int  # 0-100
    skill_matches: List[SkillMatch]
    experience_match: Dict[str, Any]
    education_match: Dict[str, Any]
    location_match: Dict[str, Any]
    salary_match: Dict[str, Any]
    must_have_coverage: Dict[str, bool]
    nice_to_have_coverage: Dict[str, bool]
    skill_gaps: List[str]
    recommendations: List[str]
    analysis_metadata: Dict[str, Any]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        result = asdict(self)
        # Convert datetime to ISO string
        result['created_at'] = self.created_at.isoformat()
        return result


class JobMatchingService:
    """
    Advanced job matching service using AI and ML techniques
    Provides comprehensive compatibility analysis between jobs and candidates
    """
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.ai_orchestrator = get_ai_orchestrator()
        
        # Initialize ML models
        self.tfidf_vectorizer = None
        self.sentence_transformer = None
        self._initialize_ml_models()
        
        # Load skill taxonomy and mappings
        self.skill_taxonomy = self._load_skill_taxonomy()
        self.skill_synonyms = self._load_skill_synonyms()
        self.experience_patterns = self._load_experience_patterns()
    
    def _initialize_ml_models(self):
        """Initialize ML models for advanced matching"""
        try:
            if TfidfVectorizer:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                self.logger.info("TF-IDF vectorizer initialized")
            
            # Initialize sentence transformer for semantic similarity
            if SentenceTransformer:
                try:
                    self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
                    self.logger.info("Sentence transformer model loaded")
                except Exception as e:
                    self.logger.warning("Failed to load sentence transformer", error=str(e))
                    
        except Exception as e:
            self.logger.error("Failed to initialize ML models", error=str(e))
    
    def _load_skill_taxonomy(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive skill taxonomy with categories and levels"""
        return {
            # Programming Languages
            "JavaScript": {
                "category": "programming",
                "difficulty": "medium",
                "synonyms": ["JS", "ECMAScript", "Node.js", "React", "Vue", "Angular"],
                "related": ["HTML", "CSS", "TypeScript", "JSON"],
                "seniority_indicators": {
                    "beginner": ["basic syntax", "DOM manipulation"],
                    "intermediate": ["async/await", "ES6+", "frameworks"],
                    "advanced": ["performance optimization", "design patterns"],
                    "expert": ["V8 internals", "framework architecture"]
                }
            },
            "Python": {
                "category": "programming",
                "difficulty": "medium",
                "synonyms": ["Python3", "Django", "Flask", "FastAPI", "NumPy", "Pandas"],
                "related": ["SQL", "Machine Learning", "Data Science"],
                "seniority_indicators": {
                    "beginner": ["basic syntax", "loops", "functions"],
                    "intermediate": ["OOP", "decorators", "frameworks"],
                    "advanced": ["metaclasses", "async programming"],
                    "expert": ["CPython internals", "performance tuning"]
                }
            },
            "React": {
                "category": "frontend_framework",
                "difficulty": "medium",
                "synonyms": ["React.js", "ReactJS", "React Native"],
                "related": ["JavaScript", "JSX", "Redux", "Hooks"],
                "seniority_indicators": {
                    "beginner": ["components", "props", "state"],
                    "intermediate": ["hooks", "context", "lifecycle"],
                    "advanced": ["performance optimization", "custom hooks"],
                    "expert": ["internals", "concurrent features"]
                }
            },
            "AWS": {
                "category": "cloud_platform",
                "difficulty": "high",
                "synonyms": ["Amazon Web Services", "EC2", "S3", "Lambda", "CloudFormation"],
                "related": ["Docker", "Kubernetes", "DevOps", "Terraform"],
                "seniority_indicators": {
                    "beginner": ["EC2", "S3", "basic services"],
                    "intermediate": ["VPC", "IAM", "CloudFormation"],
                    "advanced": ["multi-region", "cost optimization"],
                    "expert": ["well-architected", "enterprise patterns"]
                }
            },
            "Machine Learning": {
                "category": "ai_ml",
                "difficulty": "high",
                "synonyms": ["ML", "Artificial Intelligence", "AI", "Deep Learning"],
                "related": ["Python", "Statistics", "Data Science", "TensorFlow"],
                "seniority_indicators": {
                    "beginner": ["supervised learning", "basic algorithms"],
                    "intermediate": ["feature engineering", "model selection"],
                    "advanced": ["deep learning", "MLOps"],
                    "expert": ["research", "novel architectures"]
                }
            },
            # Add more skills as needed
            "SQL": {
                "category": "database",
                "difficulty": "medium",
                "synonyms": ["MySQL", "PostgreSQL", "SQLite", "Database", "RDBMS"],
                "related": ["Python", "Data Analysis", "ETL"],
                "seniority_indicators": {
                    "beginner": ["SELECT", "basic queries", "joins"],
                    "intermediate": ["subqueries", "functions", "indexes"],
                    "advanced": ["optimization", "stored procedures"],
                    "expert": ["database design", "performance tuning"]
                }
            }
        }
    
    def _load_skill_synonyms(self) -> Dict[str, List[str]]:
        """Extract skill synonyms from taxonomy"""
        synonyms = {}
        for skill, data in self.skill_taxonomy.items():
            synonyms[skill] = data.get('synonyms', [])
        return synonyms
    
    def _load_experience_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load experience level patterns and indicators"""
        return {
            "entry_level": {
                "years_range": (0, 2),
                "keywords": ["entry", "junior", "graduate", "new grad", "associate"],
                "typical_titles": ["junior", "associate", "entry-level", "trainee"]
            },
            "mid_level": {
                "years_range": (2, 5),
                "keywords": ["mid-level", "intermediate", "experienced"],
                "typical_titles": ["developer", "analyst", "specialist", "coordinator"]
            },
            "senior_level": {
                "years_range": (5, 10),
                "keywords": ["senior", "lead", "principal"],
                "typical_titles": ["senior", "lead", "principal", "architect"]
            },
            "executive_level": {
                "years_range": (10, 100),
                "keywords": ["director", "manager", "head", "VP", "CTO", "executive"],
                "typical_titles": ["director", "manager", "VP", "head", "chief"]
            }
        }
    
    async def analyze_job_match(
        self,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive job match analysis
        """
        try:
            self.logger.info(
                "Starting job match analysis",
                job_id=job_data.get('job_id'),
                user_id=user_profile.get('user_id')
            )
            
            # Step 1: Extract and analyze job requirements
            job_analysis = await self._analyze_job_requirements(job_data)
            
            # Step 2: Skill matching analysis
            skill_matches = await self._analyze_skill_matches(job_analysis, user_profile)
            
            # Step 3: Experience level matching
            experience_match = await self._analyze_experience_match(job_analysis, user_profile)
            
            # Step 4: Education matching
            education_match = await self._analyze_education_match(job_analysis, user_profile)
            
            # Step 5: Location and salary matching
            location_match = await self._analyze_location_match(job_data, user_profile)
            salary_match = await self._analyze_salary_match(job_data, user_profile)
            
            # Step 6: Calculate overall match score
            overall_score = await self._calculate_overall_match_score({
                'skills': skill_matches,
                'experience': experience_match,
                'education': education_match,
                'location': location_match,
                'salary': salary_match
            })
            
            # Step 7: Identify gaps and generate recommendations
            skill_gaps = await self._identify_skill_gaps(skill_matches)
            recommendations = await self._generate_recommendations(
                skill_matches, experience_match, skill_gaps, overall_score
            )
            
            # Step 8: Create analysis result
            analysis = JobMatchAnalysis(
                job_id=job_data.get('job_id', 'unknown'),
                user_id=user_profile.get('user_id', 'unknown'),
                overall_match_score=overall_score,
                skill_matches=skill_matches,
                experience_match=experience_match,
                education_match=education_match,
                location_match=location_match,
                salary_match=salary_match,
                must_have_coverage=self._calculate_must_have_coverage(skill_matches, job_analysis),
                nice_to_have_coverage=self._calculate_nice_to_have_coverage(skill_matches, job_analysis),
                skill_gaps=skill_gaps,
                recommendations=recommendations,
                analysis_metadata={
                    "analysis_method": "ai_enhanced" if self.sentence_transformer else "rule_based",
                    "confidence": min(overall_score / 100.0, 0.95),
                    "processing_time": 0.0,  # Would track in real implementation
                    "model_version": "1.0.0"
                },
                created_at=datetime.utcnow()
            )
            
            self.logger.info(
                "Job match analysis completed",
                overall_score=overall_score,
                skill_matches=len(skill_matches),
                gaps=len(skill_gaps)
            )
            
            return analysis.to_dict()
            
        except Exception as e:
            self.logger.error("Job match analysis failed", error=str(e))
            raise
    
    async def _analyze_job_requirements(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and categorize job requirements"""
        
        # Use AI orchestrator for advanced analysis
        task = AITask(
            task_id=f"job_req_analysis_{datetime.utcnow().timestamp()}",
            task_type=TaskType.JOB_ANALYSIS,
            input_data=job_data
        )
        
        response = await self.ai_orchestrator.execute_task(task)
        
        if response.success:
            return response.result
        else:
            # Fallback analysis
            return await self._fallback_job_analysis(job_data)
    
    async def _fallback_job_analysis(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based job analysis fallback"""
        description = job_data.get('description', '').lower()
        title = job_data.get('title', '').lower()
        
        # Extract skills using taxonomy
        required_skills = []
        nice_to_have = []
        
        for skill, info in self.skill_taxonomy.items():
            skill_lower = skill.lower()
            synonyms = [s.lower() for s in info.get('synonyms', [])]
            
            # Check if skill is mentioned
            if (skill_lower in description or 
                skill_lower in title or
                any(syn in description for syn in synonyms)):
                
                # Determine if required or nice-to-have based on context
                context_window = self._extract_context_around_skill(description, skill_lower, synonyms)
                
                if any(req_word in context_window for req_word in 
                       ['required', 'must', 'essential', 'mandatory', 'minimum']):
                    required_skills.append(skill)
                else:
                    nice_to_have.append(skill)
        
        # Extract experience level
        experience_level = "mid"  # default
        for level, patterns in self.experience_patterns.items():
            if any(keyword in description for keyword in patterns['keywords']):
                experience_level = level
                break
        
        # Extract education requirements
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma']
        education_required = any(edu in description for edu in education_keywords)
        
        return {
            "required_skills": required_skills[:15],  # Limit to top 15
            "nice_to_have": nice_to_have[:10],
            "experience_level": experience_level,
            "education_required": education_required,
            "seniority_level": self._infer_seniority_from_title(title),
            "analysis_confidence": 0.7
        }
    
    def _extract_context_around_skill(
        self, 
        text: str, 
        skill: str, 
        synonyms: List[str]
    ) -> str:
        """Extract context around skill mentions for better classification"""
        import re
        
        # Find all mentions of the skill or its synonyms
        all_terms = [skill] + synonyms
        context_parts = []
        
        for term in all_terms:
            # Create regex pattern for the term
            pattern = rf'.{{0,50}}\b{re.escape(term)}\b.{{0,50}}'
            matches = re.findall(pattern, text, re.IGNORECASE)
            context_parts.extend(matches)
        
        return ' '.join(context_parts)
    
    def _infer_seniority_from_title(self, title: str) -> str:
        """Infer seniority level from job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['senior', 'sr', 'lead', 'principal', 'architect']):
            return 'senior'
        elif any(word in title_lower for word in ['junior', 'jr', 'entry', 'associate', 'trainee']):
            return 'junior'
        else:
            return 'mid'
    
    async def _analyze_skill_matches(
        self,
        job_analysis: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> List[SkillMatch]:
        """Analyze skill matches with proficiency and importance"""
        
        required_skills = job_analysis.get('required_skills', [])
        nice_to_have = job_analysis.get('nice_to_have', [])
        user_skills = user_profile.get('skills', [])
        user_experience = user_profile.get('experience', [])
        
        skill_matches = []
        
        # Analyze required skills
        for skill in required_skills:
            match = await self._analyze_individual_skill_match(
                skill, user_skills, user_experience, importance="high"
            )
            skill_matches.append(match)
        
        # Analyze nice-to-have skills
        for skill in nice_to_have:
            match = await self._analyze_individual_skill_match(
                skill, user_skills, user_experience, importance="medium"
            )
            skill_matches.append(match)
        
        return skill_matches
    
    async def _analyze_individual_skill_match(
        self,
        required_skill: str,
        user_skills: List[str],
        user_experience: List[Dict[str, Any]],
        importance: str = "medium"
    ) -> SkillMatch:
        """Analyze match for individual skill"""
        
        # Direct match
        if required_skill in user_skills:
            proficiency = self._infer_proficiency_level(required_skill, user_experience)
            return SkillMatch(
                skill=required_skill,
                user_has=True,
                proficiency_level=proficiency,
                importance=importance,
                match_confidence=1.0
            )
        
        # Check synonyms
        skill_info = self.skill_taxonomy.get(required_skill, {})
        synonyms = skill_info.get('synonyms', [])
        
        matched_synonyms = []
        for synonym in synonyms:
            if any(synonym.lower() in user_skill.lower() for user_skill in user_skills):
                matched_synonyms.append(synonym)
        
        if matched_synonyms:
            proficiency = self._infer_proficiency_level(required_skill, user_experience)
            return SkillMatch(
                skill=required_skill,
                user_has=True,
                proficiency_level=proficiency,
                importance=importance,
                match_confidence=0.8,
                synonyms_matched=matched_synonyms
            )
        
        # Semantic similarity check (if available)
        if self.sentence_transformer:
            semantic_score = await self._calculate_semantic_similarity(
                required_skill, user_skills
            )
            if semantic_score > 0.7:
                return SkillMatch(
                    skill=required_skill,
                    user_has=True,
                    proficiency_level="beginner",
                    importance=importance,
                    match_confidence=semantic_score,
                    synonyms_matched=[f"semantic_match_{semantic_score:.2f}"]
                )
        
        # No match
        return SkillMatch(
            skill=required_skill,
            user_has=False,
            importance=importance,
            match_confidence=0.0
        )
    
    def _infer_proficiency_level(
        self,
        skill: str,
        user_experience: List[Dict[str, Any]]
    ) -> str:
        """Infer user's proficiency level for a skill"""
        
        # Look for skill mentions in experience descriptions
        skill_mentions = 0
        total_years = 0
        advanced_indicators = 0
        
        skill_info = self.skill_taxonomy.get(skill, {})
        synonyms = [skill.lower()] + [s.lower() for s in skill_info.get('synonyms', [])]
        seniority_indicators = skill_info.get('seniority_indicators', {})
        
        for exp in user_experience:
            description = exp.get('description', '').lower()
            responsibilities = exp.get('responsibilities', [])
            exp_text = f"{description} {' '.join(responsibilities)}".lower()
            
            # Check for skill mentions
            if any(syn in exp_text for syn in synonyms):
                skill_mentions += 1
                
                # Calculate years for this role
                start_date = exp.get('start_date', '')
                end_date = exp.get('end_date', 'present')
                years = self._calculate_years_of_experience(start_date, end_date)
                total_years += years
                
                # Check for advanced indicators
                advanced_keywords = seniority_indicators.get('advanced', []) + seniority_indicators.get('expert', [])
                if any(keyword.lower() in exp_text for keyword in advanced_keywords):
                    advanced_indicators += 1
        
        # Determine proficiency level
        if total_years >= 5 or advanced_indicators >= 2:
            return "expert"
        elif total_years >= 3 or advanced_indicators >= 1:
            return "advanced"
        elif total_years >= 1 or skill_mentions >= 2:
            return "intermediate"
        elif skill_mentions >= 1:
            return "beginner"
        else:
            return "beginner"
    
    def _calculate_years_of_experience(self, start_date: str, end_date: str) -> float:
        """Calculate years between two dates"""
        try:
            from datetime import datetime
            
            if end_date.lower() in ['present', 'current', '']:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Simple year calculation (assumes YYYY-MM-DD format)
            start_year = int(start_date.split('-')[0]) if start_date else 0
            end_year = int(end_date.split('-')[0]) if end_date else datetime.now().year
            
            return max(0, end_year - start_year)
        except (ValueError, IndexError):
            return 0
    
    async def _calculate_semantic_similarity(
        self,
        required_skill: str,
        user_skills: List[str]
    ) -> float:
        """Calculate semantic similarity using sentence transformers"""
        
        if not self.sentence_transformer or not user_skills:
            return 0.0
        
        try:
            # Encode required skill
            required_embedding = self.sentence_transformer.encode([required_skill])
            
            # Encode user skills
            user_embeddings = self.sentence_transformer.encode(user_skills)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(required_embedding, user_embeddings)[0]
            
            # Return maximum similarity
            return float(max(similarities))
            
        except Exception as e:
            self.logger.error("Semantic similarity calculation failed", error=str(e))
            return 0.0
    
    async def _analyze_experience_match(
        self,
        job_analysis: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze experience level compatibility"""
        
        required_level = job_analysis.get('experience_level', 'mid')
        required_patterns = self.experience_patterns.get(required_level, {})
        required_years_range = required_patterns.get('years_range', (2, 5))
        
        user_total_years = user_profile.get('experience_years', 0)
        user_relevant_years = self._calculate_relevant_experience(user_profile, job_analysis)
        
        # Calculate match scores
        total_years_match = self._calculate_years_match_score(
            user_total_years, required_years_range
        )
        
        relevant_years_match = self._calculate_years_match_score(
            user_relevant_years, required_years_range
        )
        
        # Overall experience match
        experience_match_score = (total_years_match * 0.4 + relevant_years_match * 0.6)
        
        return {
            "match_score": int(experience_match_score),
            "required_level": required_level,
            "user_total_years": user_total_years,
            "user_relevant_years": user_relevant_years,
            "required_years_range": required_years_range,
            "meets_minimum": user_total_years >= required_years_range[0],
            "overqualified": user_total_years > required_years_range[1] * 1.5
        }
    
    def _calculate_relevant_experience(
        self,
        user_profile: Dict[str, Any],
        job_analysis: Dict[str, Any]
    ) -> float:
        """Calculate years of relevant experience"""
        
        required_skills = set(skill.lower() for skill in job_analysis.get('required_skills', []))
        user_experience = user_profile.get('experience', [])
        
        relevant_years = 0.0
        
        for exp in user_experience:
            description = exp.get('description', '').lower()
            responsibilities = ' '.join(exp.get('responsibilities', [])).lower()
            exp_text = f"{description} {responsibilities}"
            
            # Check if this experience is relevant
            skill_mentions = sum(1 for skill in required_skills if skill in exp_text)
            relevance_score = min(skill_mentions / len(required_skills), 1.0) if required_skills else 0.5
            
            if relevance_score > 0.3:  # At least 30% skill overlap
                years = self._calculate_years_of_experience(
                    exp.get('start_date', ''),
                    exp.get('end_date', '')
                )
                relevant_years += years * relevance_score
        
        return relevant_years
    
    def _calculate_years_match_score(
        self, 
        user_years: float, 
        required_range: Tuple[int, int]
    ) -> float:
        """Calculate how well user's years match required range"""
        
        min_years, max_years = required_range
        
        if min_years <= user_years <= max_years:
            return 100.0
        elif user_years < min_years:
            # Under-qualified
            return max(0, (user_years / min_years) * 80)
        else:
            # Over-qualified (diminishing returns)
            excess = user_years - max_years
            penalty = min(excess * 5, 30)  # Up to 30% penalty
            return max(70, 100 - penalty)
    
    async def _analyze_education_match(
        self,
        job_analysis: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze education requirements match"""
        
        education_required = job_analysis.get('education_required', False)
        user_education = user_profile.get('education', [])
        
        if not education_required:
            return {
                "match_score": 100,
                "required": False,
                "user_meets_requirement": True,
                "highest_degree": self._get_highest_degree(user_education),
                "relevant_field": True
            }
        
        highest_degree = self._get_highest_degree(user_education)
        degree_levels = {
            "high_school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5
        }
        
        required_level = degree_levels.get("bachelor", 3)  # Default to bachelor's
        user_level = degree_levels.get(highest_degree, 0)
        
        match_score = min((user_level / required_level) * 100, 100) if required_level > 0 else 100
        
        return {
            "match_score": int(match_score),
            "required": education_required,
            "user_meets_requirement": user_level >= required_level,
            "highest_degree": highest_degree,
            "relevant_field": True  # Would analyze field relevance in full implementation
        }
    
    def _get_highest_degree(self, education: List[Dict[str, Any]]) -> str:
        """Get user's highest education level"""
        degree_hierarchy = ["phd", "master", "bachelor", "associate", "high_school"]
        
        for degree in degree_hierarchy:
            for edu in education:
                degree_type = edu.get('degree_type', '').lower()
                if degree in degree_type:
                    return degree
        
        return "high_school"  # Default
    
    async def _analyze_location_match(
        self,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze location compatibility"""
        
        job_location = job_data.get('location', '').lower()
        user_location = user_profile.get('location', '').lower()
        remote_ok = 'remote' in job_location or 'work from home' in job_data.get('description', '').lower()
        user_relocate = user_profile.get('willing_to_relocate', False)
        
        if remote_ok:
            return {
                "match_score": 100,
                "remote_available": True,
                "relocation_required": False,
                "user_willing_to_relocate": user_relocate
            }
        
        # Simple location matching (would use geocoding in production)
        location_match = self._calculate_location_similarity(job_location, user_location)
        
        if location_match > 0.8:
            match_score = 100
            relocation_required = False
        elif location_match > 0.5:  # Same city/region
            match_score = 90
            relocation_required = False
        elif user_relocate:
            match_score = 70
            relocation_required = True
        else:
            match_score = 30
            relocation_required = True
        
        return {
            "match_score": match_score,
            "remote_available": remote_ok,
            "relocation_required": relocation_required,
            "user_willing_to_relocate": user_relocate,
            "location_similarity": location_match
        }
    
    def _calculate_location_similarity(self, job_location: str, user_location: str) -> float:
        """Calculate location similarity (simplified)"""
        if not job_location or not user_location:
            return 0.0
        
        job_parts = set(job_location.replace(',', '').split())
        user_parts = set(user_location.replace(',', '').split())
        
        if job_parts.intersection(user_parts):
            return len(job_parts.intersection(user_parts)) / len(job_parts.union(user_parts))
        
        return 0.0
    
    async def _analyze_salary_match(
        self,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze salary expectations vs. offer"""
        
        job_salary = self._extract_salary_range(job_data.get('salary', ''))
        user_expectation = user_profile.get('salary_expectation', {})
        
        if not job_salary or not user_expectation:
            return {
                "match_score": 100,  # No conflict if no info
                "salary_disclosed": bool(job_salary),
                "expectation_met": True,
                "percentage_difference": 0
            }
        
        job_midpoint = (job_salary['min'] + job_salary['max']) / 2
        user_min = user_expectation.get('min', job_midpoint)
        user_max = user_expectation.get('max', job_midpoint * 1.2)
        user_midpoint = (user_min + user_max) / 2
        
        # Calculate compatibility
        if job_salary['max'] >= user_min and job_salary['min'] <= user_max:
            # Ranges overlap
            overlap = min(job_salary['max'], user_max) - max(job_salary['min'], user_min)
            total_range = max(job_salary['max'], user_max) - min(job_salary['min'], user_min)
            match_score = (overlap / total_range) * 100 if total_range > 0 else 100
        else:
            # No overlap
            if job_midpoint < user_min:
                match_score = max(0, (job_midpoint / user_min) * 60)
            else:
                match_score = max(0, (user_max / job_midpoint) * 60)
        
        percentage_diff = ((user_midpoint - job_midpoint) / job_midpoint) * 100
        
        return {
            "match_score": int(match_score),
            "salary_disclosed": True,
            "expectation_met": match_score >= 80,
            "percentage_difference": round(percentage_diff, 1),
            "job_range": job_salary,
            "user_expectation": user_expectation
        }
    
    def _extract_salary_range(self, salary_text: str) -> Optional[Dict[str, float]]:
        """Extract salary range from text"""
        import re
        
        if not salary_text:
            return None
        
        # Look for salary ranges (simplified)
        patterns = [
            r'\$(\d+,?\d*),?000?\s*-\s*\$?(\d+,?\d*),?000?',  # $50,000 - $70,000
            r'\$(\d+)k\s*-\s*\$?(\d+)k',  # $50k - $70k
            r'(\d+),?000?\s*-\s*(\d+),?000?',  # 50,000 - 70,000
        ]
        
        for pattern in patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                min_val = float(match.group(1).replace(',', ''))
                max_val = float(match.group(2).replace(',', ''))
                
                # Convert if needed (k notation)
                if 'k' in salary_text.lower():
                    min_val *= 1000
                    max_val *= 1000
                elif min_val < 1000:  # Assume thousands if number is small
                    min_val *= 1000
                    max_val *= 1000
                
                return {"min": min_val, "max": max_val}
        
        return None
    
    async def _calculate_overall_match_score(self, component_scores: Dict[str, Any]) -> int:
        """Calculate weighted overall match score"""
        
        # Extract scores from each component
        skills_score = self._calculate_skills_component_score(component_scores['skills'])
        experience_score = component_scores['experience']['match_score']
        education_score = component_scores['education']['match_score']
        location_score = component_scores['location']['match_score']
        salary_score = component_scores['salary']['match_score']
        
        # Weighted average
        overall_score = (
            skills_score * settings.SKILLS_MATCH_WEIGHT +
            experience_score * settings.EXPERIENCE_MATCH_WEIGHT +
            education_score * settings.EDUCATION_MATCH_WEIGHT +
            location_score * 0.15 +
            salary_score * 0.05
        )
        
        return min(int(overall_score), 100)
    
    def _calculate_skills_component_score(self, skill_matches: List[SkillMatch]) -> float:
        """Calculate overall skills match score"""
        if not skill_matches:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        importance_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        
        for match in skill_matches:
            weight = importance_weights.get(match.importance, 0.6)
            score = 100.0 if match.user_has else 0.0
            
            # Apply confidence factor
            score *= match.match_confidence
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_must_have_coverage(
        self,
        skill_matches: List[SkillMatch],
        job_analysis: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Calculate coverage of must-have requirements"""
        
        required_skills = job_analysis.get('required_skills', [])
        coverage = {}
        
        for skill in required_skills:
            # Find matching skill match
            match = next((sm for sm in skill_matches if sm.skill == skill), None)
            coverage[skill] = match.user_has if match else False
        
        return coverage
    
    def _calculate_nice_to_have_coverage(
        self,
        skill_matches: List[SkillMatch],
        job_analysis: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Calculate coverage of nice-to-have requirements"""
        
        nice_to_have = job_analysis.get('nice_to_have', [])
        coverage = {}
        
        for skill in nice_to_have:
            match = next((sm for sm in skill_matches if sm.skill == skill), None)
            coverage[skill] = match.user_has if match else False
        
        return coverage
    
    async def _identify_skill_gaps(self, skill_matches: List[SkillMatch]) -> List[str]:
        """Identify critical skill gaps"""
        
        gaps = []
        
        for match in skill_matches:
            if not match.user_has and match.importance in ['critical', 'high']:
                gaps.append(match.skill)
        
        return gaps
    
    async def _generate_recommendations(
        self,
        skill_matches: List[SkillMatch],
        experience_match: Dict[str, Any],
        skill_gaps: List[str],
        overall_score: int
    ) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Skill-based recommendations
        if skill_gaps:
            if len(skill_gaps) <= 2:
                recommendations.append(
                    f"Consider developing skills in {', '.join(skill_gaps)} to significantly improve your match."
                )
            else:
                top_gaps = skill_gaps[:3]
                recommendations.append(
                    f"Focus on building {', '.join(top_gaps)} skills first - these appear most critical for this role."
                )
        
        # Experience recommendations
        if experience_match['match_score'] < 70:
            if experience_match.get('user_total_years', 0) < experience_match.get('required_years_range', (0, 0))[0]:
                recommendations.append(
                    "Consider gaining more experience in relevant technologies or highlighting transferable skills from other domains."
                )
            elif experience_match.get('overqualified', False):
                recommendations.append(
                    "You may be overqualified for this role. Consider highlighting leadership or mentoring aspects of your experience."
                )
        
        # Overall score recommendations
        if overall_score >= 85:
            recommendations.append(
                "Excellent match! Ensure your resume highlights the key skills and experience that align with this role."
            )
        elif overall_score >= 70:
            recommendations.append(
                "Good match. Focus your application on demonstrating the skills and experience most relevant to this position."
            )
        elif overall_score >= 50:
            recommendations.append(
                "Moderate match. Consider gaining additional experience or skills before applying, or focus heavily on transferable skills."
            )
        else:
            recommendations.append(
                "Low match. This role may require significant skill development or might not be the right fit at this time."
            )
        
        return recommendations
    
    async def calculate_skill_match(
        self,
        user_skills: List[str],
        job_requirements: List[str],
        use_semantic_matching: bool = True
    ) -> Dict[str, Any]:
        """Calculate detailed skill matching between user and job"""
        
        try:
            self.logger.info(
                "Calculating skill match",
                user_skills_count=len(user_skills),
                job_requirements_count=len(job_requirements)
            )
            
            # Normalize skills (lowercase)
            normalized_user_skills = [skill.lower().strip() for skill in user_skills]
            normalized_job_skills = [skill.lower().strip() for skill in job_requirements]
            
            # Direct matches
            exact_matches = []
            for user_skill in normalized_user_skills:
                for job_skill in normalized_job_skills:
                    if user_skill == job_skill:
                        exact_matches.append({
                            "user_skill": user_skill,
                            "job_skill": job_skill,
                            "match_type": "exact",
                            "confidence": 1.0
                        })
            
            # Synonym and partial matches
            synonym_matches = []
            partial_matches = []
            
            for user_skill in normalized_user_skills:
                for job_skill in normalized_job_skills:
                    if user_skill != job_skill:
                        # Check synonyms
                        if self._are_synonyms(user_skill, job_skill):
                            synonym_matches.append({
                                "user_skill": user_skill,
                                "job_skill": job_skill,
                                "match_type": "synonym",
                                "confidence": 0.9
                            })
                        # Check partial matches
                        elif self._is_partial_match(user_skill, job_skill):
                            confidence = self._calculate_partial_match_confidence(user_skill, job_skill)
                            partial_matches.append({
                                "user_skill": user_skill,
                                "job_skill": job_skill,
                                "match_type": "partial",
                                "confidence": confidence
                            })
            
            # Semantic matching (if enabled and vector model available)
            semantic_matches = []
            if use_semantic_matching and hasattr(self, 'sentence_model') and self.sentence_model:
                semantic_matches = await self._find_semantic_matches(
                    normalized_user_skills, normalized_job_skills
                )
            
            # Calculate overall skill match metrics
            all_matches = exact_matches + synonym_matches + partial_matches + semantic_matches
            matched_job_skills = set()
            
            # Prioritize matches (exact > synonym > semantic > partial)
            for match_list in [exact_matches, synonym_matches, semantic_matches, partial_matches]:
                for match in match_list:
                    if match["job_skill"] not in matched_job_skills:
                        matched_job_skills.add(match["job_skill"])
            
            # Identify gaps
            unmatched_job_skills = [
                skill for skill in normalized_job_skills 
                if skill not in matched_job_skills
            ]
            
            unused_user_skills = [
                skill for skill in normalized_user_skills
                if not any(match["user_skill"] == skill for match in all_matches)
            ]
            
            # Calculate scores
            total_job_skills = len(normalized_job_skills)
            matched_skills_count = len(matched_job_skills)
            
            skill_match_percentage = (matched_skills_count / total_job_skills * 100) if total_job_skills > 0 else 0
            
            # Weighted skill match score (considering match quality)
            weighted_score = 0
            for match in all_matches:
                if match["job_skill"] in matched_job_skills:
                    weighted_score += match["confidence"] * (100 / total_job_skills)
            
            # Skill coverage analysis
            coverage_analysis = self._analyze_skill_coverage(
                normalized_user_skills, normalized_job_skills, all_matches
            )
            
            result = {
                "skill_match_percentage": round(skill_match_percentage, 1),
                "weighted_skill_score": round(weighted_score, 1),
                "total_job_skills": total_job_skills,
                "matched_skills_count": matched_skills_count,
                "matches": {
                    "exact": exact_matches,
                    "synonym": synonym_matches,
                    "partial": partial_matches,
                    "semantic": semantic_matches
                },
                "gaps": {
                    "unmatched_job_skills": unmatched_job_skills,
                    "unused_user_skills": unused_user_skills
                },
                "coverage_analysis": coverage_analysis,
                "recommendations": self._generate_skill_recommendations(
                    unmatched_job_skills, matched_job_skills, skill_match_percentage
                )
            }
            
            self.logger.info(
                "Skill match calculated",
                skill_match_percentage=skill_match_percentage,
                weighted_score=weighted_score,
                matched_skills=matched_skills_count,
                total_skills=total_job_skills
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Skill match calculation failed", error=str(e))
            raise
    
    def _are_synonyms(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are synonyms"""
        
        # Common skill synonyms
        synonyms = {
            'javascript': ['js', 'ecmascript'],
            'typescript': ['ts'],
            'python': ['py'],
            'react': ['reactjs', 'react.js'],
            'vue': ['vuejs', 'vue.js'],
            'angular': ['angularjs'],
            'node': ['nodejs', 'node.js'],
            'postgresql': ['postgres', 'psql'],
            'mongodb': ['mongo'],
            'kubernetes': ['k8s'],
            'docker': ['containerization'],
            'aws': ['amazon web services'],
            'gcp': ['google cloud platform'],
            'azure': ['microsoft azure'],
            'machine learning': ['ml', 'artificial intelligence', 'ai'],
            'database': ['db', 'databases'],
            'frontend': ['front-end', 'client-side'],
            'backend': ['back-end', 'server-side'],
            'fullstack': ['full-stack', 'full stack'],
            'devops': ['dev ops', 'site reliability'],
            'api': ['rest', 'restful', 'web service'],
            'agile': ['scrum', 'kanban'],
            'git': ['version control', 'source control']
        }
        
        # Check if skill1 has synonyms that include skill2
        for key, values in synonyms.items():
            if skill1 == key and skill2 in values:
                return True
            if skill2 == key and skill1 in values:
                return True
            if skill1 in values and skill2 in values:
                return True
        
        return False
    
    def _is_partial_match(self, skill1: str, skill2: str) -> bool:
        """Check if skills are partial matches"""
        
        # One skill contains the other
        if skill1 in skill2 or skill2 in skill1:
            return True
        
        # Both skills share significant word overlap
        words1 = set(skill1.split())
        words2 = set(skill2.split())
        
        if len(words1) > 1 and len(words2) > 1:
            overlap = words1.intersection(words2)
            min_words = min(len(words1), len(words2))
            if len(overlap) >= min_words * 0.5:  # 50% word overlap
                return True
        
        return False
    
    def _calculate_partial_match_confidence(self, skill1: str, skill2: str) -> float:
        """Calculate confidence for partial matches"""
        
        # Exact substring match gets higher confidence
        if skill1 in skill2 or skill2 in skill1:
            shorter = min(len(skill1), len(skill2))
            longer = max(len(skill1), len(skill2))
            return min(0.8, shorter / longer)
        
        # Word overlap confidence
        words1 = set(skill1.split())
        words2 = set(skill2.split())
        overlap = words1.intersection(words2)
        
        if len(overlap) > 0:
            return min(0.7, len(overlap) / max(len(words1), len(words2)))
        
        return 0.3  # Minimum confidence for detected partial matches
    
    async def _find_semantic_matches(
        self, 
        user_skills: List[str], 
        job_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """Find semantic matches using vector similarity"""
        
        if not hasattr(self, 'sentence_model') or not self.sentence_model:
            return []
        
        semantic_matches = []
        
        try:
            # Generate embeddings
            user_embeddings = self.sentence_model.encode(user_skills)
            job_embeddings = self.sentence_model.encode(job_skills)
            
            # Calculate similarities
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(user_embeddings, job_embeddings)
            
            # Find high similarity matches
            for i, user_skill in enumerate(user_skills):
                for j, job_skill in enumerate(job_skills):
                    similarity = similarities[i][j]
                    
                    # Only consider as semantic match if similarity is high
                    # and not already matched by exact/synonym/partial
                    if similarity >= 0.75 and user_skill != job_skill:
                        if not self._are_synonyms(user_skill, job_skill):
                            if not self._is_partial_match(user_skill, job_skill):
                                semantic_matches.append({
                                    "user_skill": user_skill,
                                    "job_skill": job_skill,
                                    "match_type": "semantic",
                                    "confidence": round(similarity, 2)
                                })
                        
        except Exception as e:
            self.logger.warning("Semantic matching failed", error=str(e))
        
        return semantic_matches
    
    def _analyze_skill_coverage(
        self, 
        user_skills: List[str], 
        job_skills: List[str], 
        matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze skill coverage by categories"""
        
        # Categorize skills
        skill_categories = {
            'programming_languages': ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'express', 'spring', 'laravel'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite'],
            'cloud_platforms': ['aws', 'azure', 'gcp', 'google cloud', 'amazon web services'],
            'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible'],
            'methodologies': ['agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'tdd']
        }
        
        coverage_by_category = {}
        
        for category, category_skills in skill_categories.items():
            job_skills_in_category = [skill for skill in job_skills if any(cat_skill in skill for cat_skill in category_skills)]
            matched_skills_in_category = [
                match["job_skill"] for match in matches 
                if match["job_skill"] in job_skills_in_category
            ]
            
            if job_skills_in_category:
                coverage = len(matched_skills_in_category) / len(job_skills_in_category)
                coverage_by_category[category] = {
                    "coverage_percentage": round(coverage * 100, 1),
                    "total_required": len(job_skills_in_category),
                    "matched": len(matched_skills_in_category),
                    "required_skills": job_skills_in_category,
                    "matched_skills": matched_skills_in_category
                }
        
        return coverage_by_category
    
    def _generate_skill_recommendations(
        self, 
        unmatched_skills: List[str], 
        matched_skills: set, 
        match_percentage: float
    ) -> List[str]:
        """Generate skill-based recommendations"""
        
        recommendations = []
        
        if match_percentage >= 80:
            recommendations.append("Excellent skill match! Highlight these skills prominently in your application.")
        elif match_percentage >= 60:
            recommendations.append("Good skill alignment. Focus on demonstrating depth in your matching skills.")
        elif match_percentage >= 40:
            recommendations.append("Moderate skill match. Consider gaining experience in the missing skills.")
        else:
            recommendations.append("Significant skill gaps identified. Focus on developing core required skills.")
        
        # Priority skills to develop
        if unmatched_skills:
            high_priority = unmatched_skills[:3]  # Top 3 missing skills
            recommendations.append(f"Priority skills to develop: {', '.join(high_priority)}")
        
        # Transferable skills advice
        if len(matched_skills) > 0:
            recommendations.append("Emphasize your transferable skills and demonstrate how they apply to this role.")
        
        return recommendations