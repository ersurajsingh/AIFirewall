#!/usr/bin/env python3
"""
Example script demonstrating how to use the AI Firewall API endpoints
for analyzing AI-generated code suggestions.
"""

import requests
import json
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"

def analyze_single_ai_code(code: str, language: str = "python", context: str = None) -> Dict[str, Any]:
    """
    Analyze a single AI-generated code snippet using the advanced analyzer
    """
    endpoint = f"{API_BASE_URL}/analyze-ai-code"
    
    payload = {
        "code": code,
        "language": language,
        "source": "ai_generated",
        "context": context
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def analyze_batch_ai_code(code_snippets: list) -> Dict[str, Any]:
    """
    Analyze multiple AI-generated code snippets in batch
    """
    endpoint = f"{API_BASE_URL}/batch-analyze-ai-code"
    
    try:
        response = requests.post(endpoint, json=code_snippets)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Batch API request failed: {e}"}

def print_analysis_result(result: Dict[str, Any], title: str = "Analysis Result"):
    """
    Pretty print analysis results
    """
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print(f"{'='*60}")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"🔒 Safety Score: {result['safety_score']}")
    print(f"🚨 Safety Status: {result['safety_status']}")
    print(f"📋 Total Issues: {result['total_issues']}")
    print(f"💡 Explanation: {result['explanation']}")
    print(f"🎯 Recommendation: {result['recommendation']}")
    
    if result['issues']:
        print(f"\n⚠️  DETECTED ISSUES:")
        for i, issue in enumerate(result['issues'], 1):
            print(f"  {i}. [{issue['risk_level']}] Line {issue.get('line_number', 'N/A')}")
            print(f"     📝 {issue['description']}")
            if issue.get('suggestion'):
                print(f"     💡 {issue['suggestion']}")
    else:
        print("\n✅ No security issues detected!")

def demo_dangerous_code_examples():
    """
    Demonstrate the API with various dangerous code examples
    """
    print("🚀 AI FIREWALL API DEMONSTRATION")
    print("Testing various dangerous code patterns...")
    
    # Example 1: SQL Injection Risk
    sql_injection_code = '''
import sqlite3
user_id = request.args.get('id')
query = f"DELETE FROM users WHERE id = {user_id}"
cursor.execute(query)
'''
    
    result = analyze_single_ai_code(
        sql_injection_code, 
        context="AI suggested this for user deletion functionality"
    )
    print_analysis_result(result, "SQL Injection Risk Example")
    
    # Example 2: Production Database Access
    prod_db_code = '''
import psycopg2
conn = psycopg2.connect(
    host="prod-server.company.com",
    database="production_db",
    user="admin"
)
cursor = conn.cursor()
cursor.execute("DROP TABLE user_sessions")
'''
    
    result = analyze_single_ai_code(
        prod_db_code,
        context="AI suggested this for cleaning up sessions"
    )
    print_analysis_result(result, "Production Database Access Example")
    
    # Example 3: Mass Data Creation
    bulk_creation_code = '''
from django.contrib.auth.models import User

# Create fake users for testing
for i in range(50000):
    User.objects.create_user(
        username=f"fake_user_{i}",
        email=f"fake{i}@test.com",
        password="password123"
    )
'''
    
    result = analyze_single_ai_code(
        bulk_creation_code,
        context="AI suggested this for generating test data"
    )
    print_analysis_result(result, "Mass User Creation Example")
    
    # Example 4: System Command Execution
    system_command_code = '''
import os
import subprocess

def cleanup_files(pattern):
    # AI suggested this for file cleanup
    os.system(f"rm -rf {pattern}")
    subprocess.run(f"find /tmp -name '{pattern}' -delete", shell=True)
'''
    
    result = analyze_single_ai_code(
        system_command_code,
        context="AI suggested this for file cleanup automation"
    )
    print_analysis_result(result, "System Command Execution Example")

def demo_batch_analysis():
    """
    Demonstrate batch analysis of multiple code snippets
    """
    print(f"\n{'='*60}")
    print("🔄 BATCH ANALYSIS DEMONSTRATION")
    print(f"{'='*60}")
    
    code_snippets = [
        {
            "code": "eval(user_input)",
            "language": "python",
            "context": "AI suggested dynamic evaluation"
        },
        {
            "code": "cursor.execute('DELETE FROM logs')",
            "language": "python", 
            "context": "AI suggested log cleanup"
        },
        {
            "code": "for i in range(10000): create_record(i)",
            "language": "python",
            "context": "AI suggested bulk record creation"
        },
        {
            "code": "import json\ndata = json.loads(file_content)",
            "language": "python",
            "context": "AI suggested JSON parsing"
        }
    ]
    
    result = analyze_batch_ai_code(code_snippets)
    
    if "error" in result:
        print(f"❌ Batch analysis failed: {result['error']}")
        return
    
    print(f"📊 Analyzed {result['total_analyzed']} code snippets")
    print(f"🔧 Analyzer Version: {result['analyzer_version']}")
    
    for i, analysis in enumerate(result['batch_results'], 1):
        print_analysis_result(analysis, f"Snippet {i} Analysis")

def demo_safe_code():
    """
    Demonstrate analysis of safe code
    """
    safe_code = '''
import json
from datetime import datetime
from typing import List, Optional

def calculate_user_stats(users: List[dict]) -> dict:
    """Calculate safe user statistics"""
    if not users:
        return {"total": 0, "average_age": 0}
    
    total_users = len(users)
    ages = [user.get("age", 0) for user in users if user.get("age")]
    average_age = sum(ages) / len(ages) if ages else 0
    
    return {
        "total": total_users,
        "average_age": round(average_age, 2),
        "calculated_at": datetime.now().isoformat()
    }

# Safe database query with parameterized statements
def get_user_safely(user_id: int):
    query = "SELECT * FROM users WHERE id = ? AND active = ?"
    return cursor.execute(query, (user_id, True)).fetchone()
'''
    
    result = analyze_single_ai_code(
        safe_code,
        context="AI suggested safe user statistics calculation"
    )
    print_analysis_result(result, "Safe Code Example")

def main():
    """
    Main demonstration function
    """
    print("🛡️  AI FIREWALL - ADVANCED CODE SECURITY ANALYSIS")
    print("Testing the AI Code Security Analyzer API endpoints...")
    
    # Check if API is running
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ API is running and healthy!")
        else:
            print("⚠️  API health check failed")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Make sure the backend is running on http://localhost:8000")
        print("Run: ./start.sh or python backend/main.py")
        return
    
    # Run demonstrations
    demo_dangerous_code_examples()
    demo_batch_analysis()
    demo_safe_code()
    
    print(f"\n{'='*60}")
    print("✅ API DEMONSTRATION COMPLETED!")
    print("The AI Firewall is successfully detecting security issues in AI-generated code.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 