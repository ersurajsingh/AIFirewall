import * as vscode from 'vscode';
import axios from 'axios';

export class AIFirewallWebviewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'aiFirewall.webview';
    private _view?: vscode.WebviewView;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(
            message => {
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
                    case 'getSelectedText':
                        this.sendSelectedText();
                        break;
                }
            },
            undefined,
            []
        );
    }

    private async analyzeCode(data: any) {
        try {
            const config = vscode.workspace.getConfiguration('aiFirewall');
            const apiEndpoint = config.get<string>('apiEndpoint', 'http://localhost:8000');

            // Perform policy analysis
            const policyResponse = await axios.post(`${apiEndpoint}/analyze-with-policies`, {
                code: data.code,
                file_path: data.filePath,
                context: {
                    source: data.source,
                    description: data.description
                }
            });

            // Perform security analysis
            const securityResponse = await axios.post(`${apiEndpoint}/analyze-ai-code`, {
                code: data.code,
                source: data.source,
                context: data.description
            });

            // Get code explanation
            const explanationResponse = await axios.post(`${apiEndpoint}/explain-code-simple`, {
                code: data.code
            });

            const analysisResult = {
                policyData: policyResponse.data,
                securityData: securityResponse.data,
                explanationData: explanationResponse.data
            };

            this._view?.webview.postMessage({
                command: 'analysisResult',
                data: analysisResult
            });

        } catch (error) {
            this._view?.webview.postMessage({
                command: 'analysisError',
                data: { error: (error as Error).message }
            });
        }
    }

    private async acceptCode(data: any) {
        // Log the accepted code
        const logMessage = `✅ AI Firewall: Code accepted - ${data.source} suggestion`;
        vscode.window.showInformationMessage(logMessage);
        
        // Insert code at cursor position if requested
        const editor = vscode.window.activeTextEditor;
        if (editor && data.insertCode) {
            editor.edit(editBuilder => {
                editBuilder.insert(editor.selection.active, data.code);
            });
        }
    }

    private async rejectCode(data: any) {
        const reason = data.reason || 'Security concerns';
        const logMessage = `❌ AI Firewall: Code rejected - ${reason}`;
        vscode.window.showWarningMessage(logMessage);
    }

    private sendSelectedText() {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const selection = editor.selection;
            const selectedText = editor.document.getText(selection);
            
            // Get file path
            const filePath = editor.document.fileName;
            
            this._view?.webview.postMessage({
                command: 'selectedText',
                data: {
                    code: selectedText,
                    filePath: filePath
                }
            });
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Firewall</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            margin: 0;
            padding: 16px;
        }

        .container {
            max-width: 100%;
        }

        .header {
            text-align: center;
            margin-bottom: 20px;
            padding: 16px 0;
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .header h1 {
            margin: 0;
            font-size: 1.4em;
            color: var(--vscode-textLink-foreground);
        }

        .input-section {
            margin-bottom: 20px;
        }

        .input-group {
            margin-bottom: 12px;
        }

        label {
            display: block;
            margin-bottom: 4px;
            font-weight: bold;
            color: var(--vscode-input-foreground);
        }

        textarea, input, select {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--vscode-input-border);
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            font-family: var(--vscode-editor-font-family);
            font-size: var(--vscode-editor-font-size);
            border-radius: 2px;
            box-sizing: border-box;
        }

        textarea {
            min-height: 120px;
            resize: vertical;
        }

        .button-group {
            display: flex;
            gap: 8px;
            margin: 12px 0;
            flex-wrap: wrap;
        }

        button {
            padding: 8px 16px;
            border: none;
            border-radius: 2px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            flex: 1;
            min-width: 100px;
        }

        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .btn-accept {
            background-color: var(--vscode-testing-iconPassed);
            color: white;
        }

        .btn-reject {
            background-color: var(--vscode-testing-iconFailed);
            color: white;
        }

        .analysis-result {
            margin-top: 20px;
            padding: 16px;
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            background-color: var(--vscode-editor-inactiveSelectionBackground);
        }

        .safety-score {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }

        .score-circle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 14px;
        }

        .score-high { background-color: var(--vscode-testing-iconPassed); }
        .score-medium { background-color: var(--vscode-testing-iconQueued); }
        .score-low { background-color: var(--vscode-testing-iconFailed); }

        .risk-level {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            display: inline-block;
        }

        .risk-low { 
            background-color: var(--vscode-testing-iconPassed); 
            color: white; 
        }
        .risk-medium { 
            background-color: var(--vscode-testing-iconQueued); 
            color: var(--vscode-editor-background); 
        }
        .risk-high, .risk-critical { 
            background-color: var(--vscode-testing-iconFailed); 
            color: white; 
        }

        .violations {
            margin-top: 16px;
        }

        .violation-item {
            background-color: var(--vscode-editor-background);
            border-left: 3px solid var(--vscode-testing-iconFailed);
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 0 4px 4px 0;
        }

        .violation-severity {
            font-weight: bold;
            font-size: 11px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .severity-critical { color: var(--vscode-testing-iconFailed); }
        .severity-high { color: var(--vscode-testing-iconQueued); }
        .severity-medium { color: var(--vscode-testing-iconQueued); }
        .severity-low { color: var(--vscode-testing-iconPassed); }

        .explanation {
            background-color: var(--vscode-textCodeBlock-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            padding: 12px;
            margin-top: 16px;
            font-family: var(--vscode-editor-font-family);
            font-size: 12px;
            line-height: 1.5;
            max-height: 200px;
            overflow-y: auto;
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: var(--vscode-descriptionForeground);
        }

        .blocked-notice {
            background-color: var(--vscode-inputValidation-errorBackground);
            color: var(--vscode-inputValidation-errorForeground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 16px;
            font-weight: bold;
        }

        .decision-section {
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid var(--vscode-panel-border);
        }

        .status-message {
            padding: 8px 12px;
            border-radius: 4px;
            margin-bottom: 12px;
            font-size: 12px;
        }

        .status-success {
            background-color: var(--vscode-testing-iconPassed);
            color: white;
        }

        .status-error {
            background-color: var(--vscode-testing-iconFailed);
            color: white;
        }

        .status-warning {
            background-color: var(--vscode-testing-iconQueued);
            color: var(--vscode-editor-background);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ AI Firewall</h1>
            <p>Code Security Review</p>
        </div>

        <div class="input-section">
            <div class="input-group">
                <label for="codeInput">AI Generated Code:</label>
                <textarea id="codeInput" placeholder="Paste AI-generated code here..."></textarea>
            </div>

            <div class="input-group">
                <label for="sourceInput">Source:</label>
                <select id="sourceInput">
                    <option value="copilot">GitHub Copilot</option>
                    <option value="ai_assistant">AI Assistant</option>
                    <option value="tabnine">TabNine</option>
                    <option value="codewhisperer">CodeWhisperer</option>
                    <option value="other">Other</option>
                </select>
            </div>

            <div class="input-group">
                <label for="descriptionInput">Description:</label>
                <input type="text" id="descriptionInput" placeholder="What does this code do?">
            </div>

            <div class="button-group">
                <button onclick="analyzeCode()" id="analyzeBtn">🔍 Analyze</button>
                <button onclick="getSelectedText()">📋 Get Selection</button>
                <button onclick="loadDemo()">🎯 Demo</button>
            </div>

            <div id="statusMessage"></div>
        </div>

        <div id="analysisContent"></div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let currentAnalysis = null;

        // Listen for messages from the extension
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.command) {
                case 'analysisResult':
                    displayAnalysis(message.data);
                    break;
                case 'analysisError':
                    showError(message.data.error);
                    break;
                case 'selectedText':
                    loadSelectedText(message.data);
                    break;
            }
        });

        function analyzeCode() {
            const code = document.getElementById('codeInput').value.trim();
            if (!code) {
                showStatus('Please enter some code to analyze', 'warning');
                return;
            }

            const source = document.getElementById('sourceInput').value;
            const description = document.getElementById('descriptionInput').value.trim();

            showLoading();

            vscode.postMessage({
                command: 'analyzeCode',
                data: {
                    code: code,
                    source: source,
                    description: description
                }
            });
        }

        function displayAnalysis(analysis) {
            const { policyData, securityData, explanationData } = analysis;
            
            currentAnalysis = analysis;
            
            const safetyScore = securityData.safety_score || 0.5;
            const riskLevel = policyData.risk_level || securityData.risk_level || 'MEDIUM';
            const violations = policyData.violations || [];
            const blocked = policyData.blocked || securityData.blocked || false;
            const explanation = explanationData.explanation || 'No explanation available';

            let scoreClass = 'score-medium';
            if (safetyScore >= 0.7) scoreClass = 'score-high';
            else if (safetyScore < 0.4) scoreClass = 'score-low';

            const riskClass = \`risk-\${riskLevel.toLowerCase()}\`;

            let html = \`
                <div class="analysis-result">
                    <div class="safety-score">
                        <div class="score-circle \${scoreClass}">
                            \${(safetyScore * 100).toFixed(0)}%
                        </div>
                        <div>
                            <div><strong>Safety Score</strong></div>
                            <div class="risk-level \${riskClass}">
                                \${riskLevel} RISK
                            </div>
                        </div>
                    </div>
            \`;

            if (blocked) {
                html += \`
                    <div class="blocked-notice">
                        🚫 BLOCKED - This code is prevented by security policies
                    </div>
                \`;
            }

            if (violations.length > 0) {
                html += \`
                    <div class="violations">
                        <h4>⚠️ Policy Violations (\${violations.length})</h4>
                \`;
                
                violations.forEach(violation => {
                    html += \`
                        <div class="violation-item">
                            <div class="violation-severity severity-\${violation.severity}">
                                \${violation.severity.toUpperCase()} - \${violation.rule_name}
                            </div>
                            <div>\${violation.description}</div>
                            \${violation.suggestion ? \`<div style="margin-top: 8px; font-style: italic;">💡 \${violation.suggestion}</div>\` : ''}
                        </div>
                    \`;
                });
                
                html += \`</div>\`;
            }

            if (explanation && explanation !== 'No explanation available') {
                const truncatedExplanation = explanation.length > 300 ? 
                    explanation.substring(0, 300) + '...' : explanation;
                    
                html += \`
                    <div class="explanation">
                        <h4>📚 Code Explanation</h4>
                        <div>\${truncatedExplanation}</div>
                    </div>
                \`;
            }

            html += \`
                <div class="decision-section">
                    <div class="button-group">
            \`;

            if (!blocked) {
                html += \`
                        <button class="btn-accept" onclick="acceptCode()">✅ Accept</button>
                        <button class="btn-reject" onclick="rejectCode()">❌ Reject</button>
                \`;
            } else {
                html += \`
                        <button onclick="acknowledgeBlock()">📝 Acknowledge</button>
                \`;
            }

            html += \`
                    </div>
                </div>
            </div>
            \`;

            document.getElementById('analysisContent').innerHTML = html;
        }

        function acceptCode() {
            if (!currentAnalysis) return;
            
            vscode.postMessage({
                command: 'acceptCode',
                data: {
                    code: document.getElementById('codeInput').value,
                    source: document.getElementById('sourceInput').value,
                    insertCode: true
                }
            });
            
            showStatus('✅ Code accepted!', 'success');
            clearForm();
        }

        function rejectCode() {
            if (!currentAnalysis) return;
            
            const reason = 'Security concerns identified by AI Firewall';
            
            vscode.postMessage({
                command: 'rejectCode',
                data: {
                    code: document.getElementById('codeInput').value,
                    source: document.getElementById('sourceInput').value,
                    reason: reason
                }
            });
            
            showStatus('❌ Code rejected!', 'error');
            clearForm();
        }

        function acknowledgeBlock() {
            showStatus('🚫 Block acknowledged', 'warning');
            clearForm();
        }

        function getSelectedText() {
            vscode.postMessage({ command: 'getSelectedText' });
        }

        function loadSelectedText(data) {
            document.getElementById('codeInput').value = data.code;
            showStatus('📋 Selected text loaded', 'success');
        }

        function loadDemo() {
            const demoCode = \`import os
os.environ["PROD_DATABASE_URL"] = "postgresql://admin:secret@prod/db"
print("Production database configured")\`;
            
            document.getElementById('codeInput').value = demoCode;
            document.getElementById('sourceInput').value = 'ai_assistant';
            document.getElementById('descriptionInput').value = 'Configure production database';
            
            showStatus('🎯 Demo code loaded', 'success');
        }

        function showLoading() {
            document.getElementById('analysisContent').innerHTML = \`
                <div class="loading">
                    <p>🔍 Analyzing code for security issues...</p>
                </div>
            \`;
        }

        function showError(error) {
            document.getElementById('analysisContent').innerHTML = \`
                <div style="color: var(--vscode-testing-iconFailed); text-align: center; padding: 20px;">
                    <h3>❌ Analysis Failed</h3>
                    <p>Error: \${error}</p>
                    <p>Make sure the AI Firewall backend is running</p>
                </div>
            \`;
        }

        function showStatus(message, type) {
            const statusElement = document.getElementById('statusMessage');
            statusElement.innerHTML = \`<div class="status-message status-\${type}">\${message}</div>\`;
            
            setTimeout(() => {
                statusElement.innerHTML = '';
            }, 3000);
        }

        function clearForm() {
            document.getElementById('codeInput').value = '';
            document.getElementById('descriptionInput').value = '';
            currentAnalysis = null;
            
            setTimeout(() => {
                document.getElementById('analysisContent').innerHTML = '';
            }, 2000);
        }
    </script>
</body>
</html>`;
    }
} 