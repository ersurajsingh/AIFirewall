import ast
import re
import os
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
import json
from datetime import datetime


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class CodeLine:
    line_number: int
    content: str
    indentation_level: int
    is_comment: bool
    is_blank: bool
    ast_type: Optional[str] = None


@dataclass
class ExplanationResult:
    line_number: int
    original_code: str
    explanation: str
    complexity_level: str  # "simple", "intermediate", "advanced"
    concepts: List[str]  # Programming concepts involved


class PythonCodeExplainer:
    """
    Advanced Python code explainer using LLM APIs to provide detailed,
    line-by-line explanations in natural language.
    """
    
    def __init__(self, llm_provider: LLMProvider = LLMProvider.OPENAI, api_key: Optional[str] = None):
        self.llm_provider = llm_provider
        self.api_key = api_key or self._get_api_key()
        
        # API configurations
        self.openai_config = {
            "base_url": "https://api.openai.com/v1/chat/completions",
            "model": "gpt-4",
            "max_tokens": 2000,
            "temperature": 0.3
        }
        
        self.anthropic_config = {
            "base_url": "https://api.anthropic.com/v1/messages",
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2000,
            "temperature": 0.3
        }
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables"""
        if self.llm_provider == LLMProvider.OPENAI:
            return os.getenv("OPENAI_API_KEY")
        elif self.llm_provider == LLMProvider.ANTHROPIC:
            return os.getenv("ANTHROPIC_API_KEY")
        return None
    
    def parse_code_structure(self, code: str) -> Tuple[List[CodeLine], Optional[ast.AST]]:
        """Parse code structure and extract line information"""
        lines = code.split('\n')
        code_lines = []
        ast_tree = None
        
        # Try to parse AST for additional context
        try:
            ast_tree = ast.parse(code)
        except SyntaxError:
            pass  # Continue without AST if syntax errors
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            indentation = len(line) - len(line.lstrip())
            
            code_line = CodeLine(
                line_number=i,
                content=line,
                indentation_level=indentation,
                is_comment=stripped.startswith('#'),
                is_blank=len(stripped) == 0
            )
            
            # Add AST type information if available
            if ast_tree:
                code_line.ast_type = self._get_ast_type_for_line(ast_tree, i)
            
            code_lines.append(code_line)
        
        return code_lines, ast_tree
    
    def _get_ast_type_for_line(self, ast_tree: ast.AST, line_number: int) -> Optional[str]:
        """Get AST node type for a specific line number"""
        for node in ast.walk(ast_tree):
            if hasattr(node, 'lineno') and node.lineno == line_number:
                return type(node).__name__
        return None
    
    async def explain_code_async(self, 
                                 code: str, 
                                 detail_level: str = "intermediate",
                                 include_concepts: bool = True,
                                 target_audience: str = "developers") -> str:
        """
        Asynchronously explain Python code line-by-line using LLM API
        
        Args:
            code: Python code string to explain
            detail_level: "beginner", "intermediate", or "advanced"
            include_concepts: Whether to include programming concepts
            target_audience: "beginners", "developers", "students", "experts"
        
        Returns:
            Markdown formatted explanation
        """
        if not self.api_key:
            raise ValueError(f"API key not found for {self.llm_provider.value}")
        
        # Parse code structure
        code_lines, ast_tree = self.parse_code_structure(code)
        
        # Filter out blank lines and pure comments for explanation
        significant_lines = [line for line in code_lines if not line.is_blank]
        
        # Generate explanations for each significant line
        explanations = []
        for line in significant_lines:
            if not line.is_comment or line.content.strip().startswith('"""'):
                explanation = await self._explain_single_line(
                    line, code, detail_level, target_audience, ast_tree
                )
                explanations.append(explanation)
        
        # Generate overall summary
        summary = await self._generate_code_summary(code, detail_level, target_audience)
        
        # Format as markdown
        return self._format_as_markdown(code, explanations, summary, include_concepts)
    
    def explain_code(self, 
                    code: str, 
                    detail_level: str = "intermediate",
                    include_concepts: bool = True,
                    target_audience: str = "developers") -> str:
        """
        Synchronous wrapper for explain_code_async
        """
        return asyncio.run(self.explain_code_async(
            code, detail_level, include_concepts, target_audience
        ))
    
    async def _explain_single_line(self, 
                                   line: CodeLine, 
                                   full_code: str,
                                   detail_level: str,
                                   target_audience: str,
                                   ast_tree: Optional[ast.AST]) -> ExplanationResult:
        """Explain a single line of code using LLM"""
        
        # Create context for the line
        context = self._build_line_context(line, full_code, ast_tree)
        
        # Create prompt based on provider
        prompt = self._create_explanation_prompt(
            line, context, detail_level, target_audience
        )
        
        # Call LLM API
        response = await self._call_llm_api(prompt)
        
        # Parse response
        explanation_data = self._parse_llm_response(response, line)
        
        return explanation_data
    
    def _build_line_context(self, line: CodeLine, full_code: str, ast_tree: Optional[ast.AST]) -> Dict:
        """Build contextual information for a line of code"""
        lines = full_code.split('\n')
        
        # Get surrounding lines for context
        start_idx = max(0, line.line_number - 3)
        end_idx = min(len(lines), line.line_number + 2)
        surrounding_lines = lines[start_idx:end_idx]
        
        context = {
            "line_content": line.content,
            "line_number": line.line_number,
            "indentation_level": line.indentation_level,
            "surrounding_lines": surrounding_lines,
            "ast_type": line.ast_type,
            "is_function_def": "def " in line.content,
            "is_class_def": "class " in line.content,
            "is_import": line.content.strip().startswith(("import ", "from ")),
            "has_assignment": "=" in line.content and not any(op in line.content for op in ["==", "!=", "<=", ">="]),
            "has_function_call": "(" in line.content and ")" in line.content,
        }
        
        return context
    
    def _create_explanation_prompt(self, 
                                   line: CodeLine, 
                                   context: Dict,
                                   detail_level: str,
                                   target_audience: str) -> str:
        """Create an appropriate prompt for the LLM"""
        
        base_prompt = f"""
You are an expert Python programming instructor. Explain this line of Python code in clear, natural language.

**Code Line {line.line_number}:**
```python
{line.content}
```

**Context (surrounding lines):**
```python
{chr(10).join(context['surrounding_lines'])}
```

**Requirements:**
- Target audience: {target_audience}
- Detail level: {detail_level}
- Explain what this specific line does
- If it's a complex line, break it down into parts
- Mention any important Python concepts involved
- Keep explanation concise but thorough
- Use simple, clear language

**Additional Context:**
- Line indentation level: {context['indentation_level']}
- AST node type: {context.get('ast_type', 'Unknown')}
- Contains function call: {context['has_function_call']}
- Contains assignment: {context['has_assignment']}
- Is import statement: {context['is_import']}

Please respond with a JSON object containing:
{{
    "explanation": "Natural language explanation of what this line does",
    "complexity": "simple|intermediate|advanced",
    "concepts": ["concept1", "concept2", ...],
    "breakdown": "Optional: step-by-step breakdown for complex lines"
}}
"""
        
        return base_prompt.strip()
    
    async def _call_llm_api(self, prompt: str) -> Dict:
        """Call the appropriate LLM API"""
        if self.llm_provider == LLMProvider.OPENAI:
            return await self._call_openai_api(prompt)
        elif self.llm_provider == LLMProvider.ANTHROPIC:
            return await self._call_anthropic_api(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    async def _call_openai_api(self, prompt: str) -> Dict:
        """Call OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.openai_config["model"],
            "messages": [
                {"role": "system", "content": "You are an expert Python programming instructor who explains code clearly and accurately."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.openai_config["max_tokens"],
            "temperature": self.openai_config["temperature"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.openai_config["base_url"], 
                headers=headers, 
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"content": data["choices"][0]["message"]["content"]}
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error {response.status}: {error_text}")
    
    async def _call_anthropic_api(self, prompt: str) -> Dict:
        """Call Anthropic API"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.anthropic_config["model"],
            "max_tokens": self.anthropic_config["max_tokens"],
            "temperature": self.anthropic_config["temperature"],
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.anthropic_config["base_url"],
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"content": data["content"][0]["text"]}
                else:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error {response.status}: {error_text}")
    
    def _parse_llm_response(self, response: Dict, line: CodeLine) -> ExplanationResult:
        """Parse LLM response into structured format"""
        content = response.get("content", "")
        
        try:
            # Try to parse as JSON
            if content.strip().startswith('{'):
                data = json.loads(content)
                return ExplanationResult(
                    line_number=line.line_number,
                    original_code=line.content,
                    explanation=data.get("explanation", "No explanation provided"),
                    complexity_level=data.get("complexity", "intermediate"),
                    concepts=data.get("concepts", [])
                )
        except json.JSONDecodeError:
            pass
        
        # Fallback: use raw content as explanation
        return ExplanationResult(
            line_number=line.line_number,
            original_code=line.content,
            explanation=content,
            complexity_level="intermediate",
            concepts=[]
        )
    
    async def _generate_code_summary(self, code: str, detail_level: str, target_audience: str) -> str:
        """Generate overall summary of the code"""
        summary_prompt = f"""
Analyze this Python code and provide a high-level summary:

```python
{code}
```

Provide a summary for {target_audience} at {detail_level} level that explains:
1. What this code does overall
2. Key programming patterns used
3. Main purpose/functionality
4. Any notable features or techniques

Keep it concise but informative.
"""
        
        response = await self._call_llm_api(summary_prompt)
        return response.get("content", "Code summary not available")
    
    def _format_as_markdown(self, 
                           code: str, 
                           explanations: List[ExplanationResult],
                           summary: str,
                           include_concepts: bool) -> str:
        """Format explanations as markdown"""
        
        # Header
        markdown = "# 🐍 Python Code Explanation\n\n"
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        markdown += f"*Generated on {timestamp}*\n\n"
        
        # Summary
        markdown += "## 📋 Overview\n\n"
        markdown += f"{summary}\n\n"
        
        # Original code
        markdown += "## 💻 Original Code\n\n"
        markdown += f"```python\n{code}\n```\n\n"
        
        # Line-by-line explanations
        markdown += "## 📖 Line-by-Line Explanation\n\n"
        
        for explanation in explanations:
            markdown += f"### Line {explanation.line_number}\n\n"
            markdown += f"```python\n{explanation.original_code}\n```\n\n"
            markdown += f"**Explanation:** {explanation.explanation}\n\n"
            
            if explanation.complexity_level != "simple":
                complexity_emoji = "🟡" if explanation.complexity_level == "intermediate" else "🔴"
                markdown += f"**Complexity:** {complexity_emoji} {explanation.complexity_level.title()}\n\n"
            
            if include_concepts and explanation.concepts:
                markdown += f"**Concepts:** {', '.join(explanation.concepts)}\n\n"
            
            markdown += "---\n\n"
        
        # Programming concepts summary
        if include_concepts:
            all_concepts = set()
            for exp in explanations:
                all_concepts.update(exp.concepts)
            
            if all_concepts:
                markdown += "## 🎯 Programming Concepts Used\n\n"
                for concept in sorted(all_concepts):
                    markdown += f"- {concept}\n"
                markdown += "\n"
        
        # Footer
        markdown += "---\n\n"
        markdown += "*Explanation generated by AI Firewall Code Explainer*\n"
        
        return markdown


# Convenience functions
async def explain_python_code_async(code: str, 
                                    provider: str = "openai",
                                    detail_level: str = "intermediate",
                                    target_audience: str = "developers",
                                    api_key: Optional[str] = None) -> str:
    """
    Async convenience function to explain Python code
    
    Args:
        code: Python code string
        provider: "openai" or "anthropic"
        detail_level: "beginner", "intermediate", or "advanced"
        target_audience: "beginners", "developers", "students", "experts"
        api_key: Optional API key (will use env var if not provided)
    
    Returns:
        Markdown formatted explanation
    """
    llm_provider = LLMProvider.OPENAI if provider.lower() == "openai" else LLMProvider.ANTHROPIC
    explainer = PythonCodeExplainer(llm_provider, api_key)
    
    return await explainer.explain_code_async(
        code, detail_level, include_concepts=True, target_audience=target_audience
    )


def explain_python_code(code: str, 
                       provider: str = "openai",
                       detail_level: str = "intermediate", 
                       target_audience: str = "developers",
                       api_key: Optional[str] = None) -> str:
    """
    Synchronous convenience function to explain Python code
    """
    return asyncio.run(explain_python_code_async(
        code, provider, detail_level, target_audience, api_key
    )) 