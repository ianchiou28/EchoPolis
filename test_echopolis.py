"""
Echopolis 测试文件
验证核心系统功能
"""
from core.avatar.ai_avatar import AIAvatar
from core.systems.mbti_traits import MBTIType
from core.systems.echo_system import echo_system

def test_avatar_creation():
    """测试AI化身创建"""
    print("[TEST] 测试AI化身创建...")
    avatar = AIAvatar("TestUser", MBTIType.INTP)
    
    print(f"[OK] 化身创建成功: {avatar.attributes.name}")
    print(f"   MBTI类型: {avatar.attributes.mbti_type.value}")
    print(f"   命运类型: {avatar.attributes.fate_type.value}")
    print(f"   初始资金: {avatar.attributes.credits:,} CP")
    print(f"   特殊特质: {avatar.fate_background.special_traits}")
    
    return avatar

def test_situation_generation(avatar):
    """测试情况生成"""
    print("\n[TEST] 测试情况生成...")
    situation = avatar.generate_situation()
    
    print(f"[OK] 情况生成成功:")
    print(f"   描述: {situation.situation}")
    print(f"   选项: {situation.options}")
    print(f"   类型: {situation.context_type}")
    
    return situation

def test_echo_system(avatar):
    """测试回响系统"""
    print("\n[TEST] 测试回响系统...")
    
    if not avatar.current_situation:
        avatar.generate_situation()
    
    test_echo = "我建议你小额试水，风险太大不要投太多"
    result = echo_system.process_echo(
        test_echo,
        avatar.current_situation.options,
        avatar.attributes.trust_level
    )
    
    print(f"[OK] 回响处理成功:")
    print(f"   回响内容: {test_echo}")
    print(f"   分析类型: {result['analysis'].echo_type.value}")
    print(f"   置信度: {result['analysis'].confidence:.2f}")
    print(f"   影响权重: {result['influence_weight']:.2f}")
    
    return result

def test_decision_making(avatar):
    """测试决策制定"""
    print("\n[TEST] 测试AI决策...")
    
    if not avatar.current_situation:
        avatar.generate_situation()
    
    # 测试有回响的决策
    test_echo = "我建议选择保守的方案"
    decision_result = avatar.make_decision(test_echo)
    
    print(f"[OK] AI决策完成:")
    print(f"   选择: {decision_result['chosen_option']}")
    print(f"   AI想法: {decision_result['ai_thoughts']}")
    print(f"   信任度变化: {decision_result['trust_change']:+d}")
    
    return decision_result

def test_status_display(avatar):
    """测试状态显示"""
    print("\n[TEST] 测试状态显示...")
    status = avatar.get_status()
    
    print("[OK] 状态获取成功:")
    print(f"   基本信息: {status['basic_info']['name']}, {status['basic_info']['age']}岁")
    print(f"   财务状况: {status['financial']['credits']}")
    print(f"   身心状态: 健康{status['physical_mental']['health']}, 幸福感{status['physical_mental']['happiness']}")
    print(f"   信任关系: {status['relationship']['trust_level']}/100")

def run_all_tests():
    """运行所有测试"""
    print("[START] 开始 Echopolis 系统测试")
    print("=" * 50)
    
    try:
        # 测试化身创建
        avatar = test_avatar_creation()
        
        # 测试情况生成
        test_situation_generation(avatar)
        
        # 测试回响系统
        test_echo_system(avatar)
        
        # 测试决策制定
        test_decision_making(avatar)
        
        # 测试状态显示
        test_status_display(avatar)
        
        print("\n" + "=" * 50)
        print("[SUCCESS] 所有测试通过! Echopolis 系统运行正常")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()