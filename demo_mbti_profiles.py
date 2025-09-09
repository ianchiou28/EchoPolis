"""
演示MBTI用户画像功能
"""
from echopolis_game import EchopolisGame

def demo_mbti_profiles():
    """演示MBTI用户画像"""
    print("🎭 Echopolis MBTI用户画像演示")
    print("=" * 60)
    
    game = EchopolisGame()
    game.display_mbti_options()
    
    print("\n💡 现在AI会根据这些诗意的用户画像来:")
    print("   • 生成符合人格特质的个性化情况")
    print("   • 做出符合角色性格的决策")
    print("   • 展现真实的内心想法和情感")
    print("\n🎮 开始游戏体验个性化的AI决策吧!")

if __name__ == "__main__":
    demo_mbti_profiles()