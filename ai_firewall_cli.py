#!/usr/bin/env python3
"""
AI Firewall Interactive CLI
A command-line interface for reviewing AI code suggestions with safety analysis.
"""

import os
import sys
import json
import requests
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.policy_engine import PolicyEngine, PolicyViolation
    from backend.security_analyzer import AICodeSecurityAnalyzer
    from backend.code_explainer import PythonCodeExplainer
    LOCAL_MODE = True
except ImportError:
    LOCAL_MODE = False

# ANSI Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

@dataclass
class CodeSuggestion:
    """Represents an AI code suggestion with analysis"""
    code: str
    source: str = "ai_generated"
    file_path: Optional[str] = None
    description: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class SafetyAnalysis:
    """Results from safety analysis"""
    safety_score: float
    risk_level: str
    violations: List[Dict]
    explanation: str
    blocked: bool = False
    suggestions: List[str] = None

class AIFirewallCLI:
    """Interactive CLI for AI Firewall code review"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.session_log = []
        self.accepted_suggestions = []
        self.rejected_suggestions = []
        
        # Test API connection
        self.api_available = self._test_api_connection()
        
        if not self.api_available and not LOCAL_MODE:
            print(f"{Colors.WARNING}⚠️  Warning: API not available and local mode not supported.{Colors.ENDC}")
            print("Start the backend with: ./start.sh")

    def _test_api_connection(self) -> bool:
        """Test if the API is available"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Print the CLI header"""
        self.clear_screen()
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 20 + "🛡️  AI FIREWALL - CODE REVIEW CLI" + " " * 23 + "║")
        print("║" + " " * 25 + "Secure AI Code Suggestions" + " " * 26 + "║")
        print("╚" + "═" * 78 + "╝")
        print(f"{Colors.ENDC}")

    def print_separator(self, char="─", length=80):
        """Print a separator line"""
        print(f"{Colors.OKCYAN}{char * length}{Colors.ENDC}")

    def analyze_code_suggestion(self, suggestion: CodeSuggestion) -> SafetyAnalysis:
        """Analyze a code suggestion for safety"""
        if self.api_available:
            return self._analyze_via_api(suggestion)
        elif LOCAL_MODE:
            return self._analyze_locally(suggestion)
        else:
            # Fallback analysis
            return SafetyAnalysis(
                safety_score=0.5,
                risk_level="UNKNOWN",
                violations=[],
                explanation="Analysis not available - API offline and local mode not supported",
                suggestions=["Start the backend API for full analysis"]
            )

    def _analyze_via_api(self, suggestion: CodeSuggestion) -> SafetyAnalysis:
        """Analyze code via API"""
        try:
            # Policy analysis
            policy_response = requests.post(f"{self.api_base_url}/analyze-with-policies", json={
                "code": suggestion.code,
                "file_path": suggestion.file_path,
                "context": {
                    "source": suggestion.source,
                    "timestamp": suggestion.timestamp
                }
            })
            
            # Security analysis
            security_response = requests.post(f"{self.api_base_url}/analyze-ai-code", json={
                "code": suggestion.code,
                "source": suggestion.source,
                "context": suggestion.description
            })
            
            # Code explanation
            explanation_response = requests.post(f"{self.api_base_url}/explain-code-simple", json={
                "code": suggestion.code
            })
            
            policy_data = policy_response.json() if policy_response.status_code == 200 else {}
            security_data = security_response.json() if security_response.status_code == 200 else {}
            explanation_data = explanation_response.json() if explanation_response.status_code == 200 else {}
            
            # Combine results
            safety_score = security_data.get("safety_score", 0.5)
            risk_level = policy_data.get("risk_level", security_data.get("risk_level", "MEDIUM"))
            violations = policy_data.get("violations", [])
            explanation = explanation_data.get("explanation", "No explanation available")
            blocked = policy_data.get("blocked", False) or security_data.get("blocked", False)
            
            suggestions = []
            for violation in violations:
                if violation.get("suggestion"):
                    suggestions.append(violation["suggestion"])
            
            return SafetyAnalysis(
                safety_score=safety_score,
                risk_level=risk_level,
                violations=violations,
                explanation=explanation,
                blocked=blocked,
                suggestions=suggestions
            )
            
        except requests.exceptions.RequestException as e:
            return SafetyAnalysis(
                safety_score=0.0,
                risk_level="ERROR",
                violations=[],
                explanation=f"API Error: {str(e)}",
                suggestions=["Check API connection"]
            )

    def _analyze_locally(self, suggestion: CodeSuggestion) -> SafetyAnalysis:
        """Analyze code locally using imported modules"""
        try:
            # Policy analysis
            policy_engine = PolicyEngine()
            violations = policy_engine.analyze_code(suggestion.code, suggestion.file_path)
            
            # Security analysis
            security_analyzer = AICodeSecurityAnalyzer()
            security_result = security_analyzer.analyze_code(suggestion.code)
            
            # Convert violations to dict format
            violation_dicts = []
            for v in violations:
                violation_dicts.append({
                    "rule_name": v.rule_name,
                    "severity": v.severity.value,
                    "description": v.description,
                    "suggestion": v.suggestion
                })
            
            risk_level = "LOW"
            if any(v.severity.value == "critical" for v in violations):
                risk_level = "CRITICAL"
            elif any(v.severity.value == "high" for v in violations):
                risk_level = "HIGH"
            elif len(violations) > 0:
                risk_level = "MEDIUM"
            
            blocked = any(v.action.value == "block" for v in violations)
            safety_score = security_result.get("safety_score", 0.5)
            
            suggestions = []
            for v in violations:
                if v.suggestion:
                    suggestions.append(v.suggestion)
            
            return SafetyAnalysis(
                safety_score=safety_score,
                risk_level=risk_level,
                violations=violation_dicts,
                explanation=security_result.get("explanation", "Local analysis completed"),
                blocked=blocked,
                suggestions=suggestions
            )
            
        except Exception as e:
            return SafetyAnalysis(
                safety_score=0.0,
                risk_level="ERROR",
                violations=[],
                explanation=f"Local analysis error: {str(e)}",
                suggestions=["Check local module installation"]
            )

    def display_suggestion(self, suggestion: CodeSuggestion, analysis: SafetyAnalysis):
        """Display a code suggestion with analysis"""
        self.print_header()
        
        # Suggestion header
        print(f"{Colors.BOLD}📝 AI CODE SUGGESTION{Colors.ENDC}")
        self.print_separator()
        print(f"Source: {suggestion.source}")
        if suggestion.file_path:
            print(f"File: {suggestion.file_path}")
        if suggestion.description:
            print(f"Description: {suggestion.description}")
        print(f"Timestamp: {suggestion.timestamp}")
        print()
        
        # Code block
        print(f"{Colors.BOLD}💻 GENERATED CODE:{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{'─' * 60}{Colors.ENDC}")
        print(suggestion.code)
        print(f"{Colors.OKCYAN}{'─' * 60}{Colors.ENDC}")
        print()
        
        # Safety analysis
        self._display_safety_analysis(analysis)
        
        print()

    def _display_safety_analysis(self, analysis: SafetyAnalysis):
        """Display safety analysis results"""
        # Risk level with color coding
        risk_colors = {
            "LOW": Colors.OKGREEN,
            "MEDIUM": Colors.WARNING, 
            "HIGH": Colors.WARNING,
            "CRITICAL": Colors.FAIL,
            "ERROR": Colors.FAIL
        }
        risk_color = risk_colors.get(analysis.risk_level, Colors.ENDC)
        
        print(f"{Colors.BOLD}🔍 SAFETY ANALYSIS:{Colors.ENDC}")
        self.print_separator()
        print(f"Safety Score: {self._format_safety_score(analysis.safety_score)}")
        print(f"Risk Level: {risk_color}{analysis.risk_level}{Colors.ENDC}")
        
        if analysis.blocked:
            print(f"{Colors.FAIL}{Colors.BOLD}🚫 BLOCKED - Code execution prevented by policy{Colors.ENDC}")
        
        print()
        
        # Violations
        if analysis.violations:
            print(f"{Colors.BOLD}⚠️  POLICY VIOLATIONS ({len(analysis.violations)}):{Colors.ENDC}")
            for i, violation in enumerate(analysis.violations, 1):
                severity_color = {
                    "critical": Colors.FAIL,
                    "high": Colors.WARNING,
                    "medium": Colors.WARNING,
                    "low": Colors.OKBLUE
                }.get(violation.get("severity", "medium"), Colors.ENDC)
                
                print(f"  {i}. {severity_color}[{violation.get('severity', 'UNKNOWN').upper()}]{Colors.ENDC} {violation.get('rule_name', 'Unknown Rule')}")
                print(f"     📝 {violation.get('description', 'No description')}")
                if violation.get("suggestion"):
                    print(f"     💡 {violation['suggestion']}")
                print()
        
        # Explanation
        if analysis.explanation and analysis.explanation != "No explanation available":
            print(f"{Colors.BOLD}📚 CODE EXPLANATION:{Colors.ENDC}")
            self.print_separator()
            # Truncate very long explanations for CLI display
            explanation = analysis.explanation
            if len(explanation) > 500:
                explanation = explanation[:500] + "...\n[Explanation truncated for display]"
            print(explanation)
            print()
        
        # Suggestions
        if analysis.suggestions:
            print(f"{Colors.BOLD}💡 SECURITY RECOMMENDATIONS:{Colors.ENDC}")
            for i, suggestion in enumerate(analysis.suggestions, 1):
                print(f"  {i}. {suggestion}")
            print()

    def _format_safety_score(self, score: float) -> str:
        """Format safety score with color"""
        if score >= 0.8:
            return f"{Colors.OKGREEN}{score:.2f}{Colors.ENDC}"
        elif score >= 0.6:
            return f"{Colors.WARNING}{score:.2f}{Colors.ENDC}"
        else:
            return f"{Colors.FAIL}{score:.2f}{Colors.ENDC}"

    def get_user_decision(self, analysis: SafetyAnalysis) -> str:
        """Get user decision on whether to accept or reject the suggestion"""
        if analysis.blocked:
            print(f"{Colors.FAIL}This code is BLOCKED by security policies and cannot be accepted.{Colors.ENDC}")
            input("\nPress Enter to continue...")
            return "blocked"
        
        print(f"{Colors.BOLD}🤔 DECISION REQUIRED:{Colors.ENDC}")
        self.print_separator()
        
        options = [
            f"{Colors.OKGREEN}[A]{Colors.ENDC} Accept - Use this code",
            f"{Colors.FAIL}[R]{Colors.ENDC} Reject - Don't use this code", 
            f"{Colors.OKBLUE}[E]{Colors.ENDC} Explain - Get detailed explanation",
            f"{Colors.WARNING}[M]{Colors.ENDC} Modify - Suggest improvements",
            f"{Colors.OKCYAN}[S]{Colors.ENDC} Skip - Review later"
        ]
        
        for option in options:
            print(f"  {option}")
        
        print()
        
        while True:
            choice = input("Your choice [A/R/E/M/S]: ").strip().upper()
            
            if choice in ['A', 'ACCEPT']:
                return "accept"
            elif choice in ['R', 'REJECT']:
                return "reject"
            elif choice in ['E', 'EXPLAIN']:
                return "explain"
            elif choice in ['M', 'MODIFY']:
                return "modify"
            elif choice in ['S', 'SKIP']:
                return "skip"
            else:
                print(f"{Colors.WARNING}Invalid choice. Please enter A, R, E, M, or S{Colors.ENDC}")

    def handle_decision(self, suggestion: CodeSuggestion, analysis: SafetyAnalysis, decision: str):
        """Handle user decision"""
        if decision == "accept":
            self.accepted_suggestions.append({
                "suggestion": suggestion,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            })
            print(f"{Colors.OKGREEN}✅ Code suggestion accepted and logged{Colors.ENDC}")
            
        elif decision == "reject":
            reason = input("Reason for rejection (optional): ").strip()
            self.rejected_suggestions.append({
                "suggestion": suggestion,
                "analysis": analysis,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
            print(f"{Colors.FAIL}❌ Code suggestion rejected and logged{Colors.ENDC}")
            
        elif decision == "explain":
            self._show_detailed_explanation(suggestion)
            return self.review_suggestion(suggestion, analysis)  # Continue review
            
        elif decision == "modify":
            self._suggest_modifications(analysis)
            return self.review_suggestion(suggestion, analysis)  # Continue review
            
        elif decision == "skip":
            print(f"{Colors.WARNING}⏭️  Suggestion skipped for later review{Colors.ENDC}")
            
        elif decision == "blocked":
            self.rejected_suggestions.append({
                "suggestion": suggestion,
                "analysis": analysis,
                "reason": "Blocked by security policy",
                "timestamp": datetime.now().isoformat()
            })
            print(f"{Colors.FAIL}🚫 Code suggestion blocked by security policy{Colors.ENDC}")
        
        input("\nPress Enter to continue...")

    def _show_detailed_explanation(self, suggestion: CodeSuggestion):
        """Show detailed code explanation"""
        if self.api_available:
            try:
                response = requests.post(f"{self.api_base_url}/explain-code", json={
                    "code": suggestion.code,
                    "detail_level": "advanced",
                    "target_audience": "developers"
                })
                
                if response.status_code == 200:
                    data = response.json()
                    explanation = data.get("explanation", "No detailed explanation available")
                else:
                    explanation = "Failed to get detailed explanation from API"
            except:
                explanation = "Error getting detailed explanation"
        else:
            explanation = "Detailed explanation requires API connection"
        
        self.clear_screen()
        print(f"{Colors.BOLD}📚 DETAILED CODE EXPLANATION{Colors.ENDC}")
        self.print_separator()
        print(explanation)
        print()
        input("Press Enter to return to review...")

    def _suggest_modifications(self, analysis: SafetyAnalysis):
        """Show suggestions for code modifications"""
        self.clear_screen()
        print(f"{Colors.BOLD}🔧 SUGGESTED MODIFICATIONS{Colors.ENDC}")
        self.print_separator()
        
        if analysis.suggestions:
            for i, suggestion in enumerate(analysis.suggestions, 1):
                print(f"{i}. {suggestion}")
        else:
            print("No specific modification suggestions available.")
            
        if analysis.violations:
            print(f"\n{Colors.BOLD}Security Issues to Address:{Colors.ENDC}")
            for violation in analysis.violations:
                print(f"• {violation.get('description', 'Unknown issue')}")
        
        print()
        input("Press Enter to return to review...")

    def review_suggestion(self, suggestion: CodeSuggestion, analysis: SafetyAnalysis = None):
        """Review a single code suggestion"""
        if analysis is None:
            analysis = self.analyze_code_suggestion(suggestion)
        
        self.display_suggestion(suggestion, analysis)
        decision = self.get_user_decision(analysis)
        self.handle_decision(suggestion, analysis, decision)
        
        # Log the session
        self.session_log.append({
            "suggestion": suggestion.__dict__,
            "analysis": analysis.__dict__,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        })

    def batch_review(self, suggestions: List[CodeSuggestion]):
        """Review multiple code suggestions"""
        print(f"{Colors.BOLD}📋 BATCH REVIEW MODE - {len(suggestions)} suggestions{Colors.ENDC}")
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{Colors.HEADER}Reviewing suggestion {i}/{len(suggestions)}{Colors.ENDC}")
            self.review_suggestion(suggestion)
        
        self.show_session_summary()

    def show_session_summary(self):
        """Show summary of the review session"""
        self.clear_screen()
        self.print_header()
        
        print(f"{Colors.BOLD}📊 SESSION SUMMARY{Colors.ENDC}")
        self.print_separator()
        
        total = len(self.session_log)
        accepted = len(self.accepted_suggestions)
        rejected = len(self.rejected_suggestions)
        
        print(f"Total suggestions reviewed: {total}")
        print(f"{Colors.OKGREEN}Accepted: {accepted}{Colors.ENDC}")
        print(f"{Colors.FAIL}Rejected: {rejected}{Colors.ENDC}")
        print(f"Other actions: {total - accepted - rejected}")
        
        if total > 0:
            acceptance_rate = (accepted / total) * 100
            print(f"\nAcceptance rate: {acceptance_rate:.1f}%")
        
        print()
        
        # Show risk distribution
        risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for log_entry in self.session_log:
            risk_level = log_entry["analysis"]["risk_level"]
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
        
        print(f"{Colors.BOLD}Risk Level Distribution:{Colors.ENDC}")
        for level, count in risk_counts.items():
            if count > 0:
                color = {
                    "LOW": Colors.OKGREEN,
                    "MEDIUM": Colors.WARNING,
                    "HIGH": Colors.WARNING,
                    "CRITICAL": Colors.FAIL
                }.get(level, Colors.ENDC)
                print(f"  {color}{level}: {count}{Colors.ENDC}")

    def interactive_mode(self):
        """Run interactive mode for entering code suggestions"""
        self.print_header()
        print(f"{Colors.BOLD}🔄 INTERACTIVE MODE{Colors.ENDC}")
        print("Enter code suggestions for review. Type 'quit' to exit.")
        print()
        
        while True:
            print(f"{Colors.BOLD}Enter code to review:{Colors.ENDC}")
            print("(Type 'quit' to exit, 'demo' for examples, 'summary' for session summary)")
            print()
            
            lines = []
            print("Code (press Ctrl+D or Enter twice to finish):")
            try:
                while True:
                    line = input()
                    if line == "":
                        break
                    if line.lower() == 'quit':
                        return
                    if line.lower() == 'demo':
                        self.run_demo_suggestions()
                        continue
                    if line.lower() == 'summary':
                        self.show_session_summary()
                        input("\nPress Enter to continue...")
                        break
                    lines.append(line)
                
                if not lines:
                    continue
                    
                code = '\n'.join(lines)
                
                # Get additional context
                file_path = input("File path (optional): ").strip() or None
                description = input("Description (optional): ").strip() or None
                
                suggestion = CodeSuggestion(
                    code=code,
                    file_path=file_path,
                    description=description,
                    source="user_input"
                )
                
                self.review_suggestion(suggestion)
                
            except (EOFError, KeyboardInterrupt):
                break
        
        self.show_session_summary()

    def run_demo_suggestions(self):
        """Run demo with predefined dangerous code suggestions"""
        demo_suggestions = [
            CodeSuggestion(
                code='''import os
os.environ["PROD_DATABASE_URL"] = "postgresql://admin:secret@prod/db"
print("Production database configured")''',
                description="Configure production database connection",
                file_path="config/database.py",
                source="ai_assistant"
            ),
            
            CodeSuggestion(
                code='''import pickle
import requests

def load_user_data(data_file):
    with open(data_file, 'rb') as f:
        user_data = pickle.load(f)  # Potentially dangerous!
    return user_data

api_key = "sk-1234567890abcdef1234567890abcdef"''',
                description="Load user data from file",
                file_path="utils/data_loader.py", 
                source="copilot"
            ),
            
            CodeSuggestion(
                code='''def clean_logs():
    import shutil
    import os
    
    # Clean up old log files
    shutil.rmtree("/var/log/")
    os.system("rm -rf /tmp/*")
    
    print("Logs cleaned successfully")''',
                description="Clean up system logs",
                file_path="scripts/cleanup.py",
                source="ai_assistant"
            ),
            
            CodeSuggestion(
                code='''import json
from datetime import datetime

def calculate_metrics(users):
    """Calculate user engagement metrics safely"""
    if not users:
        return {"total": 0, "active": 0}
    
    total = len(users)
    active = sum(1 for user in users if user.get("last_active"))
    
    return {
        "total_users": total,
        "active_users": active,
        "calculated_at": datetime.now().isoformat()
    }''',
                description="Calculate user metrics",
                file_path="analytics/metrics.py",
                source="developer"
            )
        ]
        
        self.batch_review(demo_suggestions)

def main():
    """Main CLI entry point"""
    cli = AIFirewallCLI()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "demo":
            cli.run_demo_suggestions()
        elif command == "interactive":
            cli.interactive_mode()
        elif command == "help":
            print_help()
        else:
            print(f"Unknown command: {command}")
            print_help()
    else:
        # Default to interactive mode
        cli.interactive_mode()

def print_help():
    """Print CLI help"""
    print(f"{Colors.BOLD}AI Firewall CLI - Help{Colors.ENDC}")
    print("Usage: python3 ai_firewall_cli.py [command]")
    print()
    print("Commands:")
    print("  demo        - Run with predefined dangerous code examples")
    print("  interactive - Interactive mode for entering code suggestions")
    print("  help        - Show this help message")
    print()
    print("Interactive mode commands:")
    print("  quit        - Exit the CLI")
    print("  demo        - Run demo suggestions")
    print("  summary     - Show session summary")

if __name__ == "__main__":
    main() 