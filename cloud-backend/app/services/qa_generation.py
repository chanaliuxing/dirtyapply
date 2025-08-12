"""
Q&A Generation Service - Automated application question answering
Generates personalized, evidence-based answers to common application questions
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import re
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

from app.core.config import settings
from app.ai.orchestrator import get_ai_orchestrator, AITask, TaskType
from app.services.evidence_vault import EvidenceVaultService

logger = structlog.get_logger(__name__)


class QuestionCategory(str, Enum):
    """Question categories"""
    MOTIVATION = "motivation"
    EXPERIENCE = "experience"
    STRENGTHS = "strengths"
    CHALLENGES = "challenges"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    COMPANY_SPECIFIC = "company_specific"
    CAREER_GOALS = "career_goals"
    SITUATIONAL = "situational"
    LOGISTICS = "logistics"


class AnswerType(str, Enum):
    """Answer generation types"""
    EVIDENCE_BASED = "evidence_based"
    TEMPLATE_BASED = "template_based"
    AI_GENERATED = "ai_generated"
    STRUCTURED_DATA = "structured_data"


@dataclass
class QuestionAnalysis:
    """Analysis of an application question"""
    original_question: str
    normalized_question: str
    category: QuestionCategory
    answer_type: AnswerType
    keywords: List[str]
    complexity: str  # simple, medium, complex
    requires_evidence: bool
    suggested_length: int  # words
    confidence: float


@dataclass
class GeneratedAnswer:
    """Generated answer with metadata"""
    question: str
    answer: str
    category: QuestionCategory
    answer_type: AnswerType
    evidence_used: List[str]
    confidence: float
    word_count: int
    generated_at: datetime
    personalization_score: float  # How personalized the answer is
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['generated_at'] = self.generated_at.isoformat()
        return result


class QAGenerationService:
    """
    Service for generating personalized answers to application questions
    Uses evidence vault and AI to create compelling, truthful responses
    """
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.ai_orchestrator = get_ai_orchestrator()
        self.evidence_vault = EvidenceVaultService()
        
        # Load question patterns and templates
        self.question_patterns = self._load_question_patterns()
        self.answer_templates = self._load_answer_templates()
        self.common_questions = self._load_common_questions()
    
    def _load_question_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load patterns for question classification"""
        return {
            "motivation": {
                "patterns": [
                    r"why.*interested.*position",
                    r"why.*want.*work.*company",
                    r"what.*motivates.*you",
                    r"why.*apply.*role",
                    r"why.*choose.*company"
                ],
                "keywords": ["why", "interested", "motivate", "passion", "drive"],
                "typical_length": 150
            },
            "experience": {
                "patterns": [
                    r"tell.*about.*experience",
                    r"describe.*background",
                    r"what.*experience.*do.*you.*have",
                    r"relevant.*experience",
                    r"years.*of.*experience"
                ],
                "keywords": ["experience", "background", "worked", "years", "role"],
                "typical_length": 200
            },
            "strengths": {
                "patterns": [
                    r"what.*are.*your.*strengths",
                    r"greatest.*strength",
                    r"what.*makes.*you.*strong",
                    r"key.*skills",
                    r"what.*do.*you.*bring"
                ],
                "keywords": ["strength", "skills", "good", "excel", "strong"],
                "typical_length": 180
            },
            "challenges": {
                "patterns": [
                    r"greatest.*weakness",
                    r"what.*challenges.*you",
                    r"difficult.*situation",
                    r"how.*do.*you.*handle",
                    r"overcome.*obstacles"
                ],
                "keywords": ["weakness", "challenge", "difficult", "problem", "overcome"],
                "typical_length": 160
            },
            "technical": {
                "patterns": [
                    r"technical.*skills",
                    r"programming.*languages",
                    r"technologies.*you.*know",
                    r"experience.*with.*\w+",
                    r"describe.*your.*approach"
                ],
                "keywords": ["technical", "programming", "technology", "framework", "tool"],
                "typical_length": 120
            },
            "behavioral": {
                "patterns": [
                    r"tell.*me.*about.*time",
                    r"describe.*situation.*when",
                    r"give.*example.*of",
                    r"how.*would.*you.*handle",
                    r"what.*would.*you.*do.*if"
                ],
                "keywords": ["example", "situation", "time", "handle", "approach"],
                "typical_length": 250
            },
            "company_specific": {
                "patterns": [
                    r"why.*company_name",
                    r"what.*do.*you.*know.*about.*us",
                    r"how.*do.*you.*fit.*culture",
                    r"why.*should.*we.*hire.*you"
                ],
                "keywords": ["company", "culture", "values", "mission", "hire"],
                "typical_length": 180
            },
            "career_goals": {
                "patterns": [
                    r"where.*do.*you.*see.*yourself",
                    r"career.*goals",
                    r"future.*plans",
                    r"long.*term.*objectives"
                ],
                "keywords": ["career", "future", "goals", "plans", "growth"],
                "typical_length": 140
            }
        }
    
    def _load_answer_templates(self) -> Dict[str, Dict[str, str]]:
        """Load answer templates for different question types"""
        return {
            "motivation": {
                "structure": "Hook + Specific Interest + Company Connection + Value Proposition",
                "opening": [
                    "I'm particularly excited about this role because",
                    "What draws me to this position is",
                    "I'm passionate about this opportunity because"
                ],
                "body_patterns": [
                    "My experience with {skills} has prepared me to {value_proposition}",
                    "Having worked on {projects}, I understand the challenges of {domain}",
                    "I'm impressed by {company}'s commitment to {values}"
                ],
                "closing": [
                    "I'm excited to contribute to {company}'s continued success",
                    "I look forward to bringing my expertise to your team",
                    "This role aligns perfectly with my career goals and passion for {field}"
                ]
            },
            "experience": {
                "structure": "Summary + Relevant Experience + Key Achievements + Skills Gained",
                "opening": [
                    "I have {years} years of experience in {field}",
                    "My background includes {experience_summary}",
                    "I've spent the last {years} years working in {domain}"
                ],
                "body_patterns": [
                    "At {company}, I {achievement}",
                    "In my role as {title}, I was responsible for {responsibilities}",
                    "One of my key accomplishments was {specific_achievement}"
                ],
                "closing": [
                    "This experience has given me strong skills in {skills}",
                    "These roles have prepared me well for the challenges of this position",
                    "I'm now ready to apply this experience to drive results at {company}"
                ]
            },
            "strengths": {
                "structure": "Primary Strength + Evidence + Impact + Relevance",
                "opening": [
                    "One of my greatest strengths is my ability to",
                    "I'm particularly strong in",
                    "My key strength lies in"
                ],
                "body_patterns": [
                    "For example, at {company}, I {specific_example}",
                    "This strength was evident when I {situation}",
                    "I demonstrated this by {action} which resulted in {outcome}"
                ],
                "closing": [
                    "I believe this strength would be valuable in {specific_role_aspect}",
                    "This ability would help me excel in this position",
                    "I'm excited to bring this strength to your team"
                ]
            },
            "technical": {
                "structure": "Skills Overview + Experience Level + Recent Projects + Learning",
                "opening": [
                    "I have experience with {technologies}",
                    "My technical background includes",
                    "I'm proficient in {skill_areas}"
                ],
                "body_patterns": [
                    "I've used {technology} for {duration} in projects involving {context}",
                    "Most recently, I worked on {project} using {tech_stack}",
                    "I have {proficiency_level} experience with {specific_technology}"
                ],
                "closing": [
                    "I stay current with industry trends and continuously learn new technologies",
                    "I'm always eager to expand my technical skills",
                    "I'm particularly excited about applying these skills to {company_context}"
                ]
            }
        }
    
    def _load_common_questions(self) -> Dict[str, List[str]]:
        """Load database of common application questions"""
        return {
            "motivation": [
                "Why are you interested in this position?",
                "What attracts you to our company?",
                "Why do you want to work here?",
                "What motivates you in your work?",
                "Why are you looking for a new opportunity?"
            ],
            "experience": [
                "Tell me about your relevant experience.",
                "Describe your background in this field.",
                "What experience do you have with [specific technology]?",
                "How many years of experience do you have?",
                "Walk me through your career progression."
            ],
            "strengths": [
                "What are your greatest strengths?",
                "What skills do you bring to this role?",
                "What makes you a strong candidate?",
                "What are you most proud of in your career?",
                "What value would you add to our team?"
            ],
            "challenges": [
                "What is your greatest weakness?",
                "Describe a challenging situation you've faced.",
                "How do you handle stress or pressure?",
                "Tell me about a time you failed.",
                "What areas are you working to improve?"
            ],
            "behavioral": [
                "Tell me about a time you led a project.",
                "Describe a situation where you had to work with a difficult team member.",
                "Give an example of when you had to learn something quickly.",
                "Tell me about a time you disagreed with your manager.",
                "Describe your biggest professional accomplishment."
            ],
            "technical": [
                "What programming languages are you most comfortable with?",
                "How do you approach debugging a complex issue?",
                "Describe your experience with [specific framework].",
                "How do you stay current with technology trends?",
                "What's your preferred development methodology?"
            ]
        }
    
    async def generate_answers(
        self,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        questions: List[str]
    ) -> List[GeneratedAnswer]:
        """
        Generate answers for a list of application questions
        """
        try:
            self.logger.info(
                "Starting Q&A generation",
                question_count=len(questions),
                job_id=job_data.get('job_id'),
                user_id=user_profile.get('user_id')
            )
            
            generated_answers = []
            
            for question in questions:
                try:
                    # Analyze question
                    analysis = await self._analyze_question(question, job_data)
                    
                    # Generate answer
                    answer = await self._generate_single_answer(
                        question, analysis, job_data, user_profile
                    )
                    
                    generated_answers.append(answer)
                    
                except Exception as e:
                    self.logger.error(f"Failed to generate answer for question", 
                                    question=question[:50], error=str(e))
                    
                    # Create fallback answer
                    fallback_answer = GeneratedAnswer(
                        question=question,
                        answer="I am excited about this opportunity and believe my background makes me a strong candidate for this position.",
                        category=QuestionCategory.MOTIVATION,
                        answer_type=AnswerType.TEMPLATE_BASED,
                        evidence_used=[],
                        confidence=0.3,
                        word_count=20,
                        generated_at=datetime.utcnow(),
                        personalization_score=0.1
                    )
                    generated_answers.append(fallback_answer)
            
            self.logger.info(
                "Q&A generation completed",
                generated_count=len(generated_answers),
                avg_confidence=sum(a.confidence for a in generated_answers) / len(generated_answers)
            )
            
            return generated_answers
            
        except Exception as e:
            self.logger.error("Q&A generation failed", error=str(e))
            raise
    
    async def _analyze_question(
        self,
        question: str,
        job_data: Dict[str, Any]
    ) -> QuestionAnalysis:
        """Analyze and classify a question"""
        
        normalized = question.lower().strip()
        
        # Classify question category
        category = self._classify_question_category(normalized)
        
        # Determine answer type needed
        answer_type = self._determine_answer_type(normalized, category)
        
        # Extract keywords
        keywords = self._extract_question_keywords(normalized)
        
        # Assess complexity
        complexity = self._assess_question_complexity(normalized)
        
        # Check if evidence is needed
        requires_evidence = self._requires_evidence(category, normalized)
        
        # Suggest answer length
        pattern_info = self.question_patterns.get(category.value, {})
        suggested_length = pattern_info.get('typical_length', 150)
        
        # Calculate analysis confidence
        confidence = self._calculate_analysis_confidence(category, keywords, complexity)
        
        return QuestionAnalysis(
            original_question=question,
            normalized_question=normalized,
            category=category,
            answer_type=answer_type,
            keywords=keywords,
            complexity=complexity,
            requires_evidence=requires_evidence,
            suggested_length=suggested_length,
            confidence=confidence
        )
    
    def _classify_question_category(self, normalized_question: str) -> QuestionCategory:
        """Classify question into category"""
        
        best_category = QuestionCategory.MOTIVATION
        best_score = 0
        
        for category_name, pattern_info in self.question_patterns.items():
            score = 0
            
            # Check regex patterns
            patterns = pattern_info.get('patterns', [])
            for pattern in patterns:
                if re.search(pattern, normalized_question, re.IGNORECASE):
                    score += 3
            
            # Check keywords
            keywords = pattern_info.get('keywords', [])
            for keyword in keywords:
                if keyword in normalized_question:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_category = QuestionCategory(category_name)
        
        return best_category
    
    def _determine_answer_type(self, question: str, category: QuestionCategory) -> AnswerType:
        """Determine the best approach for answering this question"""
        
        # Questions that benefit from evidence
        evidence_categories = [
            QuestionCategory.EXPERIENCE,
            QuestionCategory.STRENGTHS,
            QuestionCategory.BEHAVIORAL,
            QuestionCategory.TECHNICAL
        ]
        
        if category in evidence_categories:
            return AnswerType.EVIDENCE_BASED
        
        # Company-specific questions need AI generation
        if category == QuestionCategory.COMPANY_SPECIFIC:
            return AnswerType.AI_GENERATED
        
        # Logistics questions can use structured data
        if "salary" in question or "start date" in question or "relocate" in question:
            return AnswerType.STRUCTURED_DATA
        
        # Default to template-based
        return AnswerType.TEMPLATE_BASED
    
    def _extract_question_keywords(self, question: str) -> List[str]:
        """Extract relevant keywords from question"""
        import re
        
        # Remove common words
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'you', 'your', 'do', 'have', 'can',
            'would', 'could', 'should', 'me', 'my', 'we', 'us', 'our', 'i'
        }
        
        # Extract words
        words = re.findall(r'\b\w+\b', question.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Top 10 keywords
    
    def _assess_question_complexity(self, question: str) -> str:
        """Assess how complex the question is to answer"""
        
        complexity_indicators = {
            'simple': ['what', 'when', 'where', 'are you'],
            'medium': ['how', 'why', 'describe', 'tell me about'],
            'complex': ['analyze', 'compare', 'evaluate', 'give an example', 'tell me about a time']
        }
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in question for indicator in indicators):
                return level
        
        # Default based on length
        if len(question.split()) > 15:
            return 'complex'
        elif len(question.split()) > 8:
            return 'medium'
        else:
            return 'simple'
    
    def _requires_evidence(self, category: QuestionCategory, question: str) -> bool:
        """Determine if question needs evidence-based response"""
        
        evidence_categories = [
            QuestionCategory.EXPERIENCE,
            QuestionCategory.STRENGTHS, 
            QuestionCategory.BEHAVIORAL,
            QuestionCategory.TECHNICAL
        ]
        
        if category in evidence_categories:
            return True
        
        # Look for behavioral question patterns
        behavioral_patterns = [
            'tell me about a time',
            'give an example',
            'describe a situation',
            'how have you'
        ]
        
        return any(pattern in question for pattern in behavioral_patterns)
    
    def _calculate_analysis_confidence(
        self, 
        category: QuestionCategory,
        keywords: List[str],
        complexity: str
    ) -> float:
        """Calculate confidence in question analysis"""
        
        confidence = 0.7  # Base confidence
        
        # Adjust based on keyword matches
        if len(keywords) >= 3:
            confidence += 0.1
        elif len(keywords) <= 1:
            confidence -= 0.2
        
        # Adjust based on complexity (complex questions are harder to analyze)
        if complexity == 'simple':
            confidence += 0.1
        elif complexity == 'complex':
            confidence -= 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    async def _generate_single_answer(
        self,
        question: str,
        analysis: QuestionAnalysis,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> GeneratedAnswer:
        """Generate a single answer based on analysis"""
        
        if analysis.answer_type == AnswerType.EVIDENCE_BASED:
            return await self._generate_evidence_based_answer(question, analysis, job_data, user_profile)
        elif analysis.answer_type == AnswerType.AI_GENERATED:
            return await self._generate_ai_answer(question, analysis, job_data, user_profile)
        elif analysis.answer_type == AnswerType.STRUCTURED_DATA:
            return await self._generate_structured_answer(question, analysis, job_data, user_profile)
        else:
            return await self._generate_template_answer(question, analysis, job_data, user_profile)
    
    async def _generate_evidence_based_answer(
        self,
        question: str,
        analysis: QuestionAnalysis,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> GeneratedAnswer:
        """Generate answer using evidence vault"""
        
        user_id = user_profile.get('user_id', 'unknown')
        
        # Find relevant evidence
        supporting_evidence = await self.evidence_vault.find_supporting_evidence(
            user_id=user_id,
            bullet_text=question,
            context={
                'category': analysis.category.value,
                'keywords': analysis.keywords
            }
        )
        
        if not supporting_evidence:
            # Fall back to template-based answer
            return await self._generate_template_answer(question, analysis, job_data, user_profile)
        
        # Build answer from evidence
        answer_parts = []
        evidence_used = []
        
        # Opening
        category_templates = self.answer_templates.get(analysis.category.value, {})
        openings = category_templates.get('opening', ["I have experience with"])
        opening = openings[0]  # Use first template
        
        if analysis.category == QuestionCategory.EXPERIENCE:
            years = user_profile.get('experience_years', 'several')
            field = job_data.get('title', 'this field')
            opening = f"I have {years} years of experience in {field.lower()}"
        
        answer_parts.append(opening + ".")
        
        # Evidence-based body
        for evidence in supporting_evidence[:2]:  # Use top 2 pieces of evidence
            if evidence.evidence_type.value == 'achievement':
                answer_parts.append(f"For example, at {evidence.company}, I {evidence.description}")
            elif evidence.evidence_type.value == 'project':
                answer_parts.append(f"In a recent project at {evidence.company}, I {evidence.description}")
            else:
                answer_parts.append(f"At {evidence.company}, I {evidence.description}")
            
            evidence_used.append(evidence.id)
        
        # Closing with relevance to job
        company = job_data.get('company', 'your organization')
        role_title = job_data.get('title', 'this role')
        closing = f"This experience has prepared me well for the {role_title} position at {company}."
        answer_parts.append(closing)
        
        answer_text = " ".join(answer_parts)
        
        return GeneratedAnswer(
            question=question,
            answer=answer_text,
            category=analysis.category,
            answer_type=AnswerType.EVIDENCE_BASED,
            evidence_used=evidence_used,
            confidence=0.85,
            word_count=len(answer_text.split()),
            generated_at=datetime.utcnow(),
            personalization_score=0.8
        )
    
    async def _generate_ai_answer(
        self,
        question: str,
        analysis: QuestionAnalysis,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> GeneratedAnswer:
        """Generate answer using AI orchestrator"""
        
        try:
            # Prepare context for AI
            context = {
                'question': question,
                'category': analysis.category.value,
                'job_data': job_data,
                'user_profile': user_profile,
                'suggested_length': analysis.suggested_length
            }
            
            task = AITask(
                task_id=f"qa_generation_{datetime.utcnow().timestamp()}",
                task_type=TaskType.QA_GENERATION,
                input_data=context
            )
            
            response = await self.ai_orchestrator.execute_task(task)
            
            if response.success:
                qa_result = response.result
                answer_text = qa_result.get('answer', '')
                
                return GeneratedAnswer(
                    question=question,
                    answer=answer_text,
                    category=analysis.category,
                    answer_type=AnswerType.AI_GENERATED,
                    evidence_used=[],
                    confidence=qa_result.get('confidence', 0.8),
                    word_count=len(answer_text.split()),
                    generated_at=datetime.utcnow(),
                    personalization_score=qa_result.get('personalization_score', 0.7)
                )
            else:
                # Fallback to template
                return await self._generate_template_answer(question, analysis, job_data, user_profile)
                
        except Exception as e:
            self.logger.error("AI answer generation failed", error=str(e))
            return await self._generate_template_answer(question, analysis, job_data, user_profile)
    
    async def _generate_structured_answer(
        self,
        question: str,
        analysis: QuestionAnalysis,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> GeneratedAnswer:
        """Generate answer from structured profile data"""
        
        question_lower = question.lower()
        answer_text = ""
        
        # Salary questions
        if 'salary' in question_lower or 'compensation' in question_lower:
            salary_expectation = user_profile.get('salary_expectation', {})
            if salary_expectation:
                min_salary = salary_expectation.get('min', 0)
                max_salary = salary_expectation.get('max', 0)
                currency = salary_expectation.get('currency', 'CAD')
                if min_salary and max_salary:
                    answer_text = f"My salary expectation is between ${min_salary:,} and ${max_salary:,} {currency}, depending on the full compensation package and benefits."
            
            if not answer_text:
                answer_text = "I'm open to discussing compensation based on the role's responsibilities and the complete benefits package."
        
        # Start date questions
        elif 'start date' in question_lower or 'when can you start' in question_lower:
            notice_period = user_profile.get('notice_period', 'two weeks')
            answer_text = f"I can start in {notice_period} after accepting an offer, pending completion of my current commitments."
        
        # Relocation questions
        elif 'relocate' in question_lower or 'willing to move' in question_lower:
            willing_to_relocate = user_profile.get('willing_to_relocate', False)
            if willing_to_relocate:
                answer_text = "Yes, I am willing to relocate for the right opportunity."
            else:
                answer_text = "I am not currently looking to relocate, but I am open to remote work arrangements."
        
        # Authorization questions
        elif 'authorized' in question_lower or 'work authorization' in question_lower:
            work_auth = user_profile.get('work_authorization', 'citizen')
            auth_text = {
                'citizen': 'I am a Canadian citizen and authorized to work in Canada.',
                'permanent_resident': 'I am a permanent resident and authorized to work in Canada.',
                'work_permit': 'I have a valid work permit and am authorized to work in Canada.',
                'study_permit': 'I have a study permit with work authorization.',
            }.get(work_auth, 'I am authorized to work in Canada.')
            answer_text = auth_text
        
        # Default fallback
        if not answer_text:
            answer_text = "I would be happy to discuss this during our conversation."
        
        return GeneratedAnswer(
            question=question,
            answer=answer_text,
            category=analysis.category,
            answer_type=AnswerType.STRUCTURED_DATA,
            evidence_used=[],
            confidence=0.9,
            word_count=len(answer_text.split()),
            generated_at=datetime.utcnow(),
            personalization_score=0.6
        )
    
    async def _generate_template_answer(
        self,
        question: str,
        analysis: QuestionAnalysis,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> GeneratedAnswer:
        """Generate answer using templates"""
        
        category_templates = self.answer_templates.get(analysis.category.value)
        
        if not category_templates:
            # Generic fallback
            answer_text = self._create_generic_answer(question, job_data, user_profile)
        else:
            answer_text = self._build_template_answer(category_templates, job_data, user_profile, analysis)
        
        return GeneratedAnswer(
            question=question,
            answer=answer_text,
            category=analysis.category,
            answer_type=AnswerType.TEMPLATE_BASED,
            evidence_used=[],
            confidence=0.6,
            word_count=len(answer_text.split()),
            generated_at=datetime.utcnow(),
            personalization_score=0.5
        )
    
    def _build_template_answer(
        self,
        templates: Dict[str, Any],
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        analysis: QuestionAnalysis
    ) -> str:
        """Build answer from templates with substitutions"""
        
        # Get template parts
        openings = templates.get('opening', ["I am excited about this opportunity"])
        body_patterns = templates.get('body_patterns', ["I have relevant experience"])
        closings = templates.get('closing', ["I look forward to contributing"])
        
        # Select templates (could be smarter selection)
        opening = openings[0] if openings else "I am excited about this opportunity"
        body = body_patterns[0] if body_patterns else "I have relevant experience"
        closing = closings[0] if closings else "I look forward to contributing"
        
        # Perform substitutions
        substitutions = {
            'company': job_data.get('company', 'your company'),
            'role': job_data.get('title', 'this role'),
            'field': job_data.get('title', 'this field').lower(),
            'skills': ', '.join(user_profile.get('skills', [])[:3]),
            'years': str(user_profile.get('experience_years', 'several')),
            'value_proposition': 'deliver high-quality results',
            'domain': 'technology'
        }
        
        # Apply substitutions
        for key, value in substitutions.items():
            placeholder = '{' + key + '}'
            opening = opening.replace(placeholder, value)
            body = body.replace(placeholder, value)
            closing = closing.replace(placeholder, value)
        
        return f"{opening}. {body}. {closing}."
    
    def _create_generic_answer(
        self,
        question: str,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> str:
        """Create generic fallback answer"""
        
        company = job_data.get('company', 'your organization')
        role = job_data.get('title', 'this position')
        skills = user_profile.get('skills', [])
        
        if skills:
            skills_text = ', '.join(skills[:3])
            return f"I believe my experience with {skills_text} makes me well-suited for the {role} role at {company}. I'm excited about the opportunity to contribute to your team's success."
        else:
            return f"I'm excited about the {role} opportunity at {company} and believe my background aligns well with your needs. I look forward to discussing how I can contribute to your team."
    
    async def suggest_questions_for_job(
        self,
        job_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Suggest likely questions for a specific job"""
        
        suggestions = []
        job_title = job_data.get('title', '').lower()
        company = job_data.get('company', '')
        description = job_data.get('description', '').lower()
        
        # Always include motivation question (customized)
        motivation_q = f"Why are you interested in the {job_data.get('title', 'position')} role at {company}?"
        suggestions.append({
            'question': motivation_q,
            'category': 'motivation',
            'likelihood': 0.9,
            'rationale': 'Most common application question'
        })
        
        # Add experience question
        suggestions.append({
            'question': f"What experience do you have relevant to this {job_title} position?",
            'category': 'experience',
            'likelihood': 0.8,
            'rationale': 'Standard for evaluating qualifications'
        })
        
        # Technical questions for tech roles
        if any(tech in job_title for tech in ['developer', 'engineer', 'programmer', 'analyst']):
            suggestions.append({
                'question': "What programming languages and technologies are you most comfortable with?",
                'category': 'technical',
                'likelihood': 0.85,
                'rationale': 'Technical role requires skills assessment'
            })
        
        # Add strengths question
        suggestions.append({
            'question': "What are your greatest strengths that make you suitable for this role?",
            'category': 'strengths',
            'likelihood': 0.7,
            'rationale': 'Common behavioral assessment'
        })
        
        # Add company-specific if we have company info
        if company:
            suggestions.append({
                'question': f"Why do you want to work at {company}?",
                'category': 'company_specific',
                'likelihood': 0.6,
                'rationale': 'Company wants to assess cultural fit'
            })
        
        return suggestions[:count]