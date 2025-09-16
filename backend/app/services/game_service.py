"""
游戏服务层 - 业务逻辑处理
"""
import random
from typing import Dict, Any

# 尝试导入核心游戏系统
try:
    from core.avatar.ai_avatar import AIAvatar
    from core.systems.mbti_traits import MBTITraits
    from core.systems.fate_wheel import FateWheel
    from core.systems.echo_system import EchoSystem
    from core.ai.deepseek_engine import DeepSeekEngine
    AI_AVAILABLE = True
except ImportError as e:
    print(f"AI modules not available: {e}")
    AI_AVAILABLE = False

class GameService:
    def __init__(self):
        self.game_sessions = {}
        self.ai_engine = None
        
        if AI_AVAILABLE:
            try:
                self.ai_engine = DeepSeekEngine()
                print("AI Engine initialized successfully")
            except Exception as e:
                print(f"AI Engine failed to initialize: {e}")

    def get_mbti_types(self) -> Dict[str, Any]:
        if AI_AVAILABLE:
            return MBTITraits.get_all_types()
        else:
            return {
                "INTP": {"description": "逻辑学家 - 创新的发明家"},
                "ENTJ": {"description": "指挥官 - 大胆的领导者"},
                "ISFJ": {"description": "守护者 - 温暖的保护者"},
                "ESFP": {"description": "表演者 - 自发的娱乐者"}
            }

    def get_fate_wheel(self) -> Dict[str, Any]:
        if AI_AVAILABLE:
            return {fate.value: FateWheel.get_fate_info(fate) for fate in FateWheel.FateType}
        else:
            return {
                '💰 亿万富豪': {'initial_money': 100000000, 'description': '亿万富豪家庭'},
                '📚 书香门第': {'initial_money': 1000000, 'description': '知识分子家庭'},
                '💔 家道中落': {'initial_money': 10000, 'description': '曾经辉煌的家族'},
                '💰 低收入户': {'initial_money': 25000, 'description': '家庭收入微薄'}
            }

    async def create_avatar(self, name: str, mbti: str, session_id: str) -> Dict[str, Any]:
        if AI_AVAILABLE:
            avatar = AIAvatar(name, mbti)
            avatar_data = {
                "name": avatar.name,
                "mbti": avatar.mbti,
                "fate": avatar.fate.value,
                "credits": avatar.credits,
                "background_story": avatar.background_story,
                "special_traits": avatar.special_traits,
                "health": 100,
                "energy": 100,
                "happiness": 100,
                "stress": 0,
                "trust_level": 50,
                "intervention_points": 10
            }
            
            self.game_sessions[session_id] = {
                "avatar": avatar,
                "avatar_data": avatar_data,
                "echo_system": EchoSystem(avatar)
            }
        else:
            # 简化版本
            fates = ['💰 亿万富豪', '📚 书香门第', '💔 家道中落', '💰 低收入户']
            fate_name = random.choice(fates)
            credits_map = {'💰 亿万富豪': 100000000, '📚 书香门第': 1000000, '💔 家道中落': 10000, '💰 低收入户': 25000}
            
            avatar_data = {
                "name": name,
                "mbti": mbti,
                "fate": fate_name,
                "credits": credits_map[fate_name],
                "background_story": f"你是{name}，{mbti}类型。",
                "special_traits": ["智慧", "勇气", "坚持"],
                "health": 100,
                "energy": 100,
                "happiness": 100,
                "stress": 0,
                "trust_level": 50,
                "intervention_points": 10
            }
            
            self.game_sessions[session_id] = {"avatar_data": avatar_data}
        
        return avatar_data

    async def generate_situation(self, session_id: str, context: str = "") -> Dict[str, Any]:
        if session_id not in self.game_sessions:
            raise Exception("Session not found")
        
        session = self.game_sessions[session_id]
        
        if AI_AVAILABLE and "avatar" in session:
            try:
                avatar = session["avatar"]
                situation = self.ai_engine.generate_situation(avatar, context)
                session["current_situation"] = situation
                
                return {
                    "situation": situation["description"],
                    "options": situation["choices"],
                    "context_type": context
                }
            except Exception as e:
                print(f"AI situation generation failed: {e}")
        
        # 简化的情况生成
        situations = [
            {
                "situation": "银行经理向你推荐一个新的投资产品，年化收益率8%，但需要锁定资金2年。",
                "options": ["投资50万元到该产品", "只投资10万元试水", "拒绝投资，寻找其他机会"]
            },
            {
                "situation": "公司提供两个职位选择：高薪但压力大的管理岗，或稳定的技术岗。",
                "options": ["选择管理岗位，追求高收入", "选择技术岗位，追求稳定", "继续寻找其他工作机会"]
            },
            {
                "situation": "朋友邀请你投资他的创业项目，需要投入30万元，成功率不确定。",
                "options": ["全力支持朋友，投资30万", "小额投资5万表示支持", "礼貌拒绝，保持友谊"]
            }
        ]
        
        situation = random.choice(situations)
        session["current_situation"] = situation
        return situation

    async def send_echo(self, session_id: str, echo_text: str) -> Dict[str, Any]:
        if session_id not in self.game_sessions:
            raise Exception("Session not found")
        
        session = self.game_sessions[session_id]
        
        if AI_AVAILABLE and "avatar" in session and "echo_system" in session:
            try:
                avatar = session["avatar"]
                echo_system = session["echo_system"]
                current_situation = session.get("current_situation")
                
                if not current_situation:
                    raise Exception("No current situation")
                
                echo_analysis = echo_system.analyze_echo(echo_text)
                decision = self.ai_engine.make_decision(avatar, current_situation, echo_text)
                
                # 更新化身状态
                if hasattr(avatar, 'apply_decision_effects'):
                    avatar.apply_decision_effects(decision)
                
                # 更新会话数据
                session["avatar_data"] = {
                    "name": avatar.name,
                    "mbti": avatar.mbti,
                    "fate": avatar.fate.value,
                    "credits": avatar.credits,
                    "health": getattr(avatar, 'health', 100),
                    "energy": getattr(avatar, 'energy', 100),
                    "happiness": getattr(avatar, 'happiness', 100),
                    "stress": getattr(avatar, 'stress', 0),
                    "trust_level": getattr(avatar, 'trust_level', 50),
                    "intervention_points": getattr(avatar, 'intervention_points', 10)
                }
                
                return {
                    "echo_analysis": echo_analysis,
                    "decision": decision,
                    "avatar": session["avatar_data"]
                }
            except Exception as e:
                print(f"AI decision failed: {e}")
        
        # 简化的AI决策
        avatar_data = session["avatar_data"]
        current_situation = session.get("current_situation", {})
        options = current_situation.get("options", ["选择第一个选项", "选择第二个选项", "选择第三个选项"])
        
        chosen = random.choice(options)
        credit_change = random.randint(-50000, 100000)
        new_credits = max(0, avatar_data["credits"] + credit_change)
        avatar_data["credits"] = new_credits
        
        ai_thoughts = f"考虑了你的建议'{echo_text}'，我觉得{chosen}比较合适。"
        
        return {
            "echo_analysis": {"type": "advisory", "confidence": 0.8},
            "decision": {
                "chosen_option": chosen,
                "ai_thoughts": ai_thoughts,
                "new_credits": new_credits,
                "trust_change": random.randint(-2, 5)
            },
            "avatar": avatar_data
        }

    async def auto_decision(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.game_sessions:
            raise Exception("Session not found")
        
        session = self.game_sessions[session_id]
        current_situation = session.get("current_situation", {})
        
        if not current_situation:
            raise Exception("No current situation")
        
        # 简化的自主决策
        options = current_situation.get("options", ["选择第一个选项"])
        chosen = random.choice(options)
        
        avatar_data = session["avatar_data"]
        credit_change = random.randint(-30000, 80000)
        new_credits = max(0, avatar_data["credits"] + credit_change)
        avatar_data["credits"] = new_credits
        
        return {
            "decision": {
                "chosen_option": chosen,
                "ai_thoughts": f"经过深思熟虑，我选择了{chosen}。",
                "new_credits": new_credits,
                "trust_change": 0
            },
            "avatar": avatar_data
        }