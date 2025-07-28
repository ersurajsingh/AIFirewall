# AI Code Security Analyzer

A sophisticated middleware class for analyzing AI-generated code suggestions using AST parsing and pattern matching to detect potentially dangerous security vulnerabilities.

## 🎯 Overview

The `AICodeSecurityAnalyzer` is designed specifically to evaluate AI-generated code suggestions before execution, providing detailed security analysis and risk assessment. It combines multiple analysis techniques:

- **AST (Abstract Syntax Tree) Parsing**: Deep code structure analysis
- **Pattern Matching**: Regular expression-based detection
- **Risk Scoring**: Quantitative safety assessment
- **Context-Aware Detection**: Production environment indicators

## 🔍 Detected Security Patterns

### Critical Risk Patterns
- **SQL Injection Vulnerabilities**
  - `DROP TABLE` statements
  - `DELETE FROM` without `WHERE` clauses
  - `TRUNCATE TABLE` operations
  - `ALTER TABLE DROP` statements

- **Dynamic Code Execution**
  - `eval()` function calls
  - `exec()` function calls
  - Dynamic string evaluation

### High Risk Patterns
- **System Command Execution**
  - `os.system()` calls
  - `subprocess` with `shell=True`
  - Unvalidated command execution

- **Production Database Access**
  - Connection strings with production indicators
  - Hardcoded production hostnames
  - Production database operations

- **File System Operations**
  - Mass file deletion (`os.remove`, `shutil.rmtree`)
  - Uncontrolled file operations

### Medium Risk Patterns
- **Mass Data Operations**
  - Bulk user creation (>100 iterations)
  - Large-scale data insertion
  - Uncontrolled loop operations

- **External Network Requests**
  - Unvalidated HTTP requests
  - External API calls without timeout
  - File downloads from unknown sources

## 📊 Safety Scoring System

The analyzer calculates a safety score from 0.0 to 1.0:

- **1.0 - 0.8**: `SAFE` - No significant security issues
- **0.8 - 0.6**: `MODERATE_RISK` - Some issues detected, review recommended
- **0.6 - 0.3**: `HIGH_RISK` - Serious issues, immediate review required
- **0.3 - 0.0**: `CRITICAL_RISK` - DO NOT EXECUTE without security review

### Risk Weights
- **Critical Issues**: 1.0 points each
- **High Risk Issues**: 0.6 points each
- **Medium Risk Issues**: 0.3 points each
- **Low Risk Issues**: 0.1 points each

## 🚀 Usage Examples

### Basic Analysis

```python
from backend.security_analyzer import AICodeSecurityAnalyzer

analyzer = AICodeSecurityAnalyzer()
result = analyzer.analyze_code("""
import os
user_input = get_user_input()
os.system(f"rm -rf {user_input}")
""", language="python")

print(f"Safety Score: {result['safety_score']}")
print(f"Status: {result['safety_status']}")
```

### API Integration

```python
import requests

# Analyze single code snippet
response = requests.post("http://localhost:8000/analyze-ai-code", json={
    "code": "eval(user_input)",
    "language": "python",
    "context": "AI suggested dynamic evaluation"
})

analysis = response.json()
print(f"Safety Score: {analysis['safety_score']}")
```

### Batch Analysis

```python
code_snippets = [
    {
        "code": "cursor.execute('DELETE FROM users')",
        "language": "python",
        "context": "AI suggested user cleanup"
    },
    {
        "code": "for i in range(10000): create_user(i)",
        "language": "python", 
        "context": "AI suggested bulk user creation"
    }
]

response = requests.post("http://localhost:8000/batch-analyze-ai-code", json=code_snippets)
results = response.json()
```

## 📋 API Response Format

```json
{
    "safety_score": 0.4,
    "safety_status": "HIGH_RISK",
    "total_issues": 2,
    "issues": [
        {
            "pattern": "sql_delete_without_where",
            "risk_level": "CRITICAL",
            "description": "DELETE without WHERE clause - can delete all records",
            "line_number": 3,
            "column_number": null,
            "suggestion": "Always include WHERE clause in DELETE statements"
        }
    ],
    "explanation": "Code poses high security risk (score: 0.4) with 2 issue(s). Immediate review required.",
    "recommendation": "Require security team approval before execution. Implement additional safeguards.",
    "analysis_timestamp": "2024-01-15T10:30:45Z",
    "source": "ai_generated",
    "context": "AI suggested user cleanup",
    "analyzer_version": "2.0"
}
```

## 🔧 Configuration Options

### Production Indicators
The analyzer detects potential production database access by looking for these indicators:
- `prod`, `production`, `live`, `master`
- `main_db`, `prod_db`, `production_db`, `live_db`

### Customizing Detection Patterns
You can extend the analyzer by modifying the `dangerous_patterns` dictionary:

```python
analyzer = AICodeSecurityAnalyzer()
analyzer.dangerous_patterns['custom_pattern'] = {
    'patterns': [r'dangerous_function\s*\('],
    'risk_level': RiskLevel.HIGH,
    'description': 'Custom dangerous function detected'
}
```

## 🧪 Testing

### Run Local Tests
```bash
# Test the analyzer directly
python test_security_analyzer.py

# Test via API (requires backend running)
python backend/api_example.py
```

### Example Test Cases

1. **SQL Injection Detection**
```python
dangerous_code = '''
user_id = request.args.get('id')
cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
'''
```

2. **Production Database Access**
```python
dangerous_code = '''
conn = psycopg2.connect(host="prod-server.com", database="production_db")
cursor.execute("DROP TABLE sessions")
'''
```

3. **Mass Operations**
```python
dangerous_code = '''
for i in range(50000):
    User.objects.create(username=f"fake_user_{i}")
'''
```

## 🛡️ Integration with AI Tools

### VS Code Extension Integration
The security analyzer integrates with the AI Firewall VS Code extension to provide real-time analysis of AI-generated code suggestions.

### CI/CD Pipeline Integration
```yaml
# Example GitHub Actions workflow
- name: Analyze AI-Generated Code
  run: |
    python -c "
    from backend.security_analyzer import analyze_ai_code
    result = analyze_ai_code(open('ai_generated_code.py').read())
    if result['safety_score'] < 0.6:
        exit(1)
    "
```

## 🚨 Security Recommendations

### For AI-Generated Code
1. **Always analyze** AI suggestions before execution
2. **Never execute** code with `CRITICAL_RISK` status
3. **Review carefully** any code with production database indicators
4. **Limit batch sizes** for mass operations
5. **Use parameterized queries** for database operations

### Best Practices
- Set up automated analysis in your development workflow
- Configure alerts for critical security issues
- Maintain a whitelist of approved patterns
- Regular security team reviews for high-risk code
- Log all analysis results for audit trails

## 🔄 Future Enhancements

- [ ] Machine learning-based pattern detection
- [ ] Support for additional programming languages (JavaScript, Java, C#)
- [ ] Integration with external security scanning tools
- [ ] Custom rule engine for organization-specific patterns
- [ ] Real-time collaboration features for security reviews
- [ ] Historical analysis and trend reporting

## 📞 Support

For security-related questions or to report vulnerabilities:
- Email: security@aifirewall.dev
- Create an issue in the GitHub repository
- Security disclosure: Follow responsible disclosure practices 