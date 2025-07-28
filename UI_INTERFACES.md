# 🖥️ AI Firewall UI Interfaces

Comprehensive user interfaces for reviewing AI code suggestions with safety analysis, explanations, and accept/reject functionality.

## 🎯 Overview

The AI Firewall provides three different user interface options:

1. **🖥️ Interactive CLI** - Command-line interface for terminal-based reviews
2. **🌐 Web Dashboard** - Modern web interface for browser-based analysis  
3. **📝 VS Code Webview** - Integrated panel within VS Code editor

All interfaces provide the same core functionality:
- **Code suggestion input** with context information
- **Comprehensive safety analysis** using policy engine and security analyzer
- **Real-time explanations** powered by LLMs
- **Accept/reject decisions** with logging and reporting
- **Session tracking** for review history

---

## 🖥️ Interactive CLI Interface

### **Features:**
- **Colorful terminal output** with ANSI colors and emojis
- **Interactive prompts** for decision making
- **Real-time analysis** with both API and local mode support
- **Session logging** with comprehensive reporting
- **Demo mode** with pre-built dangerous code examples

### **Usage:**

```bash
# Run interactive mode (default)
python3 ai_firewall_cli.py

# Run with demo examples
python3 ai_firewall_cli.py demo

# Show help
python3 ai_firewall_cli.py help
```

### **Interactive Commands:**
- `quit` - Exit the CLI
- `demo` - Load demo suggestions
- `summary` - Show session summary

### **Example Workflow:**

```bash
$ python3 ai_firewall_cli.py

╔══════════════════════════════════════════════════════════════════════════════╗
║                    🛡️  AI FIREWALL - CODE REVIEW CLI                     ║
║                         Secure AI Code Suggestions                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

🔄 INTERACTIVE MODE
Enter code suggestions for review. Type 'quit' to exit.

Enter code to review:
(Type 'quit' to exit, 'demo' for examples, 'summary' for session summary)

Code (press Ctrl+D or Enter twice to finish):
import os
os.environ["PROD_API_KEY"] = "secret123"

File path (optional): config.py
Description (optional): Set production API key

🔍 TESTING: Production Environment Modification
════════════════════════════════════════════════════════════════════════════════
CODE:
────────────────────────────────────────────────────────────────────────────────
import os
os.environ["PROD_API_KEY"] = "secret123"
────────────────────────────────────────────────────────────────────────────────

📊 POLICY ANALYSIS RESULT:
Total Violations: 1

⚠️  POLICY VIOLATIONS DETECTED:
  1. [CRITICAL] Production Environment Modification
     📝 Prevents modification of production environment variables
     📍 Line 2
     🔍 Matched: 'os.environ["PROD_API_KEY"]'
     💡 Suggestion: Use environment-specific configuration files
     🚨 Action: block

🤔 DECISION REQUIRED:
────────────────────────────────────────────────────────────────────────────────
  [A] Accept - Use this code
  [R] Reject - Don't use this code  
  [E] Explain - Get detailed explanation
  [M] Modify - Suggest improvements
  [S] Skip - Review later

This code is BLOCKED by security policies and cannot be accepted.

Press Enter to continue...
```

### **Key CLI Features:**

#### **🎨 Rich Visual Output:**
- Color-coded risk levels (GREEN/YELLOW/RED)
- Structured violation reports with line numbers
- Safety scores with visual indicators
- Session summaries with statistics

#### **🔄 Flexible Analysis Modes:**
- **API Mode**: Full analysis via backend REST API
- **Local Mode**: Direct analysis using imported Python modules
- **Fallback Mode**: Basic analysis when both unavailable

#### **📊 Comprehensive Reporting:**
```bash
📊 SESSION SUMMARY
────────────────────────────────────────────────────────────────────────────────
Total suggestions reviewed: 5
✅ Accepted: 2
❌ Rejected: 2
Other actions: 1

Acceptance rate: 40.0%

🔍 Risk Level Distribution:
  🟢 LOW: 1
  🟡 MEDIUM: 1  
  🟠 HIGH: 2
  🔴 CRITICAL: 1
```

---

## 🌐 Web Dashboard Interface

### **Features:**
- **Modern responsive design** with gradient backgrounds
- **Real-time API status** monitoring
- **Interactive code editor** with syntax highlighting
- **Comprehensive analysis display** with visual safety scores
- **Modal dialogs** for detailed explanations
- **Session logging** with exportable history

### **Access:**
Open `ui/index.html` in any modern web browser.

### **Interface Components:**

#### **🎛️ Input Panel:**
```html
<!-- Code Suggestion Input -->
- Code textarea with auto-resize
- Source dropdown (AI Assistant, Copilot, TabNine, etc.)
- File path input (optional)
- Description input (optional)
- Analysis and Demo buttons
```

#### **📊 Analysis Panel:**
```html
<!-- Safety Analysis Display -->
- Circular safety score indicator (0-100%)
- Color-coded risk level badges
- Detailed violation list with severity levels
- Code explanation with markdown formatting
- Accept/Reject decision buttons
```

#### **📋 Session Log:**
```html
<!-- Review History -->
- Session summary statistics
- Recent decisions with timestamps
- Risk level distribution
- Filterable entry list
```

### **API Integration:**

The web interface communicates with the backend via REST API:

```javascript
// Comprehensive analysis pipeline
const analysisResults = await Promise.all([
    fetch('/analyze-with-policies', { method: 'POST', body: requestData }),
    fetch('/analyze-ai-code', { method: 'POST', body: requestData }),
    fetch('/explain-code-simple', { method: 'POST', body: requestData })
]);

// Display combined results
displayAnalysis({
    policyData: responses[0],
    securityData: responses[1], 
    explanationData: responses[2]
});
```

### **Example Screenshots:**

#### **Main Dashboard:**
```
╔══════════════════════════════════════════════════════════════════════╗
║                        🛡️ AI Firewall                              ║
║                   Code Review Dashboard                              ║
║                   Secure AI Suggestions                             ║
╚══════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────┬─────────────────────────────────────────┐
│ 💻 Code Suggestion Input    │ 📊 Safety Analysis                     │
│                             │                                         │
│ ┌─────────────────────────┐ │  ┌─────┐                                │
│ │ Generated Code:         │ │  │ 85% │ Safety Score                   │
│ │ [Large textarea]        │ │  └─────┘ 🟢 LOW RISK                  │
│ │                         │ │                                         │
│ │ Source: [Dropdown]      │ │  ⚠️ Policy Violations (0)              │
│ │ File Path: [Input]      │ │  📚 Code Explanation                   │
│ │ Description: [Input]    │ │  [Formatted explanation text...]       │
│ │                         │ │                                         │
│ │ [🔍 Analyze] [🎯 Demo]  │ │  ✅ Accept Code  ❌ Reject Code        │
│ └─────────────────────────┘ │                                         │
└─────────────────────────────┴─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 📋 Review Session Log                                              │
│                                                                     │
│ Session Summary: Total: 3 | Accepted: 2 | Rejected: 1             │
│                                                                     │
│ [Recent review entries with timestamps and decisions...]            │
└─────────────────────────────────────────────────────────────────────┘
```

### **Advanced Features:**

#### **🔄 Real-time Status:**
```javascript
// API health monitoring
const statusElement = document.getElementById('apiStatus');
checkApiStatus().then(online => {
    statusElement.textContent = online ? '✅ API Online' : '❌ API Offline';
    statusElement.className = `status-indicator status-${online ? 'online' : 'offline'}`;
});
```

#### **💾 Session Persistence:**
```javascript
// Local storage for session data
localStorage.setItem('aiFirewallSession', JSON.stringify({
    sessionData: this.reviewHistory,
    settings: this.userSettings,
    timestamp: new Date().toISOString()
}));
```

#### **🎯 Demo Integration:**
```javascript
// Load random demo examples
const demoExamples = [
    { code: "dangerous_code_1", risk: "CRITICAL" },
    { code: "dangerous_code_2", risk: "HIGH" },
    { code: "safe_code_example", risk: "LOW" }
];
```

---

## 📝 VS Code Webview Interface

### **Features:**
- **Native VS Code integration** within the Explorer panel
- **Theme consistency** with VS Code's color scheme
- **Text selection support** from active editor
- **Keyboard shortcuts** for common actions
- **Extension settings** integration

### **Installation:**

1. **Open VS Code Extension Development:**
```bash
cd vscode-extension
npm install
npm run compile
```

2. **Debug Extension:**
- Open `vscode-extension` folder in VS Code
- Press `F5` to launch Extension Development Host
- AI Firewall panel appears in Explorer sidebar

### **Interface Layout:**

```
┌─────────────────────────────┐
│ 🛡️ AI FIREWALL             │
│ Code Security Review        │
├─────────────────────────────┤
│                             │
│ AI Generated Code:          │
│ ┌─────────────────────────┐ │
│ │ [Code textarea]         │ │
│ └─────────────────────────┘ │
│                             │
│ Source: [Dropdown]          │
│ Description: [Input]        │
│                             │
│ [🔍 Analyze] [📋 Get        │
│               Selection]    │
│                             │
├─────────────────────────────┤
│ 📊 Analysis Results         │
│                             │
│ ┌─────┐                     │
│ │ 85% │ Safety Score        │
│ └─────┘ 🟢 LOW RISK        │
│                             │
│ ⚠️ Violations: 0            │
│ 📚 Explanation available    │
│                             │
│ [✅ Accept] [❌ Reject]     │
└─────────────────────────────┘
```

### **VS Code Integration:**

#### **🎯 Text Selection:**
```typescript
// Get selected text from active editor
private sendSelectedText() {
    const editor = vscode.window.activeTextEditor;
    if (editor) {
        const selection = editor.selection;
        const selectedText = editor.document.getText(selection);
        
        this._view?.webview.postMessage({
            command: 'selectedText',
            data: { code: selectedText, filePath: editor.document.fileName }
        });
    }
}
```

#### **💬 Message Handling:**
```typescript
// Handle webview messages
webviewView.webview.onDidReceiveMessage(message => {
    switch (message.command) {
        case 'analyzeCode':
            this.analyzeCode(message.data);
            break;
        case 'acceptCode':
            this.acceptCode(message.data);
            break;
        case 'rejectCode':
            this.rejectCode(message.data);
            break;
    }
});
```

#### **⚙️ Settings Integration:**
```json
{
    "aiFirewall.enabled": {
        "type": "boolean",
        "default": true,
        "description": "Enable AI Firewall analysis"
    },
    "aiFirewall.apiEndpoint": {
        "type": "string", 
        "default": "http://localhost:8000",
        "description": "AI Firewall API endpoint URL"
    },
    "aiFirewall.autoAnalyze": {
        "type": "boolean",
        "default": false,
        "description": "Automatically analyze code on save"
    }
}
```

### **Webview Communication:**

#### **Frontend (Webview HTML):**
```javascript
// Send analysis request to extension
function analyzeCode() {
    const code = document.getElementById('codeInput').value;
    
    vscode.postMessage({
        command: 'analyzeCode',
        data: {
            code: code,
            source: 'copilot',
            description: 'AI generated suggestion'
        }
    });
}

// Receive analysis results
window.addEventListener('message', event => {
    const message = event.data;
    
    switch (message.command) {
        case 'analysisResult':
            displayAnalysis(message.data);
            break;
        case 'analysisError':
            showError(message.data.error);
            break;
    }
});
```

#### **Backend (Extension Host):**
```typescript
// Process analysis request
private async analyzeCode(data: any) {
    try {
        const config = vscode.workspace.getConfiguration('aiFirewall');
        const apiEndpoint = config.get<string>('apiEndpoint');

        const response = await axios.post(`${apiEndpoint}/analyze-with-policies`, {
            code: data.code,
            file_path: data.filePath,
            context: { source: data.source }
        });

        this._view?.webview.postMessage({
            command: 'analysisResult',
            data: response.data
        });

    } catch (error) {
        this._view?.webview.postMessage({
            command: 'analysisError', 
            data: { error: error.message }
        });
    }
}
```

---

## 🔄 Common Workflows

### **1. Review AI Code Suggestion:**

#### **CLI Workflow:**
```bash
1. Start CLI: python3 ai_firewall_cli.py
2. Paste AI-generated code
3. Add context (file path, description)
4. Review analysis results
5. Make decision (Accept/Reject/Explain)
6. View session summary
```

#### **Web Workflow:**
```bash
1. Open ui/index.html in browser
2. Check API status indicator
3. Input code in textarea
4. Select source and add context
5. Click "Analyze Code"
6. Review safety score and violations  
7. Click Accept/Reject buttons
8. View session log
```

#### **VS Code Workflow:**
```bash
1. Open AI Firewall panel in Explorer
2. Select code in editor
3. Click "Get Selection" button
4. Add description and select source
5. Click "Analyze" button
6. Review results in panel
7. Accept/Reject with automatic insertion
```

### **2. Demo Mode Usage:**

All interfaces support demo mode with pre-built examples:

```python
# Demo examples included:
dangerous_examples = [
    "Production environment modification",
    "Unsafe pickle deserialization", 
    "Hardcoded API keys and secrets",
    "Destructive file operations",
    "SQL injection vulnerabilities"
]

safe_examples = [
    "Parameterized database queries",
    "Environment variable usage",
    "JSON data serialization",
    "Secure file operations"
]
```

### **3. Batch Analysis:**

#### **CLI Batch Mode:**
```python
suggestions = [
    CodeSuggestion(code="...", source="copilot"),
    CodeSuggestion(code="...", source="ai_assistant"),
    CodeSuggestion(code="...", source="tabnine")
]

cli.batch_review(suggestions)
```

#### **Web Batch Processing:**
```javascript
// Process multiple suggestions
const suggestions = loadFromFile();
for (const suggestion of suggestions) {
    const analysis = await analyzeCode(suggestion);
    logDecision(suggestion, analysis);
}
```

---

## 🎨 Customization Options

### **CLI Customization:**

#### **Color Themes:**
```python
class Colors:
    HEADER = '\033[95m'     # Purple
    OKGREEN = '\033[92m'    # Green  
    WARNING = '\033[93m'    # Yellow
    FAIL = '\033[91m'       # Red
    
# Custom color scheme
CUSTOM_COLORS = {
    "success": "\033[92m",
    "warning": "\033[93m", 
    "error": "\033[91m",
    "info": "\033[94m"
}
```

#### **Output Formatting:**
```python
def print_analysis_result(title, code, violations):
    print(f"\n{'='*80}")
    print(f"🔍 TESTING: {title}")
    print(f"{'='*80}")
    # Custom formatting logic...
```

### **Web Interface Customization:**

#### **CSS Themes:**
```css
/* Custom theme variables */
:root {
    --primary-color: #667eea;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --background-color: #1a1a1a;
        --text-color: #ffffff;
        --panel-background: #2d2d2d;
    }
}
```

#### **Layout Options:**
```css
/* Responsive layouts */
@media (max-width: 768px) {
    .main-content {
        grid-template-columns: 1fr;
        gap: 20px;
    }
}

/* Compact mode */
.compact-mode .analysis-panel {
    padding: 15px;
    font-size: 0.9em;
}
```

### **VS Code Theme Integration:**

#### **VS Code Variables:**
```css
/* Use VS Code theme colors */
body {
    background-color: var(--vscode-editor-background);
    color: var(--vscode-editor-foreground);
    font-family: var(--vscode-font-family);
}

.risk-critical {
    color: var(--vscode-testing-iconFailed);
}

.risk-low {
    color: var(--vscode-testing-iconPassed);
}
```

---

## 🔧 Configuration

### **Environment Variables:**
```bash
# API Configuration
export AI_FIREWALL_API_URL="http://localhost:8000"
export AI_FIREWALL_TIMEOUT="30"

# Analysis Configuration  
export AI_FIREWALL_STRICT_MODE="true"
export AI_FIREWALL_LOG_LEVEL="INFO"

# LLM Configuration
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### **CLI Configuration:**
```python
# ~/.ai_firewall_config.json
{
    "api_base_url": "http://localhost:8000",
    "color_mode": "auto",
    "output_format": "detailed",
    "session_logging": true,
    "auto_clear": false
}
```

### **Web Configuration:**
```javascript
// Local storage settings
const settings = {
    apiBaseUrl: "http://localhost:8000",
    theme: "auto",
    autoAnalyze: false,
    sessionPersistence: true
};
```

### **VS Code Configuration:**
```json
{
    "aiFirewall.enabled": true,
    "aiFirewall.apiEndpoint": "http://localhost:8000", 
    "aiFirewall.autoAnalyze": false,
    "aiFirewall.severityLevel": "medium",
    "aiFirewall.showNotifications": true
}
```

---

## 🚀 Getting Started

### **Quick Start - CLI:**
```bash
# 1. Start backend
./start.sh

# 2. Run CLI demo
python3 ai_firewall_cli.py demo

# 3. Try interactive mode
python3 ai_firewall_cli.py
```

### **Quick Start - Web:**
```bash
# 1. Start backend
./start.sh

# 2. Open web interface
open ui/index.html

# 3. Try demo examples
click "Load Demo" button
```

### **Quick Start - VS Code:**
```bash
# 1. Start backend
./start.sh

# 2. Open VS Code
cd vscode-extension && code .

# 3. Launch extension (F5)
# 4. Use AI Firewall panel in Explorer
```

---

## 📊 Comparison Matrix

| Feature | CLI | Web | VS Code |
|---------|-----|-----|---------|
| **Ease of Use** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Integration** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Visual Appeal** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Batch Processing** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Customization** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Offline Support** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |

The AI Firewall UI interfaces provide comprehensive, user-friendly ways to review AI code suggestions with advanced security analysis. Choose the interface that best fits your workflow and development environment! 