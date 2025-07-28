from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
from security_analyzer import AICodeSecurityAnalyzer, analyze_ai_code
from code_explainer import PythonCodeExplainer, explain_python_code_async, LLMProvider
from policy_engine import PolicyEngine, PolicyRule, PolicyViolation, PolicySeverity, PolicyAction, analyze_code_with_policies

app = FastAPI(title="AI Firewall", description="AI-powered code security firewall with policy engine", version="2.0.0")

# Initialize Policy Engine
policy_engine = PolicyEngine()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeAnalysisRequest(BaseModel):
    code: str
    language: str
    file_path: Optional[str] = None

class AICodeAnalysisRequest(BaseModel):
    code: str
    language: str = "python"
    source: Optional[str] = "ai_generated"  # Track if code is AI-generated
    context: Optional[str] = None  # Additional context about the code

class CodeExplanationRequest(BaseModel):
    code: str
    provider: str = "openai"  # "openai" or "anthropic"
    detail_level: str = "intermediate"  # "beginner", "intermediate", "advanced"
    target_audience: str = "developers"  # "beginners", "developers", "students", "experts"
    api_key: Optional[str] = None  # Optional API key override

class PolicyAnalysisRequest(BaseModel):
    code: str
    file_path: Optional[str] = None
    config_path: Optional[str] = None
    context: Optional[dict] = None

class PolicyRuleRequest(BaseModel):
    rule_id: str
    name: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    action: str    # "warn", "block", "log"
    enabled: bool = True
    patterns: List[str] = []
    forbidden_imports: List[str] = []
    forbidden_functions: List[str] = []
    forbidden_directories: List[str] = []
    forbidden_env_vars: List[str] = []
    forbidden_file_operations: List[str] = []
    allowed_exceptions: List[str] = []
    context_conditions: dict = {}
    category: str = "custom"
    tags: List[str] = []

class SecurityIssue(BaseModel):
    severity: str
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

class AnalysisResponse(BaseModel):
    is_safe: bool
    issues: List[SecurityIssue]
    confidence_score: float

@app.get("/")
async def root():
    return {"message": "AI Firewall API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-firewall"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    """
    Analyze code for security vulnerabilities and potential issues
    """
    # Placeholder implementation - replace with actual AI analysis
    # This would integrate with your AI models for security analysis
    
    # Basic example analysis
    issues = []
    
    # Simple pattern matching for demo purposes
    if "eval(" in request.code:
        issues.append(SecurityIssue(
            severity="HIGH",
            message="Use of eval() function detected - potential security risk",
            suggestion="Consider using safer alternatives like ast.literal_eval()"
        ))
    
    if "exec(" in request.code:
        issues.append(SecurityIssue(
            severity="HIGH", 
            message="Use of exec() function detected - potential security risk",
            suggestion="Avoid dynamic code execution"
        ))
    
    if "import os" in request.code and "os.system(" in request.code:
        issues.append(SecurityIssue(
            severity="MEDIUM",
            message="Direct system command execution detected",
            suggestion="Use subprocess module with proper input validation"
        ))
    
    is_safe = len([i for i in issues if i.severity == "HIGH"]) == 0
    confidence_score = 0.8 if len(issues) == 0 else 0.6
    
    return AnalysisResponse(
        is_safe=is_safe,
        issues=issues,
        confidence_score=confidence_score
    )

@app.post("/analyze-ai-code")
async def analyze_ai_generated_code(request: AICodeAnalysisRequest):
    """
    Advanced analysis specifically for AI-generated code suggestions.
    Uses AST parsing and sophisticated pattern matching for security analysis.
    """
    try:
        # Use the advanced security analyzer
        analyzer = AICodeSecurityAnalyzer()
        analysis_result = analyzer.analyze_code(request.code, request.language)
        
        # Add metadata about the analysis
        analysis_result["source"] = request.source
        analysis_result["context"] = request.context
        analysis_result["analyzer_version"] = "2.0"
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/batch-analyze")
async def batch_analyze(requests: List[CodeAnalysisRequest]):
    """
    Analyze multiple code snippets in batch
    """
    results = []
    for req in requests:
        analysis = await analyze_code(req)
        results.append(analysis)
    return {"results": results}

@app.post("/batch-analyze-ai-code") 
async def batch_analyze_ai_code(requests: List[AICodeAnalysisRequest]):
    """
    Batch analysis for multiple AI-generated code snippets
    """
    try:
        analyzer = AICodeSecurityAnalyzer()
        results = []
        
        for req in requests:
            analysis_result = analyzer.analyze_code(req.code, req.language)
            analysis_result["source"] = req.source
            analysis_result["context"] = req.context
            results.append(analysis_result)
        
        return {
            "batch_results": results,
            "total_analyzed": len(results),
            "analyzer_version": "2.0"
        }
        
    except Exception as e:
                 raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@app.post("/explain-code")
async def explain_python_code_endpoint(request: CodeExplanationRequest):
    """
    Explain Python code line-by-line using OpenAI or Anthropic LLMs.
    Returns detailed explanations in markdown format.
    """
    try:
        # Validate provider
        if request.provider.lower() not in ["openai", "anthropic"]:
            raise HTTPException(status_code=400, detail="Provider must be 'openai' or 'anthropic'")
        
        # Validate detail level
        if request.detail_level not in ["beginner", "intermediate", "advanced"]:
            raise HTTPException(status_code=400, detail="Detail level must be 'beginner', 'intermediate', or 'advanced'")
        
        # Generate explanation
        explanation_markdown = await explain_python_code_async(
            code=request.code,
            provider=request.provider,
            detail_level=request.detail_level,
            target_audience=request.target_audience,
            api_key=request.api_key
        )
        
        return {
            "explanation": explanation_markdown,
            "provider_used": request.provider,
            "detail_level": request.detail_level,
            "target_audience": request.target_audience,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "status": "success"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code explanation failed: {str(e)}")

@app.post("/explain-code-simple") 
async def explain_code_simple(request: dict):
    """
    Simple endpoint for quick code explanations using default settings.
    Expects {"code": "python code here"} and returns markdown explanation.
    """
    try:
        code = request.get("code", "")
        if not code:
            raise HTTPException(status_code=400, detail="Code field is required")
            
        explanation = await explain_python_code_async(
            code=code,
            provider="openai",
            detail_level="intermediate",
            target_audience="developers"
        )
        
        return {"explanation": explanation}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code explanation failed: {str(e)}")

@app.get("/explain-demo")
async def explanation_demo():
    """
    Demo endpoint showing code explanation capabilities with sample code
    """
    sample_code = '''
def fibonacci(n):
    """Calculate fibonacci number recursively"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Calculate first 10 fibonacci numbers
for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")
'''
    
    try:
        explanation = await explain_python_code_async(
            code=sample_code,
            provider="openai", 
            detail_level="beginner",
            target_audience="students"
        )
        
        return {
            "demo_code": sample_code,
            "explanation": explanation,
            "message": "This is a demo of the code explanation feature"
        }
        
    except Exception as e:
        return {
            "demo_code": sample_code,
            "explanation": "Demo explanation not available - API key may be missing",
            "error": str(e),
            "message": "Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable to use this feature"
        }

@app.post("/analyze-with-policies")
async def analyze_code_with_policies_endpoint(request: PolicyAnalysisRequest):
    """
    Analyze code using the policy engine with custom security rules.
    Returns policy violations and suggestions.
    """
    try:
        # Use specific policy engine if config path provided
        if request.config_path:
            engine = PolicyEngine(request.config_path)
        else:
            engine = policy_engine
        
        violations = engine.analyze_code(
            code=request.code,
            file_path=request.file_path,
            context=request.context or {}
        )
        
        # Format violations for response
        formatted_violations = []
        for violation in violations:
            formatted_violations.append({
                "rule_id": violation.rule_id,
                "rule_name": violation.rule_name,
                "severity": violation.severity.value,
                "action": violation.action.value,
                "description": violation.description,
                "line_number": violation.line_number,
                "column_number": violation.column_number,
                "matched_content": violation.matched_content,
                "suggestion": violation.suggestion,
                "category": violation.policy_category
            })
        
        # Calculate risk assessment
        critical_count = len([v for v in violations if v.severity == PolicySeverity.CRITICAL])
        high_count = len([v for v in violations if v.severity == PolicySeverity.HIGH])
        
        risk_level = "LOW"
        if critical_count > 0:
            risk_level = "CRITICAL"
        elif high_count > 0:
            risk_level = "HIGH"
        elif len(violations) > 0:
            risk_level = "MEDIUM"
        
        return {
            "violations": formatted_violations,
            "total_violations": len(violations),
            "risk_level": risk_level,
            "summary": {
                "critical": critical_count,
                "high": high_count,
                "medium": len([v for v in violations if v.severity == PolicySeverity.MEDIUM]),
                "low": len([v for v in violations if v.severity == PolicySeverity.LOW])
            },
            "blocked": any(v.action == PolicyAction.BLOCK for v in violations),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy analysis failed: {str(e)}")

@app.get("/policies")
async def get_policies():
    """Get all configured policy rules"""
    policies = {}
    for rule_id, rule in policy_engine.rules.items():
        policies[rule_id] = {
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "severity": rule.severity.value,
            "action": rule.action.value,
            "enabled": rule.enabled,
            "category": rule.category,
            "tags": rule.tags
        }
    
    return {
        "policies": policies,
        "total_rules": len(policies),
        "enabled_rules": len([r for r in policy_engine.rules.values() if r.enabled]),
        "global_settings": policy_engine.global_settings
    }

@app.get("/policies/{rule_id}")
async def get_policy(rule_id: str):
    """Get details of a specific policy rule"""
    if rule_id not in policy_engine.rules:
        raise HTTPException(status_code=404, detail=f"Policy rule '{rule_id}' not found")
    
    rule = policy_engine.rules[rule_id]
    return {
        "id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "severity": rule.severity.value,
        "action": rule.action.value,
        "enabled": rule.enabled,
        "patterns": rule.patterns,
        "forbidden_imports": rule.forbidden_imports,
        "forbidden_functions": rule.forbidden_functions,
        "forbidden_directories": rule.forbidden_directories,
        "forbidden_env_vars": rule.forbidden_env_vars,
        "forbidden_file_operations": rule.forbidden_file_operations,
        "allowed_exceptions": rule.allowed_exceptions,
        "context_conditions": rule.context_conditions,
        "category": rule.category,
        "tags": rule.tags
    }

@app.post("/policies")
async def create_policy(rule_request: PolicyRuleRequest):
    """Create a new policy rule"""
    try:
        rule = PolicyRule(
            id=rule_request.rule_id,
            name=rule_request.name,
            description=rule_request.description,
            severity=PolicySeverity(rule_request.severity),
            action=PolicyAction(rule_request.action),
            enabled=rule_request.enabled,
            patterns=rule_request.patterns,
            forbidden_imports=rule_request.forbidden_imports,
            forbidden_functions=rule_request.forbidden_functions,
            forbidden_directories=rule_request.forbidden_directories,
            forbidden_env_vars=rule_request.forbidden_env_vars,
            forbidden_file_operations=rule_request.forbidden_file_operations,
            allowed_exceptions=rule_request.allowed_exceptions,
            context_conditions=rule_request.context_conditions,
            category=rule_request.category,
            tags=rule_request.tags
        )
        
        policy_engine.add_rule(rule)
        
        return {
            "message": f"Policy rule '{rule_request.rule_id}' created successfully",
            "rule_id": rule_request.rule_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create policy: {str(e)}")

@app.put("/policies/{rule_id}/enable")
async def enable_policy(rule_id: str):
    """Enable a policy rule"""
    if policy_engine.enable_rule(rule_id):
        return {"message": f"Policy rule '{rule_id}' enabled"}
    else:
        raise HTTPException(status_code=404, detail=f"Policy rule '{rule_id}' not found")

@app.put("/policies/{rule_id}/disable")
async def disable_policy(rule_id: str):
    """Disable a policy rule"""
    if policy_engine.disable_rule(rule_id):
        return {"message": f"Policy rule '{rule_id}' disabled"}
    else:
        raise HTTPException(status_code=404, detail=f"Policy rule '{rule_id}' not found")

@app.delete("/policies/{rule_id}")
async def delete_policy(rule_id: str):
    """Delete a policy rule"""
    if policy_engine.remove_rule(rule_id):
        return {"message": f"Policy rule '{rule_id}' deleted"}
    else:
        raise HTTPException(status_code=404, detail=f"Policy rule '{rule_id}' not found")

@app.get("/policy-violations/report")
async def get_violations_report():
    """Get comprehensive policy violations report"""
    return policy_engine.generate_violation_report()

@app.get("/policy-violations/by-severity/{severity}")
async def get_violations_by_severity(severity: str):
    """Get violations filtered by severity level"""
    try:
        severity_enum = PolicySeverity(severity.lower())
        violations = policy_engine.get_violations_by_severity(severity_enum)
        
        return {
            "severity": severity,
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "rule_name": v.rule_name,
                    "description": v.description,
                    "line_number": v.line_number,
                    "matched_content": v.matched_content
                }
                for v in violations
            ],
            "count": len(violations)
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid severity level. Use: low, medium, high, critical")

@app.get("/policy-violations/by-category/{category}")
async def get_violations_by_category(category: str):
    """Get violations filtered by policy category"""
    violations = policy_engine.get_violations_by_category(category)
    
    return {
        "category": category,
        "violations": [
            {
                "rule_id": v.rule_id,
                "rule_name": v.rule_name,
                "description": v.description,
                "line_number": v.line_number,
                "matched_content": v.matched_content
            }
            for v in violations
        ],
        "count": len(violations)
    }

@app.post("/policies/export")
async def export_policies(output_format: str = "yaml"):
    """Export current policy configuration"""
    try:
        import tempfile
        import os
        
        if output_format not in ["yaml", "json"]:
            raise HTTPException(status_code=400, detail="Format must be 'yaml' or 'json'")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{output_format}', delete=False) as f:
            temp_path = f.name
        
        policy_engine.export_config(temp_path)
        
        # Read the exported content
        with open(temp_path, 'r') as f:
            content = f.read()
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return {
            "format": output_format,
            "content": content,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.post("/policies/import")
async def import_policies(config_content: str, config_format: str = "yaml"):
    """Import policy configuration from content"""
    try:
        import tempfile
        import os
        
        if config_format not in ["yaml", "json"]:
            raise HTTPException(status_code=400, detail="Format must be 'yaml' or 'json'")
        
        # Create temporary file with the content
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{config_format}', delete=False) as f:
            f.write(config_content)
            temp_path = f.name
        
        # Load policies from temporary file
        policy_engine.load_policies(temp_path)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return {
            "message": "Policies imported successfully",
            "total_rules": len(policy_engine.rules),
            "enabled_rules": len([r for r in policy_engine.rules.values() if r.enabled])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 