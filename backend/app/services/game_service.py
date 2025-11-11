"""
游戏服务层 - 业务逻辑处理
"""
import random
from typing import Dict, Any
import uuid

# 尝试导入核心游戏系统
try:
    from core.avatar.ai_avatar import AIAvatar
    from core.systems.mbti_traits import MBTITraits
    from core.systems.fate_wheel import FateWheel, FateType
    from core.systems.echo_system import EchoSystem
    from core.systems.asset_calculator import asset_calculator
    from core.systems.investment_system import investment_system
    from core.ai.deepseek_engine import DeepSeekEngine
    AI_AVAILABLE = True
except ImportError as e:
    print(f"AI modules not available: {e}")
    AI_AVAILABLE = False

class GameService:
    def __init__(self):
        self.game_sessions = {}
        self.session_to_avatar = {}  # 新增：session_id -> avatar_id 映射
        self.ai_engine = None
        
        # 初始化数据库
        try:
            from core.database.database import db
            self.db = db
            print(f"Database initialized: {self.db}")
        except ImportError as e:
            print(f"Database import failed: {e}")
            self.db = None
        
        if AI_AVAILABLE:
            try:
                self.ai_engine = DeepSeekEngine()
                print(f"AI Engine initialized successfully with API key: {self.ai_engine.api_key is not None}")
            except Exception as e:
                print(f"AI Engine failed to initialize: {e}")
                self.ai_engine = None

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
            return {fate.value: FateWheel.get_fate_info(fate) for fate in FateType}
        else:
            return {
                '💰 亿万富豪': {'initial_money': 100000000, 'description': '亿万富豪家庭'},
                '📚 书香门第': {'initial_money': 1000000, 'description': '知识分子家庭'},
                '💔 家道中落': {'initial_money': 10000, 'description': '曾经辉煌的家族'},
                '💰 低收入户': {'initial_money': 25000, 'description': '家庭收入微薄'}
            }

    def _get_investment_data(self):
        """获取投资数据"""
        try:
            active_investments = investment_system.get_active_investments()
            recent_transactions = investment_system.get_recent_transactions(10)
            return active_investments, recent_transactions
        except:
            return [], []

    def _build_avatar_data(self, avatar, session_id: str = None, avatar_id: str = None):
        """构建化身数据"""
        # 优先使用 avatar_id 在数据库中查询该化身的投资与交易
        if avatar_id and self.db:
            try:
                active_investments = self.db.get_avatar_investments(avatar_id)
                recent_transactions = self.db.get_avatar_transactions(avatar_id, 10)
            except Exception:
                active_investments, recent_transactions = self._get_investment_data()
        else:
            active_investments, recent_transactions = self._get_investment_data()
        return {
            "avatar_id": avatar_id,
            "name": avatar.attributes.name,
            "mbti": getattr(avatar.attributes.mbti_type, 'value', avatar.attributes.mbti_type),
            "fate": getattr(avatar.attributes.fate_type, 'value', avatar.attributes.fate_type),
            "credits": avatar.attributes.credits,
            "long_term_investments": avatar.attributes.long_term_investments,
            "locked_investments": avatar.attributes.locked_investments,
            "active_investments": [{
                "name": inv.get('name') if isinstance(inv, dict) else inv.name,
                "amount": inv.get('amount') if isinstance(inv, dict) else inv.amount,
                "type": inv.get('type') if isinstance(inv, dict) else inv.investment_type.value,
                "monthly_return": inv.get('monthly_return') if isinstance(inv, dict) else inv.monthly_return,
                "remaining_months": inv.get('remaining_months') if isinstance(inv, dict) else inv.remaining_months
            } for inv in active_investments],
            "transaction_history": [{
                "round": tx.get('round') if isinstance(tx, dict) else tx.round_num,
                "type": tx.get('type', '交易') if isinstance(tx, dict) else "交易",
                "amount": tx.get('amount') if isinstance(tx, dict) else tx.amount,
                "description": tx.get('description') if isinstance(tx, dict) else tx.transaction_name
            } for tx in recent_transactions],
            "total_assets": avatar.attributes.credits + avatar.attributes.long_term_investments + sum(inv.get('amount', 0) for inv in avatar.attributes.locked_investments),
            "cash_flow": avatar._calculate_cash_flow(),
            "health": avatar.attributes.health,
            "energy": avatar.attributes.energy,
            "happiness": avatar.attributes.happiness,
            "stress": avatar.attributes.stress,
            "trust_level": avatar.attributes.trust_level,
            "current_round": avatar.attributes.current_round,
            "intervention_points": 10
        }

    async def create_avatar(self, name: str, mbti: str, session_id: str, username: str = None) -> Dict[str, Any]:
        avatar_id = str(uuid.uuid4())
        if AI_AVAILABLE:
            from core.systems.mbti_traits import MBTIType
            mbti_type = MBTIType(mbti.upper())
            avatar = AIAvatar(name, mbti_type, session_id, username=username, avatar_id=avatar_id)
            if self.db and username:
                self.db.save_user(username, avatar_id, session_id, avatar.attributes.name, getattr(avatar.attributes.mbti_type, 'value', str(avatar.attributes.mbti_type)), getattr(avatar.attributes.fate_type, 'value', str(avatar.attributes.fate_type)), avatar.attributes.credits)
            avatar_data = self._build_avatar_data(avatar, session_id, avatar_id)
            try:
                echo_system = EchoSystem(avatar)
            except TypeError:
                echo_system = EchoSystem()
            self.game_sessions[session_id] = {"avatar": avatar, "avatar_data": avatar_data, "echo_system": echo_system, "avatar_id": avatar_id}
        else:
            # 简化版本
            fates = ['💰 亿万富豪', '📚 书香门第', '💔 家道中落', '💪 白手起家', '🏠 中产家庭', '🔧 工薪阶层', '💰 低收入户']
            fate_name = random.choice(fates)
            credits_map = {'💰 亿万富豪': 100000000, '📚 书香门第': 1000000, '💔 家道中落': 10000, '💪 白手起家': 50000, '🏠 中产家庭': 200000, '🔧 工薪阶层': 30000, '💰 低收入户': 25000}
            avatar_data = {"avatar_id": avatar_id, "name": name, "mbti": mbti, "fate": fate_name, "credits": credits_map[fate_name], "active_investments": [], "transaction_history": [], "background_story": f"你是{name}，{mbti}类型。", "special_traits": ["智慧", "勇气", "坚持"], "health": 100, "energy": 100, "happiness": 100, "stress": 0, "trust_level": 50, "intervention_points": 10}
            self.game_sessions[session_id] = {"avatar_data": avatar_data, "avatar_id": avatar_id}
            if self.db and username:
                self.db.save_user(username, avatar_id, session_id, name, mbti, fate_name, credits_map[fate_name])
        self.session_to_avatar[session_id] = avatar_id
        return avatar_data

    # 新增：列出账号所有化身
    def list_avatars(self, username: str):
        if self.db:
            return self.db.list_avatars(username)
        return []

    # 新增：获取单化身
    def get_avatar(self, avatar_id: str):
        if self.db:
            return self.db.get_avatar(avatar_id)
        return None

    # 新增：重置化身
    def reset_avatar(self, avatar_id: str):
        if self.db:
            ok = self.db.reset_avatar(avatar_id)
            return ok
        return False

    def start_session(self, avatar_id: str, session_id: str):
        """根据化身ID开始一个新会话，并创建 AIAvatar 实例"""
        if not self.db:
            return None
        avatar = self.db.get_avatar(avatar_id)
        if not avatar:
            return None
        # 创建 AIAvatar
        try:
            from core.systems.mbti_traits import MBTIType
            ai_avatar = AIAvatar(
                avatar["name"],
                MBTIType(avatar["mbti"]),
                session_id=session_id,
                username=avatar.get("username"),
                avatar_id=avatar_id
            )
            # 覆盖随机命运为数据库中保存的命运
            from core.systems.fate_wheel import FateType
            try:
                ai_avatar.attributes.fate_type = FateType(avatar["fate"]) if isinstance(avatar["fate"], str) else avatar["fate"]
            except Exception:
                pass
            ai_avatar.attributes.credits = avatar.get("credits", ai_avatar.attributes.credits)
            ai_avatar.attributes.health = avatar.get("health", ai_avatar.attributes.health)
            ai_avatar.attributes.energy = avatar.get("energy", ai_avatar.attributes.energy)
            ai_avatar.attributes.happiness = avatar.get("happiness", ai_avatar.attributes.happiness)
            ai_avatar.attributes.stress = avatar.get("stress", ai_avatar.attributes.stress)
            ai_avatar.attributes.trust_level = avatar.get("trust_level", ai_avatar.attributes.trust_level)
            ai_avatar.attributes.current_round = avatar.get("current_round", ai_avatar.attributes.current_round)
            ai_avatar.attributes.long_term_investments = avatar.get("long_term_investments", 0)
            ai_avatar.attributes.locked_investments = avatar.get("locked_investments", [])
        except Exception as e:
            print(f"[ERROR] start_session create AIAvatar failed: {e}")
            return None
        # 写入会话
        avatar_data = self._build_avatar_data(ai_avatar, session_id, avatar_id)
        try:
            echo_system = EchoSystem(ai_avatar)
        except TypeError:
            echo_system = EchoSystem()
        self.game_sessions[session_id] = {
            "avatar": ai_avatar,
            "avatar_data": avatar_data,
            "echo_system": echo_system,
            "avatar_id": avatar_id
        }
        self.session_to_avatar[session_id] = avatar_id
        return avatar_data

    async def generate_situation(self, session_id: str, context: str = "") -> Dict[str, Any]:
        print(f"[DEBUG] generate_situation called for session: {session_id}")
        print(f"[DEBUG] AI_AVAILABLE: {AI_AVAILABLE}")
        print(f"[DEBUG] AI engine available: {self.ai_engine is not None}")
        if self.ai_engine:
            print(f"[DEBUG] AI engine has API key: {self.ai_engine.api_key is not None}")
        
        if session_id not in self.game_sessions:
            avatar_id = self.session_to_avatar.get(session_id)
            if avatar_id and self.db:
                avatar_record = self.db.get_avatar(avatar_id)
                if avatar_record:
                    # 构造最小 avatar_data 占位供后续 AIAvatar 创建
                    self.game_sessions[session_id] = {
                        "avatar_data": {
                            "name": avatar_record["name"],
                            "mbti": avatar_record["mbti"],
                            "fate": avatar_record["fate"],
                            "credits": avatar_record["credits"]
                        },
                        "avatar_id": avatar_id
                    }
            if session_id not in self.game_sessions:
                raise Exception("Session not found")

        session = self.game_sessions[session_id]
        print(f"[DEBUG] Session has avatar: {'avatar' in session}")
        
        # 检查是否需要创建 AI Avatar
        if AI_AVAILABLE and self.ai_engine and self.ai_engine.api_key:
            if "avatar" not in session:
                # 创建 AI Avatar 实例
                try:
                    from core.systems.mbti_traits import MBTIType
                    
                    avatar_data = session["avatar_data"]
                    mbti_type = MBTIType(avatar_data["mbti"])
                    username = None
                    avatar_id = session.get("avatar_id")
                    if avatar_id and self.db:
                        rec = self.db.get_avatar(avatar_id)
                        if rec:
                            username = rec.get('username')
                    avatar = AIAvatar(avatar_data["name"], mbti_type, session_id, username=username, avatar_id=session.get("avatar_id"))
                    session["avatar"] = avatar
                    print(f"[DEBUG] Created AI Avatar for session {session_id}")
                except Exception as e:
                    print(f"[ERROR] Failed to create AI Avatar: {e}")
        
        if AI_AVAILABLE and "avatar" in session and self.ai_engine and self.ai_engine.api_key:
            try:
                print(f"[DEBUG] Trying AI situation generation...")
                avatar = session["avatar"]
                situation = avatar.generate_situation(self.ai_engine)
                if situation:
                    print(f"[DEBUG] AI situation generated successfully")
                    session["current_situation"] = situation
                    return {
                        "situation": situation.situation,
                        "options": situation.options,
                        "context_type": context,
                        "ai_generated": True
                    }
                else:
                    print(f"[DEBUG] AI situation generation returned None")
            except Exception as e:
                print(f"[ERROR] AI situation generation failed: {e}")
                import traceback
                traceback.print_exc()
        
        # 简化的情况生成（备用方案）
        print(f"[DEBUG] Using fallback situation generation")
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
        return {
            **situation,
            "ai_generated": False
        }

    async def send_echo(self, session_id: str, echo_text: str) -> Dict[str, Any]:
        if session_id not in self.game_sessions:
            avatar_id = self.session_to_avatar.get(session_id)
            if avatar_id and self.db:
                avatar_record = self.db.get_avatar(avatar_id)
                if avatar_record:
                    self.game_sessions[session_id] = {
                        "avatar_data": {
                            "name": avatar_record["name"],
                            "mbti": avatar_record["mbti"],
                            "fate": avatar_record["fate"],
                            "credits": avatar_record["credits"]
                        },
                        "avatar_id": avatar_id
                    }
            if session_id not in self.game_sessions:
                raise Exception("Session not found")

        session = self.game_sessions[session_id]
        
        if AI_AVAILABLE and "avatar" in session and self.ai_engine:
            try:
                avatar = session["avatar"]
                current_situation = session.get("current_situation")
                
                if not current_situation:
                    raise Exception("No current situation")
                
                decision_result = avatar.make_decision(echo_text, self.ai_engine)
                
                if "error" not in decision_result:
                    session["avatar_data"] = self._build_avatar_data(avatar, session_id, session.get("avatar_id"))

                    # 自动生成下一个情况
                    next_situation = None
                    if not decision_result.get("is_bankrupt", False):
                        try:
                            next_situation = avatar.generate_situation(self.ai_engine)
                            if next_situation:
                                session["current_situation"] = next_situation
                        except Exception as e:
                            print(f"Auto-generate next situation failed: {e}")
                    
                    return {
                        "echo_analysis": {"type": "advisory", "confidence": 0.8, "ai_powered": True},
                        "decision": {
                            "chosen_option": decision_result["chosen_option"],
                            "ai_thoughts": decision_result["ai_thoughts"],
                            "new_credits": decision_result["new_credits"],
                            "trust_change": decision_result["trust_change"],
                            "asset_change": decision_result.get("asset_change", 0),
                            "current_round": decision_result.get("current_round", 1),
                            "ai_powered": True,
                            "decision_impact": decision_result.get("decision_impact", {})
                        },
                        "avatar": session["avatar_data"],
                        "next_situation": {
                            "situation": next_situation.situation if next_situation else None,
                            "options": next_situation.options if next_situation else None
                        } if next_situation else None
                    }
                else:
                    raise Exception(decision_result["error"])
                    
            except Exception as e:
                print(f"AI decision failed: {e}")
        
        # 简化的AI决策
        avatar_data = session["avatar_data"]
        current_situation = session.get("current_situation", {})
        if hasattr(current_situation, 'options'):
            options = current_situation.options
        else:
            options = current_situation.get("options", ["选择第一个选项", "选择第二个选项", "选择第三个选项"])
        
        chosen = random.choice(options)
        credit_change = random.randint(-50000, 100000)
        new_credits = max(0, avatar_data["credits"] + credit_change)
        avatar_data["credits"] = new_credits
        
        ai_thoughts = f"考虑了你的建议'{echo_text}'，我觉得{chosen}比较合适。"
        
        return {
            "echo_analysis": {"type": "advisory", "confidence": 0.8, "ai_powered": False},
            "decision": {
                "chosen_option": chosen,
                "ai_thoughts": ai_thoughts,
                "new_credits": new_credits,
                "trust_change": random.randint(-2, 5),
                "ai_powered": False,
                "decision_impact": {
                    "cash_change": credit_change,
                    "trust_change": random.randint(-2, 5)
                }
            },
            "avatar": avatar_data
        }

    async def auto_decision(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.game_sessions:
            avatar_id = self.session_to_avatar.get(session_id)
            if avatar_id and self.db:
                avatar_record = self.db.get_avatar(avatar_id)
                if avatar_record:
                    self.game_sessions[session_id] = {
                        "avatar_data": {
                            "name": avatar_record["name"],
                            "mbti": avatar_record["mbti"],
                            "fate": avatar_record["fate"],
                            "credits": avatar_record["credits"]
                        },
                        "avatar_id": avatar_id
                    }
            if session_id not in self.game_sessions:
                raise Exception("Session not found")

        session = self.game_sessions[session_id]
        current_situation = session.get("current_situation", {})
        
        if not current_situation:
            raise Exception("No current situation")
        
        if AI_AVAILABLE and "avatar" in session and self.ai_engine:
            try:
                avatar = session["avatar"]
                decision_result = avatar.make_decision(None, self.ai_engine)
                
                if "error" not in decision_result:
                    session["avatar_data"] = self._build_avatar_data(avatar, session_id, session.get("avatar_id"))

                    # 自动生成下一个情况
                    next_situation = None
                    if not decision_result.get("is_bankrupt", False):
                        try:
                            next_situation = avatar.generate_situation(self.ai_engine)
                            if next_situation:
                                session["current_situation"] = next_situation
                        except Exception as e:
                            print(f"Auto-generate next situation failed: {e}")
                    
                    return {
                        "decision": {
                            "chosen_option": decision_result["chosen_option"],
                            "ai_thoughts": decision_result["ai_thoughts"],
                            "new_credits": decision_result["new_credits"],
                            "trust_change": decision_result["trust_change"],
                            "asset_change": decision_result.get("asset_change", 0),
                            "current_round": decision_result.get("current_round", 1),
                            "ai_powered": True,
                            "decision_impact": decision_result.get("decision_impact", {})
                        },
                        "avatar": session["avatar_data"],
                        "next_situation": {
                            "situation": next_situation.situation if next_situation else None,
                            "options": next_situation.options if next_situation else None
                        } if next_situation else None
                    }
                else:
                    raise Exception(decision_result["error"])
                    
            except Exception as e:
                print(f"AI auto decision failed: {e}")
        
        # 简化的自主决策（备用）
        if hasattr(current_situation, 'options'):
            options = current_situation.options
        else:
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
                "trust_change": 0,
                "ai_powered": False,
                "decision_impact": {
                    "cash_change": credit_change,
                    "trust_change": 0
                }
            },
            "avatar": avatar_data
        }
    
    def create_account(self, username: str, password: str) -> bool:
        """创建账户"""
        if self.db:
            return self.db.create_account(username, password)
        return False
    
    def verify_account(self, username: str, password: str) -> bool:
        """验证账户"""
        if self.db:
            return self.db.verify_account(username, password)
        return False
    
    def get_user_investments(self, username: str):
        """获取用户投资"""
        if self.db:
            return self.db.get_user_investments(username)
        return []
    
    def get_user_transactions(self, username: str, limit: int = 10):
        """获取用户交易记录"""
        if self.db:
            return self.db.get_user_transactions(username, limit)
        return []
    
    def get_user_info(self, username: str):
        """获取用户信息"""
        if self.db:
            return self.db.get_user_info(username)
        return None

    def get_avatar_investments(self, avatar_id: str):
        if self.db:
            return self.db.get_avatar_investments(avatar_id)
        return []

    def get_avatar_transactions(self, avatar_id: str, limit: int = 10):
        if self.db:
            return self.db.get_avatar_transactions(avatar_id, limit)
        return []
