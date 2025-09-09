"""
Echopolis 游戏管理器
协调所有子系统的核心控制器
"""
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from datetime import datetime, timedelta
import uuid
import json

from ai_models.decision_engine.agent_brain import AgentBrain, AgentState, DecisionContext, PlayerIntervention, InterventionType
from backend.economic_system.currency_system import CentralBank, WealthManager, InsightCrystalShop
from backend.event_system.event_engine import EventEngine, EventCategory
from ai_models.personality.big_five_model import PersonalityAssessment, PersonalityTraits
from config import settings, GameConstants


class GameManager:
    """游戏核心管理器"""
    
    def __init__(self):
        # 初始化子系统
        self.central_bank = CentralBank()
        self.wealth_manager = WealthManager(self.central_bank)
        self.event_engine = EventEngine()
        self.ic_shop = InsightCrystalShop()
        self.personality_assessment = PersonalityAssessment()
        
        # 游戏状态
        self.active_agents = {}  # user_id -> AgentBrain
        self.game_sessions = {}  # user_id -> session_data
        self.assessment_sessions = {}  # session_id -> assessment_data
        
        # 时间系统
        self.game_time_multiplier = settings.GAME_TIME_MULTIPLIER
        self.paused_users = set()
        
        # 启动后台任务
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """启动后台任务"""
        # 这里应该启动定时任务，如经济周期更新、事件检查等
        pass
    
    # 用户管理
    async def create_user_session(self, user_id: str) -> Dict[str, Any]:
        """创建用户游戏会话"""
        if user_id not in self.game_sessions:
            # 创建财务账户
            account = self.wealth_manager.create_account(user_id)
            
            # 初始化游戏会话
            session = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "last_active": datetime.now(),
                "game_time_offset": 0,  # 游戏时间偏移
                "is_paused": False,
                "total_play_time": 0,
                "achievements": [],
                "milestones": []
            }
            
            self.game_sessions[user_id] = session
        
        return self.game_sessions[user_id]
    
    # 人格评估系统
    async def start_personality_assessment(self, user_id: str) -> Dict[str, Any]:
        """开始人格评估"""
        session_id = str(uuid.uuid4())
        
        # 获取评估问题
        personality_questions = self.personality_assessment.questions
        
        # 简化的FQ问题（实际应用中需要更完整的题库）
        fq_questions = [
            {
                "id": 1,
                "text": "什么是复利？",
                "options": [
                    {"text": "利息的利息", "score": 5},
                    {"text": "固定利率", "score": 1},
                    {"text": "银行费用", "score": 0}
                ]
            },
            {
                "id": 2,
                "text": "分散投资的主要目的是？",
                "options": [
                    {"text": "降低风险", "score": 5},
                    {"text": "增加收益", "score": 2},
                    {"text": "减少税收", "score": 1}
                ]
            }
        ]
        
        assessment_data = {
            "session_id": session_id,
            "user_id": user_id,
            "started_at": datetime.now(),
            "personality_questions": personality_questions,
            "fq_questions": fq_questions,
            "status": "in_progress"
        }
        
        self.assessment_sessions[session_id] = assessment_data
        
        return {
            "session_id": session_id,
            "questions": personality_questions,
            "fq_questions": fq_questions
        }
    
    async def create_agent_from_assessment(self, user_id: str, answers: List[int], 
                                         fq_answers: List[int]) -> Dict[str, Any]:
        """根据评估结果创建AI化身"""
        # 计算人格档案
        personality = self.personality_assessment.calculate_personality(answers)
        
        # 推导人格特质
        traits = PersonalityTraits.derive_traits(personality)
        
        # 计算FQ等级
        fq_score = sum(fq_answers) / len(fq_answers) if fq_answers else 1
        fq_level = min(5, max(1, int(fq_score)))
        
        # 创建AI化身
        agent = AgentBrain(personality, traits)
        agent.state.fq_level = fq_level
        
        # 根据FQ等级调整初始状态
        if fq_level >= 3:
            agent.state.monthly_income *= 1.2  # 金融知识好的人收入更高
            agent.state.credit_score += 50
        
        # 存储化身
        agent_id = str(uuid.uuid4())
        self.active_agents[user_id] = agent
        
        # 创建游戏会话
        await self.create_user_session(user_id)
        
        return {
            "agent_id": agent_id,
            "personality": personality.to_dict(),
            "traits": traits,
            "fq_level": fq_level,
            "initial_state": agent.state.to_dict()
        }
    
    # AI化身管理
    async def get_agent_status(self, user_id: str) -> Dict[str, Any]:
        """获取AI化身状态"""
        if user_id not in self.active_agents:
            raise ValueError("AI化身不存在")
        
        agent = self.active_agents[user_id]
        session = self.game_sessions.get(user_id, {})
        
        # 计算当前年龄和生命阶段
        current_age = self._calculate_current_age(user_id)
        life_stage = self._get_life_stage(current_age)
        
        return {
            "agent_id": user_id,
            "state": agent.state.to_dict(),
            "personality": agent.personality.to_dict(),
            "traits": agent.traits,
            "trust_level": agent.trust_level,
            "current_age": current_age,
            "life_stage": life_stage,
            "last_updated": datetime.now()
        }
    
    async def process_player_intervention(self, user_id: str, message: str, 
                                       intervention_type: str) -> Dict[str, Any]:
        """处理玩家干预"""
        if user_id not in self.active_agents:
            raise ValueError("AI化身不存在")
        
        agent = self.active_agents[user_id]
        
        # 检查干预点数
        session = self.game_sessions[user_id]
        current_ip = self._get_current_intervention_points(user_id)
        
        if current_ip <= 0:
            return {
                "success": False,
                "message": "干预点数不足",
                "remaining_points": 0
            }
        
        # 创建干预对象
        intervention = PlayerIntervention(
            intervention_type=InterventionType(intervention_type),
            message=message,
            timestamp=datetime.now()
        )
        
        # 生成一个简单的决策上下文用于测试
        context = self._generate_sample_decision_context()
        
        # 处理干预
        decision_result = agent.make_decision(context, intervention)
        
        # 扣除干预点数
        self._consume_intervention_points(user_id, 1)
        
        return {
            "success": True,
            "ai_response": decision_result["explanation"],
            "internal_monologue": decision_result["internal_monologue"],
            "trust_change": 0,  # 需要实现信任度变化计算
            "intervention_points_used": 1,
            "remaining_points": self._get_current_intervention_points(user_id)
        }
    
    async def get_decision_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """获取决策历史"""
        if user_id not in self.active_agents:
            return []
        
        agent = self.active_agents[user_id]
        history = agent.decision_history[-limit:] if agent.decision_history else []
        
        return [
            {
                "timestamp": record["timestamp"],
                "context": record["context"].__dict__ if hasattr(record["context"], "__dict__") else record["context"],
                "chosen_option": record["chosen_option"],
                "confidence": record.get("option_scores", [0])[0] if record.get("option_scores") else 0,
                "explanation": record["explanation"],
                "player_intervention": record["player_intervention"].message if record["player_intervention"] else None,
                "outcome": {}  # 需要实现结果跟踪
            }
            for record in history
        ]
    
    # 经济系统接口
    async def get_economic_indicators(self) -> Dict[str, Any]:
        """获取经济指标"""
        indicators = self.central_bank.indicators
        
        return {
            "indicators": indicators.to_dict(),
            "last_updated": datetime.now(),
            "trend_analysis": self._analyze_economic_trends()
        }
    
    async def get_market_data(self) -> Dict[str, Any]:
        """获取市场数据"""
        # 模拟市场数据
        market_data = {
            "stock_index": 3500.0,
            "stock_index_change": 0.012,
            "bond_yield": 0.035,
            "commodity_prices": {
                "gold": 1800.0,
                "oil": 75.0,
                "copper": 8500.0
            },
            "sector_performance": {
                "technology": 0.025,
                "finance": -0.008,
                "healthcare": 0.015,
                "energy": -0.020
            },
            "currency_rates": {
                "USD": 1.0,
                "EUR": 0.85,
                "JPY": 110.0
            }
        }
        
        return {
            "market_data": market_data,
            "last_updated": datetime.now(),
            "market_status": "open"
        }
    
    async def get_wallet_balance(self, user_id: str) -> Dict[str, Any]:
        """获取钱包余额"""
        summary = self.wealth_manager.get_financial_summary(user_id)
        
        balance = {
            "credit_points": summary.get("credit_points", 0),
            "insight_crystals": summary.get("insight_crystals", 0),
            "total_assets": summary.get("credit_points", 0),  # 简化版
            "liquid_assets": summary.get("credit_points", 0),
            "invested_assets": 0
        }
        
        monthly_summary = {
            "income": summary.get("monthly_income", 0),
            "expenses": summary.get("monthly_expenses", 0),
            "net": summary.get("net_monthly", 0)
        }
        
        return {
            "balance": balance,
            "monthly_summary": monthly_summary,
            "investment_portfolio": []  # 需要实现投资组合
        }
    
    async def get_transaction_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取交易历史"""
        transactions = self.wealth_manager.transaction_history.get(user_id, [])
        recent_transactions = transactions[-limit:] if transactions else []
        
        return [
            {
                "id": tx.id,
                "timestamp": tx.timestamp,
                "transaction_type": tx.transaction_type.value,
                "currency_type": tx.currency_type.value,
                "amount": tx.amount,
                "description": tx.description,
                "balance_after": tx.balance_after,
                "category": None  # 需要实现分类
            }
            for tx in recent_transactions
        ]
    
    # 事件系统接口
    async def get_current_events(self) -> List[Dict[str, Any]]:
        """获取当前事件"""
        recent_events = self.event_engine.get_recent_events(days=1)
        
        return [
            {
                "id": record["event"].id,
                "name": record["event"].name,
                "description": record["event"].description,
                "category": record["event"].category.value,
                "severity": record["event"].severity.value,
                "effects": [
                    {
                        "target": effect.target,
                        "attribute": effect.attribute,
                        "change_type": effect.change_type,
                        "value": effect.value,
                        "duration_days": effect.duration_days
                    }
                    for effect in record["event"].effects
                ],
                "news_headline": record["event"].news_headline,
                "news_content": record["event"].news_content,
                "timestamp": record["timestamp"],
                "affected_users": None
            }
            for record in recent_events
        ]
    
    async def get_event_history(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """获取事件历史"""
        return await self.get_current_events()  # 简化版
    
    # 新闻系统
    async def get_news_feed(self, limit: int = 20, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取新闻流"""
        # 基于最近事件生成新闻
        recent_events = self.event_engine.get_recent_events(days=7)
        news_items = []
        
        for i, record in enumerate(recent_events[:limit]):
            event = record["event"]
            news_item = {
                "id": f"news_{i}",
                "headline": event.news_headline or f"{event.name}",
                "content": event.news_content or event.description,
                "category": event.category.value,
                "timestamp": record["timestamp"],
                "importance": 3 if event.severity.value == "major" else 2,
                "related_events": [event.id],
                "market_impact": {}
            }
            news_items.append(news_item)
        
        return news_items
    
    # 社交系统
    async def get_agent_relationships(self, user_id: str) -> List[Dict[str, Any]]:
        """获取社交关系"""
        # 简化版 - 返回模拟数据
        return [
            {
                "agent_id": "friend_001",
                "agent_name": "李小明",
                "relationship_type": "friend",
                "relationship_strength": 75.0,
                "interaction_history": [],
                "mutual_investments": []
            }
        ]
    
    # 商店系统
    async def get_shop_catalog(self) -> List[Dict[str, Any]]:
        """获取商店目录"""
        catalog = []
        for item_id, item_data in self.ic_shop.catalog.items():
            catalog.append({
                "id": item_id,
                "name": item_data["name"],
                "description": item_data["description"],
                "price": item_data["price"],
                "category": "tool",
                "effect_description": item_data["description"],
                "availability": True,
                "purchase_limit": None
            })
        
        return catalog
    
    async def purchase_shop_item(self, user_id: str, item_id: str) -> Dict[str, Any]:
        """购买商店物品"""
        success, message = self.ic_shop.purchase_item(
            self.wealth_manager, user_id, item_id
        )
        
        new_balance = self.wealth_manager.get_balance(
            user_id, self.wealth_manager.CurrencyType.INSIGHT_CRYSTALS
        )
        
        return {
            "success": success,
            "message": message,
            "item": self.ic_shop.catalog.get(item_id) if success else None,
            "new_balance": int(new_balance)
        }
    
    # 游戏管理
    async def pause_game_time(self, user_id: str) -> bool:
        """暂停游戏时间"""
        self.paused_users.add(user_id)
        if user_id in self.game_sessions:
            self.game_sessions[user_id]["is_paused"] = True
        return True
    
    async def resume_game_time(self, user_id: str) -> bool:
        """恢复游戏时间"""
        self.paused_users.discard(user_id)
        if user_id in self.game_sessions:
            self.game_sessions[user_id]["is_paused"] = False
        return True
    
    async def get_game_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取游戏统计"""
        session = self.game_sessions.get(user_id, {})
        
        stats = {
            "total_play_time": session.get("total_play_time", 0),
            "decisions_made": len(self.active_agents[user_id].decision_history) if user_id in self.active_agents else 0,
            "interventions_sent": 0,  # 需要实现计数
            "events_experienced": 0,  # 需要实现计数
            "achievements_unlocked": session.get("achievements", []),
            "wealth_progression": [],  # 需要实现财富轨迹
            "personality_evolution": []  # 需要实现人格演化
        }
        
        return {
            "stats": stats,
            "current_session": session,
            "milestones": session.get("milestones", [])
        }
    
    # 辅助方法
    def _calculate_current_age(self, user_id: str) -> int:
        """计算当前年龄"""
        session = self.game_sessions.get(user_id, {})
        created_at = session.get("created_at", datetime.now())
        
        # 计算游戏内时间流逝
        real_time_elapsed = datetime.now() - created_at
        game_time_elapsed = real_time_elapsed * self.game_time_multiplier
        
        # 假设起始年龄为18岁
        start_age = 18
        years_passed = game_time_elapsed.days / 365
        
        return int(start_age + years_passed)
    
    def _get_life_stage(self, age: int) -> str:
        """获取生命阶段"""
        for stage, (min_age, max_age) in settings.LIFE_STAGES.items():
            if min_age <= age <= max_age:
                return stage
        return "unknown"
    
    def _get_current_intervention_points(self, user_id: str) -> int:
        """获取当前干预点数"""
        # 简化版 - 每日重置为最大值
        return settings.MAX_INTERVENTION_POINTS
    
    def _consume_intervention_points(self, user_id: str, points: int):
        """消耗干预点数"""
        # 简化版 - 暂不实现实际扣除
        pass
    
    def _generate_sample_decision_context(self) -> DecisionContext:
        """生成示例决策上下文"""
        from ..ai_agent.agent_brain import DecisionType
        
        return DecisionContext(
            decision_type=DecisionType.INVESTMENT,
            options=[
                {
                    "id": "option_1",
                    "description": "购买稳健的指数基金",
                    "expected_return": 0.08,
                    "risk_level": 0.3,
                    "keywords": ["基金", "稳健", "指数"]
                },
                {
                    "id": "option_2", 
                    "description": "投资高风险的科技股",
                    "expected_return": 0.15,
                    "risk_level": 0.8,
                    "keywords": ["股票", "科技", "高风险"]
                }
            ],
            market_conditions={"volatility": 0.15, "sentiment": 0.1},
            personal_goals=["财富增长", "风险控制"],
            time_pressure=0.3,
            social_influence=0.2
        )
    
    def _analyze_economic_trends(self) -> Dict[str, str]:
        """分析经济趋势"""
        indicators = self.central_bank.indicators
        
        trends = {}
        
        if indicators.gdp_growth_rate > 0.03:
            trends["gdp"] = "强劲增长"
        elif indicators.gdp_growth_rate > 0:
            trends["gdp"] = "温和增长"
        else:
            trends["gdp"] = "经济衰退"
        
        if indicators.inflation_rate > 0.04:
            trends["inflation"] = "通胀压力"
        elif indicators.inflation_rate > 0.02:
            trends["inflation"] = "温和通胀"
        else:
            trends["inflation"] = "通缩风险"
        
        return trends
    
    # 管理员功能
    async def trigger_specific_event(self, event_id: str, target_users: Optional[List[str]] = None):
        """触发特定事件"""
        event = self.event_engine.get_event_by_id(event_id)
        if not event:
            return
        
        # 构建游戏状态
        game_state = {
            "economic_indicators": self.central_bank.indicators,
            "market": {},  # 需要实现市场状态
            "agent_state": {}  # 需要实现化身状态
        }
        
        # 触发事件
        result = self.event_engine.trigger_event(event, game_state)
        
        # 通知受影响的用户（通过WebSocket等）
        if target_users:
            for user_id in target_users:
                # 发送事件通知
                pass