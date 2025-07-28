# 🛡️ AI Firewall Policy Engine

A flexible, configuration-driven security policy system that allows developers to define custom "forbidden" actions and automatically enforce organizational security policies on code analysis.

## 🎯 Overview

The Policy Engine extends the AI Firewall with a comprehensive rule-based system that can detect and prevent:

- **Production environment modifications**
- **Access to sensitive directories**  
- **Usage of dangerous libraries**
- **Database credential exposure**
- **Destructive file operations**
- **Code injection risks**
- **Custom organizational policies**

## ✨ Key Features

### 🔧 **Configurable Rule Engine**
- **YAML/JSON configuration** for easy policy management
- **Runtime policy loading** without service restart
- **Custom pattern matching** with regex support
- **AST-based code analysis** for deep inspection
- **Context-aware rules** (environment, file type, etc.)

### 🎨 **Flexible Policy Types**
- **Pattern-based rules** using regular expressions
- **Import restrictions** for dangerous libraries
- **Function call monitoring** for risky operations
- **Directory access controls** for sensitive paths
- **Environment variable protection** for production configs
- **File operation restrictions** for destructive commands

### 📊 **Advanced Analysis**
- **Risk level assessment** (LOW, MEDIUM, HIGH, CRITICAL)
- **Violation tracking** with detailed reporting
- **Policy categories** for organized rule management
- **Action controls** (WARN, BLOCK, LOG)
- **Exception handling** for allowed patterns

## 🚀 Configuration Format

### **YAML Configuration Example**

```yaml
global_settings:
  strict_mode: false
  log_violations: true
  auto_block_critical: true
  environment: "development"

policies:
  prod_env_modification:
    name: "Production Environment Modification"
    description: "Prevents modification of production environment variables"
    severity: "critical"
    action: "block"
    enabled: true
    category: "environment"
    forbidden_env_vars:
      - "PROD_*"
      - "PRODUCTION_*"
      - "*_PROD"
    patterns:
      - "os\\.environ\\[['\"]PROD"
      - "export.*PROD"
    allowed_exceptions:
      - "PROD_LOG_LEVEL"
    context_conditions:
      environment: ["production", "staging"]

  dangerous_libraries:
    name: "Dangerous Library Usage"
    description: "Prevents usage of potentially dangerous libraries"
    severity: "high"
    action: "warn"
    enabled: true
    category: "imports"
    forbidden_imports:
      - "pickle"
      - "marshal"
      - "eval"
    patterns:
      - "import\\s+pickle"
      - "subprocess\\.call.*shell=True"
    suggestion: "Use safer alternatives like json for serialization"
```

### **JSON Configuration Example**

```json
{
  "global_settings": {
    "strict_mode": false,
    "environment": "development"
  },
  "policies": {
    "secret_exposure": {
      "name": "API Key and Secret Exposure",
      "severity": "critical",
      "action": "block",
      "patterns": [
        "api_key\\s*=\\s*['\"][A-Za-z0-9]{20,}['\"]",
        "sk-[A-Za-z0-9]{20,}"
      ]
    }
  }
}
```

## 📋 Policy Rule Structure

### **Core Fields**
- `id`: Unique identifier for the rule
- `name`: Human-readable rule name
- `description`: Detailed explanation of what the rule prevents
- `severity`: Risk level (`low`, `medium`, `high`, `critical`)
- `action`: Response action (`warn`, `block`, `log`)
- `enabled`: Whether the rule is active

### **Detection Methods**
- `patterns`: Regular expressions for text matching
- `forbidden_imports`: Python import restrictions
- `forbidden_functions`: Function call restrictions
- `forbidden_directories`: File/directory access restrictions
- `forbidden_env_vars`: Environment variable restrictions
- `forbidden_file_operations`: File operation restrictions

### **Advanced Options**
- `allowed_exceptions`: Patterns that bypass the rule
- `context_conditions`: Environment/file-specific conditions
- `custom_ast_checks`: Custom AST analysis rules
- `category`: Organization category for the rule
- `tags`: Metadata tags for filtering

## 🔧 API Endpoints

### **Analysis Endpoints**

#### `POST /analyze-with-policies`
Analyze code against configured policies.

**Request:**
```json
{
  "code": "os.environ['PROD_API_KEY'] = 'secret'",
  "file_path": "config.py",
  "config_path": "policies/custom.yaml",
  "context": {"environment": "production"}
}
```

**Response:**
```json
{
  "violations": [
    {
      "rule_id": "prod_env_modification",
      "rule_name": "Production Environment Modification",
      "severity": "critical",
      "action": "block",
      "description": "Prevents modification of production environment variables",
      "line_number": 1,
      "matched_content": "os.environ['PROD_API_KEY']",
      "suggestion": "Use environment-specific configuration files"
    }
  ],
  "total_violations": 1,
  "risk_level": "CRITICAL",
  "blocked": true,
  "summary": {
    "critical": 1,
    "high": 0,
    "medium": 0,
    "low": 0
  }
}
```

### **Policy Management Endpoints**

#### `GET /policies`
Get all configured policies.

#### `GET /policies/{rule_id}`
Get details of a specific policy.

#### `POST /policies`
Create a new policy rule.

#### `PUT /policies/{rule_id}/enable`
Enable a policy rule.

#### `PUT /policies/{rule_id}/disable`
Disable a policy rule.

#### `DELETE /policies/{rule_id}`
Delete a policy rule.

### **Reporting Endpoints**

#### `GET /policy-violations/report`
Get comprehensive violations report.

#### `GET /policy-violations/by-severity/{severity}`
Get violations filtered by severity.

#### `GET /policy-violations/by-category/{category}`
Get violations filtered by category.

### **Configuration Management**

#### `POST /policies/export`
Export current policy configuration.

#### `POST /policies/import`
Import policy configuration from content.

## 💻 Usage Examples

### **Python Direct Usage**

```python
from backend.policy_engine import PolicyEngine

# Load policies from configuration
engine = PolicyEngine("policies/security_policies.yaml")

# Analyze code
code = '''
import os
os.environ["PROD_DATABASE_URL"] = "postgresql://user:pass@prod/db"
'''

violations = engine.analyze_code(
    code=code,
    file_path="config/production.py",
    context={"environment": "production"}
)

for violation in violations:
    print(f"[{violation.severity.value}] {violation.description}")
    if violation.action.value == "block":
        print("🚫 CODE EXECUTION BLOCKED")
```

### **API Usage with curl**

```bash
# Analyze code with policies
curl -X POST http://localhost:8000/analyze-with-policies \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import pickle\ndata = pickle.loads(user_input)",
    "file_path": "utils/serialization.py"
  }'

# Get all policies
curl http://localhost:8000/policies

# Create custom policy
curl -X POST http://localhost:8000/policies \
  -H "Content-Type: application/json" \
  -d '{
    "rule_id": "my_custom_rule",
    "name": "Custom Security Rule",
    "description": "Prevents usage of dangerous patterns",
    "severity": "high",
    "action": "warn",
    "patterns": ["dangerous_function\\("]
  }'
```

### **API Usage with Python requests**

```python
import requests

# Analyze dangerous code
response = requests.post("http://localhost:8000/analyze-with-policies", json={
    "code": """
import subprocess
subprocess.call("rm -rf /", shell=True)  # Extremely dangerous!
""",
    "context": {"environment": "production"}
})

result = response.json()
if result["blocked"]:
    print("🚫 Code execution prevented by policy engine!")

for violation in result["violations"]:
    print(f"⚠️  {violation['rule_name']}: {violation['description']}")
```

## 🎯 Built-in Policy Categories

### **Environment Protection**
- Production environment variable modification
- Staging environment access controls
- Development-only library usage

### **Credential Security**
- Database credential exposure
- API key hardcoding detection
- Secret token scanning

### **File System Security**
- Sensitive directory access prevention
- Destructive file operation controls
- Temporary file security

### **Code Injection Prevention**
- Dynamic code execution detection
- Unsafe deserialization prevention
- Input validation enforcement

### **Network Security**
- External request monitoring
- Unsafe SSL configuration detection
- Suspicious network activity

### **Cryptographic Security**
- Weak algorithm detection
- Poor random number generation
- Deprecated cryptographic practices

## 🔧 Creating Custom Policies

### **Example: Preventing Test Data in Production**

```yaml
test_data_in_production:
  name: "Test Data in Production"
  description: "Prevents creation of test data in production environment"
  severity: "high"
  action: "block"
  enabled: true
  category: "data-integrity"
  patterns:
    - "create_test_.*"
    - "generate_fake_.*"
    - "FactoryBot\\.create"
  context_conditions:
    environment: ["production"]
  suggestion: "Use production-appropriate data sources"
```

### **Example: Database Query Monitoring**

```yaml
unsafe_database_queries:
  name: "Unsafe Database Queries"
  description: "Detects potentially unsafe database operations"
  severity: "medium"
  action: "warn"
  enabled: true
  category: "database"
  patterns:
    - "SELECT \\* FROM \\w+ WHERE.*=.*\\+.*"  # SQL injection risk
    - "cursor\\.execute\\(.*\\%.*\\)"        # String formatting
  forbidden_functions:
    - "cursor.execute"
  allowed_exceptions:
    - "cursor.execute.*\\?.*"  # Parameterized queries OK
  suggestion: "Use parameterized queries to prevent SQL injection"
```

## 🧪 Testing

### **Run Policy Engine Tests**

```bash
# Test policy engine directly
python3 test_policy_engine.py

# Test via API (requires backend running)
python3 api_policy_example.py

# Start backend with policies
./start.sh
```

### **Test Configuration**

Create a test configuration file:

```yaml
# test_policies.yaml
global_settings:
  strict_mode: true
  environment: "testing"

policies:
  test_only_rule:
    name: "Test Only Rule"
    description: "Rule for testing purposes"
    severity: "low"
    action: "log"
    patterns:
      - "test_pattern_.*"
```

```python
# Test with custom config
from backend.policy_engine import PolicyEngine

engine = PolicyEngine("test_policies.yaml")
violations = engine.analyze_code("test_pattern_detected()")
```

## 📊 Monitoring and Reporting

### **Violation Reports**

The policy engine provides comprehensive reporting:

```python
# Generate violation report
report = engine.generate_violation_report()

print(f"Total violations: {report['summary']['total_violations']}")
print(f"Critical: {report['summary']['critical']}")
print(f"By category: {report['violations_by_category']}")
print(f"By rule: {report['violations_by_rule']}")
```

### **Real-time Monitoring**

```python
# Get violations by severity
critical_violations = engine.get_violations_by_severity(PolicySeverity.CRITICAL)

# Get violations by category
credential_violations = engine.get_violations_by_category("credentials")

# Monitor specific rules
for violation in engine.violation_history:
    if violation.action == PolicyAction.BLOCK:
        alert_security_team(violation)
```

## 🔄 Integration Examples

### **CI/CD Pipeline Integration**

```yaml
# .github/workflows/security-check.yml
name: Security Policy Check
on: [push, pull_request]

jobs:
  security-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Policy Engine
        run: |
          python -c "
          from backend.policy_engine import PolicyEngine
          import sys
          
          engine = PolicyEngine('policies/ci_policies.yaml')
          
          # Check all Python files
          import glob
          for file in glob.glob('**/*.py', recursive=True):
              with open(file, 'r') as f:
                  code = f.read()
              violations = engine.analyze_code(code, file)
              
              critical = [v for v in violations if v.severity.value == 'critical']
              if critical:
                  print(f'❌ Critical violations in {file}')
                  sys.exit(1)
          
          print('✅ No critical policy violations found')
          "
```

### **Pre-commit Hook**

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run policy engine on staged files
python3 -c "
from backend.policy_engine import PolicyEngine
import subprocess
import sys

engine = PolicyEngine()

# Get staged Python files
result = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'], 
                       capture_output=True, text=True)
files = [f for f in result.stdout.strip().split('\n') if f.endswith('.py')]

for file in files:
    try:
        with open(file, 'r') as f:
            code = f.read()
        violations = engine.analyze_code(code, file)
        
        blocking_violations = [v for v in violations if v.action.value == 'block']
        if blocking_violations:
            print(f'🚫 Policy violations in {file}:')
            for v in blocking_violations:
                print(f'  - {v.rule_name}: {v.description}')
            sys.exit(1)
    except Exception as e:
        print(f'Error analyzing {file}: {e}')

print('✅ All files pass policy checks')
"
```

## ⚙️ Advanced Configuration

### **Environment-Specific Policies**

```yaml
policies:
  strict_production_only:
    name: "Strict Production Controls"
    enabled: true
    context_conditions:
      environment: ["production"]
      file_patterns: ["*/config/*", "*/settings/*"]
    patterns:
      - "DEBUG\\s*=\\s*True"
      - "ALLOWED_HOSTS\\s*=\\s*\\[\\s*\\]"
```

### **File-Type Specific Rules**

```yaml
policies:
  django_security:
    name: "Django Security Settings"
    enabled: true
    context_conditions:
      file_patterns: ["**/settings.py", "**/config.py"]
    patterns:
      - "SECRET_KEY\\s*=\\s*['\"]\\w+['\"]"
      - "DEBUG\\s*=\\s*True"
```

### **Time-Based Restrictions**

```yaml
policies:
  business_hours_only:
    name: "Business Hours Deployments"
    enabled: true
    context_conditions:
      time_restrictions:
        allowed_hours: ["09:00-17:00"]
        timezone: "UTC"
        weekdays_only: true
```

## 🔒 Security Best Practices

### **Policy Configuration Security**
1. **Store policies in version control** for audit trails
2. **Use environment-specific configurations** for different stages
3. **Implement policy review processes** for changes
4. **Monitor policy violations** for security insights
5. **Regular policy updates** to address new threats

### **Deployment Considerations**
1. **Test policies in development** before production deployment
2. **Gradual rollout** of new strict policies
3. **Exception handling** for legitimate use cases
4. **Performance monitoring** for large codebases
5. **Backup configurations** before major changes

## 📞 Support

For questions about the Policy Engine:
- Review configuration examples in `policies/` directory
- Check test scripts for usage patterns
- Consult API documentation for endpoint details
- Monitor violation reports for policy effectiveness

The Policy Engine provides a powerful, flexible foundation for enforcing organizational security policies at the code level! 