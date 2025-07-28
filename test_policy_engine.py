#!/usr/bin/env python3
"""
Test script for the Policy Engine functionality.
This demonstrates various policy violations and how they are detected.
"""

import os
import sys
import json
from typing import Dict, Any

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.policy_engine import PolicyEngine, PolicyRule, PolicySeverity, PolicyAction

def print_analysis_result(title: str, code: str, violations: list):
    """Helper function to print policy analysis results"""
    print(f"\n{'='*80}")
    print(f"🔍 TESTING: {title}")
    print(f"{'='*80}")
    print("CODE:")
    print("-" * 40)
    print(code)
    print("-" * 40)
    
    print(f"\n📊 POLICY ANALYSIS RESULT:")
    print(f"Total Violations: {len(violations)}")
    
    if violations:
        print(f"\n⚠️  POLICY VIOLATIONS DETECTED:")
        for i, violation in enumerate(violations, 1):
            print(f"  {i}. [{violation.severity.value.upper()}] {violation.rule_name}")
            print(f"     📝 {violation.description}")
            if violation.line_number:
                print(f"     📍 Line {violation.line_number}")
            if violation.matched_content:
                print(f"     🔍 Matched: '{violation.matched_content}'")
            if violation.suggestion:
                print(f"     💡 Suggestion: {violation.suggestion}")
            print(f"     🚨 Action: {violation.action.value}")
            print()
    else:
        print("✅ No policy violations detected!")

def test_production_env_modification():
    """Test production environment modification detection"""
    dangerous_code = '''
import os

# Dangerous: Modifying production environment variables
os.environ["PROD_DATABASE_URL"] = "postgresql://user:pass@localhost/db"
os.environ["PRODUCTION_API_KEY"] = "secret-key-123"

# Also dangerous
production_config = {
    "DATABASE_URL_PROD": "mysql://admin:password@prod-server/db"
}
'''
    
    engine = PolicyEngine()
    violations = engine.analyze_code(dangerous_code)
    print_analysis_result("Production Environment Modification", dangerous_code, violations)

def test_sensitive_directory_access():
    """Test sensitive directory access detection"""
    dangerous_code = '''
import os
from pathlib import Path

# Dangerous: Accessing sensitive system directories
with open("/etc/passwd", "r") as f:
    users = f.read()

# Also dangerous
config_path = Path("/sys/class/net")
files = os.listdir("/proc/")

# Windows equivalent
windows_system = open("C:\\Windows\\System32\\config\\SAM", "r")
'''
    
    engine = PolicyEngine()
    violations = engine.analyze_code(dangerous_code)
    print_analysis_result("Sensitive Directory Access", dangerous_code, violations)

def test_dangerous_libraries():
    """Test dangerous library usage detection"""
    dangerous_code = '''
import pickle
import marshal
from pickle import loads, dumps

# Dangerous: Using pickle for deserialization
data = pickle.loads(user_input)
serialized = pickle.dumps(sensitive_data)

# Also dangerous
compiled_code = marshal.loads(untrusted_bytes)

# Subprocess with shell=True
import subprocess
result = subprocess.call("rm -rf /tmp/*", shell=True)
'''
    
    engine = PolicyEngine()
    violations = engine.analyze_code(dangerous_code)
    print_analysis_result("Dangerous Library Usage", dangerous_code, violations)

def test_database_credentials():
    """Test database credential exposure detection"""
    dangerous_code = '''
import psycopg2
import mysql.connector

# Dangerous: Hardcoded database credentials
conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="admin",
    password="secret123"
)

# Also dangerous
DATABASE_URL = "postgresql://user:password123@prod-server:5432/production_db"
mysql_config = {
    "host": "mysql-server",
    "user": "root",
    "passwd": "admin123",
    "database": "users"
}

# API keys in code
api_key = "sk-1234567890abcdef1234567890abcdef"
github_token = "ghp_1234567890123456789012345678901234567890"
'''
    
    engine = PolicyEngine()
    violations = engine.analyze_code(dangerous_code)
    print_analysis_result("Database Credential Exposure", dangerous_code, violations)

def test_destructive_file_operations():
    """Test destructive file operations detection"""
    dangerous_code = '''
import os
import shutil
from pathlib import Path

# Dangerous: Destructive file operations
os.remove("/important/file.txt")
os.rmdir("/temp/data")
shutil.rmtree("/user/documents")

# Pathlib operations
Path("/critical/config.json").unlink()

# Subprocess file operations
import subprocess
subprocess.run("rm -rf /var/log/*", shell=True)
subprocess.call(["rmdir", "/tmp/cache"])
'''
    
    engine = PolicyEngine()
    violations = engine.analyze_code(dangerous_code)
    print_analysis_result("Destructive File Operations", dangerous_code, violations)

def test_code_injection():
    """Test code injection risks detection"""
    dangerous_code = '''
# Dangerous: Dynamic code execution
user_formula = input("Enter formula: ")
result = eval(user_formula)

# Also dangerous
code_snippet = request.json.get("code")
exec(code_snippet)

# Compilation risks
compiled = compile(user_input, "<string>", "exec")
exec(compiled)

# Dynamic imports
module_name = user_provided_module
imported_module = __import__(module_name)
'''
    
    engine = PolicyEngine()
    violations = engine.analyze_code(dangerous_code)
    print_analysis_result("Code Injection Risks", dangerous_code, violations)

def test_weak_cryptography():
    """Test weak cryptographic practices detection"""
    dangerous_code = '''
import hashlib
import ssl
import random

# Dangerous: Weak hashing algorithms
password_hash = hashlib.md5(password.encode()).hexdigest()
checksum = hashlib.sha1(data).digest()

# Weak SSL configuration
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# Poor random number generation for passwords
password = str(random.random() * 1000000)
token = random.randint(1000, 9999)
'''
    
    engine = PolicyEngine()
    violations = engine.analyze_code(dangerous_code)
    print_analysis_result("Weak Cryptographic Practices", dangerous_code, violations)

def test_custom_policy():
    """Test creating and using custom policies"""
    print(f"\n{'='*80}")
    print("🔧 TESTING: Custom Policy Creation")
    print(f"{'='*80}")
    
    # Create a custom policy
    custom_rule = PolicyRule(
        id="custom_test_rule",
        name="Test Data Creation",
        description="Prevents creation of test data in production",
        severity=PolicySeverity.HIGH,
        action=PolicyAction.WARN,
        patterns=[
            r"create_test_.*",
            r"generate_fake_.*",
            r"\.factory\.create"
        ],
        context_conditions={"environment": ["production"]},
        category="testing"
    )
    
    engine = PolicyEngine()
    engine.add_rule(custom_rule)
    
    test_code = '''
# Code that should trigger custom policy
def setup_test_environment():
    create_test_users(1000)
    generate_fake_orders(500)
    UserFactory.create(email="test@example.com")
    
    return "Test environment ready"
'''
    
    violations = engine.analyze_code(
        test_code, 
        context={"environment": "production"}
    )
    print_analysis_result("Custom Policy Test", test_code, violations)

def test_safe_code():
    """Test code that should not trigger any violations"""
    safe_code = '''
import json
import logging
from datetime import datetime
from typing import List, Optional

def calculate_user_metrics(users: List[dict]) -> dict:
    """Safely calculate user metrics"""
    if not users:
        return {"total": 0, "active": 0}
    
    total_users = len(users)
    active_users = len([u for u in users if u.get("is_active", False)])
    
    return {
        "total": total_users,
        "active": active_users,
        "calculated_at": datetime.now().isoformat()
    }

def safe_database_query(user_id: int) -> Optional[dict]:
    """Safe parameterized database query"""
    query = "SELECT * FROM users WHERE id = ? AND active = ?"
    # Using parameterized queries is safe
    return execute_query(query, (user_id, True))

# Safe logging
logger = logging.getLogger(__name__)
logger.info("Application started successfully")

# Safe configuration from environment
database_url = os.getenv("DATABASE_URL", "sqlite:///default.db")
'''
    
    engine = PolicyEngine()
    violations = engine.analyze_code(safe_code)
    print_analysis_result("Safe Code Example", safe_code, violations)

def test_policy_management():
    """Test policy management operations"""
    print(f"\n{'='*80}")
    print("🛠️  TESTING: Policy Management Operations")
    print(f"{'='*80}")
    
    engine = PolicyEngine()
    
    # Test rule enabling/disabling
    print("📋 Available Policies:")
    for rule_id, rule in engine.rules.items():
        status = "✅ Enabled" if rule.enabled else "❌ Disabled"
        print(f"  • {rule_id}: {rule.name} ({status})")
    
    # Disable a rule
    print(f"\n🔧 Disabling 'dangerous_libraries' rule...")
    engine.disable_rule("dangerous_libraries")
    
    # Test code that should trigger the disabled rule
    test_code = "import pickle\ndata = pickle.loads(user_input)"
    violations_before = engine.analyze_code(test_code)
    print(f"Violations with rule disabled: {len(violations_before)}")
    
    # Re-enable the rule
    print(f"🔧 Re-enabling 'dangerous_libraries' rule...")
    engine.enable_rule("dangerous_libraries")
    violations_after = engine.analyze_code(test_code)
    print(f"Violations with rule enabled: {len(violations_after)}")
    
    # Generate violation report
    print(f"\n📊 Generating violation report...")
    report = engine.generate_violation_report()
    print(f"Total violations in history: {report['summary']['total_violations']}")
    print(f"Critical violations: {report['summary']['critical']}")
    print(f"High violations: {report['summary']['high']}")

def run_comprehensive_tests():
    """Run all policy engine tests"""
    print("🚀 POLICY ENGINE - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("This test suite demonstrates the policy engine capabilities.")
    print("Testing various security violations and custom policy creation.")
    print("=" * 80)
    
    try:
        print("\n🔍 Testing Production Environment Protection...")
        test_production_env_modification()
        
        print("\n🔍 Testing Sensitive Directory Access...")
        test_sensitive_directory_access()
        
        print("\n🔍 Testing Dangerous Library Usage...")
        test_dangerous_libraries()
        
        print("\n🔍 Testing Database Credential Exposure...")
        test_database_credentials()
        
        print("\n🔍 Testing Destructive File Operations...")
        test_destructive_file_operations()
        
        print("\n🔍 Testing Code Injection Risks...")
        test_code_injection()
        
        print("\n🔍 Testing Weak Cryptography...")
        test_weak_cryptography()
        
        print("\n🔍 Testing Custom Policy Creation...")
        test_custom_policy()
        
        print("\n🔍 Testing Safe Code...")
        test_safe_code()
        
        print("\n🔍 Testing Policy Management...")
        test_policy_management()
        
        print("\n" + "=" * 80)
        print("✅ ALL POLICY ENGINE TESTS COMPLETED!")
        print("The Policy Engine is working correctly and ready for use.")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_comprehensive_tests() 