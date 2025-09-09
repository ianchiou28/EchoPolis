"""
测试AI情况生成功能
"""
from core.avatar.ai_avatar import AIAvatar
from core.systems.mbti_traits import MBTIType
from core.ai.deepseek_engine import initialize_deepseek
import json
import os

def test_ai_situation_generation():
    """测试AI情况生成"""
    print("测试AI情况生成功能...")
    
    # 读取API key
    config_file = 'config.json'
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                api_key = config.get('deepseek_api_key', '')
                if api_key and api_key != 'sk-your-deepseek-api-key-here':
                    # 初始化DeepSeek
                    initialize_deepseek(api_key)
                    print("✓ DeepSeek AI已初始化")
                else:
                    print("✗ 未找到有效的API Key，将使用预设情况")
                    return
        except Exception as e:
            print(f"✗ 配置文件读取失败: {e}")
            return
    else:
        print("✗ 未找到配置文件")
        return
    
    # 创建测试化身
    avatar = AIAvatar("TestUser", MBTIType.INTP)
    print(f"✓ 创建测试化身: {avatar.attributes.name}")
    
    # 生成AI情况
    print("\n正在生成AI情况...")
    situation = avatar.generate_situation()
    
    if situation:
        print("✓ AI情况生成成功!")
        print(f"情况描述: {situation.situation}")
        print("可选行动:")
        for i, option in enumerate(situation.options, 1):
            print(f"  {i}. {option}")
        print(f"情况类型: {situation.context_type}")
    else:
        print("✗ AI情况生成失败，使用预设情况")

if __name__ == "__main__":
    test_ai_situation_generation()