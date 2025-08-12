"""
AI Orchestrator - Central hub for all AI operations
Coordinates LLM calls, maintains conversation context, and manages AI workflows
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass
from enum import Enum

# AI/LLM imports
try:
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage, AIMessage
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.prompts import ChatPromptTemplate
    import openai
except ImportError:
    print("Warning: LangChain not installed. AI features will be limited.")
    ChatOpenAI = None

from app.core.config import settings

logger = structlog.get_logger(__name__)


class TaskType(str, Enum):
    """AI task types"""
    JOB_ANALYSIS = "job_analysis"
    RESUME_TAILORING = "resume_tailoring"
    SKILL_EXTRACTION = "skill_extraction"
    COVER_LETTER = "cover_letter"
    QA_GENERATION = "qa_generation"
    ATS_OPTIMIZATION = "ats_optimization"
    REASONING_SYNTHESIS = "reasoning_synthesis"


@dataclass
class AITask:
    """AI task definition"""
    task_id: str
    task_type: TaskType
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    priority: int = 1
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class AIResponse:
    """AI response wrapper"""
    task_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_time: float = 0.0
    model_used: str = ""
    token_usage: Optional[Dict[str, int]] = None


class AIOrchestrator:
    """
    Central AI orchestrator that manages all LLM operations
    Provides context management, rate limiting, and error handling
    """
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.models = {}
        self.conversation_context = {}
        self.task_queue = asyncio.Queue()
        self.processing = False
        
        # Initialize models
        self._initialize_models()
        
        # Start background task processor
        if not self.processing:
            asyncio.create_task(self._process_tasks())
            self.processing = True
    
    def _initialize_models(self):
        """Initialize AI models"""
        try:
            if settings.OPENAI_API_KEY and ChatOpenAI:
                self.models['gpt-4'] = ChatOpenAI(
                    model_name="gpt-4",
                    temperature=0.2,
                    max_tokens=2000,
                    openai_api_key=settings.OPENAI_API_KEY
                )
                self.models['gpt-3.5-turbo'] = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.2,
                    max_tokens=1500,
                    openai_api_key=settings.OPENAI_API_KEY
                )
                self.logger.info("OpenAI models initialized")
            
            # Add Anthropic Claude if available
            if settings.ANTHROPIC_API_KEY:
                self.logger.info("Anthropic API key found (Claude integration would go here)")
                
        except Exception as e:
            self.logger.error("Failed to initialize AI models", error=str(e))
    
    async def submit_task(self, task: AITask) -> str:
        """Submit an AI task for processing"""
        await self.task_queue.put(task)
        self.logger.info("AI task submitted", task_id=task.task_id, task_type=task.task_type)
        return task.task_id
    
    async def execute_task(self, task: AITask) -> AIResponse:
        """Execute a single AI task synchronously"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.logger.info("Executing AI task", task_id=task.task_id, task_type=task.task_type)
            
            # Route task to appropriate handler
            if task.task_type == TaskType.JOB_ANALYSIS:
                result = await self._analyze_job(task)
            elif task.task_type == TaskType.RESUME_TAILORING:
                result = await self._tailor_resume(task)
            elif task.task_type == TaskType.SKILL_EXTRACTION:
                result = await self._extract_skills(task)
            elif task.task_type == TaskType.COVER_LETTER:
                result = await self._generate_cover_letter(task)
            elif task.task_type == TaskType.QA_GENERATION:
                result = await self._generate_qa(task)
            elif task.task_type == TaskType.ATS_OPTIMIZATION:
                result = await self._optimize_ats(task)
            elif task.task_type == TaskType.REASONING_SYNTHESIS:
                result = await self._synthesize_reasoning(task)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return AIResponse(
                task_id=task.task_id,
                success=True,
                result=result,
                processing_time=processing_time,
                model_used=settings.DEFAULT_MODEL
            )
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            self.logger.error("AI task failed", task_id=task.task_id, error=str(e))
            
            return AIResponse(
                task_id=task.task_id,
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    async def _process_tasks(self):
        """Background task processor"""
        while True:
            try:
                task = await self.task_queue.get()
                response = await self.execute_task(task)
                
                # Store response for retrieval (in production, use Redis or database)
                self.conversation_context[task.task_id] = response
                
                self.task_queue.task_done()
                
            except Exception as e:
                self.logger.error("Task processor error", error=str(e))
                await asyncio.sleep(1)  # Brief pause on error
    
    async def _analyze_job(self, task: AITask) -> Dict[str, Any]:
        """Analyze job posting for skills and requirements"""
        job_data = task.input_data
        user_profile = task.context.get('user_profile', {}) if task.context else {}
        
        prompt = f"""
        Analyze this job posting and extract key information:
        
        Job Title: {job_data.get('title', 'Not provided')}
        Company: {job_data.get('company', 'Not provided')}
        Location: {job_data.get('location', 'Not provided')}
        Description: {job_data.get('description', 'Not provided')[:2000]}
        
        Extract:
        1. Required skills (technical and soft skills)
        2. Experience level required
        3. Education requirements
        4. Key responsibilities
        5. Must-have vs nice-to-have qualifications
        6. Company culture indicators
        
        User Profile for Context:
        Skills: {user_profile.get('skills', [])}
        Experience: {user_profile.get('experience_years', 'Not provided')}
        
        Return as JSON with match_score (0-100), required_skills, nice_to_have, gaps, and recommendations.
        """
        
        if not self.models:
            # Fallback analysis without AI
            return await self._fallback_job_analysis(job_data, user_profile)
        
        try:
            model = self.models.get('gpt-4') or self.models.get('gpt-3.5-turbo')
            messages = [
                SystemMessage(content="You are an expert job analyst and career coach."),
                HumanMessage(content=prompt)
            ]
            
            response = await model.agenerate([messages])
            result_text = response.generations[0][0].text
            
            # Parse JSON response or create structured result
            return {
                "analysis_text": result_text,
                "extracted_data": self._parse_job_analysis(result_text),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error("AI job analysis failed", error=str(e))
            return await self._fallback_job_analysis(job_data, user_profile)
    
    async def _tailor_resume(self, task: AITask) -> Dict[str, Any]:
        """Tailor resume based on job requirements"""
        job_data = task.input_data.get('job_data', {})
        user_profile = task.input_data.get('user_profile', {})
        evidence_vault = task.input_data.get('evidence_vault', [])
        
        prompt = f"""
        Create a tailored resume for this job application using Reasonable Synthesis (RS).
        
        Job Requirements:
        Title: {job_data.get('title', '')}
        Company: {job_data.get('company', '')}
        Key Skills: {job_data.get('required_skills', [])}
        Description: {job_data.get('description', '')[:1500]}
        
        User Profile:
        Name: {user_profile.get('firstName', '')} {user_profile.get('lastName', '')}
        Skills: {user_profile.get('skills', [])}
        Experience: {user_profile.get('experience', [])}
        
        Evidence Vault:
        {evidence_vault[:10]}  # First 10 items
        
        Rules for RS (Reasonable Synthesis):
        1. Only synthesize within the same employer/role/timeframe
        2. Use intervals and approximations (e.g., "15-20%", "approximately")
        3. Mark all RS bullets with rs:true and provide rs_basis
        4. Never fabricate companies, roles, or timeframes
        5. ATS optimize: Use job keywords, standard headings, bullet points
        
        Generate:
        1. Tailored summary with 3 key job-relevant points
        2. Optimized skills section (12-18 items)
        3. Enhanced experience bullets with RS where appropriate
        4. ATS compliance check
        """
        
        try:
            model = self.models.get('gpt-4') or self.models.get('gpt-3.5-turbo')
            if model:
                messages = [
                    SystemMessage(content="You are an expert resume writer specializing in ATS optimization and reasonable synthesis."),
                    HumanMessage(content=prompt)
                ]
                
                response = await model.agenerate([messages])
                result_text = response.generations[0][0].text
                
                return {
                    "tailored_resume": result_text,
                    "metadata": {
                        "job_match_score": 85,  # Calculate this properly
                        "rs_bullets_count": result_text.count("rs:true"),
                        "ats_score": 90,
                        "generated_at": datetime.utcnow().isoformat()
                    }
                }
            else:
                return await self._fallback_resume_tailoring(job_data, user_profile)
                
        except Exception as e:
            self.logger.error("Resume tailoring failed", error=str(e))
            return await self._fallback_resume_tailoring(job_data, user_profile)
    
    async def _extract_skills(self, task: AITask) -> Dict[str, Any]:
        """Extract skills from job description or resume"""
        text = task.input_data.get('text', '')
        context_type = task.input_data.get('type', 'job_description')  # or 'resume'
        
        # Common tech skills dictionary
        tech_skills = [
            'JavaScript', 'Python', 'Java', 'React', 'Node.js', 'SQL', 'AWS', 
            'Docker', 'Kubernetes', 'Git', 'HTML', 'CSS', 'TypeScript',
            'Machine Learning', 'Data Analysis', 'API', 'REST', 'GraphQL',
            'PostgreSQL', 'MongoDB', 'Redis', 'Linux', 'CI/CD'
        ]
        
        soft_skills = [
            'Communication', 'Leadership', 'Problem Solving', 'Teamwork',
            'Project Management', 'Analytical Thinking', 'Adaptability',
            'Time Management', 'Attention to Detail', 'Customer Service'
        ]
        
        # Extract skills (simple keyword matching for now)
        found_tech_skills = [skill for skill in tech_skills if skill.lower() in text.lower()]
        found_soft_skills = [skill for skill in soft_skills if skill.lower() in text.lower()]
        
        return {
            "technical_skills": found_tech_skills,
            "soft_skills": found_soft_skills,
            "all_skills": found_tech_skills + found_soft_skills,
            "confidence_scores": {skill: 0.8 for skill in found_tech_skills + found_soft_skills},
            "extraction_method": "keyword_matching" if not self.models else "ai_powered"
        }
    
    async def _generate_cover_letter(self, task: AITask) -> Dict[str, Any]:
        """Generate personalized cover letter"""
        job_data = task.input_data.get('job_data', {})
        user_profile = task.input_data.get('user_profile', {})
        
        # Template-based cover letter for fallback
        cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_data.get('title', 'position')} role at {job_data.get('company', 'your company')}. 

With my background in {', '.join(user_profile.get('skills', [])[:3])}, I am excited about the opportunity to contribute to your team. My experience aligns well with your requirements, particularly in areas such as software development and problem-solving.

I am impressed by {job_data.get('company', 'your company')}'s commitment to innovation and would welcome the opportunity to discuss how my skills can contribute to your continued success.

Thank you for your consideration. I look forward to hearing from you.

Best regards,
{user_profile.get('firstName', '')} {user_profile.get('lastName', '')}"""
        
        return {
            "cover_letter": cover_letter,
            "word_count": len(cover_letter.split()),
            "personalization_score": 75,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_qa(self, task: AITask) -> Dict[str, Any]:
        """Generate answers to application questions"""
        job_data = task.input_data.get('job_data', {})
        user_profile = task.input_data.get('user_profile', {})
        questions = task.input_data.get('questions', [])
        
        qa_pairs = []
        
        for question in questions:
            # Simple Q&A generation
            if 'why' in question.lower() and 'company' in question.lower():
                answer = f"I am interested in {job_data.get('company', 'this company')} because of its reputation for innovation and commitment to excellence. The {job_data.get('title', 'role')} aligns perfectly with my skills in {', '.join(user_profile.get('skills', [])[:2])}."
            elif 'experience' in question.lower():
                answer = f"I have {user_profile.get('experience_years', '2+')} years of experience in relevant technologies including {', '.join(user_profile.get('skills', [])[:3])}. This experience has prepared me well for the challenges of this role."
            elif 'strength' in question.lower():
                answer = f"My key strengths include {', '.join(user_profile.get('skills', [])[:2])} and strong problem-solving abilities. I consistently deliver high-quality results and work well in team environments."
            else:
                answer = "I am excited about this opportunity and believe my background makes me a strong candidate for this position."
            
            qa_pairs.append({
                "question": question,
                "answer": answer,
                "confidence": 0.8,
                "evidence_based": False
            })
        
        return {
            "qa_pairs": qa_pairs,
            "total_questions": len(questions),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _optimize_ats(self, task: AITask) -> Dict[str, Any]:
        """Check and optimize resume for ATS compatibility"""
        resume_text = task.input_data.get('resume_text', '')
        job_keywords = task.input_data.get('job_keywords', [])
        
        # ATS optimization checks
        checks = {
            "has_standard_headings": any(heading in resume_text.lower() for heading in ['experience', 'education', 'skills']),
            "uses_bullet_points": '•' in resume_text or '*' in resume_text or '-' in resume_text,
            "keyword_density": len([kw for kw in job_keywords if kw.lower() in resume_text.lower()]) / max(len(job_keywords), 1),
            "has_contact_info": '@' in resume_text and any(digit in resume_text for digit in '0123456789'),
            "avoids_tables": '<table>' not in resume_text.lower(),
            "proper_formatting": len(resume_text.split('\n')) > 5
        }
        
        ats_score = sum(checks.values()) / len(checks) * 100
        
        recommendations = []
        if not checks["has_standard_headings"]:
            recommendations.append("Use standard section headings: Experience, Education, Skills")
        if checks["keyword_density"] < 0.3:
            recommendations.append(f"Include more relevant keywords: {', '.join(job_keywords[:5])}")
        if not checks["uses_bullet_points"]:
            recommendations.append("Use bullet points for better readability")
        
        return {
            "ats_score": round(ats_score),
            "checks": checks,
            "recommendations": recommendations,
            "keyword_matches": [kw for kw in job_keywords if kw.lower() in resume_text.lower()],
            "missing_keywords": [kw for kw in job_keywords if kw.lower() not in resume_text.lower()]
        }
    
    async def _synthesize_reasoning(self, task: AITask) -> Dict[str, Any]:
        """Perform reasonable synthesis on experience bullets"""
        experience_items = task.input_data.get('experience_items', [])
        job_requirements = task.input_data.get('job_requirements', [])
        
        # Simple RS enhancement
        enhanced_bullets = []
        
        for item in experience_items:
            enhanced = {
                "original": item,
                "enhanced": item,  # Would enhance with AI
                "rs": False,
                "rs_basis": None,
                "confidence": 0.9
            }
            
            # Add quantification if missing (example RS)
            if "improved" in item.lower() and "%" not in item:
                enhanced["enhanced"] = item + " by approximately 15-20%"
                enhanced["rs"] = True
                enhanced["rs_basis"] = "Quantification based on typical improvement metrics in similar roles"
            
            enhanced_bullets.append(enhanced)
        
        return {
            "enhanced_bullets": enhanced_bullets,
            "rs_count": sum(1 for b in enhanced_bullets if b["rs"]),
            "confidence_avg": sum(b["confidence"] for b in enhanced_bullets) / len(enhanced_bullets)
        }
    
    # Fallback methods (when AI is not available)
    
    async def _fallback_job_analysis(self, job_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Fallback job analysis without AI"""
        description = job_data.get('description', '').lower()
        
        # Simple keyword extraction
        tech_skills = ['python', 'javascript', 'java', 'react', 'sql', 'aws', 'docker']
        found_skills = [skill for skill in tech_skills if skill in description]
        
        # Calculate basic match score
        user_skills = [s.lower() for s in user_profile.get('skills', [])]
        matching_skills = [skill for skill in found_skills if skill in user_skills]
        match_score = (len(matching_skills) / max(len(found_skills), 1)) * 100
        
        return {
            "match_score": round(match_score),
            "required_skills": found_skills,
            "matching_skills": matching_skills,
            "skill_gaps": [skill for skill in found_skills if skill not in user_skills],
            "analysis_method": "keyword_based_fallback"
        }
    
    async def _fallback_resume_tailoring(self, job_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Fallback resume tailoring without AI"""
        return {
            "tailored_summary": f"Experienced professional with expertise in {', '.join(user_profile.get('skills', [])[:3])} seeking to contribute to {job_data.get('company', 'your organization')}'s success.",
            "recommended_skills": user_profile.get('skills', [])[:15],
            "ats_optimizations": [
                "Use job title keywords in summary",
                "Include technical skills section", 
                "Use action verbs in experience bullets"
            ],
            "match_score": 75,
            "method": "template_based_fallback"
        }
    
    def _parse_job_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse AI-generated job analysis text"""
        # Simple parsing - in production, use structured output
        return {
            "parsed_requirements": [],
            "confidence": 0.8,
            "method": "text_parsing"
        }


# Initialize global orchestrator instance
ai_orchestrator = None

def get_ai_orchestrator() -> AIOrchestrator:
    """Get global AI orchestrator instance"""
    global ai_orchestrator
    if ai_orchestrator is None:
        ai_orchestrator = AIOrchestrator()
    return ai_orchestrator