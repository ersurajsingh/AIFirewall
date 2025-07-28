# 🛡️ AI Firewall

> **Secure AI Code Suggestions with Real-time Safety Analysis**

AI Firewall is a comprehensive security system that analyzes AI-generated code suggestions for potential security vulnerabilities, policy violations, and dangerous patterns. It provides real-time safety scoring, detailed explanations, and interactive review interfaces to ensure AI-generated code meets your security standards.

![AI Firewall Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 **The Problem**

As AI code generation tools (GitHub Copilot, ChatGPT, Claude, etc.) become ubiquitous, developers face a critical challenge:

- **🔴 Security Risks**: AI models can suggest code with hardcoded secrets, SQL injection vulnerabilities, or unsafe operations
- **⚠️ Policy Violations**: Generated code might violate company security policies or best practices  
- **🚨 Production Dangers**: AI might suggest code that could damage production systems or databases
- **📝 Lack of Review**: No systematic way to review AI suggestions before implementation

**AI Firewall solves these problems** by providing real-time security analysis, policy enforcement, and interactive review interfaces.

## ✨ **Features**

### 🔍 **Comprehensive Security Analysis**
- **Policy Engine**: Custom YAML/JSON security rules for your organization
- **AST Analysis**: Deep code structure analysis for dangerous patterns
- **Pattern Matching**: Regex-based detection of security anti-patterns
- **Risk Scoring**: 0-100% safety score with detailed explanations

### 🎨 **Multiple Interface Options**
- **🖥️ Interactive CLI**: Terminal-based interface with colorful output
- **🌐 Web Dashboard**: Modern browser interface with real-time analysis
- **📝 VS Code Extension**: Integrated panel within your editor

### 🤖 **AI-Powered Explanations**
- **LLM Integration**: OpenAI and Anthropic for natural language explanations
- **Line-by-line Analysis**: Detailed breakdown of code functionality
- **Security Context**: Explains why code is flagged as dangerous

### 📊 **Review & Decision System**
- **Accept/Reject Workflow**: Interactive decision making with logging
- **Session Tracking**: Comprehensive review history and statistics
- **Batch Processing**: Review multiple suggestions efficiently

### 🛡️ **Built-in Security Policies**
- **Production Environment Protection**: Prevents prod env var modification
- **Database Security**: Blocks dangerous SQL operations
- **File System Safety**: Prevents destructive file operations
- **Secret Detection**: Identifies hardcoded API keys and tokens
- **Code Injection Prevention**: Blocks unsafe eval/exec usage

## 🚀 **Quick Start**

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/AIFirewall.git
cd AIFirewall
```

### **2. Install Dependencies**
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Or use the setup script
./start.sh
```

### **3. Start the Backend**
```bash
# Option 1: Use the start script
./start.sh

# Option 2: Manual start
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **4. Choose Your Interface**

#### **🖥️ CLI Interface (Recommended for first-time users)**
```bash
# Interactive mode
python3 ai_firewall_cli.py

# Demo with dangerous examples
python3 ai_firewall_cli.py demo

# Help
python3 ai_firewall_cli.py help
```

#### **🌐 Web Interface**
```bash
# Open in your browser
open ui/index.html
```

#### **📝 VS Code Extension**
```bash
cd vscode-extension
npm install
npm run compile
# Press F5 in VS Code to launch extension
```

## 📋 **Installation Guide**

### **Prerequisites**
- Python 3.8+
- Node.js 16+ (for VS Code extension)
- Git

### **Step-by-Step Installation**

#### **1. System Dependencies**
```bash
# macOS
brew install python3 node

# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip nodejs npm

# Windows
# Download Python and Node.js from official websites
```

#### **2. Clone and Setup**
```bash
git clone https://github.com/yourusername/AIFirewall.git
cd AIFirewall

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt
```

#### **3. Environment Configuration**
```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys (optional for basic usage)
nano .env
```

#### **4. Verify Installation**
```bash
# Test CLI
python3 ai_firewall_cli.py help

# Test backend
curl http://localhost:8000/health
```

## 🎯 **Usage Examples**

### **CLI Demo - Reviewing Dangerous Code**
```bash
$ python3 ai_firewall_cli.py demo

╔══════════════════════════════════════════════════════════════════════════════╗
║                    🛡️  AI FIREWALL - CODE REVIEW CLI                       ║
║                         Secure AI Code Suggestions                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

📝 AI CODE SUGGESTION
────────────────────────────────────────────────────────────────────────────────
Source: ai_assistant
File: config/database.py
Description: Configure production database connection

💻 GENERATED CODE:
────────────────────────────────────────────────────────────
import os
os.environ["PROD_DATABASE_URL"] = "postgresql://admin:secret@prod/db"
print("Production database configured")
────────────────────────────────────────────────────────────

🔍 SAFETY ANALYSIS:
────────────────────────────────────────────────────────────────────────────────
Safety Score: 0.15 (🔴 LOW)
Risk Level: 🔴 CRITICAL

⚠️  POLICY VIOLATIONS DETECTED:
  1. [CRITICAL] Production Environment Modification
     📝 Prevents modification of production environment variables
     📍 Line 2
     🔍 Matched: 'os.environ["PROD_DATABASE_URL"]'
     💡 Suggestion: Use environment-specific configuration files
     🚨 Action: block

🤔 DECISION REQUIRED:
  ✅ [A] Accept - Use this code
  ❌ [R] Reject - Don't use this code  
  📖 [E] Explain - Get detailed explanation
  🔧 [M] Modify - Suggest improvements
  ⏭️  [S] Skip - Review later

This code is BLOCKED by security policies and cannot be accepted.
```

### **Web Interface - Modern Dashboard**
Open `ui/index.html` in your browser to see:
- **Real-time API status** monitoring
- **Interactive code editor** with syntax highlighting
- **Visual safety scores** with color-coded risk levels
- **Detailed violation reports** with improvement suggestions
- **Session logging** with exportable history

### **VS Code Integration**
The VS Code extension provides:
- **Native panel integration** in the Explorer sidebar
- **Text selection support** from active editor
- **Theme consistency** with VS Code color scheme
- **Keyboard shortcuts** for common actions

## ⚙️ **Configuration**

### **Backend Configuration** (`backend/main.py`)
```python
# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG_MODE = True

# LLM Configuration (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

### **Policy Configuration** (`policies/security_policies.yaml`)
```yaml
global_settings:
  strict_mode: true
  log_violations: true
  auto_block_critical: true
  environment: production

policies:
  prod_env_modification:
    name: "Production Environment Modification"
    description: "Prevents modification of production environment variables"
    severity: "critical"
    action: "block"
    enabled: true
    patterns:
      - 'os\.environ\["PROD_'
      - 'os\.environ\["PRODUCTION_'
    forbidden_env_vars:
      - "PROD_DATABASE_URL"
      - "PROD_API_KEY"
      - "PRODUCTION_SECRET"
    context_conditions:
      environment: production
    category: "environment"
    tags: ["production", "environment", "critical"]

  dangerous_libraries:
    name: "Dangerous Libraries"
    description: "Prevents usage of potentially dangerous libraries"
    severity: "high"
    action: "warn"
    enabled: true
    forbidden_imports:
      - "pickle"
      - "marshal"
      - "subprocess"
    allowed_exceptions:
      - "safe_pickle_usage.py"
    category: "libraries"
    tags: ["security", "libraries"]
```

### **CLI Configuration** (`~/.ai_firewall_config.json`)
```json
{
  "api_base_url": "http://localhost:8000",
  "color_mode": "auto",
  "output_format": "detailed",
  "session_logging": true,
  "auto_clear": false,
  "timeout": 30
}
```

### **VS Code Extension Settings** (`settings.json`)
```json
{
  "aiFirewall.enabled": true,
  "aiFirewall.apiEndpoint": "http://localhost:8000",
  "aiFirewall.autoAnalyze": false,
  "aiFirewall.severityLevel": "medium",
  "aiFirewall.showNotifications": true
}
```

## 🔧 **API Endpoints**

### **Core Analysis Endpoints**
```bash
# Policy-based analysis
POST /analyze-with-policies
{
  "code": "import os\nos.environ['PROD_KEY'] = 'secret'",
  "file_path": "config.py",
  "context": {"source": "copilot"}
}

# Security analysis
POST /analyze-ai-code
{
  "code": "import pickle\ndata = pickle.loads(user_input)",
  "source": "ai_assistant",
  "context": "Data loading function"
}

# Code explanation
POST /explain-code-simple
{
  "code": "def calculate_metrics(users):\n    return len(users)"
}
```

### **Policy Management Endpoints**
```bash
# Get all policies
GET /policies

# Create custom policy
POST /policies
{
  "rule_id": "custom_rule",
  "name": "Custom Security Rule",
  "description": "Custom security policy",
  "severity": "high",
  "action": "warn",
  "patterns": ["dangerous_pattern"],
  "enabled": true
}

# Get violation report
GET /policy-violations/report
```

## 📊 **Demo Screenshots**

### **CLI Interface**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🛡️  AI FIREWALL - CODE REVIEW CLI                       ║
║                         Secure AI Code Suggestions                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

📝 AI CODE SUGGESTION
────────────────────────────────────────────────────────────────────────────────
Source: copilot
File: utils/data_loader.py
Description: Load user data from file

💻 GENERATED CODE:
────────────────────────────────────────────────────────────
import pickle

def load_user_data(data_file):
    with open(data_file, 'rb') as f:
        user_data = pickle.load(f)  # Potentially dangerous!
    return user_data

api_key = "sk-1234567890abcdef1234567890abcdef"
────────────────────────────────────────────────────────────

🔍 SAFETY ANALYSIS:
────────────────────────────────────────────────────────────────────────────────
Safety Score: 0.25 (🔴 LOW)
Risk Level: 🔴 CRITICAL

⚠️  POLICY VIOLATIONS DETECTED:
  1. [CRITICAL] Dangerous Libraries
     📝 Prevents usage of potentially dangerous libraries
     📍 Line 1, 5
     🔍 Matched: 'import pickle', 'pickle.load(f)'
     💡 Suggestion: Use json or yaml for data serialization
     🚨 Action: block

  2. [CRITICAL] Secret Exposure
     📝 Detects hardcoded API keys and secrets
     📍 Line 9
     🔍 Matched: 'sk-1234567890abcdef1234567890abcdef'
     💡 Suggestion: Use environment variables for secrets
     🚨 Action: block

🤔 DECISION REQUIRED:
  ✅ [A] Accept - Use this code
  ❌ [R] Reject - Don't use this code  
  📖 [E] Explain - Get detailed explanation
  🔧 [M] Modify - Suggest improvements
  ⏭️  [S] Skip - Review later

This code is BLOCKED by security policies and cannot be accepted.
```

### **Web Dashboard**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🛡️ AI Firewall - Code Review Dashboard                                    │
│                    Secure AI Suggestions                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 💻 Code Suggestion Input                    📊 Safety Analysis             │
│                                             │                               │
│ ┌─────────────────────────────────────────┐ │  ┌─────┐                      │
│ │ Generated Code:                        │ │  │ 85% │ Safety Score          │
│ │ [Large textarea with syntax highlight] │ │  └─────┘ 🟢 LOW RISK         │
│ │                                         │ │                               │
│ │ Source: [Dropdown]                      │ │  ⚠️ Policy Violations (0)     │
│ │ File Path: [Input]                      │ │  📚 Code Explanation         │
│ │ Description: [Input]                    │ │  [Formatted explanation...]  │
│ │                                         │ │                               │
│ │ [🔍 Analyze] [🎯 Demo]                  │ │  ✅ Accept Code  ❌ Reject    │
│ └─────────────────────────────────────────┘ │                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **VS Code Extension**
```
┌─────────────────────────────────────────┐
│ 🛡️ AI FIREWALL                        │
│ Code Security Review                   │
├─────────────────────────────────────────┤
│                                         │
│ AI Generated Code:                      │
│ ┌─────────────────────────────────────┐ │
│ │ [Code textarea]                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Source: [Dropdown]                      │
│ Description: [Input]                    │
│                                         │
│ [🔍 Analyze] [📋 Get Selection]        │
│                                         │
├─────────────────────────────────────────┤
│ 📊 Analysis Results                     │
│                                         │
│ ┌─────┐                                │
│ │ 85% │ Safety Score                   │
│ └─────┘ 🟢 LOW RISK                   │
│                                         │
│ ⚠️ Violations: 0                       │
│ 📚 Explanation available                │
│                                         │
│ [✅ Accept] [❌ Reject]                 │
└─────────────────────────────────────────┘
```

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI Firewall Architecture                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   CLI UI    │    │  Web UI     │    │ VS Code UI  │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
│         │                   │                   │                          │
│         └───────────────────┼───────────────────┘                          │
│                             │                                             │
│                    ┌────────▼────────┐                                   │
│                    │   FastAPI       │                                   │
│                    │   Backend       │                                   │
│                    └────────┬────────┘                                   │
│                             │                                             │
│  ┌──────────────────────────┼──────────────────────────┐                  │
│  │                          │                          │                  │
│  ▼                          ▼                          ▼                  │
│ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│ │  Policy     │    │  Security   │    │   Code      │                    │
│ │  Engine     │    │  Analyzer   │    │ Explainer   │                    │
│ └─────────────┘    └─────────────┘    └─────────────┘                    │
│         │                   │                   │                          │
│         └───────────────────┼───────────────────┘                          │
│                             │                                             │
│                    ┌────────▼────────┐                                   │
│                    │   LLM APIs      │                                   │
│                    │ (OpenAI/Anthropic)                                 │
│                    └─────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 **Development**

### **Project Structure**
```
AIFirewall/
├── backend/                 # FastAPI backend
│   ├── main.py             # API endpoints
│   ├── policy_engine.py    # Policy enforcement
│   ├── security_analyzer.py # Security analysis
│   └── code_explainer.py   # LLM integration
├── policies/               # Security policy configs
│   ├── security_policies.yaml
│   └── example_config.json
├── ui/                     # Web interface
│   ├── index.html         # Main dashboard
│   └── static/app.js      # JavaScript module
├── vscode-extension/       # VS Code extension
│   ├── src/extension.ts   # Extension logic
│   └── src/webview.ts     # Webview provider
├── ai_firewall_cli.py     # CLI interface
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### **Running Tests**
```bash
# Test security analyzer
python3 test_security_analyzer.py

# Test policy engine
python3 test_policy_engine.py

# Test code explainer
python3 test_code_explainer.py

# API examples
python3 api_policy_example.py
```

### **Contributing**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **FastAPI** for the high-performance web framework
- **OpenAI & Anthropic** for LLM-powered explanations
- **VS Code Extension API** for editor integration
- **PyYAML** for flexible policy configuration

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/yourusername/AIFirewall/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/AIFirewall/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/AIFirewall/wiki)

---

**🛡️ Secure your AI-generated code with AI Firewall - because safety shouldn't be an afterthought!** 