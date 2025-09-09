"""
测试DeepSeek API调用
"""
from core.ai.deepseek_engine import deepseek_engine

def test_deepseek():
    print("测试DeepSeek API...")
    
    context = {
        'name': 'Test',
        'age': 25,
        'mbti': 'INTP',
        'credits': 50000,
        'health': 100,
        'happiness': 50,
        'stress': 30,
        'life_stage': 'exploration',
        'background': 'Test background',
        'traits': 'Test traits',
        'decision_count': 1
    }
    
    result = deepseek_engine.generate_situation(context)
    print('Result:', result)

if __name__ == "__main__":
    test_deepseek()