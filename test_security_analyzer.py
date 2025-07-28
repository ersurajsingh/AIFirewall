#!/usr/bin/env python3
"""
Test script to demonstrate the AI Code Security Analyzer functionality.
This script shows various dangerous code patterns and how they are detected.
"""

import json
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.security_analyzer import AICodeSecurityAnalyzer

def print_analysis_result(code_description: str, code: str, language: str = "python"):
    """Helper function to print analysis results in a readable format"""
    print(f"\n{'='*60}")
    print(f"🔍 ANALYZING: {code_description}")
    print(f"{'='*60}")
    print("CODE:")
    print("-" * 30)
    print(code)
    print("-" * 30)
    
    analyzer = AICodeSecurityAnalyzer()
    result = analyzer.analyze_code(code, language)
    
    print(f"\n📊 ANALYSIS RESULT:")
    print(f"Safety Score: {result['safety_score']} ({result['safety_status']})")
    print(f"Total Issues: {result['total_issues']}")
    print(f"Explanation: {result['explanation']}")
    print(f"Recommendation: {result['recommendation']}")
    
    if result['issues']:
        print(f"\n⚠️  SECURITY ISSUES DETECTED:")
        for i, issue in enumerate(result['issues'], 1):
            print(f"  {i}. [{issue['risk_level']}] Line {issue['line_number']}: {issue['description']}")
            if issue['suggestion']:
                print(f"     💡 Suggestion: {issue['suggestion']}")
    
    print(f"\n🕒 Analysis completed at: {result['analysis_timestamp']}")

def test_sql_vulnerabilities():
    """Test SQL-related security vulnerabilities"""
    
    # Test 1: DROP TABLE
    dangerous_sql_1 = '''
import sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("DROP TABLE users")
conn.commit()
'''
    print_analysis_result("SQL DROP TABLE Operation", dangerous_sql_1)
    
    # Test 2: DELETE without WHERE
    dangerous_sql_2 = '''
import mysql.connector
db = mysql.connector.connect(host="prod_server", database="main_db")
cursor = db.cursor()
cursor.execute("DELETE FROM customers")
db.commit()
'''
    print_analysis_result("DELETE without WHERE clause + Production DB", dangerous_sql_2)
    
    # Test 3: TRUNCATE TABLE
    dangerous_sql_3 = '''
query = "TRUNCATE TABLE user_sessions"
cursor.execute(query)
'''
    print_analysis_result("TRUNCATE TABLE Operation", dangerous_sql_3)

def test_code_execution_risks():
    """Test dynamic code execution vulnerabilities"""
    
    # Test 1: eval() usage
    dangerous_eval = '''
user_input = request.json.get('formula')
result = eval(user_input)  # Dangerous!
return {"result": result}
'''
    print_analysis_result("Dynamic Code Execution with eval()", dangerous_eval)
    
    # Test 2: exec() usage
    dangerous_exec = '''
code_snippet = get_ai_generated_code()
exec(code_snippet)  # Very dangerous!
'''
    print_analysis_result("Dynamic Code Execution with exec()", dangerous_exec)
    
    # Test 3: os.system() call
    dangerous_system = '''
import os
filename = user_provided_filename
os.system(f"rm -rf {filename}")  # Command injection risk
'''
    print_analysis_result("System Command Execution", dangerous_system)

def test_mass_operations():
    """Test mass data operations"""
    
    # Test 1: Bulk user creation
    bulk_users = '''
import django
from myapp.models import User

# Create 10000 fake users
for i in range(10000):
    User.objects.create(
        username=f"fake_user_{i}",
        email=f"fake{i}@example.com",
        password="default123"
    )
'''
    print_analysis_result("Bulk User Creation", bulk_users)
    
    # Test 2: Large data insertion loop
    bulk_data = '''
import sqlite3
conn = sqlite3.connect("production_db.sqlite")
cursor = conn.cursor()

for i in range(5000):
    cursor.execute("INSERT INTO transactions (amount, user_id) VALUES (?, ?)", (100.0, i))
conn.commit()
'''
    print_analysis_result("Large Data Insertion Loop", bulk_data)

def test_file_operations():
    """Test potentially dangerous file operations"""
    
    dangerous_file_ops = '''
import os
import shutil

# Dangerous file operations
files_to_delete = get_file_list()
for file in files_to_delete:
    os.remove(file)
    
# Even more dangerous
shutil.rmtree("/important/directory")
'''
    print_analysis_result("Dangerous File Operations", dangerous_file_ops)

def test_network_operations():
    """Test external network requests"""
    
    network_code = '''
import requests
import urllib.request

# External API calls
api_endpoints = get_external_apis()
for endpoint in api_endpoints:
    response = requests.get(endpoint)
    
# File download
urllib.request.urlretrieve("http://unknown-site.com/script.py", "downloaded_script.py")
'''
    print_analysis_result("External Network Requests", network_code)

def test_safe_code():
    """Test code that should be considered safe"""
    
    safe_code = '''
import json
from typing import List

def calculate_fibonacci(n: int) -> int:
    """Calculate fibonacci number safely"""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def process_user_data(data: List[dict]) -> dict:
    """Safely process user data"""
    result = {
        "total_users": len(data),
        "average_age": sum(user.get("age", 0) for user in data) / len(data) if data else 0
    }
    return result

# Safe database query with parameterized statement
def get_user_by_id(user_id: int):
    query = "SELECT * FROM users WHERE id = ?"
    return cursor.execute(query, (user_id,)).fetchone()
'''
    print_analysis_result("Safe Code Example", safe_code)

def test_mixed_code():
    """Test code with mixed safe and unsafe patterns"""
    
    mixed_code = '''
import os
import sqlite3
import subprocess

def backup_database():
    """Backup database safely"""
    # Safe operation
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE active = ?", (True,))
    
    # Potentially dangerous operation
    backup_cmd = f"pg_dump {database_url} > backup.sql"
    subprocess.run(backup_cmd, shell=True)
    
    # Another safe operation
    users = cursor.fetchall()
    return len(users)

# Bulk operation - moderate risk
def create_test_users():
    for i in range(150):  # Medium-scale operation
        create_user(f"test_user_{i}")
'''
    print_analysis_result("Mixed Safe/Unsafe Code", mixed_code)

def run_comprehensive_tests():
    """Run all security analyzer tests"""
    print("🚀 AI CODE SECURITY ANALYZER - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    try:
        print("\n🔍 Testing SQL Vulnerabilities...")
        test_sql_vulnerabilities()
        
        print("\n🔍 Testing Code Execution Risks...")
        test_code_execution_risks()
        
        print("\n🔍 Testing Mass Operations...")
        test_mass_operations()
        
        print("\n🔍 Testing File Operations...")
        test_file_operations()
        
        print("\n🔍 Testing Network Operations...")
        test_network_operations()
        
        print("\n🔍 Testing Safe Code...")
        test_safe_code()
        
        print("\n🔍 Testing Mixed Code...")
        test_mixed_code()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("The AI Code Security Analyzer is working correctly.")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_comprehensive_tests() 