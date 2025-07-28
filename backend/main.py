from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from security_analyzer import AICodeSecurityAnalyzer, analyze_ai_code

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 