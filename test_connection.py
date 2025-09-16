"""
测试前后端连接
"""
import requests
import json

def test_backend():
    """测试后端API"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试后端API连接...")
    
    try:
        # 测试根路径
        response = requests.get(f"{base_url}/")
        print(f"✅ 根路径: {response.status_code}")
        
        # 测试MBTI类型
        response = requests.get(f"{base_url}/api/mbti-types")
        print(f"✅ MBTI类型: {response.status_code}")
        print(f"   数据: {list(response.json().keys())}")
        
        # 测试创建化身
        avatar_data = {
            "name": "测试用户",
            "mbti": "INTP",
            "session_id": "test_session_123"
        }
        response = requests.post(f"{base_url}/api/create-avatar", json=avatar_data)
        print(f"✅ 创建化身: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   化身: {result['avatar']['name']} ({result['avatar']['mbti']})")
            print(f"   命运: {result['avatar']['fate']}")
            print(f"   资金: {result['avatar']['credits']} CP")
        
        print("🎉 后端API测试完成!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务器")
        print("   请确保后端服务器正在运行: python start_backend.py")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_frontend():
    """测试前端服务"""
    frontend_url = "http://localhost:3000"
    
    print("\n🧪 测试前端服务...")
    
    try:
        response = requests.get(frontend_url, timeout=5)
        print(f"✅ 前端服务: {response.status_code}")
        print("🎉 前端服务测试完成!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到前端服务器")
        print("   请确保前端服务器正在运行: python start_frontend.py")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    print("🔗 Echopolis 前后端连接测试")
    print("=" * 50)
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    print("\n📊 测试结果:")
    print(f"   后端API: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"   前端服务: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 前后端连接正常!")
        print("🌐 访问 http://localhost:3000 开始游戏")
    else:
        print("\n⚠️  请检查服务器状态")

if __name__ == "__main__":
    main()