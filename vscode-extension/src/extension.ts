import * as vscode from 'vscode';
import axios from 'axios';
import { AIFirewallWebviewProvider } from './webview';

interface SecurityIssue {
    severity: string;
    message: string;
    lineNumber?: number;
    suggestion?: string;
}

interface AnalysisResponse {
    isSafe: boolean;
    issues: SecurityIssue[];
    confidenceScore: number;
}

export function activate(context: vscode.ExtensionContext) {
    console.log('AI Firewall extension is now active!');

    const outputChannel = vscode.window.createOutputChannel("AI Firewall");
    
    // Register commands
    const analyzeFileCommand = vscode.commands.registerCommand('ai-firewall.analyzeFile', () => {
        analyzeCurrentFile();
    });

    const analyzeWorkspaceCommand = vscode.commands.registerCommand('ai-firewall.analyzeWorkspace', () => {
        analyzeWorkspace();
    });

    const toggleFirewallCommand = vscode.commands.registerCommand('ai-firewall.toggleFirewall', () => {
        toggleFirewall();
    });

    // Auto-analyze on save if enabled
    const onSaveListener = vscode.workspace.onDidSaveTextDocument((document) => {
        const config = vscode.workspace.getConfiguration('aiFirewall');
        if (config.get('autoAnalyze') && config.get('enabled')) {
            analyzeDocument(document);
        }
    });

    context.subscriptions.push(
        analyzeFileCommand,
        analyzeWorkspaceCommand,
        toggleFirewallCommand,
        onSaveListener,
        outputChannel
    );

    // Show welcome message
    vscode.window.showInformationMessage('AI Firewall is protecting your code!');

    async function analyzeCurrentFile() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor found');
            return;
        }

        await analyzeDocument(editor.document);
    }

    async function analyzeDocument(document: vscode.TextDocument) {
        const config = vscode.workspace.getConfiguration('aiFirewall');
        
        if (!config.get('enabled')) {
            return;
        }

        const apiEndpoint = config.get('apiEndpoint') as string;
        const code = document.getText();
        const language = document.languageId;
        const filePath = document.fileName;

        try {
            outputChannel.appendLine(`Analyzing ${filePath}...`);
            
            const response = await axios.post(`${apiEndpoint}/analyze`, {
                code,
                language,
                filePath
            });

            const analysis: AnalysisResponse = response.data;
            
            // Clear previous diagnostics
            diagnosticCollection.clear();
            
            if (analysis.issues.length > 0) {
                const diagnostics: vscode.Diagnostic[] = [];
                const severityFilter = config.get('severityLevel') as string;
                
                for (const issue of analysis.issues) {
                    if (shouldShowIssue(issue.severity, severityFilter)) {
                        const line = issue.lineNumber ? issue.lineNumber - 1 : 0;
                        const range = new vscode.Range(line, 0, line, Number.MAX_VALUE);
                        
                        const diagnostic = new vscode.Diagnostic(
                            range,
                            `${issue.message}${issue.suggestion ? ` Suggestion: ${issue.suggestion}` : ''}`,
                            getSeverity(issue.severity)
                        );
                        
                        diagnostic.source = 'AI Firewall';
                        diagnostics.push(diagnostic);
                    }
                }
                
                diagnosticCollection.set(document.uri, diagnostics);
                
                const issueCount = diagnostics.length;
                outputChannel.appendLine(`Found ${issueCount} security issue(s) in ${filePath}`);
                
                if (!analysis.isSafe) {
                    vscode.window.showWarningMessage(
                        `AI Firewall detected ${issueCount} security issue(s) in ${document.fileName}`,
                        'Show Problems'
                    ).then(selection => {
                        if (selection === 'Show Problems') {
                            vscode.commands.executeCommand('workbench.panel.markers.view.focus');
                        }
                    });
                }
            } else {
                outputChannel.appendLine(`No security issues found in ${filePath}`);
            }
            
        } catch (error) {
            outputChannel.appendLine(`Error analyzing ${filePath}: ${error}`);
            vscode.window.showErrorMessage('Failed to analyze code. Check AI Firewall API connection.');
        }
    }

    async function analyzeWorkspace() {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showWarningMessage('No workspace folder found');
            return;
        }

        vscode.window.showInformationMessage('Analyzing workspace files...');
        
        const files = await vscode.workspace.findFiles('**/*.{py,js,ts,jsx,tsx}', '**/node_modules/**');
        
        for (const file of files) {
            const document = await vscode.workspace.openTextDocument(file);
            await analyzeDocument(document);
        }
        
        vscode.window.showInformationMessage('Workspace analysis complete!');
    }

    function toggleFirewall() {
        const config = vscode.workspace.getConfiguration('aiFirewall');
        const currentState = config.get('enabled') as boolean;
        config.update('enabled', !currentState, vscode.ConfigurationTarget.Global);
        
        const status = !currentState ? 'enabled' : 'disabled';
        vscode.window.showInformationMessage(`AI Firewall ${status}`);
        outputChannel.appendLine(`AI Firewall ${status}`);
    }

    function shouldShowIssue(issueSeverity: string, filterLevel: string): boolean {
        const severityLevels = { 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3 };
        return severityLevels[issueSeverity as keyof typeof severityLevels] >= 
               severityLevels[filterLevel as keyof typeof severityLevels];
    }

    function getSeverity(severity: string): vscode.DiagnosticSeverity {
        switch (severity) {
            case 'HIGH': return vscode.DiagnosticSeverity.Error;
            case 'MEDIUM': return vscode.DiagnosticSeverity.Warning;
            case 'LOW': return vscode.DiagnosticSeverity.Information;
            default: return vscode.DiagnosticSeverity.Hint;
        }
    }

    // Create diagnostic collection
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('ai-firewall');
    context.subscriptions.push(diagnosticCollection);
}

export function deactivate() {
    console.log('AI Firewall extension deactivated');
} 