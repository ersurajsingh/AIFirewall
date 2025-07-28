# AI Firewall

An AI-powered code security firewall that integrates with VS Code to provide real-time security analysis and protection for your codebase.

## Features

- **Real-time Security Analysis**: Analyze code for security vulnerabilities as you type
- **VS Code Integration**: Seamless integration with Visual Studio Code
- **FastAPI Backend**: High-performance Python backend for AI processing
- **Configurable Security Levels**: Customize security sensitivity levels
- **Batch Analysis**: Analyze entire workspaces or multiple files
- **Smart Suggestions**: Get AI-powered recommendations for security improvements

## Architecture

The project consists of two main components:

1. **Backend** (`/backend`): FastAPI-based Python server that performs AI-powered security analysis
2. **VS Code Extension** (`/vscode-extension`): TypeScript extension that integrates with VS Code

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- VS Code

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r ../requirements.txt
```

3. Run the FastAPI server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### VS Code Extension Setup

1. Navigate to the extension directory:
```bash
cd vscode-extension
```

2. Install dependencies:
```bash
npm install
```

3. Compile the extension:
```bash
npm run compile
```

4. Open VS Code in the extension directory and press `F5` to launch a new Extension Development Host window.

## API Endpoints

### `POST /analyze`
Analyze a single code snippet for security vulnerabilities.

**Request Body:**
```json
{
  "code": "string",
  "language": "string", 
  "file_path": "string (optional)"
}
```

**Response:**
```json
{
  "is_safe": boolean,
  "issues": [
    {
      "severity": "HIGH|MEDIUM|LOW",
      "message": "string",
      "line_number": "number (optional)",
      "suggestion": "string (optional)"
    }
  ],
  "confidence_score": number
}
```

### `POST /batch-analyze`
Analyze multiple code snippets in batch.

### `GET /health`
Health check endpoint.

## VS Code Extension Commands

- **AI Firewall: Analyze Current File** - Analyze the currently open file
- **AI Firewall: Analyze Workspace** - Analyze all supported files in the workspace
- **AI Firewall: Toggle Protection** - Enable/disable the firewall

## Configuration

The VS Code extension can be configured through VS Code settings:

- `aiFirewall.enabled`: Enable/disable AI Firewall protection
- `aiFirewall.apiEndpoint`: AI Firewall API endpoint URL
- `aiFirewall.autoAnalyze`: Automatically analyze files on save
- `aiFirewall.severityLevel`: Minimum severity level to show warnings

## Development

### Backend Development

The backend uses FastAPI with a simple pattern-matching approach for security analysis. To extend the analysis:

1. Modify the `analyze_code` function in `backend/main.py`
2. Add more sophisticated AI models for better detection
3. Integrate with external security scanning tools

### Extension Development

The VS Code extension is built with TypeScript. Key files:

- `src/extension.ts`: Main extension logic
- `package.json`: Extension manifest and configuration

To debug the extension:
1. Open the `vscode-extension` folder in VS Code
2. Press `F5` to launch the Extension Development Host
3. Test the extension in the new window

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security

If you discover a security vulnerability, please send an email to security@aifirewall.dev. All security vulnerabilities will be promptly addressed.

## Roadmap

- [ ] Machine learning-based vulnerability detection
- [ ] Support for more programming languages
- [ ] Integration with CI/CD pipelines
- [ ] Advanced threat intelligence
- [ ] Team collaboration features
- [ ] Custom rule engine 