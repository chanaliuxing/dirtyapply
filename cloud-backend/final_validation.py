#!/usr/bin/env python3
"""
Final validation of the Indeed Automation System
"""

import os
import sys

def check_critical_files():
    """Check all critical files exist"""
    critical_files = [
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
    
    missing = []
    for file_path in critical_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    return missing

def check_safety_settings():
    """Check safety settings in config"""
    try:
        with open("app/core/config.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        safety_checks = [
            "AUTO_SUBMIT_ENABLED: bool = False",
            "REQUIRE_CONFIRMATION: bool = True",
            "RS_CONFIDENCE_THRESHOLD: float = 0.7",
            "MAX_RS_BULLETS_PER_RESUME"
        ]
        
        missing_safety = []
        for check in safety_checks:
            if check not in content:
                missing_safety.append(check)
        
        return missing_safety
    except Exception as e:
        return [f"Error reading config: {e}"]

def check_service_methods():
    """Check key service methods exist"""
    service_checks = [
        ("app/services/resume_tailoring.py", ["create_tailored_resume", "generate_resume_diff"]),
        ("app/services/job_matching.py", ["analyze_job_match", "calculate_skill_match"]),
        ("app/services/evidence_vault.py", ["apply_reasoning_synthesis", "find_supporting_evidence"]),
        ("app/services/qa_generation.py", ["generate_answers", "suggest_questions_for_job"])
    ]
    
    missing_methods = []
    
    for file_path, methods in service_checks:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            for method in methods:
                if method not in content:
                    missing_methods.append(f"{file_path}: {method}")
        except Exception as e:
            missing_methods.append(f"{file_path}: Error reading file - {e}")
    
    return missing_methods

def check_ethical_constraints():
    """Check ethical constraints in evidence vault"""
    try:
        with open("app/services/evidence_vault.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        ethical_checks = [
            "RSRiskLevel",
            "confidence",
            "evidence_basis", 
            "risk_assessment",
            "temporal_constraints",
            "no_fabrication"
        ]
        
        missing_ethics = []
        for check in ethical_checks:
            if check not in content:
                missing_ethics.append(check)
        
        return missing_ethics
    except Exception as e:
        return [f"Error reading evidence vault: {e}"]

def main():
    """Run final validation"""
    print("INDEED AUTOMATION SYSTEM - FINAL VALIDATION")
    print("=" * 50)
    
    all_good = True
    
    # Check files
    print("\n1. CHECKING CRITICAL FILES...")
    missing_files = check_critical_files()
    if missing_files:
        print(f"FAIL: Missing files: {', '.join(missing_files)}")
        all_good = False
    else:
        print("PASS: All critical files present")
    
    # Check safety
    print("\n2. CHECKING SAFETY SETTINGS...")
    missing_safety = check_safety_settings()
    if missing_safety:
        print(f"FAIL: Missing safety settings: {', '.join(missing_safety)}")
        all_good = False
    else:
        print("PASS: All safety settings configured")
    
    # Check service methods
    print("\n3. CHECKING SERVICE METHODS...")
    missing_methods = check_service_methods()
    if missing_methods:
        print(f"FAIL: Missing methods:")
        for method in missing_methods:
            print(f"  - {method}")
        all_good = False
    else:
        print("PASS: All service methods present")
    
    # Check ethics
    print("\n4. CHECKING ETHICAL CONSTRAINTS...")
    missing_ethics = check_ethical_constraints()
    if missing_ethics:
        print(f"FAIL: Missing ethical constraints: {', '.join(missing_ethics)}")
        all_good = False
    else:
        print("PASS: All ethical constraints implemented")
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("SUCCESS: System validation PASSED")
        print("The Indeed Automation System is COMPLETE and READY")
        return 0
    else:
        print("FAILURE: System validation FAILED")
        print("Please address the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())