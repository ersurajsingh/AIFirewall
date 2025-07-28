#!/usr/bin/env python3
"""
Example script demonstrating how to use the AI Firewall Policy Engine API endpoints.
"""

import requests
import json
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"

def analyze_code_with_policies(code: str, 
                              file_path: str = None,
                              config_path: str = None,
                              context: dict = None) -> Dict[str, Any]:
    """
    Analyze code using the policy engine
    """
    endpoint = f"{API_BASE_URL}/analyze-with-policies"
    
    payload = {
        "code": code,
        "file_path": file_path,
        "config_path": config_path,
        "context": context or {}
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def get_all_policies() -> Dict[str, Any]:
    """Get all configured policies"""
    endpoint = f"{API_BASE_URL}/policies"
    
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def get_policy_details(rule_id: str) -> Dict[str, Any]:
    """Get details of a specific policy"""
    endpoint = f"{API_BASE_URL}/policies/{rule_id}"
    
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def create_custom_policy(policy_data: dict) -> Dict[str, Any]:
    """Create a new custom policy"""
    endpoint = f"{API_BASE_URL}/policies"
    
    try:
        response = requests.post(endpoint, json=policy_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def enable_policy(rule_id: str) -> Dict[str, Any]:
    """Enable a policy rule"""
    endpoint = f"{API_BASE_URL}/policies/{rule_id}/enable"
    
    try:
        response = requests.put(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def disable_policy(rule_id: str) -> Dict[str, Any]:
    """Disable a policy rule"""
    endpoint = f"{API_BASE_URL}/policies/{rule_id}/disable"
    
    try:
        response = requests.put(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def get_violations_report() -> Dict[str, Any]:
    """Get comprehensive violations report"""
    endpoint = f"{API_BASE_URL}/policy-violations/report"
    
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def export_policies(output_format: str = "yaml") -> Dict[str, Any]:
    """Export policy configuration"""
    endpoint = f"{API_BASE_URL}/policies/export"
    
    try:
        response = requests.post(endpoint, params={"output_format": output_format})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def print_analysis_result(result: Dict[str, Any], title: str = "Policy Analysis"):
    """Pretty print policy analysis results"""
    print(f"\n{'='*80}")
    print(f"🔍 {title}")
    print(f"{'='*80}")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"🚨 Risk Level: {result.get('risk_level', 'UNKNOWN')}")
    print(f"📊 Total Violations: {result.get('total_violations', 0)}")
    print(f"🚫 Blocked: {'Yes' if result.get('blocked', False) else 'No'}")
    
    summary = result.get('summary', {})
    print(f"\n📈 Summary:")
    print(f"  Critical: {summary.get('critical', 0)}")
    print(f"  High: {summary.get('high', 0)}")
    print(f"  Medium: {summary.get('medium', 0)}")
    print(f"  Low: {summary.get('low', 0)}")
    
    violations = result.get('violations', [])
    if violations:
        print(f"\n⚠️  VIOLATIONS DETECTED:")
        for i, violation in enumerate(violations, 1):
            print(f"  {i}. [{violation['severity'].upper()}] {violation['rule_name']}")
            print(f"     📝 {violation['description']}")
            if violation.get('line_number'):
                print(f"     📍 Line {violation['line_number']}")
            if violation.get('matched_content'):
                print(f"     🔍 Matched: '{violation['matched_content']}'")
            if violation.get('suggestion'):
                print(f"     💡 {violation['suggestion']}")
            print(f"     🚨 Action: {violation['action']}")
            print()
    else:
        print("\n✅ No policy violations detected!")

def demo_production_environment_violation():
    """Demo production environment protection"""
    code = '''
import os

# Dangerous: Setting production environment variables
os.environ["PROD_DATABASE_URL"] = "postgresql://admin:secret@prod-server/db"
os.environ["PRODUCTION_API_KEY"] = "sk-1234567890abcdef"

# Configure production settings
prod_config = {
    "DATABASE_URL_PROD": "mysql://root:password@prod-db:3306/app",
    "REDIS_URL_PRODUCTION": "redis://prod-redis:6379/0"
}

print("Production environment configured")
'''
    
    print("🚀 DEMO: Production Environment Violation")
    print(f"Code to analyze:\n{code}")
    
    result = analyze_code_with_policies(
        code=code,
        file_path="config/production.py",
        context={"environment": "production"}
    )
    print_analysis_result(result, "Production Environment Analysis")

def demo_dangerous_libraries():
    """Demo dangerous library detection"""
    code = '''
import pickle
import marshal
import subprocess

# Dangerous: Using pickle with untrusted data
def deserialize_user_data(data):
    return pickle.loads(data)  # Security risk!

# Dangerous: subprocess with shell=True
def cleanup_files(pattern):
    subprocess.call(f"rm -rf {pattern}", shell=True)

# Dangerous: marshal with user input
def load_compiled_code(bytecode):
    return marshal.loads(bytecode)

# Process user upload
user_file = request.files['data']
user_data = deserialize_user_data(user_file.read())
'''
    
    print("\n🔍 DEMO: Dangerous Library Detection")
    print(f"Code to analyze:\n{code}")
    
    result = analyze_code_with_policies(
        code=code,
        file_path="utils/serialization.py"
    )
    print_analysis_result(result, "Dangerous Library Analysis")

def demo_api_key_exposure():
    """Demo API key and secret detection"""
    code = '''
import requests

     # Dangerous: Hardcoded API keys and secrets
     OPENAI_API_KEY = "sk-FAKE123456789abcdef123456789abcdef"
     GITHUB_TOKEN = "ghp_FAKE123456789012345678901234567890"
     SLACK_TOKEN = "slack-token-fake-example-not-real"

# Database credentials
DATABASE_CONFIG = {
    "host": "prod-server.company.com",
    "user": "admin",
    "password": "supersecret123",
    "database": "production_db"
}

# Making API calls with exposed keys
headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
response = requests.get("https://api.github.com/user", headers=headers)
'''
    
    print("\n🔐 DEMO: API Key and Secret Exposure")
    print(f"Code to analyze:\n{code}")
    
    result = analyze_code_with_policies(
        code=code,
        file_path="config/secrets.py"
    )
    print_analysis_result(result, "Secret Exposure Analysis")

def demo_destructive_operations():
    """Demo destructive file operations"""
    code = '''
import os
import shutil
import subprocess
from pathlib import Path

def dangerous_cleanup():
    # Dangerous: Mass file deletion
    os.remove("/important/config.json")
    shutil.rmtree("/user/documents")
    
    # Dangerous: Directory removal
    os.rmdir("/temp/cache")
    
    # Using pathlib for deletion
    Path("/critical/data.db").unlink()
    
    # Subprocess file operations
    subprocess.run("rm -rf /var/log/*", shell=True)
    subprocess.call(["rmdir", "/tmp/uploads"])

def format_drive():
    # Extremely dangerous
    os.system("format C: /fs:NTFS /q")
    subprocess.call("mkfs.ext4 /dev/sda1", shell=True)

# Execute cleanup
dangerous_cleanup()
format_drive()
'''
    
    print("\n💥 DEMO: Destructive File Operations")
    print(f"Code to analyze:\n{code}")
    
    result = analyze_code_with_policies(
        code=code,
        file_path="scripts/cleanup.py"
    )
    print_analysis_result(result, "Destructive Operations Analysis")

def demo_policy_management():
    """Demo policy management operations"""
    print("\n🛠️  DEMO: Policy Management")
    print("=" * 50)
    
    # Get all policies
    print("📋 Getting all policies...")
    policies = get_all_policies()
    if "error" not in policies:
        print(f"Total policies: {policies['total_rules']}")
        print(f"Enabled policies: {policies['enabled_rules']}")
        
        print("\nAvailable policies:")
        for policy_id, policy in policies['policies'].items():
            status = "✅" if policy['enabled'] else "❌"
            print(f"  {status} {policy_id}: {policy['name']} ({policy['severity']})")
    
    # Get specific policy details
    print("\n🔍 Getting details for 'prod_env_modification' policy...")
    policy_details = get_policy_details("prod_env_modification")
    if "error" not in policy_details:
        print(f"Policy: {policy_details['name']}")
        print(f"Description: {policy_details['description']}")
        print(f"Severity: {policy_details['severity']}")
        print(f"Patterns: {len(policy_details['patterns'])} defined")
    
    # Create custom policy
    print("\n🔧 Creating custom policy...")
    custom_policy = {
        "rule_id": "demo_custom_rule",
        "name": "Demo Custom Rule",
        "description": "Detects demo-specific dangerous patterns",
        "severity": "medium",
        "action": "warn",
        "enabled": True,
        "patterns": [
            "demo_dangerous_function\\(",
            "test_only_.*delete"
        ],
        "category": "demo",
        "tags": ["demo", "test"]
    }
    
    result = create_custom_policy(custom_policy)
    if "error" not in result:
        print(f"✅ Custom policy created: {result['message']}")
    else:
        print(f"❌ Failed to create policy: {result['error']}")

def demo_violations_reporting():
    """Demo violations reporting"""
    print("\n📊 DEMO: Violations Reporting")
    print("=" * 50)
    
    # Get violations report
    print("📈 Getting violations report...")
    report = get_violations_report()
    if "error" not in report:
        summary = report.get('summary', {})
        print(f"Total violations: {summary.get('total_violations', 0)}")
        print(f"Critical: {summary.get('critical', 0)}")
        print(f"High: {summary.get('high', 0)}")
        print(f"Medium: {summary.get('medium', 0)}")
        print(f"Low: {summary.get('low', 0)}")
        
        if report.get('violations_by_category'):
            print("\nViolations by category:")
            for category, violations in report['violations_by_category'].items():
                print(f"  {category}: {len(violations)} violations")

def demo_policy_export_import():
    """Demo policy export and import"""
    print("\n📤 DEMO: Policy Export/Import")
    print("=" * 50)
    
    # Export policies
    print("📤 Exporting policies to YAML...")
    export_result = export_policies("yaml")
    if "error" not in export_result:
        print(f"✅ Policies exported successfully")
        print("YAML content preview:")
        lines = export_result['content'].split('\n')[:10]
        for line in lines:
            print(f"  {line}")
        if len(export_result['content'].split('\n')) > 10:
            print("  ... (truncated)")
    else:
        print(f"❌ Export failed: {export_result['error']}")

def main():
    """Main demonstration function"""
    print("🛡️  AI FIREWALL - POLICY ENGINE API DEMONSTRATION")
    print("Testing the Policy Engine API endpoints...")
    
    # Check if API is running
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ API is running and healthy!")
        else:
            print("⚠️  API health check failed")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Make sure the backend is running:")
        print("   ./start.sh")
        print("   or")
        print("   python3 backend/main.py")
        return
    
    # Run demonstrations
    demo_production_environment_violation()
    demo_dangerous_libraries() 
    demo_api_key_exposure()
    demo_destructive_operations()
    demo_policy_management()
    demo_violations_reporting()
    demo_policy_export_import()
    
    print(f"\n{'='*80}")
    print("✅ POLICY ENGINE API DEMONSTRATION COMPLETED!")
    print("The AI Firewall Policy Engine is successfully enforcing custom security rules.")
    print(f"{'='*80}")
    
    # Usage examples
    print("\n💡 USAGE EXAMPLES:")
    print("""
# Analyze code with policies:
curl -X POST http://localhost:8000/analyze-with-policies \\
  -H "Content-Type: application/json" \\
  -d '{
    "code": "os.environ[\\"PROD_API_KEY\\"] = \\"secret\\"",
    "file_path": "config.py",
    "context": {"environment": "production"}
  }'

# Get all policies:
curl http://localhost:8000/policies

# Create custom policy:
curl -X POST http://localhost:8000/policies \\
  -H "Content-Type: application/json" \\
  -d '{
    "rule_id": "my_custom_rule",
    "name": "My Custom Rule",
    "description": "Custom security rule",
    "severity": "high",
    "action": "warn",
    "patterns": ["dangerous_pattern.*"]
  }'

# Export policies:
curl -X POST http://localhost:8000/policies/export?output_format=yaml
""")

if __name__ == "__main__":
    main() 