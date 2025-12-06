"""
游戏服务层 - 业务逻辑处理
"""
import random
from typing import Dict, Any, Optional, List

# 尝试导入核心游戏系统
try:
    from core.avatar.ai_avatar import AIAvatar
    from core.systems.mbti_traits import MBTITraits
    from core.systems.fate_wheel import FateWheel
    from core.systems.echo_system import EchoSystem
    from core.systems.asset_calculator import asset_calculator
    from core.systems.investment_system import investment_system
    from core.systems.macro_economy import macro_economy
    from core.systems.behavior_insight_system import BehaviorInsightSystem
    from core.ai.deepseek_engine import DeepSeekEngine
    AI_AVAILABLE = True
except ImportError as e:
    print(f"AI modules not available: {e}")
    AI_AVAILABLE = False

class GameService:
    def __init__(self):
        self.game_sessions = {}
        self.ai_engine = None
        self.behavior_system = None
        
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
            
            # 初始化行为洞察系统
            try:
                if self.db:
                    self.behavior_system = BehaviorInsightSystem(self.db)
                    print("Behavior Insight System initialized successfully")
            except Exception as e:
                print(f"Behavior Insight System failed to initialize: {e}")
                self.behavior_system = None

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

    def _get_investment_data(self):
        """获取投资数据"""
        try:
            active_investments = investment_system.get_active_investments()
            recent_transactions = investment_system.get_recent_transactions(10)
            return active_investments, recent_transactions
        except:
            return [], []

    def _build_avatar_data(self, avatar, session_id: str = None):
        """构建化身数据"""
        # 从数据库获取数据
        if session_id and self.db:
            active_investments = self.db.get_user_investments(session_id)
            recent_transactions = self.db.get_user_transactions(session_id, 10)
        else:
            active_investments, recent_transactions = self._get_investment_data()
        
        return {
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

    async def create_avatar(self, name: str, mbti: str, session_id: str) -> Dict[str, Any]:
        if AI_AVAILABLE:
            from core.systems.mbti_traits import MBTIType
            mbti_type = MBTIType(mbti.upper())
            avatar = AIAvatar(name, mbti_type, session_id)
            
            # 保存用户到数据库
            if self.db:
                self.db.save_user(session_id, session_id, avatar.attributes.name, 
                               getattr(avatar.attributes.mbti_type, 'value', str(avatar.attributes.mbti_type)),
                               getattr(avatar.attributes.fate_type, 'value', str(avatar.attributes.fate_type)),
                               avatar.attributes.credits)
            
            avatar_data = self._build_avatar_data(avatar, session_id)
            
            try:
                echo_system = EchoSystem(avatar)
            except TypeError:
                echo_system = EchoSystem()
            
            self.game_sessions[session_id] = {
                "avatar": avatar,
                "avatar_data": avatar_data,
                "echo_system": echo_system
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
                "active_investments": [],
                "transaction_history": [],
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
        context_str = context if isinstance(context, str) else (context or "")
        print(f"[DEBUG] generate_situation called for session: {session_id}, context={context_str}")
        print(f"[DEBUG] AI_AVAILABLE: {AI_AVAILABLE}")
        print(f"[DEBUG] AI engine available: {self.ai_engine is not None}")
        if self.ai_engine:
            print(f"[DEBUG] AI engine has API key: {self.ai_engine.api_key is not None}")
        
        if session_id not in self.game_sessions:
            # 如果没有session，尝试从数据库通过session_id加载用户信息
            import sqlite3
            user_info = None
            if self.db:
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT name, mbti, fate, credits FROM users WHERE session_id = ?', (session_id,))
                    result = cursor.fetchone()
                    if result:
                        user_info = {
                            'name': result[0],
                            'mbti': result[1],
                            'fate': result[2],
                            'credits': result[3]
                        }
            
            if not user_info:
                raise Exception(f"Session {session_id} not found in database")
            
            # 创建临时session
            self.game_sessions[session_id] = {
                "avatar_data": user_info
            }
        session = self.game_sessions[session_id]
        print(f"[DEBUG] Session has avatar: {'avatar' in session}")
        
        # 检查是否需要创建 AI Avatar
        if AI_AVAILABLE and self.ai_engine and self.ai_engine.api_key:
            if "avatar" not in session:
                # 创建 AI Avatar 实例
                try:
                    from core.avatar.ai_avatar import AIAvatar
                    from core.systems.mbti_traits import MBTIType
                    
                    avatar_data = session["avatar_data"]
                    mbti_type = MBTIType(avatar_data["mbti"])
                    avatar = AIAvatar(avatar_data["name"], mbti_type, session_id)
                    session["avatar"] = avatar
                    print(f"[DEBUG] Created AI Avatar for session {session_id}")
                except Exception as e:
                    print(f"[ERROR] Failed to create AI Avatar: {e}")
        
        if AI_AVAILABLE and "avatar" in session and self.ai_engine and self.ai_engine.api_key:
            try:
                print(f"[DEBUG] Trying AI situation generation...")
                avatar = session["avatar"]
                
                # 设置用户标签到 avatar
                try:
                    import sqlite3
                    with sqlite3.connect(self.db.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT tags FROM users WHERE session_id = ?', (session_id,))
                        row = cursor.fetchone()
                        if row and row[0]:
                            avatar.set_user_tags(row[0])
                            print(f"[DEBUG] Set user tags: {row[0]}")
                except Exception as e:
                    print(f"[DEBUG] Failed to get user tags: {e}")
                
                # 设置行为画像数据到 avatar
                if self.behavior_system:
                    try:
                        behavior_profile = self.db.get_behavior_profile(session_id)
                        if behavior_profile:
                            avatar.set_behavior_profile(behavior_profile)
                            # 设置自动标签
                            if behavior_profile.get('auto_tags'):
                                avatar.set_auto_tags(behavior_profile.get('auto_tags'))
                            print(f"[DEBUG] Set behavior profile: {behavior_profile.get('risk_preference')}")
                    except Exception as e:
                        print(f"[DEBUG] Failed to get behavior profile: {e}")
                
                # 设置职业状态到 avatar
                try:
                    from core.systems.career_system import career_system
                    career_info = career_system.get_career_status(session_id)
                    # career_info 可能为 None（玩家无业时），需要转换为标准格式
                    if career_info:
                        avatar.set_career_status({"current_job": career_info})
                        print(f"[DEBUG] Set career status: {career_info.get('title', '未知')}")
                    else:
                        avatar.set_career_status({"current_job": None})
                        print(f"[DEBUG] Set career status: 无业")
                except Exception as e:
                    print(f"[DEBUG] Failed to get career status: {e}")
                
                # 使用 asyncio.to_thread 将阻塞的 AI 调用放到线程池，避免阻塞事件循环
                import asyncio
                situation = await asyncio.to_thread(avatar.generate_situation, self.ai_engine)
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
            # 如果没有session，尝试从数据库加载用户信息
            user_info = self.get_user_info(session_id)
            if not user_info:
                raise Exception("Session not found")
            
            # 创建临时session
            self.game_sessions[session_id] = {
                "avatar_data": user_info
            }
        
        session = self.game_sessions[session_id]
        
        if AI_AVAILABLE and "avatar" in session and self.ai_engine:
            try:
                avatar = session["avatar"]
                current_situation = session.get("current_situation")
                
                if not current_situation:
                    raise Exception("No current situation")
                
                decision_result = avatar.make_decision(echo_text, self.ai_engine)
                
                if "error" not in decision_result:
                    session["avatar_data"] = self._build_avatar_data(avatar, session_id)
                    
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
            # 如果没有session，尝试从数据库加载用户信息
            user_info = self.get_user_info(session_id)
            if not user_info:
                raise Exception("Session not found")
            
            # 创建临时session
            self.game_sessions[session_id] = {
                "avatar_data": user_info
            }
        
        session = self.game_sessions[session_id]
        current_situation = session.get("current_situation", {})
        
        if not current_situation:
            raise Exception("No current situation")
        
        if AI_AVAILABLE and "avatar" in session and self.ai_engine:
            try:
                avatar = session["avatar"]
                decision_result = avatar.make_decision(None, self.ai_engine)
                
                if "error" not in decision_result:
                    session["avatar_data"] = self._build_avatar_data(avatar, session_id)
                    
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

    def start_session(self, username: str, name: str, mbti: str) -> Dict[str, Any]:
        """创建一个新的游戏会话并返回基础状态"""
        if not self.db:
            raise Exception("数据库未初始化")
        # 简单使用 username+随机后缀 作为 session_id
        import uuid
        session_id = f"{username}_{uuid.uuid4().hex[:8]}"
        # 默认命运先用中产阶级，或由前端命运轮盘单独写入
        fate = "DEFAULT"
        # 初始信用点（可根据命运轮盘扩展）
        initial_credits = 50000
        # 保存用户与会话
        self.db.save_user(username=username, session_id=session_id, name=name, mbti=mbti, fate=fate, credits=initial_credits)
        self.db.upsert_session(session_id=session_id, username=username)
        # 初始化月度快照（第1月）
        self.db.save_monthly_snapshot(
            session_id=session_id,
            month=1,
            total_assets=initial_credits,
            cash=initial_credits,
            invested_assets=0,
            trust_level=50,
            happiness=60,
            stress=20,
        )
        return {
            "session_id": session_id,
            "username": username,
            "name": name,
            "mbti": mbti,
            "current_month": 1,
            "total_assets": initial_credits,
            "cash": initial_credits,
            "trust_level": 50,
        }

    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """聚合会话当前状态：资产/投资/情绪"""
        if not self.db:
            raise Exception("数据库未初始化")
        import sqlite3
        from core.systems.market_engine import market_engine
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, mbti, credits, username FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if not row:
                raise Exception("会话不存在")
            name, mbti, credits, username = row
            cursor.execute('SELECT current_month FROM sessions WHERE session_id = ?', (session_id,))
            srow = cursor.fetchone()
            current_month = srow[0] if srow else 1
            
            # 当前投资（非股票类）
            cursor.execute('''
                SELECT SUM(amount) FROM investments
                WHERE session_id = ? AND remaining_months > 0
            ''', (session_id,))
            invested = cursor.fetchone()[0] or 0
            
            # 存款总额
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) FROM financial_holdings
                WHERE session_id = ? AND product_type = 'deposit' AND is_active = 1
            ''', (session_id,))
            deposits = cursor.fetchone()[0] or 0
            
            # 股票持仓市值
            cursor.execute('''
                SELECT stock_id, shares, avg_cost FROM stock_holdings
                WHERE session_id = ? AND shares > 0
            ''', (session_id,))
            stock_holdings = cursor.fetchall()
            stock_value = 0
            for stock_id, shares, avg_cost in stock_holdings:
                stock = market_engine.get_stock_quote(stock_id)
                if stock:
                    stock_value += int(stock["price"] * shares)
                else:
                    stock_value += int(avg_cost * shares)  # fallback to cost
            
            # 贷款负债
            cursor.execute('''
                SELECT COALESCE(SUM(remaining_principal), 0) FROM loans
                WHERE session_id = ? AND remaining_months > 0
            ''', (session_id,))
            loans = cursor.fetchone()[0] or 0
            
            # 总资产 = 现金 + 存款 + 投资 + 股票市值 - 贷款
            total_assets = credits + deposits + invested + stock_value - loans
            
        timeline = self.db.get_session_timeline(session_id, limit=36)
        return {
            "session_id": session_id,
            "name": name,
            "mbti": mbti,
            "username": username,
            "current_month": current_month,
            "cash": credits,
            "invested_assets": invested + stock_value,
            "deposits": deposits,
            "loans": loans,
            "stock_value": stock_value,
            "total_assets": total_assets,
            "timeline": timeline,
        }

    def advance_session(self, session_id: str, echo_text: Optional[str] = None) -> Dict[str, Any]:
        """推进一个月份：整合所有系统的月度更新"""
        print(f"[GameService] advance_session start: {session_id}")
        if not self.db:
            raise Exception("数据库未初始化")
            
        # 推进宏观经济
        macro_stats = macro_economy.advance_month()
        print(f"[GameService] Macro stats: {macro_stats}")
        asset_impact = macro_economy.get_asset_impact()
        
        import sqlite3
        # 加载基本状态
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取用户完整状态（包括生活属性）
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            has_stats = 'happiness' in columns
            
            if has_stats:
                cursor.execute('SELECT name, mbti, credits, username, happiness, energy, health FROM users WHERE session_id = ?', (session_id,))
            else:
                cursor.execute('SELECT name, mbti, credits, username FROM users WHERE session_id = ?', (session_id,))
            
            row = cursor.fetchone()
            if not row:
                raise Exception("会话不存在")
            
            name, mbti, cash, username = row[:4]
            happiness = row[4] if has_stats and len(row) > 4 else 70
            energy = row[5] if has_stats and len(row) > 5 else 75
            health = row[6] if has_stats and len(row) > 6 else 80
            
            # ============ 1. 投资系统 ============
            cursor.execute('SELECT SUM(amount) FROM investments WHERE session_id = ? AND remaining_months > 0', (session_id,))
            invested = cursor.fetchone()[0] or 0
            
            # 投资收益计算
            cursor.execute('''
                SELECT id, name, amount, return_rate, monthly_return, investment_type
                FROM investments 
                WHERE session_id = ? AND remaining_months > 0
            ''', (session_id,))
            
            investment_income = 0
            for inv in cursor.fetchall():
                inv_type = inv[5]
                base_return = inv[4]
                amount = inv[2]
                return_rate = inv[3]
                
                # 根据资产类型应用宏观影响
                impact_factor = 1.0
                if "股票" in inv_type or "基金" in inv_type:
                    impact_factor = asset_impact["stock"]
                elif "房产" in inv_type:
                    impact_factor = asset_impact["real_estate"]
                elif "债券" in inv_type:
                    impact_factor = asset_impact["bond"]
                
                # 月收益 = 本金 * 年化收益率 / 12 * 宏观影响
                if return_rate and return_rate > 0:
                    monthly_return = int(amount * return_rate / 12 * impact_factor)
                    investment_income += monthly_return

            # 更新投资剩余月数
            cursor.execute('''
                UPDATE investments SET remaining_months = remaining_months - 1
                WHERE session_id = ? AND remaining_months > 0
            ''', (session_id,))
            
            # 处理到期投资
            cursor.execute('''
                SELECT id, name, amount, return_rate, investment_type
                FROM investments WHERE session_id = ? AND remaining_months <= 0
            ''', (session_id,))
            
            matured_return = 0
            for iid, iname, amount, return_rate, inv_type in cursor.fetchall():
                impact_factor = 1.0
                if "股票" in (inv_type or ''):
                    impact_factor = asset_impact["stock"]
                
                final_amount = int(amount * impact_factor)
                matured_return += final_amount
                cursor.execute('DELETE FROM investments WHERE id = ?', (iid,))
            
            # ============ 2. 职业收入系统 ============
            from core.systems.career_system import career_system
            
            # 获取职业工资
            salary_info = career_system.get_monthly_salary(session_id)
            monthly_salary = salary_info.get('total', 0)
            
            # 如果没有职业，给默认收入
            if monthly_salary == 0:
                monthly_salary = 5000 + random.randint(-500, 1500)
            
            # ============ 3. 副业收入 ============
            side_business_income = 0
            try:
                cursor.execute('''
                    SELECT name, expected_return, risk_rate FROM side_businesses
                    WHERE session_id = ? AND status = 'running'
                ''', (session_id,))
                for biz_name, expected, risk in cursor.fetchall():
                    # 根据风险决定实际收入
                    if random.random() > risk:
                        actual_income = int(expected * random.uniform(0.8, 1.2))
                        side_business_income += actual_income
                    else:
                        # 亏损月
                        side_business_income -= int(expected * random.uniform(0.1, 0.3))
            except:
                pass
            
            # ============ 4. 房产系统 ============
            property_income = 0
            try:
                cursor.execute('''
                    SELECT monthly_rent FROM properties
                    WHERE session_id = ? AND is_rented = 1
                ''', (session_id,))
                for (rent,) in cursor.fetchall():
                    property_income += rent or 0
            except:
                pass
            
            # ============ 5. 贷款还款 ============
            loan_payment = 0
            try:
                cursor.execute('''
                    SELECT loan_id, monthly_payment, remaining_months, remaining_principal
                    FROM loans WHERE session_id = ? AND remaining_months > 0
                ''', (session_id,))
                for loan_id, payment, remaining, principal in cursor.fetchall():
                    loan_payment += payment
                    # 更新贷款
                    cursor.execute('''
                        UPDATE loans SET remaining_months = remaining_months - 1,
                            remaining_principal = remaining_principal - ?
                        WHERE loan_id = ?
                    ''', (int(principal / remaining) if remaining > 0 else 0, loan_id))
            except:
                pass
            
            # ============ 6. 保险费用 ============
            insurance_cost = 0
            try:
                cursor.execute('''
                    SELECT monthly_premium FROM insurance_policies
                    WHERE session_id = ? AND is_active = 1
                ''', (session_id,))
                for (premium,) in cursor.fetchall():
                    insurance_cost += premium
                # 更新保险剩余月数
                cursor.execute('''
                    UPDATE insurance_policies SET remaining_months = remaining_months - 1
                    WHERE session_id = ? AND remaining_months > 0
                ''', (session_id,))
            except:
                pass
            
            # ============ 7. 居住成本 ============
            living_cost = 800  # 默认
            living_happiness_effect = 0
            try:
                cursor.execute('''
                    SELECT monthly_cost, happiness_effect FROM living_status WHERE session_id = ?
                ''', (session_id,))
                row = cursor.fetchone()
                if row:
                    living_cost = row[0]
                    living_happiness_effect = row[1] or 0
            except:
                pass
            
            # ============ 8. 基本生活开支 ============
            base_expense = 2000 + random.randint(0, 500)  # 食物、交通等
            
            # ============ 汇总现金流 ============
            total_income = monthly_salary + investment_income + matured_return + property_income + side_business_income
            total_expense = loan_payment + insurance_cost + living_cost + base_expense
            net_cashflow = total_income - total_expense
            
            new_cash = int(cash + net_cashflow)
            
            print(f"[GameService] Income: salary={monthly_salary}, invest={investment_income}, matured={matured_return}, property={property_income}, side={side_business_income}")
            print(f"[GameService] Expense: loan={loan_payment}, insurance={insurance_cost}, living={living_cost}, base={base_expense}")
            print(f"[GameService] Net: {net_cashflow}, New cash: {new_cash}")
            
            # ============ 9. 更新生活状态 ============
            # 每月自然恢复/消耗
            new_energy = min(100, max(0, energy + 5))  # 自然恢复
            new_health = max(0, health - 1)  # 轻微消耗
            new_happiness = max(0, min(100, happiness + living_happiness_effect))
            
            # 经济状况影响幸福度
            if new_cash < 10000:
                new_happiness = max(0, new_happiness - 5)
            elif new_cash > 500000:
                new_happiness = min(100, new_happiness + 2)
            
            # 更新用户状态
            if has_stats:
                cursor.execute('''
                    UPDATE users SET credits = ?, happiness = ?, energy = ?, health = ?
                    WHERE session_id = ?
                ''', (new_cash, new_happiness, new_energy, new_health, session_id))
            else:
                cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
            
            conn.commit()
            
        # 更新月份与快照
        new_month = self.db.advance_session_month(session_id)
        
        # 计算当前总投资
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(amount) FROM investments WHERE session_id = ? AND remaining_months > 0', (session_id,))
            current_invested = cursor.fetchone()[0] or 0
        
        total_assets = new_cash + current_invested
        
        # 保存月度现金流记录
        saving_rate = net_cashflow / total_income if total_income > 0 else 0
        self.db.save_monthly_cashflow(
            session_id, new_month, total_income, total_expense,
            net_cashflow, saving_rate, new_cash
        )
        
        # 保存月度快照
        self.db.save_monthly_snapshot(
            session_id=session_id,
            month=new_month,
            total_assets=total_assets,
            cash=new_cash,
            invested_assets=current_invested,
            happiness=new_happiness if has_stats else None,
        )
        
        # ============ 10. 事件系统 - 可能触发随机事件 ============
        from core.systems.event_system import event_system
        triggered_events = []
        try:
            events = event_system.get_random_events(
                session_id, new_month, total_assets, macro_stats.get('phase', 'expansion')
            )
            for event in events:
                triggered_events.append({
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "category": event.category.value,
                    "options": [
                        {"text": opt.text, "success_rate": opt.success_rate}
                        for opt in event.options
                    ]
                })
        except Exception as e:
            print(f"[GameService] Event generation failed: {e}")
        
        # ============ 11. 成就检查 ============
        from core.systems.achievement_system import achievement_system
        new_achievements = []
        try:
            unlocked = achievement_system.check_wealth_achievements(total_assets, new_month)
            for ach in unlocked:
                new_achievements.append(ach)
                self.db.save_achievement_unlock(session_id, {
                    "achievement_id": ach["achievement"]["id"],
                    "achievement_name": ach["achievement"]["name"],
                    "rarity": ach["achievement"]["rarity"],
                    "reward_coins": ach["rewards"]["coins"],
                    "reward_exp": ach["rewards"]["exp"],
                    "reward_title": ach["rewards"].get("title"),
                    "unlocked_month": new_month
                })
        except Exception as e:
            print(f"[GameService] Achievement check failed: {e}")
        
        # 生成新情境
        situation_payload = None
        try:
            if AI_AVAILABLE and self.ai_engine and self.ai_engine.api_key:
                if session_id in self.game_sessions and "avatar" in self.game_sessions[session_id]:
                    avatar = self.game_sessions[session_id]["avatar"]
                else:
                    from core.systems.mbti_traits import MBTIType
                    try:
                        mbti_enum = MBTIType(mbti)
                    except:
                        mbti_enum = MBTIType.INTJ
                        
                    avatar = AIAvatar(name, mbti_enum, session_id)
                    self.game_sessions[session_id] = {"avatar": avatar}
                
                # 同步最新状态给 Avatar 实例
                avatar.attributes.credits = new_cash
                avatar.attributes.current_month = new_month
                avatar.attributes.invested_assets = current_invested
                avatar.attributes.decision_count = new_month  # 用月份作为决策计数
                
                # 从数据库加载用户标签
                try:
                    with sqlite3.connect(self.db.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT tags FROM users WHERE session_id = ?', (session_id,))
                        row = cursor.fetchone()
                        if row and row[0]:
                            avatar.set_user_tags(row[0])
                            print(f"[GameService] 加载用户标签: {row[0]}")
                except Exception as e:
                    print(f"[GameService] 加载用户标签失败: {e}")
                
                # 加载职业状态
                try:
                    from core.systems.career_system import career_system
                    career_info = career_system.get_career_status(session_id)
                    avatar.set_career_status(career_info)
                except Exception as e:
                    print(f"[GameService] 加载职业状态失败: {e}")
                
                ctx = avatar.generate_situation(self.ai_engine)
                
                if ctx:
                    situation_payload = {
                        "situation": ctx.situation,
                        "options": ctx.options,
                        "ai_generated": True,
                    }
            
            if not situation_payload:
                phase_map = {
                    "expansion": "经济扩张",
                    "peak": "经济繁荣",
                    "contraction": "经济衰退",
                    "trough": "经济萧条"
                }
                phase_cn = phase_map.get(macro_stats.get('phase', 'expansion'), "经济波动")
                
                situation_payload = {
                    "situation": f"第{new_month}个月开始了。当前经济处于{phase_cn}阶段，通胀率{macro_stats.get('inflation', 2.5):.1f}%。本月收入¥{total_income:,}，支出¥{total_expense:,}，净现金流¥{net_cashflow:,}。",
                    "options": [
                        "继续当前策略，保持稳健发展",
                        "调整投资组合，寻求更高收益",
                        "提升生活品质，享受当下"
                    ],
                    "ai_generated": False,
                }
        except Exception as e:
            print(f"[advance_session] 生成情境失败: {e}")
            situation_payload = {
                "situation": f"新的一个月（第{new_month}月）开始了。",
                "options": ["保持现状", "调整策略", "积极投资"],
                "ai_generated": False,
            }
            
        # ============ 12. 行为洞察分析 ============
        behavior_profile = None
        behavior_achievements = []
        try:
            if self.behavior_system:
                # 每3个月更新一次行为画像
                if new_month % 3 == 0:
                    behavior_profile = self.behavior_system.analyze_profile(session_id, new_month)
                    print(f"[GameService] Behavior profile updated: {behavior_profile['risk_preference']} / {behavior_profile['decision_style']}")
                    
                    # 检查行为相关成就
                    if behavior_profile:
                        behavior_achievements = self.achievement_system.check_behavior_achievements(
                            behavior_profile, new_month
                        )
                        
                        # 检查资产多元化成就
                        portfolio = {
                            'stocks': session.portfolio.get('stocks', {}),
                            'deposits': session.portfolio.get('time_deposits', []),
                            'real_estate': session.portfolio.get('houses', []),
                            'insurance': session.portfolio.get('insurances', [])
                        }
                        diverse_ach = self.achievement_system.check_behavior_diversity(portfolio, new_month)
                        if diverse_ach:
                            behavior_achievements.append(diverse_ach)
                        
                        if behavior_achievements:
                            print(f"[GameService] Behavior achievements unlocked: {[a['name'] for a in behavior_achievements]}")
                
                # 每6个月生成一次群体洞察
                if new_month % 6 == 0:
                    cohort_insights = self.behavior_system.generate_cohort_insights(new_month)
                    print(f"[GameService] Generated {len(cohort_insights)} cohort insights")
        except Exception as e:
            print(f"[GameService] Behavior insight analysis failed: {e}")
        
        print(f"[GameService] advance_session completed. New month: {new_month}, Cash: {new_cash}, Total: {total_assets}")
        
        # 生成 AI 思考/反思
        reflection = self._generate_financial_reflection(
            new_month, new_cash, total_assets, total_income, total_expense, 
            net_cashflow, macro_stats, new_happiness if has_stats else 70
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "new_month": new_month,
            "cash": new_cash,
            "total_assets": total_assets,
            "invested_assets": current_invested,
            # 收入明细
            "income_breakdown": {
                "salary": monthly_salary,
                "investment": investment_income,
                "matured": matured_return,
                "property": property_income,
                "side_business": side_business_income,
                "total": total_income
            },
            # 支出明细
            "expense_breakdown": {
                "loan": loan_payment,
                "insurance": insurance_cost,
                "living": living_cost,
                "basic": base_expense,
                "total": total_expense
            },
            "net_cashflow": net_cashflow,
            # 生活状态
            "life_status": {
                "happiness": new_happiness if has_stats else 70,
                "energy": new_energy if has_stats else 75,
                "health": new_health if has_stats else 80
            },
            # 情境
            "situation": situation_payload["situation"],
            "options": situation_payload["options"],
            "ai_generated": situation_payload["ai_generated"],
            # AI 思考
            "reflection": reflection,
            # 宏观经济
            "macro_economy": macro_stats,
            # 触发的事件
            "events": triggered_events,
            # 解锁的成就（包括行为成就）
            "achievements": new_achievements + behavior_achievements
        }

    def _generate_financial_reflection(self, month: int, cash: int, total_assets: int, 
                                         income: int, expense: int, net_cashflow: int,
                                         macro_stats: dict, happiness: int) -> str:
        """生成 AI 财务思考/反思"""
        import random
        
        # 经济阶段描述
        phase_desc = {
            "expansion": "扩张期，市场机会增多",
            "peak": "繁荣期，需警惕泡沫风险",
            "contraction": "收缩期，宜保守投资",
            "trough": "萧条期，逢低布局的好时机"
        }
        phase = macro_stats.get('phase', 'expansion')
        phase_text = phase_desc.get(phase, "经济波动中")
        
        # 储蓄率分析
        saving_rate = net_cashflow / income * 100 if income > 0 else 0
        
        # 根据财务状况生成不同的思考
        reflections = []
        
        # 现金流分析
        if net_cashflow > 0:
            if saving_rate >= 30:
                reflections.append(f"本月储蓄率{saving_rate:.0f}%，财务纪律优秀！可以考虑增加投资比例。")
            elif saving_rate >= 10:
                reflections.append(f"本月储蓄率{saving_rate:.0f}%，维持正向现金流是好的开始。")
            else:
                reflections.append(f"本月勉强收支平衡，建议关注开支结构，提升储蓄率。")
        else:
            reflections.append(f"本月现金流为负（¥{net_cashflow:,}），需要警惕！考虑开源节流。")
        
        # 资产规模分析
        if total_assets >= 1000000:
            reflections.append("资产已突破百万大关，建议优化资产配置，分散风险。")
        elif total_assets >= 500000:
            reflections.append("资产稳步增长，距离财务自由更近一步。")
        elif total_assets >= 100000:
            reflections.append("原始积累进行中，保持耐心，复利需要时间。")
        elif total_assets >= 50000:
            reflections.append("资产起步阶段，建议先建立应急储备金。")
        else:
            reflections.append("资产较少，当务之急是增加收入来源。")
        
        # 宏观经济建议
        if phase == "expansion":
            reflections.append("经济扩张期，可适度增加风险资产配置。")
        elif phase == "peak":
            reflections.append("经济见顶迹象，建议逐步降低杠杆，锁定收益。")
        elif phase == "contraction":
            reflections.append("经济收缩期，现金为王，保持流动性。")
        elif phase == "trough":
            reflections.append("经济触底，优质资产打折中，可考虑逐步加仓。")
        
        # 生活状态提醒
        if happiness < 50:
            reflections.append("幸福感较低，财富不是唯一目标，适当关注生活品质。")
        elif happiness > 80:
            reflections.append("生活状态良好，身心平衡是长期财富增长的基础。")
        
        # 随机选择2-3条组合
        selected = random.sample(reflections, min(3, len(reflections)))
        return " ".join(selected)

    def finish_session(self, session_id: str) -> Dict[str, Any]:
        """简单的结局报告：基于净资产与波动给评分"""
        state = self.get_session_state(session_id)
        timeline = state.get("timeline", [])
        final_assets = state["total_assets"]
        # 简单评分规则
        if final_assets >= 1_000_000:
            grade = "S"
            comment = "你成功在金融沙盘中实现了财务自由，资产结构健康且风险可控。"
        elif final_assets >= 500_000:
            grade = "A"
            comment = "你的长期规划非常稳健，已经接近财务自由。"
        elif final_assets >= 200_000:
            grade = "B"
            comment = "你懂得利用复利和资产配置，财务状况良好。"
        elif final_assets > 0:
            grade = "C"
            comment = "你避免了破产，但资产增长有限，可以继续优化风险管理。"
        else:
            grade = "D"
            comment = "你在沙盘中经历了破产，这是非常宝贵的学习机会。"
        return {
            "session_id": session_id,
            "final_assets": final_assets,
            "grade": grade,
            "comment": comment,
            "timeline": timeline,
        }

    def get_city_snapshot(self, session_id: str) -> Dict[str, Any]:
        if not self.db:
            raise Exception("数据库未初始化")
        self.db.ensure_district_states(session_id)
        states = self.db.get_district_states(session_id)
        events = self.db.get_city_events(session_id, limit=12)
        return {
            "districts": states,
            "events": events,
        }

    def generate_district_event(self, session_id: str, district_id: str, context: Optional[str] = None) -> Dict[str, Any]:
        if not self.db:
            raise Exception("数据库未初始化")
        self.db.ensure_district_states(session_id)
        state = self.db.get_or_create_district_state(session_id, district_id)
        
        # 补充区域元数据
        district_meta = {
            'finance': {'name': '中央银行群', 'type': 'finance'},
            'tech': {'name': '量化交易所', 'type': 'tech'},
            'housing': {'name': '房产中枢', 'type': 'housing'},
            'learning': {'name': '知识引擎院', 'type': 'learning'},
            'leisure': {'name': '文娱漫游区', 'type': 'leisure'},
            'green': {'name': '绿色能源港', 'type': 'green'}
        }
        meta = district_meta.get(district_id, {'name': '未知区域', 'type': 'unknown'})
        state.update(meta)
        
        description = ""
        options = []
        
        # 尝试使用AI生成事件
        ai_success = False
        if AI_AVAILABLE and self.ai_engine and self.ai_engine.api_key:
            try:
                ai_context = {
                    "name": state["name"],
                    "type": state["type"],
                    "influence": state["influence"],
                    "heat": state["heat"],
                    "prosperity": state["prosperity"]
                }
                ai_result = self.ai_engine.generate_district_event(ai_context)
                if ai_result:
                    description = ai_result["description"]
                    options = ai_result["options"]
                    ai_success = True
            except Exception as e:
                print(f"[WARN] AI district event generation failed: {e}")
        
        # Fallback logic
        if not ai_success:
            influence = state["influence"]
            heat = state["heat"]
            prosperity = state["prosperity"]
            description = f"{state['name']} 检测到数据异常波动。影响力 {influence:.2f}、热度 {heat:.2f}、繁荣 {prosperity:.2f}。"
            options = [
                "投入资源稳固该区块",
                "观望市场情绪",
                "转移资金到其他区域"
            ]
            
        payload = {
            "district_id": district_id,
            "description": description,
            "options": options,
        }
        
        self.db.save_city_event(session_id, district_id, f"{state['name']} 事件", description)
        
        # 更新状态 (模拟波动)
        import random
        self.db.update_district_state(
            session_id,
            district_id,
            influence=min(1.0, max(0.0, state["influence"] + random.uniform(-0.05, 0.05))),
            heat=min(1.0, max(0.0, state["heat"] + random.uniform(-0.05, 0.05))),
            prosperity=min(1.0, max(0.0, state["prosperity"] + random.uniform(-0.05, 0.05))),
            events_completed=(state["events_completed"] or 0) + 1,
            last_event=description,
        )
        return payload

    async def ai_chat(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        context = {}
        if session_id:
            try:
                # 优先从内存获取丰富上下文
                if session_id in self.game_sessions:
                    session = self.game_sessions[session_id]
                    if "avatar_data" in session:
                        data = session["avatar_data"]
                        context.update({
                            "name": data.get("name"),
                            "mbti": data.get("mbti"),
                            "cash": data.get("credits"),
                            "total_assets": data.get("total_assets"),
                            "current_month": data.get("current_round", 0)
                        })
                    
                    if "current_situation" in session:
                        sit = session["current_situation"]
                        if isinstance(sit, dict):
                            context["current_situation"] = sit.get("situation") or sit.get("description")
                            context["options"] = sit.get("options") or sit.get("choices")
                        elif hasattr(sit, "situation"):
                            context["current_situation"] = sit.situation
                            context["options"] = getattr(sit, "options", None) or getattr(sit, "choices", None)

                # 如果内存信息不足，从数据库补充
                if (not context.get("name") or not context.get("current_situation")) and self.db:
                    import sqlite3
                    with sqlite3.connect(self.db.db_path) as conn:
                        cursor = conn.cursor()
                        
                        if not context.get("name"):
                            cursor.execute('SELECT name, mbti, credits FROM users WHERE session_id = ?', (session_id,))
                            row = cursor.fetchone()
                            if row:
                                context["name"] = row[0]
                                context["mbti"] = row[1]
                                context["cash"] = row[2]
                                # 估算总资产
                                cursor.execute('SELECT SUM(amount) FROM investments WHERE session_id = ? AND remaining_months > 0', (session_id,))
                                invested = cursor.fetchone()[0] or 0
                                context["total_assets"] = row[2] + invested
                                
                                cursor.execute('SELECT current_month FROM sessions WHERE session_id = ?', (session_id,))
                                srow = cursor.fetchone()
                                if srow:
                                    context["current_month"] = srow[0]

                        if not context.get("current_situation"):
                            # 获取最新事件
                            cursor.execute('SELECT description FROM city_events WHERE session_id = ? ORDER BY created_at DESC LIMIT 1', (session_id,))
                            evt = cursor.fetchone()
                            if evt:
                                context["current_situation"] = evt[0]
                                # 尝试从数据库获取选项 (如果存储了的话，目前 city_events 表结构似乎没有专门存 options，可能在 description 里或者没存)
                                # 这里暂时不从数据库恢复 options，因为 city_events 主要是日志

            
            except Exception as e:
                print(f"[AI Chat] Context build error: {e}")

        if self.ai_engine and self.ai_engine.api_key:
            try:
                return await self.ai_engine.chat(message, session_id=session_id, context=context)
            except Exception as e:
                print(f"[AI Chat] error: {e}")
        
        # Fallback
        return {
            "response": f"系统离线中... (收到: {message})",
            "reflection": "连接断开",
            "monologue": "..."
        }

    def get_macro_indicators(self) -> Dict[str, Any]:
        """获取宏观经济指标"""
        return {
            "gdp_growth": macro_economy.state.gdp_growth,
            "inflation": macro_economy.state.inflation,
            "interest_rate": macro_economy.state.interest_rate,
            "market_sentiment": macro_economy.state.market_sentiment,
            "phase": macro_economy.state.phase
        }

    def delete_character(self, session_id: str) -> bool:
        """删除角色"""
        if self.db:
            # 从内存中移除
            if session_id in self.game_sessions:
                del self.game_sessions[session_id]
            # 从数据库中移除
            return self.db.delete_user(session_id)
        return False
    
    def get_session_transactions(self, session_id: str, limit: int = 20) -> List[Dict]:
        """获取会话交易记录"""
        if not self.db:
            return []
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT round_num, transaction_name, amount, created_at, ai_thoughts
                FROM transactions 
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    'round': row[0],
                    'type': 'transaction',
                    'title': row[1],
                    'amount': row[2],
                    'timestamp': row[3],
                    'description': row[4] or ''
                })
            return transactions

    def process_decision(self, session_id: str, option_index: int, option_text: str) -> Dict[str, Any]:
        """处理用户的决策，解析文本并执行资金操作"""
        if not self.db:
            raise Exception("数据库未初始化")
            
        print(f"[GameService] Processing decision: {option_text}")
        
        import re
        import sqlite3
        
        # 1. 解析金额
        # 匹配 "投资50万", "50万元", "50000", "5万", "50w" 等
        amount = 0
        clean_text = option_text.replace(',', '')
        amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(万|w|W|k|K|亿|元|块)?', clean_text)
        
        if amount_match:
            num = float(amount_match.group(1))
            unit = amount_match.group(2)
            
            if unit in ['万', 'w', 'W']:
                amount = int(num * 10000)
            elif unit in ['亿']:
                amount = int(num * 100000000)
            elif unit in ['k', 'K']:
                amount = int(num * 1000)
            else:
                # 无单位或 "元"/"块"
                if num >= 1000:
                    amount = int(num)
                elif "万" in option_text:
                    # 补充检测：如果正则没匹配到单位但文本里有万（例如 "50 万" 中间有特殊字符）
                    amount = int(num * 10000)
                elif unit in ['元', '块']:
                    amount = int(num)
                # 如果数字很小且无单位，可能是序号，忽略
        
        # 2. 解析行为类型
        action_type = "none"
        
        # 明确的投资关键词 (优先级高)
        invest_keywords = ["股票", "基金", "房产", "债券", "期货", "股权", "理财", "定投", "投资", "买入", "持有", "建仓", "跟投", "投入", "支持项目", "众筹", "入股", "注资", "项目", "回报", "收益"]
        # 明确的存款关键词
        deposit_keywords = ["储蓄", "存入", "存款", "存钱"]
        # 明确的消费关键词
        spend_keywords = ["消费", "购买", "花费", "支付", "买", "租"]
        # 资金关键词（表示涉及金钱操作）
        money_keywords = ["CP", "元", "块钱", "资金", "费用", "成本"]
        
        if any(k in option_text for k in invest_keywords):
            action_type = "invest"
        elif any(k in option_text for k in deposit_keywords):
            action_type = "deposit"
        elif any(k in option_text for k in spend_keywords):
            action_type = "spend"
        elif amount > 0 and any(k in option_text for k in money_keywords):
            # 如果有金额且有资金关键词，默认当作投资/支出
            # 检查是否有正面词汇（投入、支持）暗示是投资
            if any(k in option_text for k in ["投入", "支持", "贡献", "赞助"]):
                action_type = "invest"
            else:
                action_type = "spend"
        
        print(f"[GameService] Parsed decision: type={action_type}, amount={amount}")
        
        # 3. 执行逻辑
        cash_change = 0
        ai_thoughts = f"执行操作：{option_text}"
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取当前现金
            cursor.execute('SELECT credits, username FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if not row:
                raise Exception("用户不存在")
            current_cash, username = row
            
            if action_type == "invest" and amount > 0:
                if current_cash >= amount:
                    cash_change = -amount
                    # 创建投资记录
                    # 尝试解析期限
                    duration = 12 # 默认12个月
                    if "短期" in option_text or "3个月" in option_text: duration = 3
                    elif "中期" in option_text or "6个月" in option_text: duration = 6
                    elif "2年" in option_text: duration = 24
                    elif "长期" in option_text: duration = 24
                    
                    # 尝试解析收益率
                    return_rate = 0.05 # 默认5%
                    if "高收益" in option_text or "股票" in option_text or "期货" in option_text: return_rate = 0.15
                    elif "稳健" in option_text or "债券" in option_text: return_rate = 0.04
                    elif "基金" in option_text: return_rate = 0.08
                    elif "房产" in option_text: return_rate = 0.03 # 房产主要是资产增值，收益率低一点
                    
                    # 提取投资名称
                    inv_name = "投资项目"
                    if "股票" in option_text: inv_name = "股票投资"
                    elif "基金" in option_text: inv_name = "基金理财"
                    elif "理财" in option_text: inv_name = "银行理财"
                    elif "创业" in option_text: inv_name = "创业投资"
                    elif "房产" in option_text: inv_name = "房产投资"
                    elif "债券" in option_text: inv_name = "债券投资"
                    
                    # 确定投资类型
                    inv_type = "中期"
                    if duration <= 3: inv_type = "短期"
                    elif duration >= 12: inv_type = "长期"
                    
                    cursor.execute('''
                        INSERT INTO investments (username, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (username, session_id, inv_name, amount, inv_type, duration, 0, return_rate, 1, ai_thoughts))
                    
                    ai_thoughts = f"已投入 {amount} 用于 {inv_name}。"
                else:
                    ai_thoughts = f"资金不足，无法投资 {amount}。"
                    
            elif action_type == "spend" and amount > 0:
                if current_cash >= amount:
                    cash_change = -amount
                    ai_thoughts = f"消费了 {amount}。"
                else:
                    ai_thoughts = f"资金不足，无法支付 {amount}。"
            
            elif action_type == "deposit" and amount > 0:
                 if current_cash >= amount:
                    cash_change = -amount
                    cursor.execute('''
                        INSERT INTO investments (username, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (username, session_id, "定期存款", amount, "短期", 12, 0, 0.03, 1, ai_thoughts))
                    ai_thoughts = f"存入 {amount} 定期存款。"
            
            # 更新现金
            if cash_change != 0:
                new_cash = current_cash + cash_change
                cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
                # 记录交易
                cursor.execute('''
                    INSERT INTO transactions (username, session_id, round_num, transaction_name, amount, ai_thoughts)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, session_id, 1, option_text[:20], cash_change, ai_thoughts))
                conn.commit()
                
        return {
            "success": True,
            "ai_thoughts": ai_thoughts,
            "decision_impact": {
                "cash_change": cash_change,
                "trust_change": 0
            }
        }
