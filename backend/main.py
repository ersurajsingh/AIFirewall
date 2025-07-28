from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
from security_analyzer import AICodeSecurityAnalyzer, analyze_ai_code
from code_explainer import PythonCodeExplainer, explain_python_code_async, LLMProvider

app = FastAPI(title="AI Firewall", description="AI-powered code security firewall", version="1.0.0")

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 