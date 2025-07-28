# 🐍 Python Code Explainer

An advanced code explanation system that uses OpenAI GPT-4 or Anthropic Claude to provide detailed, line-by-line explanations of Python code in natural language, formatted as markdown.

## 🎯 Overview

The Python Code Explainer is designed to help developers, students, and code reviewers understand complex Python code by providing:

- **Line-by-line explanations** in natural language
- **Programming concept identification** for educational purposes
- **Complexity assessment** for each code segment
- **Multiple detail levels** from beginner to advanced
- **Flexible target audiences** (students, developers, experts)
- **Beautiful markdown formatting** for easy reading

## ✨ Features

### 🔍 **Advanced Code Analysis**
- **AST (Abstract Syntax Tree) parsing** for deep code understanding
- **Context-aware explanations** using surrounding code
- **Programming concept extraction** (loops, functions, classes, etc.)
- **Complexity level assessment** (simple, intermediate, advanced)

### 🎨 **Flexible Configuration**
- **Multiple LLM providers**: OpenAI GPT-4, Anthropic Claude
- **Detail levels**: Beginner, Intermediate, Advanced
- **Target audiences**: Students, Developers, Experts
- **Custom API key support** for different accounts

### 📖 **Rich Output**
- **Markdown formatted** explanations
- **Programming concepts summary**
- **Overall code summary**
- **Line-by-line breakdowns**
- **Timestamp and metadata**

## 🚀 API Endpoints

### `POST /explain-code`
Comprehensive code explanation with full configuration options.

**Request:**
```json
{
  "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "provider": "openai",
  "detail_level": "intermediate", 
  "target_audience": "developers",
  "api_key": "optional-api-key-override"
}
```

**Response:**
```json
{
  "explanation": "# 🐍 Python Code Explanation\n\n*Generated on 2024-01-15 10:30:45*\n\n## 📋 Overview...",
  "provider_used": "openai",
  "detail_level": "intermediate",
  "target_audience": "developers", 
  "timestamp": "2024-01-15T10:30:45Z",
  "status": "success"
}
```

### `POST /explain-code-simple`
Quick explanation with default settings.

**Request:**
```json
{
  "code": "def hello(): return 'Hello World'"
}
```

### `GET /explain-demo`
Demo endpoint with sample code explanation.

## 📋 Configuration Options

### **LLM Providers**
- `"openai"` - Uses GPT-4 for explanations
- `"anthropic"` - Uses Claude-3-Sonnet for explanations

### **Detail Levels**
- `"beginner"` - Simple explanations with basic concepts
- `"intermediate"` - Balanced detail with programming concepts
- `"advanced"` - In-depth technical explanations

### **Target Audiences**
- `"students"` - Educational focus with learning concepts
- `"developers"` - Technical focus with implementation details
- `"experts"` - Advanced analysis with optimization insights

## 🔧 Setup and Configuration

### **Environment Variables**
```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### **Installation**
```bash
# Install additional dependencies
pip install aiohttp openai

# Start the backend
./start.sh
```

## 💻 Usage Examples

### **Python Direct Usage**
```python
from backend.code_explainer import explain_python_code

code = '''
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
'''

explanation = explain_python_code(
    code=code,
    provider="openai",
    detail_level="intermediate",
    target_audience="developers"
)

print(explanation)
```

### **API Usage with curl**
```bash
# Simple explanation
curl -X POST http://localhost:8000/explain-code-simple \
  -H "Content-Type: application/json" \
  -d '{"code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"}'

# Comprehensive explanation
curl -X POST http://localhost:8000/explain-code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "class Calculator:\n    def __init__(self):\n        self.value = 0\n    def add(self, x):\n        self.value += x\n        return self",
    "provider": "anthropic",
    "detail_level": "beginner",
    "target_audience": "students"
  }'
```

### **API Usage with Python requests**
```python
import requests

response = requests.post("http://localhost:8000/explain-code", json={
    "code": """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
""",
    "provider": "openai",
    "detail_level": "advanced",
    "target_audience": "experts"
})

explanation = response.json()["explanation"]
print(explanation)
```

## 📄 Example Output

```markdown
# 🐍 Python Code Explanation

*Generated on 2024-01-15 10:30:45*

## 📋 Overview

This code implements a recursive Fibonacci number calculator. The Fibonacci sequence 
is a mathematical series where each number is the sum of the two preceding ones, 
starting from 0 and 1.

## 💻 Original Code

```python
def fibonacci(n):
    """Calculate fibonacci number recursively"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

## 📖 Line-by-Line Explanation

### Line 1
```python
def fibonacci(n):
```
**Explanation:** This line defines a function named 'fibonacci' that takes one parameter 'n', which represents the position in the Fibonacci sequence we want to calculate.

**Complexity:** 🟡 Intermediate

**Concepts:** function definition, parameters

### Line 2
```python
    """Calculate fibonacci number recursively"""
```
**Explanation:** This is a docstring that provides documentation for the function, explaining that it calculates Fibonacci numbers using a recursive approach.

**Complexity:** 🟢 Simple

**Concepts:** docstrings, documentation

### Line 3
```python
    if n <= 1:
```
**Explanation:** This is the base case for the recursion. It checks if the input 'n' is less than or equal to 1, which handles the first two numbers of the Fibonacci sequence (0 and 1).

**Complexity:** 🟡 Intermediate

**Concepts:** conditional statements, base case, recursion

---

## 🎯 Programming Concepts Used

- function definition
- recursion
- conditional statements
- base case
- docstrings
- mathematical algorithms

---

*Explanation generated by AI Firewall Code Explainer*
```

## 🧪 Testing

### **Run Tests**
```bash
# Test the explainer directly (no API keys required for structure analysis)
python3 test_code_explainer.py

# Test via API (requires API keys)
python3 api_explainer_example.py
```

### **Example Test Cases**

1. **Simple Function**
```python
def greet(name):
    return f"Hello, {name}!"
```

2. **Class Definition**
```python
class BankAccount:
    def __init__(self, balance=0):
        self.balance = balance
    
    def deposit(self, amount):
        self.balance += amount
```

3. **Algorithm Implementation**
```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    # ... implementation
```

## 🎯 Use Cases

### **Educational**
- **Code review sessions** with detailed explanations
- **Learning programming concepts** through real examples
- **Teaching Python** to beginners with line-by-line breakdowns

### **Professional Development**
- **Onboarding new developers** with codebase explanations
- **Documentation generation** for complex algorithms
- **Code audit support** with automated explanations

### **Code Analysis**
- **Understanding legacy code** without original documentation
- **Reverse engineering** complex algorithms
- **Security audits** with detailed code understanding

## ⚙️ Advanced Configuration

### **Custom Model Settings**
```python
from backend.code_explainer import PythonCodeExplainer, LLMProvider

explainer = PythonCodeExplainer(LLMProvider.OPENAI, "your-api-key")

# Customize OpenAI settings
explainer.openai_config.update({
    "model": "gpt-4-turbo",
    "max_tokens": 3000,
    "temperature": 0.2
})
```

### **Batch Processing**
```python
code_snippets = [
    "def add(a, b): return a + b",
    "class Point:\n    def __init__(self, x, y):\n        self.x, self.y = x, y",
    "for i in range(10):\n    print(i)"
]

for i, code in enumerate(code_snippets):
    explanation = explain_python_code(code, detail_level="beginner")
    with open(f"explanation_{i}.md", "w") as f:
        f.write(explanation)
```

## 🚨 Limitations and Considerations

### **API Costs**
- LLM API calls have associated costs
- Longer code snippets require more tokens
- Consider caching explanations for repeated code

### **Rate Limits**
- OpenAI and Anthropic have rate limits
- Implement proper retry logic for production use
- Consider async processing for batch operations

### **Code Complexity**
- Very large code files may exceed token limits
- Complex code might require multiple API calls
- Consider breaking large files into smaller chunks

## 🔄 Future Enhancements

- [ ] **Multi-language support** (JavaScript, Java, C++)
- [ ] **Interactive explanations** with Q&A capability
- [ ] **Code suggestion improvements** based on explanations
- [ ] **Integration with IDEs** beyond VS Code
- [ ] **Explanation caching** for performance optimization
- [ ] **Custom explanation templates** for specific use cases

## 📞 Support

For questions about the Code Explainer:
- Check the test scripts for usage examples
- Review API documentation for endpoint details
- Ensure API keys are properly configured
- Monitor API rate limits and costs

The Code Explainer is a powerful tool for understanding and documenting Python code using the latest AI technology! 