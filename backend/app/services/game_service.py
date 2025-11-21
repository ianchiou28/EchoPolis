"""
游戏服务层 - 业务逻辑处理
"""
import random
from typing import Dict, Any, Optional

# 尝试导入核心游戏系统
try:
    from core.avatar.ai_avatar import AIAvatar
    from core.systems.mbti_traits import MBTITraits
    from core.systems.fate_wheel import FateWheel
    from core.systems.echo_system import EchoSystem
    from core.systems.asset_calculator import asset_calculator
    from core.systems.investment_system import investment_system
    from core.systems.macro_economy import macro_economy
    from core.ai.deepseek_engine import DeepSeekEngine
    AI_AVAILABLE = True
except ImportError as e:
    print(f"AI modules not available: {e}")
    AI_AVAILABLE = False

class GameService:
    def __init__(self):
        self.game_sessions = {}
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
            # 当前投资
            cursor.execute('''
                SELECT SUM(amount) FROM investments
                WHERE session_id = ? AND remaining_months > 0
            ''', (session_id,))
            invested = cursor.fetchone()[0] or 0
            total_assets = credits + invested
        timeline = self.db.get_session_timeline(session_id, limit=36)
        return {
            "session_id": session_id,
            "name": name,
            "mbti": mbti,
            "username": username,
            "current_month": current_month,
            "cash": credits,
            "invested_assets": invested,
            "total_assets": total_assets,
            "timeline": timeline,
        }

    def advance_session(self, session_id: str, echo_text: Optional[str] = None) -> Dict[str, Any]:
        """推进一个月份：发放月收益、递减投资、生成新情境"""
        if not self.db:
            raise Exception("数据库未初始化")
            
        # 推进宏观经济
        macro_stats = macro_economy.advance_month()
        asset_impact = macro_economy.get_asset_impact()
        
        import sqlite3
        # 加载基本状态
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, mbti, credits, username FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if not row:
                raise Exception("会话不存在")
            name, mbti, cash, username = row
            
            # 计算月度基础收益（受宏观经济影响）
            cursor.execute('SELECT SUM(amount) FROM investments WHERE session_id = ? AND remaining_months > 0', (session_id,))
            invested = cursor.fetchone()[0] or 0
            
            # 现金贬值
            real_cash_value = cash * asset_impact["cash"]
            inflation_loss = cash - real_cash_value
            
            # 投资收益计算
            cursor.execute('''
                SELECT id, name, amount, return_rate, monthly_return, investment_type
                FROM investments 
                WHERE session_id = ? AND remaining_months > 0
            ''', (session_id,))
            
            monthly_income = 0
            for inv in cursor.fetchall():
                inv_type = inv[5] # investment_type
                base_return = inv[4] # monthly_return
                
                # 根据资产类型应用宏观影响
                impact_factor = 1.0
                if "股票" in inv_type or "基金" in inv_type:
                    impact_factor = asset_impact["stock"]
                elif "房产" in inv_type:
                    impact_factor = asset_impact["real_estate"]
                elif "债券" in inv_type:
                    impact_factor = asset_impact["bond"]
                
                # 实际收益 = 基础收益 * 宏观影响
                actual_return = int(base_return * impact_factor)
                monthly_income += actual_return

            # 更新投资剩余月数
            cursor.execute('''
                UPDATE investments
                SET remaining_months = remaining_months - 1
                WHERE session_id = ? AND remaining_months > 0
            ''', (session_id,))
            
            # 处理到期投资
            cursor.execute('''
                SELECT id, name, amount, return_rate, monthly_return, remaining_months, investment_type
                FROM investments
                WHERE session_id = ?
            ''', (session_id,))
            
            matured_return = 0
            for iid, iname, amount, return_rate, monthly_ret, remaining, inv_type in cursor.fetchall():
                if remaining <= 0:
                    # 到期本金回收也受宏观影响（例如股市崩盘）
                    impact_factor = 1.0
                    if "股票" in inv_type:
                        impact_factor = asset_impact["stock"]
                    
                    final_amount = int(amount * impact_factor)
                    
                    if monthly_ret and monthly_ret > 0:
                        matured_return += final_amount
                    else:
                        # 一次性收益型
                        total_ret = int(final_amount * (1 + (return_rate or 0)))
                        matured_return += total_ret
                        
                    cursor.execute('DELETE FROM investments WHERE id = ?', (iid,))
            
            # 加入收益
            new_cash = int(cash + monthly_income + matured_return)
            cursor.execute('UPDATE users SET credits = ? WHERE session_id = ?', (new_cash, session_id))
            conn.commit()
            
        # 更新月份与快照
        new_month = self.db.advance_session_month(session_id)
        total_assets = new_cash + invested  # 投资在上面已经更新/可能减少
        self.db.save_monthly_snapshot(
            session_id=session_id,
            month=new_month,
            total_assets=total_assets,
            cash=new_cash,
            invested_assets=invested,
        )
        
        # 生成新情境（复用现有 generate_situation 逻辑）
        situation_payload = None
        try:
            situation_payload = None
            # 尝试沿用 generate_situation 作为高阶情境器
            situation = None
            if AI_AVAILABLE and self.ai_engine and self.ai_engine.api_key:
                # 构造一个最小上下文，让 AIAvatar 生成故事
                if session_id in self.game_sessions and "avatar" in self.game_sessions[session_id]:
                    avatar = self.game_sessions[session_id]["avatar"]
                else:
                    from core.systems.mbti_traits import MBTIType
                    # 尝试转换 MBTI 字符串为枚举
                    try:
                        mbti_enum = MBTIType(mbti)
                    except:
                        mbti_enum = MBTIType.INTJ
                        
                    avatar = AIAvatar(name, mbti_enum, session_id)
                    self.game_sessions[session_id] = {"avatar": avatar}
                
                # 同步最新状态给 Avatar 实例，确保 AI 知道当前财务状况
                avatar.attributes.credits = new_cash
                avatar.attributes.current_month = new_month
                avatar.attributes.invested_assets = invested
                
                # 将宏观经济数据注入上下文
                macro_context = f"当前宏观经济：GDP增长{macro_stats['gdp_growth']}%, 通胀{macro_stats['inflation']}%, 市场情绪{macro_stats['market_sentiment']}({macro_stats['phase']})"
                
                # 这里需要修改 AIAvatar.generate_situation 接口来接受额外上下文，或者临时修改属性
                # 暂时通过 prompt injection 的方式（如果 DeepSeekEngine 支持）
                # 假设 generate_situation 内部会调用 engine
                
                ctx = avatar.generate_situation(self.ai_engine)
                if ctx:
                    situation_payload = {
                        "situation": f"[{macro_stats['phase'].upper()}] {ctx.situation}",
                        "options": ctx.options,
                        "ai_generated": True,
                    }
            if not situation_payload:
                # Fallback：简单情境
                situation_payload = {
                    "situation": f"新的一个月开始了。当前经济处于{macro_stats['phase']}阶段，通胀率{macro_stats['inflation']}%。",
                    "options": [
                        "继续当前策略，保持观望",
                        "调整投资组合，增加稳健资产",
                        "兑现部分收益，提升生活质量",
                    ],
                    "ai_generated": False,
                }
        except Exception as e:
            print(f"[advance_session] 生成情境失败: {e}")
            situation_payload = {
                "situation": "系统暂时无法生成详细情境，但时间仍然在推进。",
                "options": ["保持现状", "略微增加投资", "增加储蓄"],
                "ai_generated": False,
            }
            
        return {
            "session_id": session_id,
            "new_month": new_month,
            "cash": new_cash,
            "total_assets": total_assets,
            "monthly_income": monthly_income,
            "matured_return": matured_return,
            "situation": situation_payload["situation"],
            "options": situation_payload["options"],
            "ai_generated": situation_payload["ai_generated"],
            "macro_economy": macro_stats
        }

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
        if self.ai_engine and self.ai_engine.api_key:
            try:
                return await self.ai_engine.chat(message, session_id=session_id)
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
