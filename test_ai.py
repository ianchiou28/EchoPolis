"""
测试AI模块导入
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧪 测试AI模块导入...")

try:
    from core.avatar.ai_avatar import AIAvatar
    print("✅ AIAvatar导入成功")
except ImportError as e:
    print(f"❌ AIAvatar导入失败: {e}")

try:
    from core.systems.mbti_traits import MBTITraits
    print("✅ MBTITraits导入成功")
except ImportError as e:
    print(f"❌ MBTITraits导入失败: {e}")

try:
    from core.systems.fate_wheel import FateWheel
    print("✅ FateWheel导入成功")
except ImportError as e:
    print(f"❌ FateWheel导入失败: {e}")

try:
    from core.systems.echo_system import EchoSystem
    print("✅ EchoSystem导入成功")
except ImportError as e:
    print(f"❌ EchoSystem导入失败: {e}")

try:
    from core.ai.deepseek_engine import DeepSeekEngine
    print("✅ DeepSeekEngine导入成功")
    
    # 测试初始化
    try:
        engine = DeepSeekEngine()
        print("✅ DeepSeek引擎初始化成功")
    except Exception as e:
        print(f"❌ DeepSeek引擎初始化失败: {e}")
        
except ImportError as e:
    print(f"❌ DeepSeekEngine导入失败: {e}")

print("\n📋 测试完成")