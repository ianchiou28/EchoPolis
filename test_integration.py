#!/usr/bin/env python3
"""
Echopolis 前后端AI集成测试
"""

import requests
import json
import time

BASE_URL = "http://localhost:8002"

def test_api_connection():
    """测试API连接"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"[OK] API连接成功: {response.json()}")
        return True
    except Exception as e:
        print(f"[ERROR] API连接失败: {e}")
        return False

def test_mbti_types():
    """测试MBTI类型获取"""
    try:
        response = requests.get(f"{BASE_URL}/api/mbti-types")
        mbti_types = response.json()
        print(f"[OK] MBTI类型获取成功，共{len(mbti_types)}种类型")
        return mbti_types
    except Exception as e:
        print(f"[ERROR] MBTI类型获取失败: {e}")
        return None

def test_create_avatar():
    """测试创建AI化身"""
    try:
        session_id = f"test_session_{int(time.time())}"
        data = {
            "name": "测试AI",
            "mbti": "INTP",
            "session_id": session_id
        }
        response = requests.post(f"{BASE_URL}/api/create-avatar", json=data)
        result = response.json()
        if result.get("success"):
            print(f"[OK] AI化身创建成功: {result['avatar']['name']} ({result['avatar']['mbti']})")
            print(f"     初始资金: {result['avatar']['credits']:,} CP")
            print(f"     命运: {result['avatar']['fate']}")
            return session_id, result['avatar']
        else:
            print(f"[ERROR] AI化身创建失败: {result}")
            return None, None
    except Exception as e:
        print(f"[ERROR] AI化身创建异常: {e}")
        return None, None

def test_generate_situation(session_id):
    """测试AI情况生成"""
    try:
        data = {"session_id": session_id, "context": ""}
        response = requests.post(f"{BASE_URL}/api/generate-situation", json=data)
        situation = response.json()
        print(f"[OK] 情况生成成功:")
        print(f"     AI生成: {situation.get('ai_generated', False)}")
        print(f"     情况: {situation['situation'][:100]}...")
        print(f"     选项数量: {len(situation['options'])}")
        for i, option in enumerate(situation['options']):
            print(f"       {i+1}. {option}")
        return situation
    except Exception as e:
        print(f"[ERROR] 情况生成失败: {e}")
        return None

def test_send_echo(session_id):
    """测试发送回响"""
    try:
        data = {
            "session_id": session_id,
            "echo_text": "我建议选择第二个选项，这样比较稳妥"
        }
        response = requests.post(f"{BASE_URL}/api/echo", json=data)
        result = response.json()
        print(f"[OK] 回响发送成功:")
        print(f"     AI驱动: {result['echo_analysis'].get('ai_powered', False)}")
        print(f"     AI选择: {result['decision']['chosen_option']}")
        print(f"     AI想法: {result['decision']['ai_thoughts']}")
        print(f"     资产变化: {result['decision'].get('credit_change', 0):+,} CP")
        return result
    except Exception as e:
        print(f"[ERROR] 回响发送失败: {e}")
        return None

def test_auto_decision(session_id):
    """测试AI自主决策"""
    try:
        data = {"session_id": session_id}
        response = requests.post(f"{BASE_URL}/api/auto-decision", json=data)
        result = response.json()
        print(f"[OK] AI自主决策成功:")
        print(f"     AI驱动: {result['decision'].get('ai_powered', False)}")
        print(f"     AI选择: {result['decision']['chosen_option']}")
        print(f"     AI想法: {result['decision']['ai_thoughts']}")
        print(f"     资产变化: {result['decision'].get('credit_change', 0):+,} CP")
        return result
    except Exception as e:
        print(f"[ERROR] AI自主决策失败: {e}")
        return None

def main():
    """主测试流程"""
    print("=" * 60)
    print("Echopolis 前后端AI集成测试")
    print("=" * 60)
    
    # 1. 测试API连接
    if not test_api_connection():
        print("[FATAL] API连接失败，请确保后端服务器运行在端口8001")
        return
    
    # 2. 测试MBTI类型
    mbti_types = test_mbti_types()
    if not mbti_types:
        return
    
    # 3. 测试创建AI化身
    session_id, avatar = test_create_avatar()
    if not session_id:
        return
    
    # 4. 测试AI情况生成
    situation = test_generate_situation(session_id)
    if not situation:
        return
    
    # 5. 测试发送回响
    echo_result = test_send_echo(session_id)
    if not echo_result:
        return
    
    # 6. 重新生成情况
    print("\n[INFO] 重新生成情况进行自主决策测试...")
    situation2 = test_generate_situation(session_id)
    if not situation2:
        return
    
    # 7. 测试AI自主决策
    auto_result = test_auto_decision(session_id)
    if not auto_result:
        return
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！前后端AI功能集成成功！")
    print("=" * 60)

if __name__ == "__main__":
    main()