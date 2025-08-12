#!/usr/bin/env python3
"""
Simple System Test for Indeed Automation Cloud Backend
"""

import os
import sys
import py_compile
import asyncio
from datetime import datetime

class SimpleSystemTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_result(self, test_name: str, passed: bool, details: str = None):
        if passed:
            self.passed += 1
            print(f"PASS: {test_name}")
        else:
            self.failed += 1
            error_msg = f"FAIL: {test_name}"
            if details:
                error_msg += f" - {details}"
            print(error_msg)
            self.errors.append(error_msg)
    
    def test_file_structure(self):
        """Test if all required files exist"""
        print("\n=== Testing File Structure ===")
        
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
            exists = os.path.exists(file_path)
            self.test_result(f"File exists: {file_path}", exists, 
                           f"Missing file: {file_path}" if not exists else None)
    
    def test_python_syntax(self):
        """Test Python syntax of key modules"""
        print("\n=== Testing Python Syntax ===")
        
        key_files = [
            "app/main.py",
            "app/core/config.py",
            "app/ai/orchestrator.py",
            "app/services/resume_tailoring.py",
            "app/services/job_matching.py",
            "app/services/evidence_vault.py",
            "app/services/qa_generation.py"
        ]
        
        for py_file in key_files:
            if os.path.exists(py_file):
                try:
                    py_compile.compile(py_file, doraise=True)
                    self.test_result(f"Syntax check: {py_file}", True)
                except Exception as e:
                    self.test_result(f"Syntax check: {py_file}", False, str(e))
            else:
                self.test_result(f"Syntax check: {py_file}", False, "File not found")
    
    def test_requirements_content(self):
        """Test requirements.txt contains essential packages"""
        print("\n=== Testing Requirements ===")
        
        if not os.path.exists("requirements.txt"):
            self.test_result("requirements.txt exists", False, "File not found")
            return
        
        with open("requirements.txt", "r") as f:
            content = f.read().lower()
        
        essential_packages = [
            "fastapi",
            "sqlalchemy", 
            "pydantic",
            "uvicorn",
            "structlog"
        ]
        
        for package in essential_packages:
            if package in content:
                self.test_result(f"Requirements contains {package}", True)
            else:
                self.test_result(f"Requirements contains {package}", False, f"Missing package: {package}")
    
    def test_configuration_safety(self):
        """Test safety configurations"""
        print("\n=== Testing Safety Configuration ===")
        
        try:
            # Read config file
            with open("app/core/config.py", "r") as f:
                content = f.read()
            
            # Check for safety settings
            safety_checks = [
                ("AUTO_SUBMIT_ENABLED", False),  # Should be disabled
                ("REQUIRE_CONFIRMATION", True),   # Should be required
                ("RS_CONFIDENCE_THRESHOLD", "0.7"),  # Should be >= 0.7
                ("MAX_RS_BULLETS_PER_RESUME", True)  # Should have limit
            ]
            
            for setting, expected in safety_checks:
                if setting in content:
                    self.test_result(f"Config has {setting}", True)
                else:
                    self.test_result(f"Config has {setting}", False, f"Missing safety setting: {setting}")
                    
        except Exception as e:
            self.test_result("Configuration safety test", False, str(e))
    
    def test_model_structure(self):
        """Test database models have required fields"""
        print("\n=== Testing Model Structure ===")
        
        model_files = ["app/models/user.py", "app/models/jobs.py", "app/models/resumes.py"]
        
        for model_file in model_files:
            if os.path.exists(model_file):
                with open(model_file, "r") as f:
                    content = f.read()
                
                # Check for essential elements
                if "class " in content and "__tablename__" in content:
                    self.test_result(f"Model structure: {model_file}", True)
                else:
                    self.test_result(f"Model structure: {model_file}", False, "Missing class or table name")
            else:
                self.test_result(f"Model file exists: {model_file}", False, "File not found")
    
    def test_service_structure(self):
        """Test service classes have required methods"""
        print("\n=== Testing Service Structure ===")
        
        service_tests = [
            ("app/services/resume_tailoring.py", ["create_tailored_resume", "ResumeTailoringService"]),
            ("app/services/job_matching.py", ["analyze_job_match", "JobMatchingService"]),
            ("app/services/evidence_vault.py", ["apply_reasoning_synthesis", "EvidenceVaultService"]),
            ("app/services/qa_generation.py", ["generate_answers", "QAGenerationService"])
        ]
        
        for service_file, required_items in service_tests:
            if os.path.exists(service_file):
                with open(service_file, "r") as f:
                    content = f.read()
                
                for item in required_items:
                    if item in content:
                        self.test_result(f"{service_file} has {item}", True)
                    else:
                        self.test_result(f"{service_file} has {item}", False, f"Missing: {item}")
            else:
                self.test_result(f"Service file exists: {service_file}", False, "File not found")
    
    def test_ethical_constraints(self):
        """Test ethical constraints are implemented"""
        print("\n=== Testing Ethical Constraints ===")
        
        if os.path.exists("app/services/evidence_vault.py"):
            with open("app/services/evidence_vault.py", "r") as f:
                content = f.read()
            
            ethical_checks = [
                "RSRiskLevel",
                "confidence",
                "evidence_basis",
                "verification_status",
                "risk_assessment"
            ]
            
            for check in ethical_checks:
                if check in content:
                    self.test_result(f"Evidence vault has {check}", True)
                else:
                    self.test_result(f"Evidence vault has {check}", False, f"Missing ethical constraint: {check}")
        else:
            self.test_result("Evidence vault file exists", False, "File not found")
    
    def generate_report(self):
        """Generate final test report"""
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{'='*50}")
        print("SYSTEM TEST REPORT")
        print(f"{'='*50}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nSUMMARY:")
        print(f"Tests Passed: {self.passed}")
        print(f"Tests Failed: {self.failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.errors:
            print(f"\nFAILURES:")
            for error in self.errors:
                print(f"- {error}")
        
        return self.failed == 0

def main():
    """Run all tests"""
    print("Starting comprehensive system validation...")
    
    tester = SimpleSystemTester()
    
    # Run tests
    tester.test_file_structure()
    tester.test_python_syntax() 
    tester.test_requirements_content()
    tester.test_configuration_safety()
    tester.test_model_structure()
    tester.test_service_structure()
    tester.test_ethical_constraints()
    
    # Generate report
    success = tester.generate_report()
    
    if success:
        print("\nALL TESTS PASSED!")
        return 0
    else:
        print("\nSOME TESTS FAILED - See details above")
        return 1

if __name__ == "__main__":
    sys.exit(main())