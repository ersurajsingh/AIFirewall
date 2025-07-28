// AI Firewall Web Interface - Main Application Module
class AIFirewallApp {
    constructor() {
        this.apiBaseUrl = window.location.origin.replace(':3000', ':8000'); // Development adjustment
        this.currentAnalysis = null;
        this.sessionData = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkApiStatus();
        this.loadSettings();
    }

    setupEventListeners() {
        // Analysis button
        document.getElementById('analyzeBtn')?.addEventListener('click', () => this.analyzeCode());
        
        // Demo button
        document.getElementById('demoBtn')?.addEventListener('click', () => this.loadDemoCode());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'Enter':
                        e.preventDefault();
                        this.analyzeCode();
                        break;
                    case 'd':
                        e.preventDefault();
                        this.loadDemoCode();
                        break;
                }
            }
        });

        // Auto-resize textarea
        const codeInput = document.getElementById('codeInput');
        if (codeInput) {
            codeInput.addEventListener('input', this.autoResizeTextarea);
        }
    }

    autoResizeTextarea(event) {
        const textarea = event.target;
        textarea.style.height = 'auto';
        textarea.style.height = Math.max(200, textarea.scrollHeight) + 'px';
    }

    async checkApiStatus() {
        const statusElement = document.getElementById('apiStatus');
        if (!statusElement) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            if (response.ok) {
                statusElement.textContent = '✅ API Online';
                statusElement.className = 'status-indicator status-online';
            } else {
                throw new Error('API not healthy');
            }
        } catch (error) {
            statusElement.textContent = '❌ API Offline';
            statusElement.className = 'status-indicator status-offline';
            this.showNotification('Backend API is offline. Start with: ./start.sh', 'error');
        }
        
        // Hide status after 3 seconds
        setTimeout(() => {
            statusElement.style.display = 'none';
        }, 3000);
    }

    async analyzeCode() {
        const code = document.getElementById('codeInput')?.value.trim();
        if (!code) {
            this.showNotification('Please enter some code to analyze', 'warning');
            return;
        }

        const source = document.getElementById('sourceInput')?.value || 'unknown';
        const filePath = document.getElementById('filePathInput')?.value.trim() || null;
        const description = document.getElementById('descriptionInput')?.value.trim() || null;

        this.showLoading();
        this.disableAnalyzeButton();
        
        try {
            // Perform comprehensive analysis
            const analysisResults = await this.performComprehensiveAnalysis({
                code,
                source,
                filePath,
                description
            });

            this.currentAnalysis = {
                code,
                source,
                filePath,
                description,
                ...analysisResults,
                timestamp: new Date().toISOString()
            };

            this.displayAnalysis(this.currentAnalysis);
            this.showNotification('Analysis completed successfully', 'success');

        } catch (error) {
            console.error('Analysis failed:', error);
            this.showError(error.message);
            this.showNotification('Analysis failed: ' + error.message, 'error');
        } finally {
            this.enableAnalyzeButton();
        }
    }

    async performComprehensiveAnalysis(requestData) {
        const requests = [
            this.fetchAnalysis('/analyze-with-policies', requestData),
            this.fetchAnalysis('/analyze-ai-code', {
                code: requestData.code,
                source: requestData.source,
                context: requestData.description
            }),
            this.fetchAnalysis('/explain-code-simple', {
                code: requestData.code
            })
        ];

        const [policyData, securityData, explanationData] = await Promise.all(requests);

        return {
            policyData: policyData || {},
            securityData: securityData || {},
            explanationData: explanationData || {}
        };
    }

    async fetchAnalysis(endpoint, data) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...data,
                    context: {
                        ...data.context,
                        timestamp: new Date().toISOString(),
                        user_agent: navigator.userAgent
                    }
                })
            });

            if (!response.ok) {
                throw new Error(`${endpoint} failed: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.warn(`${endpoint} request failed:`, error);
            return null;
        }
    }

    displayAnalysis(analysis) {
        const { policyData, securityData, explanationData } = analysis;
        
        // Calculate combined metrics
        const safetyScore = securityData.safety_score || 0.5;
        const riskLevel = policyData.risk_level || securityData.risk_level || 'MEDIUM';
        const violations = policyData.violations || [];
        const blocked = policyData.blocked || securityData.blocked || false;
        const explanation = explanationData.explanation || 'No explanation available';

        const analysisElement = document.getElementById('analysisContent');
        if (!analysisElement) return;

        analysisElement.innerHTML = this.generateAnalysisHTML({
            safetyScore,
            riskLevel,
            violations,
            blocked,
            explanation
        });

        // Add event listeners to decision buttons
        this.setupDecisionButtons(blocked);
    }

    generateAnalysisHTML({ safetyScore, riskLevel, violations, blocked, explanation }) {
        const scoreClass = this.getScoreClass(safetyScore);
        const riskClass = `risk-${riskLevel.toLowerCase()}`;

        let html = `
            <div class="analysis-result">
                <div class="safety-score">
                    <div class="score-circle ${scoreClass}">
                        ${(safetyScore * 100).toFixed(0)}%
                    </div>
                    <div>
                        <h3>Safety Score</h3>
                        <div class="risk-level ${riskClass}">
                            ${riskLevel} RISK
                        </div>
                    </div>
                </div>
        `;

        if (blocked) {
            html += `
                <div class="blocked-notice">
                    🚫 BLOCKED - This code is prevented by security policies and cannot be accepted
                </div>
            `;
        }

        if (violations.length > 0) {
            html += this.generateViolationsHTML(violations);
        }

        if (explanation && explanation !== 'No explanation available') {
            html += this.generateExplanationHTML(explanation);
        }

        html += this.generateDecisionButtonsHTML(blocked);
        html += `</div>`;

        return html;
    }

    generateViolationsHTML(violations) {
        let html = `
            <div class="violations">
                <h4>⚠️ Policy Violations (${violations.length})</h4>
        `;
        
        violations.forEach(violation => {
            html += `
                <div class="violation-item">
                    <div class="violation-severity severity-${violation.severity}">
                        ${violation.severity.toUpperCase()} - ${violation.rule_name}
                    </div>
                    <div class="violation-description">${violation.description}</div>
                    ${violation.suggestion ? `<div class="violation-suggestion">💡 ${violation.suggestion}</div>` : ''}
                </div>
            `;
        });
        
        html += `</div>`;
        return html;
    }

    generateExplanationHTML(explanation) {
        const truncatedExplanation = explanation.length > 500 ? 
            explanation.substring(0, 500) + '...\n[Click "Detailed Explanation" for full analysis]' : 
            explanation;
            
        return `
            <div class="explanation">
                <h4>📚 Code Explanation</h4>
                <div class="explanation-content">${this.formatExplanation(truncatedExplanation)}</div>
            </div>
        `;
    }

    generateDecisionButtonsHTML(blocked) {
        if (blocked) {
            return `
                <div class="decision-buttons">
                    <button class="btn btn-secondary" onclick="app.acknowledgeBlock()">
                        📝 Acknowledge Block
                    </button>
                    <button class="btn" onclick="app.getDetailedExplanation()">
                        📖 Detailed Explanation
                    </button>
                </div>
            `;
        } else {
            return `
                <div class="decision-buttons">
                    <button class="btn btn-accept" onclick="app.acceptCode()">
                        ✅ Accept Code
                    </button>
                    <button class="btn btn-reject" onclick="app.rejectCode()">
                        ❌ Reject Code
                    </button>
                    <button class="btn" onclick="app.getDetailedExplanation()">
                        📖 Detailed Explanation
                    </button>
                    <button class="btn btn-secondary" onclick="app.suggestImprovements()">
                        🔧 Suggest Improvements
                    </button>
                </div>
            `;
        }
    }

    setupDecisionButtons(blocked) {
        // Event listeners are handled by onclick attributes for simplicity
        // This method can be used for any additional setup if needed
    }

    getScoreClass(score) {
        if (score >= 0.7) return 'score-high';
        if (score >= 0.4) return 'score-medium';
        return 'score-low';
    }

    formatExplanation(explanation) {
        // Simple formatting for better readability
        return explanation
            .replace(/\n/g, '<br>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>');
    }

    acceptCode() {
        if (!this.currentAnalysis) return;
        
        const logEntry = {
            ...this.currentAnalysis,
            decision: 'accepted',
            decisionTime: new Date().toISOString()
        };
        
        this.sessionData.push(logEntry);
        this.updateSessionLog();
        this.showNotification('✅ Code accepted and logged!', 'success');
        this.clearForm();
    }

    rejectCode() {
        if (!this.currentAnalysis) return;
        
        const reason = prompt('Reason for rejection (optional):') || 'Security concerns';
        
        const logEntry = {
            ...this.currentAnalysis,
            decision: 'rejected',
            reason: reason,
            decisionTime: new Date().toISOString()
        };
        
        this.sessionData.push(logEntry);
        this.updateSessionLog();
        this.showNotification('❌ Code rejected and logged!', 'warning');
        this.clearForm();
    }

    acknowledgeBlock() {
        if (!this.currentAnalysis) return;
        
        const logEntry = {
            ...this.currentAnalysis,
            decision: 'blocked',
            reason: 'Blocked by security policy',
            decisionTime: new Date().toISOString()
        };
        
        this.sessionData.push(logEntry);
        this.updateSessionLog();
        this.showNotification('🚫 Block acknowledged and logged!', 'info');
        this.clearForm();
    }

    async getDetailedExplanation() {
        if (!this.currentAnalysis) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/explain-code`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code: this.currentAnalysis.code,
                    detail_level: 'advanced',
                    target_audience: 'developers'
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                const explanation = data.explanation || 'No detailed explanation available';
                this.showModal('📚 Detailed Code Explanation', this.formatExplanation(explanation));
            } else {
                throw new Error('Failed to get detailed explanation');
            }
        } catch (error) {
            this.showNotification('Error getting detailed explanation: ' + error.message, 'error');
        }
    }

    suggestImprovements() {
        if (!this.currentAnalysis) return;
        
        const { policyData, securityData } = this.currentAnalysis;
        const violations = policyData.violations || [];
        
        let suggestions = [];
        
        if (violations.length > 0) {
            violations.forEach(violation => {
                if (violation.suggestion) {
                    suggestions.push(violation.suggestion);
                }
            });
        }
        
        if (suggestions.length === 0) {
            suggestions.push('No specific improvement suggestions available');
            suggestions.push('Consider following security best practices');
            suggestions.push('Use parameterized queries for database operations');
            suggestions.push('Avoid hardcoding sensitive information');
        }
        
        const content = suggestions.map((s, i) => `${i + 1}. ${s}`).join('<br><br>');
        this.showModal('🔧 Suggested Improvements', content);
    }

    showModal(title, content) {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-content">
                    ${content}
                </div>
                <div class="modal-footer">
                    <button class="btn" onclick="this.closest('.modal-overlay').remove()">Close</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        // Close on outside click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
            }
        });
    }

    updateSessionLog() {
        const logContainer = document.getElementById('sessionLog');
        if (!logContainer) return;
        
        if (this.sessionData.length === 0) {
            logContainer.innerHTML = `
                <p style="color: #6c757d; text-align: center; padding: 20px;">
                    Review decisions will appear here...
                </p>
            `;
            return;
        }
        
        const summary = this.generateSessionSummary();
        const recentEntries = this.sessionData.slice(-5).reverse();
        
        let html = summary;
        
        recentEntries.forEach(entry => {
            const time = new Date(entry.decisionTime).toLocaleTimeString();
            const riskLevel = entry.policyData?.risk_level || entry.securityData?.risk_level || 'MEDIUM';
            
            html += `
                <div class="log-entry ${entry.decision}">
                    <div class="log-header">
                        <strong>${entry.source || 'Unknown'} - ${entry.decision.toUpperCase()}</strong>
                        <span class="log-time">${time}</span>
                    </div>
                    <div class="log-code">
                        ${entry.code.substring(0, 100)}${entry.code.length > 100 ? '...' : ''}
                    </div>
                    <div class="log-details">
                        Risk Level: <span class="risk-level risk-${riskLevel.toLowerCase()}">${riskLevel}</span>
                        ${entry.reason ? `<br>Reason: ${entry.reason}` : ''}
                    </div>
                </div>
            `;
        });
        
        logContainer.innerHTML = html;
    }

    generateSessionSummary() {
        const total = this.sessionData.length;
        const accepted = this.sessionData.filter(entry => entry.decision === 'accepted').length;
        const rejected = this.sessionData.filter(entry => entry.decision === 'rejected').length;
        const blocked = this.sessionData.filter(entry => entry.decision === 'blocked').length;
        
        return `
            <div class="session-summary">
                <strong>Session Summary:</strong>
                Total: ${total} | 
                <span class="summary-accepted">Accepted: ${accepted}</span> | 
                <span class="summary-rejected">Rejected: ${rejected}</span> | 
                <span class="summary-blocked">Blocked: ${blocked}</span>
            </div>
        `;
    }

    loadDemoCode() {
        const demoExamples = [
            {
                code: `import os\nos.environ["PROD_DATABASE_URL"] = "postgresql://admin:secret@prod/db"\nprint("Production database configured")`,
                source: 'ai_assistant',
                filePath: 'config/database.py',
                description: 'Configure production database connection'
            },
            {
                code: `import pickle\n\ndef load_user_data(data_file):\n    with open(data_file, 'rb') as f:\n        user_data = pickle.load(f)  # Potentially dangerous!\n    return user_data\n\napi_key = "sk-example123fake456token789"`,
                source: 'copilot',
                filePath: 'utils/data_loader.py',
                description: 'Load user data from file'
            },
            {
                code: `import json\nfrom datetime import datetime\n\ndef calculate_metrics(users):\n    """Calculate user engagement metrics safely"""\n    if not users:\n        return {"total": 0, "active": 0}\n    \n    total = len(users)\n    active = sum(1 for user in users if user.get("last_active"))\n    \n    return {\n        "total_users": total,\n        "active_users": active,\n        "calculated_at": datetime.now().isoformat()\n    }`,
                source: 'developer',
                filePath: 'analytics/metrics.py',
                description: 'Calculate user metrics'
            }
        ];
        
        const example = demoExamples[Math.floor(Math.random() * demoExamples.length)];
        
        document.getElementById('codeInput').value = example.code;
        document.getElementById('sourceInput').value = example.source;
        document.getElementById('filePathInput').value = example.filePath;
        document.getElementById('descriptionInput').value = example.description;
        
        this.showNotification('🎯 Demo code loaded!', 'info');
    }

    showLoading() {
        const analysisElement = document.getElementById('analysisContent');
        if (!analysisElement) return;
        
        analysisElement.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Analyzing code for security issues...</p>
                <p class="loading-details">Running policy checks, security analysis, and code explanation...</p>
            </div>
        `;
    }

    showError(message) {
        const analysisElement = document.getElementById('analysisContent');
        if (!analysisElement) return;
        
        analysisElement.innerHTML = `
            <div class="error-message">
                <h3>❌ Analysis Failed</h3>
                <p>Error: ${message}</p>
                <p>Make sure the AI Firewall backend is running on ${this.apiBaseUrl}</p>
                <button class="btn" onclick="app.checkApiStatus()">🔄 Retry Connection</button>
            </div>
        `;
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Position notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            z-index: 10000;
            max-width: 400px;
            word-wrap: break-word;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        // Color based on type
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Auto remove after 4 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 4000);
    }

    disableAnalyzeButton() {
        const btn = document.getElementById('analyzeBtn');
        if (btn) {
            btn.disabled = true;
            btn.textContent = '🔍 Analyzing...';
        }
    }

    enableAnalyzeButton() {
        const btn = document.getElementById('analyzeBtn');
        if (btn) {
            btn.disabled = false;
            btn.textContent = '🔍 Analyze Code';
        }
    }

    clearForm() {
        document.getElementById('codeInput').value = '';
        document.getElementById('filePathInput').value = '';
        document.getElementById('descriptionInput').value = '';
        this.currentAnalysis = null;
        
        setTimeout(() => {
            const analysisElement = document.getElementById('analysisContent');
            if (analysisElement) {
                analysisElement.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #6c757d;">
                        <p>Enter code and click "Analyze Code" to see safety analysis</p>
                    </div>
                `;
            }
        }, 2000);
    }

    loadSettings() {
        // Load user preferences from localStorage
        const savedSettings = localStorage.getItem('aiFirewallSettings');
        if (savedSettings) {
            try {
                const settings = JSON.parse(savedSettings);
                if (settings.apiBaseUrl) {
                    this.apiBaseUrl = settings.apiBaseUrl;
                }
            } catch (error) {
                console.warn('Failed to load settings:', error);
            }
        }
    }

    saveSettings() {
        const settings = {
            apiBaseUrl: this.apiBaseUrl,
            timestamp: new Date().toISOString()
        };
        localStorage.setItem('aiFirewallSettings', JSON.stringify(settings));
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AIFirewallApp();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIFirewallApp;
} 