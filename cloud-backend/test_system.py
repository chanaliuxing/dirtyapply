#!/usr/bin/env python3
"""
Comprehensive System Test for Indeed Automation Cloud Backend
Tests all core components against requirements
"""

import asyncio
import json
import sys
from typing import Dict, List, Any
from datetime import datetime
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemTester:
    """Comprehensive system tester"""
    
    def __init__(self):
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "details": {}
        }
    
    def test_result(self, test_name: str, passed: bool, details: str = None):
        """Record test result"""
        if passed:
            self.test_results["passed"] += 1
            logger.info(f"✅ {test_name}")
        else:
            self.test_results["failed"] += 1
            logger.error(f"❌ {test_name}: {details}")
            self.test_results["errors"].append(f"{test_name}: {details}")
        
        self.test_results["details"][test_name] = {
            "passed": passed,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def test_file_structure(self):
        """Test if all required files exist"""
        import os
        
        required_files = [
            "app/main.py",
            "app/core/config.py", 
            "app/ai/orchestrator.py",
            "app/services/resume_tailoring.py",
            "app/services/job_matching.py",
            "app/services/evidence_vault.py",
            "app/services/qa_generation.py",
            "app/models/user.py",
            "app/models/jobs.py", 
            "app/models/resumes.py",
            "requirements.txt"
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                self.test_result(f"File exists: {file_path}", True)
            else:
                self.test_result(f"File exists: {file_path}", False, f"Missing file: {file_path}")
    
    def test_python_syntax(self):
        """Test Python syntax of all modules"""
        import py_compile
        import os
        
        python_files = []
        for root, dirs, files in os.walk("app"):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        
        for py_file in python_files:
            try:
                py_compile.compile(py_file, doraise=True)
                self.test_result(f"Syntax check: {py_file}", True)
            except Exception as e:
                self.test_result(f"Syntax check: {py_file}", False, str(e))
    
    def test_imports(self):
        """Test critical imports"""
        test_cases = [
            ("FastAPI imports", lambda: __import__('fastapi')),
            ("Pydantic imports", lambda: __import__('pydantic')), 
            ("SQLAlchemy imports", lambda: __import__('sqlalchemy')),
            ("Structlog imports", lambda: __import__('structlog')),
        ]
        
        for test_name, import_func in test_cases:
            try:
                import_func()
                self.test_result(test_name, True)
            except ImportError as e:
                self.test_result(test_name, False, f"Import error: {e}")
            except Exception as e:
                self.test_result(test_name, False, f"Unexpected error: {e}")
    
    def test_configuration(self):
        """Test configuration settings"""
        try:
            import sys
            import os
            sys.path.append(os.getcwd())
            
            from app.core.config import Settings
            settings = Settings()
            
            # Test security settings
            self.test_result(
                "Auto-submit disabled", 
                not getattr(settings, 'AUTO_SUBMIT_ENABLED', True),
                "Auto-submit should be disabled by default"
            )
            
            self.test_result(
                "Confirmation required",
                getattr(settings, 'REQUIRE_CONFIRMATION', False),
                "Confirmation should be required by default"
            )
            
            self.test_result(
                "RS confidence threshold",
                getattr(settings, 'RS_CONFIDENCE_THRESHOLD', 0) >= 0.7,
                f"RS threshold: {getattr(settings, 'RS_CONFIDENCE_THRESHOLD', 'not set')}"
            )
            
            self.test_result(
                "Max RS bullets limit",
                getattr(settings, 'MAX_RS_BULLETS_PER_RESUME', 999) <= 20,
                f"Max RS bullets: {getattr(settings, 'MAX_RS_BULLETS_PER_RESUME', 'not set')}"
            )
            
        except Exception as e:
            self.test_result("Configuration test", False, str(e))
    
    def test_models_structure(self):
        """Test database models structure"""
        try:
            import sys
            import os
            sys.path.append(os.getcwd())
            
            # Test user models
            from app.models.user import User, UserProfile, UserExperience, UserEducation, UserSettings
            
            required_user_fields = ['email', 'hashed_password', 'is_active', 'subscription_tier']
            user_fields = [field.name for field in User.__table__.columns]
            
            for field in required_user_fields:
                if field in user_fields:
                    self.test_result(f"User model has {field}", True)
                else:
                    self.test_result(f"User model has {field}", False, f"Missing field: {field}")
            
            # Test job models
            from app.models.jobs import JobPosting, JobAnalysis, JobApplication, CompanyProfile
            
            required_job_fields = ['title', 'company', 'description', 'requirements']
            job_fields = [field.name for field in JobPosting.__table__.columns]
            
            for field in required_job_fields:
                if field in job_fields:
                    self.test_result(f"JobPosting model has {field}", True)
                else:
                    self.test_result(f"JobPosting model has {field}", False, f"Missing field: {field}")
            
            # Test resume models
            from app.models.resumes import GeneratedResume, EvidenceItem, CoverLetter
            
            required_resume_fields = ['user_id', 'name', 'is_tailored', 'ats_score']
            resume_fields = [field.name for field in GeneratedResume.__table__.columns]
            
            for field in required_resume_fields:
                if field in resume_fields:
                    self.test_result(f"GeneratedResume model has {field}", True)
                else:
                    self.test_result(f"GeneratedResume model has {field}", False, f"Missing field: {field}")
            
        except Exception as e:
            self.test_result("Models structure test", False, str(e))
    
    def test_service_interfaces(self):
        """Test service class interfaces"""
        try:
            import sys
            import os
            sys.path.append(os.getcwd())
            
            # Test Resume Tailoring Service
            from app.services.resume_tailoring import ResumeTailoringService
            service = ResumeTailoringService()
            
            required_methods = ['create_tailored_resume', 'generate_resume_diff']
            for method in required_methods:
                if hasattr(service, method):
                    self.test_result(f"ResumeTailoringService has {method}", True)
                else:
                    self.test_result(f"ResumeTailoringService has {method}", False, f"Missing method: {method}")
            
            # Test Job Matching Service
            from app.services.job_matching import JobMatchingService
            service = JobMatchingService()
            
            required_methods = ['analyze_job_match', 'calculate_skill_match']
            for method in required_methods:
                if hasattr(service, method):
                    self.test_result(f"JobMatchingService has {method}", True)
                else:
                    self.test_result(f"JobMatchingService has {method}", False, f"Missing method: {method}")
            
            # Test Evidence Vault Service
            from app.services.evidence_vault import EvidenceVaultService
            service = EvidenceVaultService()
            
            required_methods = ['add_evidence_item', 'apply_reasoning_synthesis', 'find_supporting_evidence']
            for method in required_methods:
                if hasattr(service, method):
                    self.test_result(f"EvidenceVaultService has {method}", True)
                else:
                    self.test_result(f"EvidenceVaultService has {method}", False, f"Missing method: {method}")
            
            # Test Q&A Generation Service
            from app.services.qa_generation import QAGenerationService
            service = QAGenerationService()
            
            required_methods = ['generate_answers', 'suggest_questions_for_job']
            for method in required_methods:
                if hasattr(service, method):
                    self.test_result(f"QAGenerationService has {method}", True)
                else:
                    self.test_result(f"QAGenerationService has {method}", False, f"Missing method: {method}")
                    
        except Exception as e:
            self.test_result("Service interfaces test", False, str(e))
    
    def test_ai_orchestrator(self):
        """Test AI Orchestrator functionality"""
        try:
            import sys
            import os
            sys.path.append(os.getcwd())
            
            from app.ai.orchestrator import AIOrchestrator, AITask, TaskType
            
            orchestrator = AIOrchestrator()
            
            # Test task types are defined
            required_task_types = ['JTR_GENERATION', 'JOB_ANALYSIS', 'QA_GENERATION', 'RESUME_OPTIMIZATION']
            for task_type in required_task_types:
                if hasattr(TaskType, task_type):
                    self.test_result(f"TaskType has {task_type}", True)
                else:
                    self.test_result(f"TaskType has {task_type}", False, f"Missing task type: {task_type}")
            
            # Test orchestrator methods
            required_methods = ['execute_task', 'get_available_models']
            for method in required_methods:
                if hasattr(orchestrator, method):
                    self.test_result(f"AIOrchestrator has {method}", True)
                else:
                    self.test_result(f"AIOrchestrator has {method}", False, f"Missing method: {method}")
            
        except Exception as e:
            self.test_result("AI Orchestrator test", False, str(e))
    
    def test_ethical_constraints(self):
        """Test ethical constraints and safety measures"""
        try:
            import sys
            import os
            sys.path.append(os.getcwd())
            
            from app.services.evidence_vault import RSRiskLevel, EvidenceVaultService
            
            service = EvidenceVaultService()
            
            # Test risk levels are defined
            required_risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            for risk_level in required_risk_levels:
                if hasattr(RSRiskLevel, risk_level):
                    self.test_result(f"RSRiskLevel has {risk_level}", True)
                else:
                    self.test_result(f"RSRiskLevel has {risk_level}", False, f"Missing risk level: {risk_level}")
            
            # Test RS rules exist
            if hasattr(service, 'rs_rules') and service.rs_rules:
                self.test_result("RS rules loaded", True)
                
                # Check specific ethical constraints
                rules = service.rs_rules
                if 'enhancement_limits' in rules:
                    limits = rules['enhancement_limits']
                    if limits.get('require_evidence_basis'):
                        self.test_result("RS requires evidence basis", True)
                    else:
                        self.test_result("RS requires evidence basis", False, "Evidence basis not required")
                    
                    if limits.get('no_fabrication'):
                        self.test_result("RS prohibits fabrication", True)
                    else:
                        self.test_result("RS prohibits fabrication", False, "Fabrication not explicitly prohibited")
                else:
                    self.test_result("RS enhancement limits defined", False, "Enhancement limits missing")
            else:
                self.test_result("RS rules loaded", False, "RS rules not found")
            
        except Exception as e:
            self.test_result("Ethical constraints test", False, str(e))
    
    async def test_async_functionality(self):
        """Test async functionality"""
        try:
            import sys
            import os
            sys.path.append(os.getcwd())
            
            from app.services.resume_tailoring import ResumeTailoringService
            from app.services.job_matching import JobMatchingService
            
            resume_service = ResumeTailoringService()
            job_service = JobMatchingService()
            
            # Test async methods exist and are callable
            async_methods = [
                (resume_service, 'create_tailored_resume'),
                (job_service, 'analyze_job_match'),
            ]
            
            for service, method_name in async_methods:
                method = getattr(service, method_name, None)
                if method and asyncio.iscoroutinefunction(method):
                    self.test_result(f"Async method: {service.__class__.__name__}.{method_name}", True)
                else:
                    self.test_result(f"Async method: {service.__class__.__name__}.{method_name}", False, 
                                   f"Method not async or missing: {method_name}")
            
        except Exception as e:
            self.test_result("Async functionality test", False, str(e))
    
    def generate_report(self):
        """Generate test report"""
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""
=== INDEED AUTOMATION SYSTEM TEST REPORT ===
Generated: {datetime.utcnow().isoformat()}

SUMMARY:
✅ Tests Passed: {self.test_results["passed"]}
❌ Tests Failed: {self.test_results["failed"]}
📊 Success Rate: {success_rate:.1f}%

"""
        
        if self.test_results["failed"] > 0:
            report += "FAILURES:\n"
            for error in self.test_results["errors"]:
                report += f"- {error}\n"
            report += "\n"
        
        report += "DETAILED RESULTS:\n"
        for test_name, result in self.test_results["details"].items():
            status = "✅" if result["passed"] else "❌"
            report += f"{status} {test_name}"
            if result["details"] and not result["passed"]:
                report += f": {result['details']}"
            report += "\n"
        
        return report

async def main():
    """Run all tests"""
    tester = SystemTester()
    
    print("🚀 Starting comprehensive system test...\n")
    
    # Run tests
    tester.test_file_structure()
    tester.test_python_syntax() 
    tester.test_imports()
    tester.test_configuration()
    tester.test_models_structure()
    tester.test_service_interfaces()
    tester.test_ai_orchestrator()
    tester.test_ethical_constraints()
    await tester.test_async_functionality()
    
    # Generate and print report
    report = tester.generate_report()
    print(report)
    
    # Save report to file
    with open("test_report.txt", "w") as f:
        f.write(report)
    
    # Exit with appropriate code
    if tester.test_results["failed"] > 0:
        print("⚠️  Some tests failed. See report above.")
        sys.exit(1)
    else:
        print("🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())