"""
测试DeepSeek API连接
"""
import requests
import json

def test_deepseek_api():
    # 从config.json读取API key
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get('deepseek_api_key')
    except:
        print("❌ 无法读取config.json")
        return False
    
    if not api_key:
        print("❌ 未找到DeepSeek API key")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}...")
    
    # 测试API连接
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "你好，请回复'测试成功'"}],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        print("🧪 测试API连接...")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            print(f"✅ AI回复: {ai_response}")
            return True
        else:
            print(f"❌ API错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 DeepSeek API 连接测试")
    print("=" * 40)
    
    if test_deepseek_api():
        print("\n🎉 DeepSeek API连接正常!")
    else:
        print("\n💡 请检查:")
        print("   1. config.json中的API key是否正确")
        print("   2. 网络连接是否正常")
        print("   3. API key是否有效")