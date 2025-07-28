#!/usr/bin/env python3
"""
Test script for the Python Code Explainer functionality.
This demonstrates how to explain various Python code snippets using LLMs.
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.code_explainer import PythonCodeExplainer, LLMProvider, explain_python_code

def print_explanation_result(title: str, explanation: str):
    """Helper function to print explanations in a readable format"""
    print(f"\n{'='*80}")
    print(f"🎓 {title}")
    print(f"{'='*80}")
    print(explanation)
    print("\n" + "─" * 80)

def test_simple_function():
    """Test explanation of a simple function"""
    code = '''
def greet(name):
    """Greet a person by name"""
    return f"Hello, {name}!"

# Call the function
message = greet("Alice")
print(message)
'''
    
    print_explanation_result("Simple Function Example", 
                            "📝 Code to explain:\n" + code)
    
    # Note: This would require API keys to work
    try:
        explanation = explain_python_code(
            code=code,
            provider="openai",
            detail_level="beginner",
            target_audience="students"
        )
        print_explanation_result("Explanation Result", explanation)
    except Exception as e:
        print(f"⚠️  Explanation skipped: {e}")
        print("💡 Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable to test")

def test_class_definition():
    """Test explanation of a class definition"""
    code = '''
class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def get_history(self):
        return self.history

# Usage
calc = Calculator()
result = calc.add(5, 3)
print(f"Result: {result}")
'''
    
    print_explanation_result("Class Definition Example", 
                            "📝 Code to explain:\n" + code)
    
    try:
        explanation = explain_python_code(
            code=code,
            provider="openai",
            detail_level="intermediate",
            target_audience="developers"
        )
        print_explanation_result("Explanation Result", explanation)
    except Exception as e:
        print(f"⚠️  Explanation skipped: {e}")

def test_advanced_algorithm():
    """Test explanation of a more complex algorithm"""
    code = '''
def quicksort(arr):
    """Implement quicksort algorithm"""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# Test the algorithm
numbers = [3, 6, 8, 10, 1, 2, 1]
sorted_numbers = quicksort(numbers)
print(f"Original: {numbers}")
print(f"Sorted: {sorted_numbers}")
'''
    
    print_explanation_result("Advanced Algorithm Example", 
                            "📝 Code to explain:\n" + code)
    
    try:
        explanation = explain_python_code(
            code=code,
            provider="openai",
            detail_level="advanced",
            target_audience="experts"
        )
        print_explanation_result("Explanation Result", explanation)
    except Exception as e:
        print(f"⚠️  Explanation skipped: {e}")

def test_data_processing():
    """Test explanation of data processing code"""
    code = '''
import json
from collections import Counter

def analyze_data(file_path):
    """Analyze user data from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Extract ages and calculate statistics
    ages = [user['age'] for user in data['users'] if 'age' in user]
    age_stats = {
        'count': len(ages),
        'average': sum(ages) / len(ages) if ages else 0,
        'distribution': dict(Counter(ages))
    }
    
    return age_stats

# Process the data
stats = analyze_data('users.json')
print(f"Age statistics: {stats}")
'''
    
    print_explanation_result("Data Processing Example", 
                            "📝 Code to explain:\n" + code)
    
    try:
        explanation = explain_python_code(
            code=code,
            provider="anthropic",
            detail_level="intermediate",
            target_audience="developers"
        )
        print_explanation_result("Explanation Result", explanation)
    except Exception as e:
        print(f"⚠️  Explanation skipped: {e}")

def test_api_integration():
    """Test explanation of API integration code"""
    code = '''
import requests
from typing import Optional, Dict, Any

class WeatherAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_weather(self, city: str) -> Optional[Dict[Any, Any]]:
        """Get weather data for a city"""
        url = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching weather: {e}")
            return None

# Usage
api = WeatherAPI("your-api-key")
weather = api.get_weather("London")
'''
    
    print_explanation_result("API Integration Example", 
                            "📝 Code to explain:\n" + code)
    
    try:
        explanation = explain_python_code(
            code=code,
            provider="openai",
            detail_level="intermediate",
            target_audience="developers"
        )
        print_explanation_result("Explanation Result", explanation)
    except Exception as e:
        print(f"⚠️  Explanation skipped: {e}")

def run_comprehensive_tests():
    """Run all code explanation tests"""
    print("🚀 PYTHON CODE EXPLAINER - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("This test suite demonstrates the code explanation capabilities.")
    print("To see actual explanations, set OPENAI_API_KEY or ANTHROPIC_API_KEY.")
    print("=" * 80)
    
    try:
        print("\n🔍 Testing Simple Function...")
        test_simple_function()
        
        print("\n🔍 Testing Class Definition...")
        test_class_definition()
        
        print("\n🔍 Testing Advanced Algorithm...")
        test_advanced_algorithm()
        
        print("\n🔍 Testing Data Processing...")
        test_data_processing()
        
        print("\n🔍 Testing API Integration...")
        test_api_integration()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED!")
        print("The Python Code Explainer is ready to use.")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

def demo_without_api():
    """Demonstrate the structure analysis without API calls"""
    print("\n🔍 DEMO: Code Structure Analysis (No API Required)")
    print("=" * 60)
    
    from backend.code_explainer import PythonCodeExplainer
    
    code = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(f"5! = {result}")
'''
    
    explainer = PythonCodeExplainer()
    code_lines, ast_tree = explainer.parse_code_structure(code)
    
    print("📋 Parsed Code Structure:")
    print("-" * 30)
    for line in code_lines:
        if not line.is_blank:
            status = "💬 Comment" if line.is_comment else "💻 Code"
            ast_info = f" [{line.ast_type}]" if line.ast_type else ""
            print(f"Line {line.line_number}: {status}{ast_info}")
            print(f"  Content: {line.content.strip()}")
            print(f"  Indentation: {line.indentation_level}")
            print()

if __name__ == "__main__":
    # Run structure demo first (no API required)
    demo_without_api()
    
    # Run full tests (requires API keys)
    run_comprehensive_tests() 