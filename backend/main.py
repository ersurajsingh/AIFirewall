from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 