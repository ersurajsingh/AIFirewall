import ast
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SecurityIssue:
    pattern: str
    risk_level: RiskLevel
    description: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    suggestion: Optional[str] = None


class AICodeSecurityAnalyzer:
    """
    Middleware class for analyzing AI-generated code suggestions for security vulnerabilities.
    Uses AST parsing and pattern matching to detect dangerous code patterns.
    """
    
    def __init__(self):
        self.dangerous_patterns = self._init_dangerous_patterns()
        self.production_indicators = [
            'prod', 'production', 'live', 'master', 'main_db',
            'prod_db', 'production_db', 'live_db'
        ]
        
    def _init_dangerous_patterns(self) -> Dict[str, Dict]:
        """Initialize patterns for dangerous code detection"""
        return {
            # SQL Injection and Database Operations
            'sql_drop_table': {
                'patterns': [r'DROP\s+TABLE', r'drop\s+table'],
                'risk_level': RiskLevel.CRITICAL,
                'description': 'DROP TABLE statement detected - can destroy data permanently'
            },
            'sql_delete_without_where': {
                'patterns': [
                    r'DELETE\s+FROM\s+\w+(?!\s+WHERE)', 
                    r'delete\s+from\s+\w+(?!\s+where)'
                ],
                'risk_level': RiskLevel.CRITICAL,
                'description': 'DELETE without WHERE clause - can delete all records'
            },
            'sql_truncate': {
                'patterns': [r'TRUNCATE\s+TABLE', r'truncate\s+table'],
                'risk_level': RiskLevel.HIGH,
                'description': 'TRUNCATE TABLE statement detected'
            },
            'sql_alter_drop': {
                'patterns': [r'ALTER\s+TABLE.*DROP', r'alter\s+table.*drop'],
                'risk_level': RiskLevel.HIGH,
                'description': 'ALTER TABLE DROP statement detected'
            },
            
            # Mass Operations
            'bulk_user_creation': {
                'patterns': [
                    r'for.*range\(\s*\d{3,}\s*\).*user',
                    r'while.*user.*create',
                    r'bulk_create.*user'
                ],
                'risk_level': RiskLevel.MEDIUM,
                'description': 'Mass user creation detected'
            },
            'bulk_data_insertion': {
                'patterns': [
                    r'for.*range\(\s*\d{3,}\s*\).*insert',
                    r'INSERT.*VALUES.*\(',
                    r'executemany'
                ],
                'risk_level': RiskLevel.MEDIUM,
                'description': 'Bulk data insertion operation detected'
            },
            
            # Code Execution Risks
            'eval_exec': {
                'patterns': [r'\beval\s*\(', r'\bexec\s*\('],
                'risk_level': RiskLevel.CRITICAL,
                'description': 'Dynamic code execution (eval/exec) detected'
            },
            'system_commands': {
                'patterns': [
                    r'os\.system\s*\(',
                    r'subprocess\.call',
                    r'subprocess\.run',
                    r'shell=True'
                ],
                'risk_level': RiskLevel.HIGH,
                'description': 'System command execution detected'
            },
            
            # File Operations
            'file_deletion': {
                'patterns': [
                    r'os\.remove\s*\(',
                    r'os\.unlink\s*\(',
                    r'shutil\.rmtree\s*\(',
                    r'pathlib.*unlink\s*\('
                ],
                'risk_level': RiskLevel.HIGH,
                'description': 'File deletion operation detected'
            },
            
            # Network Operations
            'external_requests': {
                'patterns': [
                    r'requests\.(get|post|put|delete)',
                    r'urllib\.request',
                    r'http\.client'
                ],
                'risk_level': RiskLevel.MEDIUM,
                'description': 'External network request detected'
            }
        }
    
    def analyze_code(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """
        Main method to analyze AI-generated code for security issues.
        
        Args:
            code: The code string to analyze
            language: Programming language (currently supports 'python')
            
        Returns:
            JSON object with safety score and detailed analysis
        """
        issues = []
        
        # Perform string-based pattern matching
        string_issues = self._analyze_string_patterns(code)
        issues.extend(string_issues)
        
        # Perform AST-based analysis for Python code
        if language.lower() == 'python':
            ast_issues = self._analyze_python_ast(code)
            issues.extend(ast_issues)
        
        # Check for production database indicators
        prod_issues = self._check_production_indicators(code)
        issues.extend(prod_issues)
        
        # Calculate safety score
        safety_score = self._calculate_safety_score(issues)
        
        # Generate response
        return self._generate_response(safety_score, issues)
    
    def _analyze_string_patterns(self, code: str) -> List[SecurityIssue]:
        """Analyze code using string pattern matching"""
        issues = []
        lines = code.split('\n')
        
        for pattern_name, pattern_config in self.dangerous_patterns.items():
            for pattern in pattern_config['patterns']:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        issue = SecurityIssue(
                            pattern=pattern_name,
                            risk_level=pattern_config['risk_level'],
                            description=pattern_config['description'],
                            line_number=line_num,
                            suggestion=self._get_suggestion(pattern_name)
                        )
                        issues.append(issue)
        
        return issues
    
    def _analyze_python_ast(self, code: str) -> List[SecurityIssue]:
        """Analyze Python code using AST parsing"""
        issues = []
        
        try:
            tree = ast.parse(code)
            visitor = SecurityASTVisitor()
            visitor.visit(tree)
            issues.extend(visitor.issues)
        except SyntaxError:
            # If code has syntax errors, we'll rely on string analysis only
            pass
        except Exception as e:
            # Log error but continue with string analysis
            print(f"AST analysis error: {e}")
        
        return issues
    
    def _check_production_indicators(self, code: str) -> List[SecurityIssue]:
        """Check for production database connection indicators"""
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for indicator in self.production_indicators:
                if indicator in line.lower():
                    # Additional context checks
                    if any(keyword in line.lower() for keyword in ['connect', 'database', 'db', 'host', 'url']):
                        issue = SecurityIssue(
                            pattern='production_db_access',
                            risk_level=RiskLevel.HIGH,
                            description=f'Potential production database access detected: "{indicator}"',
                            line_number=line_num,
                            suggestion='Use development/staging databases for testing and AI-generated code'
                        )
                        issues.append(issue)
        
        return issues
    
    def _calculate_safety_score(self, issues: List[SecurityIssue]) -> float:
        """Calculate safety score based on detected issues"""
        if not issues:
            return 1.0
        
        # Weight factors for different risk levels
        risk_weights = {
            RiskLevel.LOW: 0.1,
            RiskLevel.MEDIUM: 0.3,
            RiskLevel.HIGH: 0.6,
            RiskLevel.CRITICAL: 1.0
        }
        
        # Calculate total risk score
        total_risk = sum(risk_weights[issue.risk_level] for issue in issues)
        
        # Normalize to 0-1 scale (lower is more dangerous)
        # Max risk assumption: 5 critical issues = 0 safety
        max_risk = 5.0
        safety_score = max(0.0, 1.0 - (total_risk / max_risk))
        
        return round(safety_score, 3)
    
    def _get_suggestion(self, pattern_name: str) -> str:
        """Get security suggestions for specific patterns"""
        suggestions = {
            'sql_drop_table': 'Use DROP TABLE with explicit WHERE conditions and backups',
            'sql_delete_without_where': 'Always include WHERE clause in DELETE statements',
            'sql_truncate': 'Consider using DELETE with WHERE for safer data removal',
            'eval_exec': 'Use ast.literal_eval() or safer alternatives to dynamic execution',
            'system_commands': 'Use subprocess with shell=False and input validation',
            'bulk_user_creation': 'Limit batch sizes and add proper validation',
            'file_deletion': 'Add existence checks and use try-catch blocks',
            'external_requests': 'Validate URLs and use timeout parameters'
        }
        return suggestions.get(pattern_name, 'Review this operation for security implications')
    
    def _generate_response(self, safety_score: float, issues: List[SecurityIssue]) -> Dict[str, Any]:
        """Generate the final JSON response"""
        
        # Determine overall safety status
        if safety_score >= 0.8:
            safety_status = "SAFE"
        elif safety_score >= 0.6:
            safety_status = "MODERATE_RISK"
        elif safety_score >= 0.3:
            safety_status = "HIGH_RISK"
        else:
            safety_status = "CRITICAL_RISK"
        
        # Format issues for response
        formatted_issues = []
        for issue in issues:
            formatted_issues.append({
                'pattern': issue.pattern,
                'risk_level': issue.risk_level.name,
                'description': issue.description,
                'line_number': issue.line_number,
                'column_number': issue.column_number,
                'suggestion': issue.suggestion
            })
        
        # Generate explanation
        explanation = self._generate_explanation(safety_score, safety_status, len(issues))
        
        return {
            'safety_score': safety_score,
            'safety_status': safety_status,
            'total_issues': len(issues),
            'issues': formatted_issues,
            'explanation': explanation,
            'recommendation': self._get_recommendation(safety_status),
            'analysis_timestamp': self._get_timestamp()
        }
    
    def _generate_explanation(self, score: float, status: str, issue_count: int) -> str:
        """Generate human-readable explanation"""
        if status == "SAFE":
            return f"Code appears safe with a high safety score of {score}. No significant security issues detected."
        elif status == "MODERATE_RISK":
            return f"Code has moderate risk (score: {score}) with {issue_count} issue(s) detected. Review recommended."
        elif status == "HIGH_RISK":
            return f"Code poses high security risk (score: {score}) with {issue_count} issue(s). Immediate review required."
        else:
            return f"Code poses critical security risk (score: {score}) with {issue_count} issue(s). DO NOT EXECUTE without thorough security review."
    
    def _get_recommendation(self, status: str) -> str:
        """Get recommendations based on safety status"""
        recommendations = {
            "SAFE": "Code can be executed with normal precautions.",
            "MODERATE_RISK": "Review flagged issues before execution. Consider additional security measures.",
            "HIGH_RISK": "Require security team approval before execution. Implement additional safeguards.",
            "CRITICAL_RISK": "DO NOT EXECUTE. Requires complete security review and refactoring."
        }
        return recommendations.get(status, "Manual security review required.")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for analysis"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


class SecurityASTVisitor(ast.NodeVisitor):
    """AST visitor class for detecting security issues in Python code"""
    
    def __init__(self):
        self.issues = []
        self.current_line = 1
    
    def visit_Call(self, node):
        """Visit function calls to detect dangerous operations"""
        
        # Check for eval/exec calls
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec']:
                self.issues.append(SecurityIssue(
                    pattern='ast_eval_exec',
                    risk_level=RiskLevel.CRITICAL,
                    description=f'Dynamic code execution ({node.func.id}) detected in AST',
                    line_number=getattr(node, 'lineno', None),
                    column_number=getattr(node, 'col_offset', None)
                ))
        
        # Check for os.system calls
        if isinstance(node.func, ast.Attribute):
            if (isinstance(node.func.value, ast.Name) and 
                node.func.value.id == 'os' and 
                node.func.attr == 'system'):
                self.issues.append(SecurityIssue(
                    pattern='ast_os_system',
                    risk_level=RiskLevel.HIGH,
                    description='os.system() call detected in AST',
                    line_number=getattr(node, 'lineno', None),
                    column_number=getattr(node, 'col_offset', None)
                ))
        
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Visit for loops to detect mass operations"""
        # Check for large range iterations
        if isinstance(node.iter, ast.Call):
            if (isinstance(node.iter.func, ast.Name) and 
                node.iter.func.id == 'range' and 
                len(node.iter.args) > 0):
                
                # Try to evaluate the range size
                try:
                    if isinstance(node.iter.args[0], ast.Constant):
                        range_size = node.iter.args[0].value
                        if isinstance(range_size, int) and range_size > 100:
                            self.issues.append(SecurityIssue(
                                pattern='ast_large_iteration',
                                risk_level=RiskLevel.MEDIUM,
                                description=f'Large iteration detected: range({range_size})',
                                line_number=getattr(node, 'lineno', None),
                                column_number=getattr(node, 'col_offset', None),
                                suggestion='Consider batch processing or limiting iteration size'
                            ))
                except:
                    pass
        
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Visit import statements to detect dangerous modules"""
        dangerous_modules = ['subprocess', 'shutil', 'pickle']
        
        for alias in node.names:
            if alias.name in dangerous_modules:
                risk_level = RiskLevel.HIGH if alias.name == 'subprocess' else RiskLevel.MEDIUM
                self.issues.append(SecurityIssue(
                    pattern=f'ast_import_{alias.name}',
                    risk_level=risk_level,
                    description=f'Import of potentially dangerous module: {alias.name}',
                    line_number=getattr(node, 'lineno', None),
                    column_number=getattr(node, 'col_offset', None),
                    suggestion=f'Ensure {alias.name} is used safely with proper input validation'
                ))
        
        self.generic_visit(node)


# Convenience function for direct usage
def analyze_ai_code(code: str, language: str = 'python') -> Dict[str, Any]:
    """
    Convenience function to analyze AI-generated code.
    
    Args:
        code: The code string to analyze
        language: Programming language
        
    Returns:
        JSON analysis result
    """
    analyzer = AICodeSecurityAnalyzer()
    return analyzer.analyze_code(code, language) 