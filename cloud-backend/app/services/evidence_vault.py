"""
Evidence Vault and Reasoning Synthesis (RS) System
Manages evidence-based resume enhancement with proper attribution
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
import json
import hashlib
from dataclasses import dataclass, asdict, field
from enum import Enum
import structlog
from collections import defaultdict

# Vector database for evidence retrieval
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Warning: Vector database libraries not installed")
    chromadb = None

from app.core.config import settings
from app.ai.orchestrator import get_ai_orchestrator, AITask, TaskType

logger = structlog.get_logger(__name__)


class EvidenceType(str, Enum):
    """Types of evidence"""
    PROJECT = "project"
    ACHIEVEMENT = "achievement"
    RESPONSIBILITY = "responsibility"
    METRIC = "metric"
    SKILL_USAGE = "skill_usage"
    LEADERSHIP = "leadership"
    COLLABORATION = "collaboration"
    PROCESS_IMPROVEMENT = "process_improvement"


class RSRiskLevel(str, Enum):
    """Risk levels for Reasoning Synthesis"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EvidenceItem:
    """Individual evidence item"""
    id: str
    user_id: str
    evidence_type: EvidenceType
    title: str
    description: str
    company: str
    role: str
    start_date: str
    end_date: Optional[str]
    skills: List[str]
    metrics: Dict[str, Any]  # Quantitative data
    context: Dict[str, Any]  # Additional context
    confidence: float  # 0.0 to 1.0
    verification_status: str  # unverified, verified, disputed
    created_at: datetime
    updated_at: datetime
    tags: List[str] = field(default_factory=list)
    source_documents: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        return result


@dataclass
class RSBullet:
    """Reasonably Synthesized bullet point with attribution"""
    id: str
    original_text: str
    enhanced_text: str
    rs_applied: bool
    rs_basis: Optional[str]
    supporting_evidence_ids: List[str]
    confidence: float
    risk_level: RSRiskLevel
    quantification: Optional[Dict[str, Any]]
    ats_keywords: List[str]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['created_at'] = self.created_at.isoformat()
        return result


@dataclass
class RSAnalysis:
    """Analysis of RS application potential"""
    can_apply_rs: bool
    evidence_strength: float
    risk_assessment: RSRiskLevel
    recommended_enhancements: List[str]
    supporting_evidence: List[str]
    limitations: List[str]
    confidence_score: float


class EvidenceVaultService:
    """
    Service for managing evidence vault and applying Reasoning Synthesis
    Ensures all RS is properly attributed and within ethical boundaries
    """
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.ai_orchestrator = get_ai_orchestrator()
        
        # Initialize vector database
        self.chroma_client = None
        self.sentence_model = None
        self._initialize_vector_db()
        
        # Evidence storage (in-memory for now, would use database in production)
        self.evidence_store: Dict[str, EvidenceItem] = {}
        self.user_evidence_index: Dict[str, Set[str]] = defaultdict(set)
        
        # RS rules and patterns
        self.rs_rules = self._load_rs_rules()
        self.quantification_patterns = self._load_quantification_patterns()
    
    def _initialize_vector_db(self):
        """Initialize vector database for semantic evidence search"""
        try:
            if chromadb and SentenceTransformer:
                self.chroma_client = chromadb.Client(Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory="./evidence_db"
                ))
                
                # Create collection for evidence embeddings
                self.evidence_collection = self.chroma_client.get_or_create_collection(
                    name="evidence_vault",
                    metadata={"hnsw:space": "cosine"}
                )
                
                # Load sentence transformer model
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("Vector database initialized")
                
        except Exception as e:
            self.logger.warning("Vector database initialization failed", error=str(e))
    
    def _load_rs_rules(self) -> Dict[str, Any]:
        """Load rules for ethical Reasoning Synthesis"""
        return {
            "temporal_constraints": {
                "same_company": True,
                "same_role_or_related": True,
                "overlapping_timeframe": True,
                "max_time_gap_months": 6
            },
            "quantification_rules": {
                "use_intervals": True,  # 15-20% instead of exact numbers
                "use_approximations": True,  # "approximately", "around"
                "source_similar_contexts": True,
                "confidence_threshold": 0.7
            },
            "enhancement_limits": {
                "max_rs_bullets_per_resume": settings.MAX_RS_BULLETS_PER_RESUME,
                "rs_confidence_threshold": settings.RS_CONFIDENCE_THRESHOLD,
                "require_evidence_basis": True,
                "no_fabrication": True
            },
            "attribution_requirements": {
                "mark_rs_bullets": True,
                "provide_rs_basis": True,
                "track_source_evidence": True,
                "enable_rollback": True
            }
        }
    
    def _load_quantification_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load patterns for quantifying achievements"""
        return {
            "performance_improvement": {
                "keywords": ["improved", "optimized", "enhanced", "increased"],
                "typical_ranges": {
                    "code_performance": (10, 40, "%"),
                    "process_efficiency": (15, 35, "%"),
                    "user_experience": (20, 50, "%"),
                    "system_reliability": (5, 25, "%")
                },
                "context_indicators": ["performance", "speed", "efficiency", "throughput"]
            },
            "cost_reduction": {
                "keywords": ["reduced", "saved", "cut", "decreased"],
                "typical_ranges": {
                    "operational_costs": (10, 30, "%"),
                    "development_time": (20, 40, "%"),
                    "maintenance_effort": (15, 35, "%"),
                    "resource_usage": (10, 25, "%")
                },
                "context_indicators": ["cost", "expense", "budget", "resource", "time"]
            },
            "scale_achievements": {
                "keywords": ["scaled", "expanded", "grew", "increased"],
                "typical_ranges": {
                    "user_base": (2, 10, "x"),
                    "traffic": (50, 200, "%"),
                    "data_volume": (100, 500, "%"),
                    "team_size": (2, 5, "people")
                },
                "context_indicators": ["users", "traffic", "volume", "scale", "growth"]
            },
            "quality_improvements": {
                "keywords": ["improved", "enhanced", "upgraded", "refined"],
                "typical_ranges": {
                    "bug_reduction": (30, 70, "%"),
                    "test_coverage": (20, 40, "%"),
                    "code_quality": (15, 35, "%"),
                    "user_satisfaction": (10, 30, "%")
                },
                "context_indicators": ["quality", "bugs", "errors", "satisfaction", "reliability"]
            }
        }
    
    async def add_evidence_item(
        self,
        user_id: str,
        evidence_data: Dict[str, Any]
    ) -> str:
        """Add new evidence item to vault"""
        try:
            # Generate unique ID
            evidence_id = self._generate_evidence_id(user_id, evidence_data)
            
            # Create evidence item
            evidence = EvidenceItem(
                id=evidence_id,
                user_id=user_id,
                evidence_type=EvidenceType(evidence_data.get('type', 'achievement')),
                title=evidence_data['title'],
                description=evidence_data['description'],
                company=evidence_data.get('company', ''),
                role=evidence_data.get('role', ''),
                start_date=evidence_data.get('start_date', ''),
                end_date=evidence_data.get('end_date'),
                skills=evidence_data.get('skills', []),
                metrics=evidence_data.get('metrics', {}),
                context=evidence_data.get('context', {}),
                confidence=float(evidence_data.get('confidence', 1.0)),
                verification_status=evidence_data.get('verification_status', 'unverified'),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                tags=evidence_data.get('tags', []),
                source_documents=evidence_data.get('source_documents', [])
            )
            
            # Store evidence
            self.evidence_store[evidence_id] = evidence
            self.user_evidence_index[user_id].add(evidence_id)
            
            # Add to vector database
            if self.evidence_collection and self.sentence_model:
                await self._add_to_vector_db(evidence)
            
            self.logger.info(
                "Evidence item added",
                evidence_id=evidence_id,
                user_id=user_id,
                type=evidence.evidence_type
            )
            
            return evidence_id
            
        except Exception as e:
            self.logger.error("Failed to add evidence item", error=str(e))
            raise
    
    async def _add_to_vector_db(self, evidence: EvidenceItem):
        """Add evidence to vector database for semantic search"""
        try:
            # Create searchable text
            searchable_text = f"{evidence.title} {evidence.description} {' '.join(evidence.skills)}"
            
            # Generate embedding
            embedding = self.sentence_model.encode([searchable_text])[0].tolist()
            
            # Add to collection
            self.evidence_collection.add(
                ids=[evidence.id],
                embeddings=[embedding],
                metadatas=[{
                    "user_id": evidence.user_id,
                    "type": evidence.evidence_type.value,
                    "company": evidence.company,
                    "start_date": evidence.start_date,
                    "confidence": evidence.confidence
                }],
                documents=[searchable_text]
            )
            
        except Exception as e:
            self.logger.error("Failed to add evidence to vector DB", error=str(e))
    
    def _generate_evidence_id(self, user_id: str, evidence_data: Dict[str, Any]) -> str:
        """Generate unique evidence ID"""
        content = f"{user_id}_{evidence_data.get('title', '')}_{evidence_data.get('company', '')}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    async def find_supporting_evidence(
        self,
        user_id: str,
        bullet_text: str,
        context: Dict[str, Any]
    ) -> List[EvidenceItem]:
        """Find evidence items that can support a bullet point"""
        try:
            # Get user's evidence
            user_evidence_ids = self.user_evidence_index.get(user_id, set())
            if not user_evidence_ids:
                return []
            
            # Use vector search if available
            if self.evidence_collection and self.sentence_model:
                return await self._vector_search_evidence(user_id, bullet_text, context)
            else:
                return await self._keyword_search_evidence(user_id, bullet_text, context)
                
        except Exception as e:
            self.logger.error("Failed to find supporting evidence", error=str(e))
            return []
    
    async def _vector_search_evidence(
        self,
        user_id: str,
        bullet_text: str,
        context: Dict[str, Any]
    ) -> List[EvidenceItem]:
        """Use vector similarity to find relevant evidence"""
        try:
            # Generate query embedding
            query_embedding = self.sentence_model.encode([bullet_text])[0].tolist()
            
            # Search similar evidence
            results = self.evidence_collection.query(
                query_embeddings=[query_embedding],
                n_results=10,
                where={"user_id": user_id}
            )
            
            # Convert results to EvidenceItem objects
            evidence_items = []
            for evidence_id in results['ids'][0]:
                if evidence_id in self.evidence_store:
                    evidence = self.evidence_store[evidence_id]
                    
                    # Apply temporal and contextual filters
                    if await self._is_evidence_applicable(evidence, context):
                        evidence_items.append(evidence)
            
            return evidence_items[:5]  # Top 5 most relevant
            
        except Exception as e:
            self.logger.error("Vector search failed", error=str(e))
            return []
    
    async def _keyword_search_evidence(
        self,
        user_id: str,
        bullet_text: str,
        context: Dict[str, Any]
    ) -> List[EvidenceItem]:
        """Fallback keyword-based evidence search"""
        bullet_keywords = set(bullet_text.lower().split())
        matching_evidence = []
        
        user_evidence_ids = self.user_evidence_index.get(user_id, set())
        
        for evidence_id in user_evidence_ids:
            evidence = self.evidence_store.get(evidence_id)
            if not evidence:
                continue
            
            # Calculate keyword overlap
            evidence_text = f"{evidence.title} {evidence.description}".lower()
            evidence_keywords = set(evidence_text.split())
            
            overlap = len(bullet_keywords.intersection(evidence_keywords))
            if overlap >= 2:  # Minimum 2 keyword matches
                # Check temporal constraints
                if await self._is_evidence_applicable(evidence, context):
                    matching_evidence.append((evidence, overlap))
        
        # Sort by relevance and return top 5
        matching_evidence.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in matching_evidence[:5]]
    
    async def _is_evidence_applicable(
        self,
        evidence: EvidenceItem,
        context: Dict[str, Any]
    ) -> bool:
        """Check if evidence can be ethically used for RS"""
        rules = self.rs_rules["temporal_constraints"]
        
        # Same company check
        if rules["same_company"]:
            context_company = context.get('company', '').lower()
            if context_company and evidence.company.lower() != context_company:
                return False
        
        # Timeframe overlap check
        if rules["overlapping_timeframe"]:
            if not self._timeframes_overlap(evidence, context):
                return False
        
        # Confidence threshold
        if evidence.confidence < self.rs_rules["quantification_rules"]["confidence_threshold"]:
            return False
        
        return True
    
    def _timeframes_overlap(self, evidence: EvidenceItem, context: Dict[str, Any]) -> bool:
        """Check if evidence and context timeframes overlap"""
        try:
            from datetime import datetime
            
            # Parse dates
            context_start = datetime.strptime(context.get('start_date', ''), '%Y-%m-%d') if context.get('start_date') else None
            context_end = datetime.strptime(context.get('end_date', ''), '%Y-%m-%d') if context.get('end_date') else datetime.now()
            
            evidence_start = datetime.strptime(evidence.start_date, '%Y-%m-%d') if evidence.start_date else None
            evidence_end = datetime.strptime(evidence.end_date, '%Y-%m-%d') if evidence.end_date else datetime.now()
            
            if not context_start or not evidence_start:
                return False
            
            # Check for overlap
            return (context_start <= evidence_end and context_end >= evidence_start)
            
        except (ValueError, TypeError):
            return False
    
    async def apply_reasoning_synthesis(
        self,
        user_id: str,
        bullet_text: str,
        context: Dict[str, Any],
        job_requirements: List[str] = None
    ) -> RSBullet:
        """Apply Reasoning Synthesis to enhance a bullet point"""
        try:
            # Find supporting evidence
            supporting_evidence = await self.find_supporting_evidence(user_id, bullet_text, context)
            
            if not supporting_evidence:
                # No RS applied
                return RSBullet(
                    id=self._generate_bullet_id(bullet_text),
                    original_text=bullet_text,
                    enhanced_text=bullet_text,
                    rs_applied=False,
                    rs_basis=None,
                    supporting_evidence_ids=[],
                    confidence=1.0,
                    risk_level=RSRiskLevel.LOW,
                    quantification=None,
                    ats_keywords=job_requirements or [],
                    created_at=datetime.utcnow()
                )
            
            # Analyze RS potential
            rs_analysis = await self._analyze_rs_potential(bullet_text, supporting_evidence, context)
            
            if not rs_analysis.can_apply_rs:
                return RSBullet(
                    id=self._generate_bullet_id(bullet_text),
                    original_text=bullet_text,
                    enhanced_text=bullet_text,
                    rs_applied=False,
                    rs_basis=f"RS not applicable: {'; '.join(rs_analysis.limitations)}",
                    supporting_evidence_ids=[],
                    confidence=rs_analysis.confidence_score,
                    risk_level=rs_analysis.risk_assessment,
                    quantification=None,
                    ats_keywords=job_requirements or [],
                    created_at=datetime.utcnow()
                )
            
            # Apply enhancements
            enhanced_text = await self._enhance_bullet_with_rs(
                bullet_text, supporting_evidence, rs_analysis, job_requirements or []
            )
            
            return RSBullet(
                id=self._generate_bullet_id(bullet_text),
                original_text=bullet_text,
                enhanced_text=enhanced_text,
                rs_applied=True,
                rs_basis=self._generate_rs_basis(supporting_evidence, rs_analysis),
                supporting_evidence_ids=[e.id for e in supporting_evidence],
                confidence=rs_analysis.confidence_score,
                risk_level=rs_analysis.risk_assessment,
                quantification=self._extract_quantification(enhanced_text),
                ats_keywords=job_requirements or [],
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error("RS application failed", error=str(e))
            # Return unenhanced bullet on error
            return RSBullet(
                id=self._generate_bullet_id(bullet_text),
                original_text=bullet_text,
                enhanced_text=bullet_text,
                rs_applied=False,
                rs_basis=f"RS failed: {str(e)}",
                supporting_evidence_ids=[],
                confidence=0.0,
                risk_level=RSRiskLevel.CRITICAL,
                quantification=None,
                ats_keywords=[],
                created_at=datetime.utcnow()
            )
    
    def _generate_bullet_id(self, bullet_text: str) -> str:
        """Generate unique bullet ID"""
        content = f"{bullet_text}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    async def _analyze_rs_potential(
        self,
        bullet_text: str,
        supporting_evidence: List[EvidenceItem],
        context: Dict[str, Any]
    ) -> RSAnalysis:
        """Analyze potential for applying RS"""
        
        # Check if quantification is possible and appropriate
        can_quantify = self._can_apply_quantification(bullet_text)
        
        # Calculate evidence strength
        evidence_strength = self._calculate_evidence_strength(supporting_evidence)
        
        # Assess risk level
        risk_level = self._assess_rs_risk(bullet_text, supporting_evidence, context)
        
        # Determine if RS can be applied
        can_apply_rs = (
            len(supporting_evidence) > 0 and
            evidence_strength >= 0.6 and
            risk_level != RSRiskLevel.CRITICAL
        )
        
        # Generate recommendations
        recommendations = []
        if can_quantify and evidence_strength >= 0.7:
            recommendations.append("Add quantification based on similar achievements")
        if any(e.skills for e in supporting_evidence):
            recommendations.append("Include relevant technical skills")
        if risk_level == RSRiskLevel.LOW:
            recommendations.append("Safe to apply moderate enhancements")
        
        # Identify limitations
        limitations = []
        if evidence_strength < 0.6:
            limitations.append("Insufficient evidence strength")
        if risk_level == RSRiskLevel.HIGH:
            limitations.append("High risk of misrepresentation")
        if not self._meets_temporal_constraints(supporting_evidence, context):
            limitations.append("Evidence outside temporal constraints")
        
        confidence_score = min(evidence_strength * 0.7 + (1.0 - len(limitations) * 0.2), 1.0)
        
        return RSAnalysis(
            can_apply_rs=can_apply_rs,
            evidence_strength=evidence_strength,
            risk_assessment=risk_level,
            recommended_enhancements=recommendations,
            supporting_evidence=[e.id for e in supporting_evidence],
            limitations=limitations,
            confidence_score=max(0.0, confidence_score)
        )
    
    def _can_apply_quantification(self, bullet_text: str) -> bool:
        """Check if bullet can be quantified"""
        quantifiable_verbs = []
        for pattern_type, pattern_data in self.quantification_patterns.items():
            quantifiable_verbs.extend(pattern_data["keywords"])
        
        return any(verb in bullet_text.lower() for verb in quantifiable_verbs)
    
    def _calculate_evidence_strength(self, evidence_list: List[EvidenceItem]) -> float:
        """Calculate overall strength of supporting evidence"""
        if not evidence_list:
            return 0.0
        
        # Factors: quantity, confidence, verification status, recency
        quantity_score = min(len(evidence_list) / 3.0, 1.0)  # Max 3 pieces of evidence
        
        avg_confidence = sum(e.confidence for e in evidence_list) / len(evidence_list)
        
        verification_score = sum(
            1.0 if e.verification_status == 'verified' else 
            0.8 if e.verification_status == 'unverified' else 0.3
            for e in evidence_list
        ) / len(evidence_list)
        
        # Recency score (more recent evidence is stronger)
        recency_scores = []
        for evidence in evidence_list:
            try:
                if evidence.end_date:
                    end_date = datetime.strptime(evidence.end_date, '%Y-%m-%d')
                else:
                    end_date = datetime.now()
                
                months_ago = (datetime.now() - end_date).days / 30
                recency_score = max(0.5, 1.0 - (months_ago / 24))  # Decay over 2 years
                recency_scores.append(recency_score)
            except (ValueError, TypeError):
                recency_scores.append(0.7)  # Default for invalid dates
        
        avg_recency = sum(recency_scores) / len(recency_scores)
        
        # Weighted average
        overall_strength = (
            quantity_score * 0.2 +
            avg_confidence * 0.3 +
            verification_score * 0.3 +
            avg_recency * 0.2
        )
        
        return min(overall_strength, 1.0)
    
    def _assess_rs_risk(
        self,
        bullet_text: str,
        supporting_evidence: List[EvidenceItem],
        context: Dict[str, Any]
    ) -> RSRiskLevel:
        """Assess risk level of applying RS"""
        
        risk_factors = []
        
        # Low evidence support
        if len(supporting_evidence) == 0:
            risk_factors.append("no_evidence")
        elif len(supporting_evidence) == 1:
            risk_factors.append("single_evidence")
        
        # Low confidence evidence
        if supporting_evidence:
            min_confidence = min(e.confidence for e in supporting_evidence)
            if min_confidence < 0.5:
                risk_factors.append("low_confidence")
            elif min_confidence < 0.7:
                risk_factors.append("medium_confidence")
        
        # Temporal misalignment
        if not self._meets_temporal_constraints(supporting_evidence, context):
            risk_factors.append("temporal_mismatch")
        
        # Different company/role context
        context_company = context.get('company', '').lower()
        if supporting_evidence and context_company:
            if not all(e.company.lower() == context_company for e in supporting_evidence):
                risk_factors.append("company_mismatch")
        
        # Determine overall risk level
        if "no_evidence" in risk_factors or "temporal_mismatch" in risk_factors:
            return RSRiskLevel.CRITICAL
        elif len(risk_factors) >= 3:
            return RSRiskLevel.HIGH
        elif len(risk_factors) >= 1:
            return RSRiskLevel.MEDIUM
        else:
            return RSRiskLevel.LOW
    
    def _meets_temporal_constraints(
        self,
        evidence_list: List[EvidenceItem],
        context: Dict[str, Any]
    ) -> bool:
        """Check if evidence meets temporal constraints"""
        for evidence in evidence_list:
            if not self._timeframes_overlap(evidence, context):
                return False
        return True
    
    async def _enhance_bullet_with_rs(
        self,
        bullet_text: str,
        supporting_evidence: List[EvidenceItem],
        rs_analysis: RSAnalysis,
        job_requirements: List[str]
    ) -> str:
        """Apply actual enhancements to bullet text"""
        
        enhanced_text = bullet_text
        
        # Apply quantification if possible
        if self._can_apply_quantification(bullet_text):
            quantified_text = await self._add_quantification(bullet_text, supporting_evidence)
            if quantified_text != bullet_text:
                enhanced_text = quantified_text
        
        # Add relevant skills if not present
        enhanced_text = self._add_relevant_skills(enhanced_text, supporting_evidence, job_requirements)
        
        # Improve action verbs
        enhanced_text = self._strengthen_action_verbs(enhanced_text)
        
        # ATS optimization
        enhanced_text = self._optimize_for_ats(enhanced_text, job_requirements)
        
        return enhanced_text
    
    async def _add_quantification(
        self,
        bullet_text: str,
        supporting_evidence: List[EvidenceItem]
    ) -> str:
        """Add quantification based on evidence"""
        
        # Find relevant quantification pattern
        for pattern_name, pattern_data in self.quantification_patterns.items():
            if any(keyword in bullet_text.lower() for keyword in pattern_data["keywords"]):
                
                # Look for relevant metrics in evidence
                for evidence in supporting_evidence:
                    metrics = evidence.metrics
                    
                    # Find matching metric type
                    for metric_type, (min_val, max_val, unit) in pattern_data["typical_ranges"].items():
                        if metric_type in str(metrics).lower():
                            # Use evidence-based quantification
                            if metric_type in metrics:
                                value = metrics[metric_type]
                                interval = f"{int(value * 0.8)}-{int(value * 1.2)}"
                            else:
                                # Use typical range
                                interval = f"{min_val}-{max_val}"
                            
                            # Apply quantification with approximation language
                            if unit == "%":
                                quantification = f"by approximately {interval}%"
                            elif unit == "x":
                                quantification = f"by {interval} times"
                            else:
                                quantification = f"by approximately {interval} {unit}"
                            
                            # Add to bullet if not already quantified
                            if not any(char.isdigit() for char in bullet_text):
                                return f"{bullet_text} {quantification}"
        
        return bullet_text
    
    def _add_relevant_skills(
        self,
        bullet_text: str,
        supporting_evidence: List[EvidenceItem],
        job_requirements: List[str]
    ) -> str:
        """Add relevant technical skills to bullet"""
        
        # Collect skills from evidence
        evidence_skills = set()
        for evidence in supporting_evidence:
            evidence_skills.update(skill.lower() for skill in evidence.skills)
        
        # Find job-relevant skills not mentioned in bullet
        job_skills = set(skill.lower() for skill in job_requirements)
        relevant_skills = evidence_skills.intersection(job_skills)
        
        # Remove skills already mentioned in bullet
        bullet_lower = bullet_text.lower()
        new_skills = [skill for skill in relevant_skills if skill not in bullet_lower]
        
        # Add up to 2 most relevant skills
        if new_skills:
            skills_to_add = new_skills[:2]
            skills_text = ", ".join(skills_to_add)
            return f"{bullet_text} using {skills_text}"
        
        return bullet_text
    
    def _strengthen_action_verbs(self, bullet_text: str) -> str:
        """Replace weak verbs with stronger alternatives"""
        
        verb_replacements = {
            "worked on": "developed",
            "helped": "collaborated to",
            "did": "executed",
            "made": "created",
            "used": "leveraged",
            "was responsible for": "managed",
            "was involved in": "contributed to"
        }
        
        enhanced_text = bullet_text
        for weak_verb, strong_verb in verb_replacements.items():
            enhanced_text = enhanced_text.replace(weak_verb, strong_verb)
        
        return enhanced_text
    
    def _optimize_for_ats(self, bullet_text: str, job_requirements: List[str]) -> str:
        """Optimize bullet for ATS keywords"""
        
        # This is a simplified version - would use more sophisticated ATS optimization
        enhanced_text = bullet_text
        
        # Ensure job-relevant keywords are present
        for requirement in job_requirements[:3]:  # Top 3 requirements
            if requirement.lower() not in bullet_text.lower():
                # Try to naturally incorporate the keyword
                if "developed" in bullet_text.lower() and requirement.lower() in ["python", "javascript", "react"]:
                    enhanced_text = enhanced_text.replace("developed", f"developed {requirement}-based")
                    break
        
        return enhanced_text
    
    def _generate_rs_basis(
        self,
        supporting_evidence: List[EvidenceItem],
        rs_analysis: RSAnalysis
    ) -> str:
        """Generate human-readable RS basis explanation"""
        
        if not supporting_evidence:
            return "No supporting evidence available"
        
        evidence_summary = []
        for evidence in supporting_evidence[:2]:  # Top 2 pieces
            summary = f"{evidence.evidence_type.value} from {evidence.company} ({evidence.start_date})"
            evidence_summary.append(summary)
        
        basis = f"Enhancement based on {', '.join(evidence_summary)}"
        
        if rs_analysis.confidence_score < 0.8:
            basis += f" (confidence: {rs_analysis.confidence_score:.1f})"
        
        return basis
    
    def _extract_quantification(self, enhanced_text: str) -> Optional[Dict[str, Any]]:
        """Extract quantification information from enhanced text"""
        import re
        
        # Look for percentage improvements
        percent_match = re.search(r'(\d+)-(\d+)%', enhanced_text)
        if percent_match:
            return {
                "type": "percentage",
                "range": [int(percent_match.group(1)), int(percent_match.group(2))],
                "unit": "%"
            }
        
        # Look for multiplier improvements
        times_match = re.search(r'(\d+)-(\d+) times', enhanced_text)
        if times_match:
            return {
                "type": "multiplier",
                "range": [int(times_match.group(1)), int(times_match.group(2))],
                "unit": "x"
            }
        
        return None
    
    async def get_user_evidence_vault(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all evidence for a user"""
        user_evidence_ids = self.user_evidence_index.get(user_id, set())
        evidence_items = []
        
        for evidence_id in user_evidence_ids:
            evidence = self.evidence_store.get(evidence_id)
            if evidence:
                evidence_items.append(evidence.to_dict())
        
        # Sort by creation date (newest first)
        evidence_items.sort(key=lambda x: x['created_at'], reverse=True)
        
        return evidence_items
    
    async def validate_rs_bullet(self, bullet: RSBullet) -> Dict[str, Any]:
        """Validate an RS bullet for ethical compliance"""
        
        validation_results = {
            "valid": True,
            "risk_level": bullet.risk_level.value,
            "confidence": bullet.confidence,
            "issues": [],
            "recommendations": []
        }
        
        # Check confidence threshold
        if bullet.confidence < settings.RS_CONFIDENCE_THRESHOLD:
            validation_results["issues"].append("Confidence below threshold")
            validation_results["valid"] = False
        
        # Check risk level
        if bullet.risk_level in [RSRiskLevel.HIGH, RSRiskLevel.CRITICAL]:
            validation_results["issues"].append(f"Risk level too high: {bullet.risk_level.value}")
            validation_results["valid"] = False
        
        # Check for proper attribution
        if bullet.rs_applied and not bullet.rs_basis:
            validation_results["issues"].append("Missing RS basis attribution")
            validation_results["valid"] = False
        
        # Generate recommendations
        if not validation_results["valid"]:
            validation_results["recommendations"].append("Consider using original bullet without RS")
            if bullet.confidence < 0.7:
                validation_results["recommendations"].append("Gather more evidence to support enhancement")
        
        return validation_results