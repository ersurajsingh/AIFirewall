#!/usr/bin/env python3
"""
Simple demo of the Code Explainer functionality.
This demo shows the API endpoints and structure without requiring API keys.
"""

import requests
import json

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running and healthy!")
            return True
        else:
            print("⚠️  API health check failed")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Make sure the backend is running:")
        print("   ./start.sh")
        print("   or")
        print("   python3 backend/main.py")
        return False

def demo_explain_endpoint():
    """Demo the explain-demo endpoint that doesn't require API keys"""
    print("\n🎯 TESTING: Built-in Demo Endpoint")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/explain-demo")
        result = response.json()
        
        print("📝 Demo Code:")
        print(result.get("demo_code", "No demo code available"))
        
        if "explanation" in result and "Demo explanation not available" not in result["explanation"]:
            print("\n📖 Explanation Generated:")
            explanation = result["explanation"]
            # Show first few lines of the explanation
            lines = explanation.split('\n')[:15]
            print('\n'.join(lines))
            if len(explanation.split('\n')) > 15:
                print("... (explanation continues)")
        else:
            print("\n⚠️  Explanation not available - API key required")
            print("💡 To see full explanations, set environment variables:")
            print("   export OPENAI_API_KEY='your-openai-key'")
            print("   export ANTHROPIC_API_KEY='your-anthropic-key'")
        
        print(f"\n📊 Status: {result.get('message', 'No message')}")
        
    except Exception as e:
        print(f"❌ Demo endpoint failed: {e}")

def demo_api_structure():
    """Show the API structure and available endpoints"""
    print("\n🚀 CODE EXPLAINER API STRUCTURE")
    print("=" * 60)
    
    endpoints = [
        {
            "endpoint": "POST /explain-code",
            "description": "Comprehensive code explanation with full options",
            "example": {
                "code": "def hello(): return 'Hello World'",
                "provider": "openai",
                "detail_level": "beginner",
                "target_audience": "students"
            }
        },
        {
            "endpoint": "POST /explain-code-simple", 
            "description": "Quick explanation with default settings",
            "example": {
                "code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
            }
        },
        {
            "endpoint": "GET /explain-demo",
            "description": "Demo with sample code explanation",
            "example": "No request body required"
        }
    ]
    
    for ep in endpoints:
        print(f"\n📌 {ep['endpoint']}")
        print(f"   {ep['description']}")
        print(f"   Example: {json.dumps(ep['example'], indent=2) if isinstance(ep['example'], dict) else ep['example']}")

def demo_usage_examples():
    """Show usage examples"""
    print("\n💡 USAGE EXAMPLES")
    print("=" * 60)
    
    print("\n🔧 Install Dependencies:")
    print("pip install aiohttp openai")
    
    print("\n🔑 Set API Keys:")
    print("export OPENAI_API_KEY='your-openai-api-key'")
    print("export ANTHROPIC_API_KEY='your-anthropic-api-key'")
    
    print("\n🚀 Start Backend:")
    print("./start.sh")
    
    print("\n📡 Test with curl:")
    print('''
# Simple explanation
curl -X POST http://localhost:8000/explain-code-simple \\
  -H "Content-Type: application/json" \\
  -d '{"code": "def greet(name): return f\\"Hello {name}\\""}'

# Comprehensive explanation  
curl -X POST http://localhost:8000/explain-code \\
  -H "Content-Type: application/json" \\
  -d '{
    "code": "class Calculator:\\n    def add(self, a, b):\\n        return a + b",
    "provider": "openai",
    "detail_level": "intermediate",
    "target_audience": "developers"
  }'

# Get demo
curl http://localhost:8000/explain-demo
''')
    
    print("\n🐍 Python Usage:")
    print('''
import requests

# Simple usage
response = requests.post("http://localhost:8000/explain-code-simple", 
                        json={"code": "def hello(): return 'Hello'"})
explanation = response.json()["explanation"]
print(explanation)
''')

def main():
    """Main demo function"""
    print("🛡️  AI FIREWALL - PYTHON CODE EXPLAINER DEMO")
    print("=" * 60)
    print("This demo shows the code explanation functionality.")
    print("For full explanations, configure OpenAI or Anthropic API keys.")
    
    # Check if API is running
    if not check_api_health():
        return
    
    # Show API structure
    demo_api_structure()
    
    # Test demo endpoint
    demo_explain_endpoint()
    
    # Show usage examples
    demo_usage_examples()
    
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETED!")
    print("The Code Explainer is ready to explain Python code line-by-line.")
    print("Configure API keys for full functionality.")
    print("=" * 60)

if __name__ == "__main__":
    main() 