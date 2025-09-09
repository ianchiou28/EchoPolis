"""
查看AI想法记录工具
"""
import json
import os
from datetime import datetime

def view_ai_thoughts(avatar_name: str = None):
    """查看AI想法记录"""
    if avatar_name:
        log_file = f"ai_thoughts_{avatar_name}.json"
        if not os.path.exists(log_file):
            print(f"❌ 未找到 {avatar_name} 的想法记录")
            return
        view_single_log(log_file, avatar_name)
    else:
        # 查找所有AI想法记录文件
        log_files = [f for f in os.listdir('.') if f.startswith('ai_thoughts_') and f.endswith('.json')]
        if not log_files:
            print("❌ 未找到任何AI想法记录")
            return
        
        print("📚 发现以下AI想法记录:")
        for i, log_file in enumerate(log_files, 1):
            name = log_file.replace('ai_thoughts_', '').replace('.json', '')
            print(f"  {i}. {name}")
        
        try:
            choice = int(input("\n请选择要查看的记录 (输入数字): ")) - 1
            if 0 <= choice < len(log_files):
                name = log_files[choice].replace('ai_thoughts_', '').replace('.json', '')
                view_single_log(log_files[choice], name)
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入有效数字")

def view_single_log(log_file: str, avatar_name: str):
    """查看单个AI想法记录"""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            thoughts_log = json.load(f)
        
        if not thoughts_log:
            print(f"📝 {avatar_name} 还没有想法记录")
            return
        
        print(f"\n🧠 {avatar_name} 的AI想法记录 (共 {len(thoughts_log)} 条)")
        print("=" * 60)
        
        # 显示最近10条记录
        recent_thoughts = thoughts_log[-10:]
        
        for i, entry in enumerate(recent_thoughts, 1):
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n📅 记录 {i} - {timestamp}")
            print(f"👤 {entry['avatar_name']} ({entry['mbti_type']}) - {entry['age']}岁")
            print(f"🎯 决策 #{entry['decision_count']}: {entry['chosen_option']}")
            print(f"💭 内心独白:")
            print(f"   {entry['ai_thoughts']}")
            print(f"🤝 信任度: {entry['trust_level']}/100 ({entry['trust_change']:+d})")
            print("-" * 40)
        
        if len(thoughts_log) > 10:
            print(f"\n💡 显示了最近10条记录，总共有 {len(thoughts_log)} 条记录")
            
        # 统计信息
        print(f"\n📊 统计信息:")
        avg_trust = sum(entry['trust_level'] for entry in thoughts_log) / len(thoughts_log)
        print(f"   平均信任度: {avg_trust:.1f}/100")
        positive_changes = sum(1 for entry in thoughts_log if entry['trust_change'] > 0)
        print(f"   信任度提升次数: {positive_changes}/{len(thoughts_log)}")
        
    except Exception as e:
        print(f"❌ 读取记录失败: {e}")

def main():
    """主函数"""
    print("🧠 AI想法记录查看器")
    print("=" * 30)
    
    import sys
    if len(sys.argv) > 1:
        avatar_name = sys.argv[1]
        view_ai_thoughts(avatar_name)
    else:
        view_ai_thoughts()

if __name__ == "__main__":
    main()