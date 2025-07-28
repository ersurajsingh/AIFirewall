#!/usr/bin/env python3
"""
Example script demonstrating how to use the AI Firewall Code Explanation API endpoints.
"""

import requests
import json
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"

def explain_code_via_api(code: str, 
                        provider: str = "openai",
                        detail_level: str = "intermediate",
                        target_audience: str = "developers",
                        api_key: str = None) -> Dict[str, Any]:
    """
    Explain code using the comprehensive API endpoint
    """
    endpoint = f"{API_BASE_URL}/explain-code"
    
    payload = {
        "code": code,
        "provider": provider,
        "detail_level": detail_level,
        "target_audience": target_audience
    }
    
    if api_key:
        payload["api_key"] = api_key
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def explain_code_simple(code: str) -> Dict[str, Any]:
    """
    Explain code using the simple API endpoint
    """
    endpoint = f"{API_BASE_URL}/explain-code-simple"
    
    try:
        response = requests.post(endpoint, json={"code": code})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Simple API request failed: {e}"}

def get_explanation_demo() -> Dict[str, Any]:
    """
    Get the demo explanation
    """
    endpoint = f"{API_BASE_URL}/explain-demo"
    
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Demo API request failed: {e}"}

def print_explanation_result(result: Dict[str, Any], title: str = "Code Explanation"):
    """
    Pretty print explanation results
    """
    print(f"\n{'='*80}")
    print(f"📖 {title}")
    print(f"{'='*80}")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    if "explanation" in result:
        print("📝 EXPLANATION:")
        print("-" * 40)
        print(result["explanation"])
        print("-" * 40)
    
    # Print metadata if available
    if "provider_used" in result:
        print(f"\n🔧 Provider: {result['provider_used']}")
    if "detail_level" in result:
        print(f"📊 Detail Level: {result['detail_level']}")
    if "target_audience" in result:
        print(f"👥 Target Audience: {result['target_audience']}")
    if "timestamp" in result:
        print(f"🕒 Generated: {result['timestamp']}")

def demo_simple_function():
    """Demo explanation of a simple function"""
    code = '''
def calculate_area(radius):
    """Calculate area of a circle"""
    import math
    return math.pi * radius ** 2

# Calculate area for radius 5
area = calculate_area(5)
print(f"Area: {area:.2f}")
'''
    
    print("🚀 DEMO: Simple Function Explanation")
    print(f"Code to explain:\n{code}")
    
    # Test comprehensive endpoint
    result = explain_code_via_api(
        code=code,
        provider="openai",
        detail_level="beginner", 
        target_audience="students"
    )
    print_explanation_result(result, "Comprehensive API Result")
    
    # Test simple endpoint
    simple_result = explain_code_simple(code)
    print_explanation_result(simple_result, "Simple API Result")

def demo_class_example():
    """Demo explanation of a class"""
    code = '''
class BankAccount:
    def __init__(self, account_number, initial_balance=0):
        self.account_number = account_number
        self.balance = initial_balance
        self.transactions = []
    
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.transactions.append(f"Deposit: +${amount}")
            return True
        return False
    
    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.transactions.append(f"Withdrawal: -${amount}")
            return True
        return False
    
    def get_balance(self):
        return self.balance

# Create account and perform transactions
account = BankAccount("12345", 1000)
account.deposit(500)
account.withdraw(200)
print(f"Final balance: ${account.get_balance()}")
'''
    
    print("\n🏦 DEMO: Bank Account Class Explanation")
    print(f"Code to explain:\n{code}")
    
    result = explain_code_via_api(
        code=code,
        provider="anthropic",
        detail_level="intermediate",
        target_audience="developers"
    )
    print_explanation_result(result, "Bank Account Class Explanation")

def demo_algorithm_example():
    """Demo explanation of an algorithm"""
    code = '''
def binary_search(arr, target):
    """Binary search algorithm implementation"""
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

# Test the algorithm
sorted_list = [1, 3, 5, 7, 9, 11, 13, 15]
position = binary_search(sorted_list, 7)
print(f"Found 7 at position: {position}")
'''
    
    print("\n🔍 DEMO: Binary Search Algorithm Explanation")
    print(f"Code to explain:\n{code}")
    
    result = explain_code_via_api(
        code=code,
        provider="openai",
        detail_level="advanced",
        target_audience="experts"
    )
    print_explanation_result(result, "Binary Search Algorithm Explanation")

def demo_data_processing():
    """Demo explanation of data processing code"""
    code = '''
import pandas as pd
from datetime import datetime

def process_sales_data(csv_file):
    """Process sales data and generate summary"""
    # Load data
    df = pd.read_csv(csv_file)
    
    # Clean data
    df['date'] = pd.to_datetime(df['date'])
    df['revenue'] = df['quantity'] * df['price']
    
    # Calculate metrics
    total_revenue = df['revenue'].sum()
    avg_order_value = df['revenue'].mean()
    top_products = df.groupby('product')['revenue'].sum().sort_values(ascending=False).head(5)
    
    # Generate summary
    summary = {
        'total_revenue': total_revenue,
        'average_order_value': avg_order_value,
        'top_products': top_products.to_dict(),
        'analysis_date': datetime.now().isoformat()
    }
    
    return summary

# Process sales data
sales_summary = process_sales_data('sales_2024.csv')
print(f"Sales Summary: {sales_summary}")
'''
    
    print("\n📊 DEMO: Data Processing Explanation")
    print(f"Code to explain:\n{code}")
    
    result = explain_code_via_api(
        code=code,
        provider="openai",
        detail_level="intermediate",
        target_audience="developers"
    )
    print_explanation_result(result, "Data Processing Explanation")

def demo_built_in_example():
    """Demo the built-in example endpoint"""
    print("\n🎯 DEMO: Built-in Example")
    
    result = get_explanation_demo()
    print_explanation_result(result, "Built-in Demo Explanation")

def main():
    """
    Main demonstration function
    """
    print("🛡️  AI FIREWALL - CODE EXPLANATION API DEMONSTRATION")
    print("Testing the Code Explanation API endpoints...")
    
    # Check if API is running
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ API is running and healthy!")
        else:
            print("⚠️  API health check failed")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Make sure the backend is running on http://localhost:8000")
        print("Run: ./start.sh or python backend/main.py")
        return
    
    # Check if API keys are configured
    print("\n🔑 API Key Status:")
    print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables for full functionality")
    
    # Run demonstrations
    demo_built_in_example()
    demo_simple_function()
    demo_class_example()
    demo_algorithm_example()
    demo_data_processing()
    
    print(f"\n{'='*80}")
    print("✅ CODE EXPLANATION API DEMONSTRATION COMPLETED!")
    print("The AI Firewall can now explain Python code line-by-line using advanced LLMs.")
    print(f"{'='*80}")
    
    # Usage examples
    print("\n💡 USAGE EXAMPLES:")
    print("""
# Simple explanation:
curl -X POST http://localhost:8000/explain-code-simple \\
  -H "Content-Type: application/json" \\
  -d '{"code": "def hello(): return \\"Hello World\\""}'

# Comprehensive explanation:
curl -X POST http://localhost:8000/explain-code \\
  -H "Content-Type: application/json" \\
  -d '{
    "code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
    "provider": "openai",
    "detail_level": "beginner",
    "target_audience": "students"
  }'

# Get demo:
curl http://localhost:8000/explain-demo
""")

if __name__ == "__main__":
    main() 