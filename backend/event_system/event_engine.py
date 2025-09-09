"""
Echopolis 事件系统
实现动态的宏观经济事件、个人事件和黑天鹅事件
"""
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import random
import math


class EventCategory(Enum):
    """事件类别"""
    MACRO = "macro"  # 宏观事件
    INDUSTRY = "industry"  # 行业事件
    PERSONAL = "personal"  # 个人事件
    BLACK_SWAN = "black_swan"  # 黑天鹅事件
    WHITE_SWAN = "white_swan"  # 白天鹅事件


class EventSeverity(Enum):
    """事件严重程度"""
    MINOR = "minor"  # 轻微
    MODERATE = "moderate"  # 中等
    MAJOR = "major"  # 重大
    CRITICAL = "critical"  # 危机级


@dataclass
class EventEffect:
    """事件效果"""
    target: str  # 影响目标 (economic_indicators, agent_state, market, etc.)
    attribute: str  # 具体属性
    change_type: str  # 变化类型 (absolute, percentage, multiplier)
    value: float  # 变化值
    duration_days: int = 0  # 持续天数，0表示永久


@dataclass
class GameEvent:
    """游戏事件"""
    id: str
    name: str
    description: str
    category: EventCategory
    severity: EventSeverity
    probability: float  # 发生概率 (0-1)
    effects: List[EventEffect]
    prerequisites: Dict[str, Any] = None  # 触发条件
    cooldown_days: int = 30  # 冷却期
    news_headline: str = ""  # 新闻标题
    news_content: str = ""  # 新闻内容
    
    def can_trigger(self, game_state: Dict[str, Any]) -> bool:
        """检查是否可以触发"""
        if not self.prerequisites:
            return True
        
        for condition, required_value in self.prerequisites.items():
            if condition not in game_state:
                return False
            
            current_value = game_state[condition]
            
            # 支持不同类型的条件检查
            if isinstance(required_value, dict):
                if "min" in required_value and current_value < required_value["min"]:
                    return False
                if "max" in required_value and current_value > required_value["max"]:
                    return False
            else:
                if current_value != required_value:
                    return False
        
        return True


class EventEngine:
    """事件引擎"""
    
    def __init__(self):
        self.events_catalog = self._initialize_events()
        self.active_events = []  # 当前活跃的事件
        self.event_history = []  # 事件历史
        self.last_trigger_times = {}  # 事件最后触发时间
        self.event_listeners = {}  # 事件监听器
    
    def _initialize_events(self) -> List[GameEvent]:
        """初始化事件目录"""
        events = []
        
        # 宏观经济事件
        events.extend(self._create_macro_events())
        
        # 行业事件
        events.extend(self._create_industry_events())
        
        # 个人事件
        events.extend(self._create_personal_events())
        
        # 黑天鹅/白天鹅事件
        events.extend(self._create_swan_events())
        
        return events
    
    def _create_macro_events(self) -> List[GameEvent]:
        """创建宏观经济事件"""
        return [
            GameEvent(
                id="interest_rate_hike",
                name="央行加息",
                description="中央银行宣布加息25个基点以控制通胀",
                category=EventCategory.MACRO,
                severity=EventSeverity.MODERATE,
                probability=0.15,
                effects=[
                    EventEffect("economic_indicators", "base_interest_rate", "absolute", 0.0025),
                    EventEffect("market", "stock_index", "percentage", -0.02),
                    EventEffect("market", "bond_yield", "absolute", 0.0025)
                ],
                prerequisites={"inflation_rate": {"min": 0.03}},
                news_headline="央行宣布加息25个基点",
                news_content="为应对持续上升的通胀压力，中央银行决定将基准利率上调25个基点。此举旨在稳定物价水平，但可能对股市造成短期冲击。"
            ),
            
            GameEvent(
                id="economic_stimulus",
                name="经济刺激计划",
                description="政府推出大规模经济刺激计划",
                category=EventCategory.MACRO,
                severity=EventSeverity.MAJOR,
                probability=0.08,
                effects=[
                    EventEffect("economic_indicators", "gdp_growth_rate", "absolute", 0.01),
                    EventEffect("economic_indicators", "market_sentiment", "absolute", 0.2),
                    EventEffect("market", "stock_index", "percentage", 0.05)
                ],
                prerequisites={"gdp_growth_rate": {"max": 0.01}},
                news_headline="政府推出千亿刺激计划",
                news_content="面对经济增长放缓，政府宣布推出总额达千亿的经济刺激计划，重点投资基础设施和新兴产业。"
            ),
            
            GameEvent(
                id="inflation_surge",
                name="通胀飙升",
                description="消费者价格指数大幅上涨",
                category=EventCategory.MACRO,
                severity=EventSeverity.MAJOR,
                probability=0.12,
                effects=[
                    EventEffect("economic_indicators", "inflation_rate", "absolute", 0.015),
                    EventEffect("economic_indicators", "consumer_price_index", "percentage", 0.03),
                    EventEffect("market", "commodity_prices", "percentage", 0.08)
                ],
                news_headline="CPI创十年新高",
                news_content="最新数据显示，消费者价格指数同比上涨创下十年来新高，食品和能源价格是主要推动因素。"
            )
        ]
    
    def _create_industry_events(self) -> List[GameEvent]:
        """创建行业事件"""
        return [
            GameEvent(
                id="ai_breakthrough",
                name="AI技术突破",
                description="人工智能领域取得重大技术突破",
                category=EventCategory.INDUSTRY,
                severity=EventSeverity.MODERATE,
                probability=0.20,
                effects=[
                    EventEffect("market", "tech_sector", "percentage", 0.15),
                    EventEffect("market", "ai_stocks", "percentage", 0.25)
                ],
                news_headline="AI芯片技术实现重大突破",
                news_content="硅芯谷某科技公司宣布在AI芯片技术方面取得重大突破，性能提升300%，相关概念股大涨。"
            ),
            
            GameEvent(
                id="real_estate_regulation",
                name="房地产调控",
                description="政府出台房地产市场调控政策",
                category=EventCategory.INDUSTRY,
                severity=EventSeverity.MAJOR,
                probability=0.18,
                effects=[
                    EventEffect("market", "real_estate_prices", "percentage", -0.10),
                    EventEffect("market", "real_estate_stocks", "percentage", -0.15),
                    EventEffect("economic_indicators", "market_sentiment", "absolute", -0.1)
                ],
                news_headline="政府出台房地产调控新政",
                news_content="为稳定房地产市场，政府出台新一轮调控政策，包括提高首付比例和限制投机性购房。"
            ),
            
            GameEvent(
                id="green_energy_boom",
                name="绿色能源热潮",
                description="新能源政策推动绿色能源板块大涨",
                category=EventCategory.INDUSTRY,
                severity=EventSeverity.MODERATE,
                probability=0.25,
                effects=[
                    EventEffect("market", "green_energy_stocks", "percentage", 0.20),
                    EventEffect("market", "traditional_energy_stocks", "percentage", -0.05)
                ],
                news_headline="新能源扶持政策出台",
                news_content="政府发布新能源产业扶持政策，承诺未来五年投资万亿发展清洁能源，相关股票应声上涨。"
            )
        ]
    
    def _create_personal_events(self) -> List[GameEvent]:
        """创建个人事件"""
        return [
            GameEvent(
                id="job_promotion",
                name="工作晋升",
                description="获得工作晋升机会",
                category=EventCategory.PERSONAL,
                severity=EventSeverity.MODERATE,
                probability=0.15,
                effects=[
                    EventEffect("agent_state", "monthly_income", "percentage", 0.25),
                    EventEffect("agent_state", "job_satisfaction", "absolute", 20),
                    EventEffect("agent_state", "happiness", "absolute", 15)
                ],
                prerequisites={"job_satisfaction": {"min": 60}, "experience_points": {"min": 100}}
            ),
            
            GameEvent(
                id="health_crisis",
                name="健康危机",
                description="突发健康问题需要医疗费用",
                category=EventCategory.PERSONAL,
                severity=EventSeverity.MAJOR,
                probability=0.08,
                effects=[
                    EventEffect("agent_state", "health", "absolute", -30),
                    EventEffect("agent_state", "credit_points", "absolute", -15000),
                    EventEffect("agent_state", "stress", "absolute", 25)
                ],
                prerequisites={"health": {"max": 70}, "stress": {"min": 60}}
            ),
            
            GameEvent(
                id="investment_windfall",
                name="投资意外收获",
                description="早期投资的公司成功上市",
                category=EventCategory.PERSONAL,
                severity=EventSeverity.MODERATE,
                probability=0.05,
                effects=[
                    EventEffect("agent_state", "credit_points", "absolute", 50000),
                    EventEffect("agent_state", "happiness", "absolute", 25),
                    EventEffect("agent_state", "insight_crystals", "absolute", 5)
                ],
                prerequisites={"investment_portfolio": {"min": 10000}}
            ),
            
            GameEvent(
                id="family_emergency",
                name="家庭紧急情况",
                description="家人需要经济支持",
                category=EventCategory.PERSONAL,
                severity=EventSeverity.MODERATE,
                probability=0.12,
                effects=[
                    EventEffect("agent_state", "credit_points", "absolute", -8000),
                    EventEffect("agent_state", "stress", "absolute", 15),
                    EventEffect("agent_state", "happiness", "absolute", -10)
                ]
            ),
            
            GameEvent(
                id="skill_certification",
                name="技能认证",
                description="获得专业技能认证",
                category=EventCategory.PERSONAL,
                severity=EventSeverity.MINOR,
                probability=0.20,
                effects=[
                    EventEffect("agent_state", "fq_level", "absolute", 0.5),
                    EventEffect("agent_state", "experience_points", "absolute", 50),
                    EventEffect("agent_state", "job_satisfaction", "absolute", 10)
                ],
                prerequisites={"fq_level": {"max": 4}}
            )
        ]
    
    def _create_swan_events(self) -> List[GameEvent]:
        """创建黑天鹅/白天鹅事件"""
        return [
            GameEvent(
                id="financial_crisis",
                name="金融危机",
                description="全球性金融危机爆发",
                category=EventCategory.BLACK_SWAN,
                severity=EventSeverity.CRITICAL,
                probability=0.02,
                effects=[
                    EventEffect("market", "stock_index", "percentage", -0.30),
                    EventEffect("economic_indicators", "gdp_growth_rate", "absolute", -0.05),
                    EventEffect("economic_indicators", "unemployment_rate", "absolute", 0.03),
                    EventEffect("economic_indicators", "market_sentiment", "absolute", -0.8)
                ],
                cooldown_days=365,
                news_headline="全球金融危机爆发",
                news_content="由于多重因素叠加，全球金融市场出现剧烈震荡，多国股市暴跌，经济衰退风险急剧上升。"
            ),
            
            GameEvent(
                id="technological_singularity",
                name="技术奇点",
                description="革命性技术突破改变世界",
                category=EventCategory.WHITE_SWAN,
                severity=EventSeverity.CRITICAL,
                probability=0.01,
                effects=[
                    EventEffect("market", "tech_sector", "percentage", 0.50),
                    EventEffect("economic_indicators", "gdp_growth_rate", "absolute", 0.08),
                    EventEffect("economic_indicators", "market_sentiment", "absolute", 0.9)
                ],
                cooldown_days=1000,
                news_headline="技术奇点到来",
                news_content="科学家宣布在量子计算和人工智能融合方面取得突破性进展，预计将彻底改变人类社会的运作方式。"
            ),
            
            GameEvent(
                id="pandemic_outbreak",
                name="疫情爆发",
                description="全球性疫情影响经济活动",
                category=EventCategory.BLACK_SWAN,
                severity=EventSeverity.CRITICAL,
                probability=0.03,
                effects=[
                    EventEffect("economic_indicators", "gdp_growth_rate", "absolute", -0.08),
                    EventEffect("market", "travel_stocks", "percentage", -0.40),
                    EventEffect("market", "healthcare_stocks", "percentage", 0.20),
                    EventEffect("agent_state", "health", "absolute", -10, 90)
                ],
                cooldown_days=730,
                news_headline="全球疫情爆发",
                news_content="新型传染病在全球范围内快速传播，各国政府采取封锁措施，经济活动受到严重冲击。"
            )
        ]
    
    def register_event_listener(self, event_id: str, callback: Callable):
        """注册事件监听器"""
        if event_id not in self.event_listeners:
            self.event_listeners[event_id] = []
        self.event_listeners[event_id].append(callback)
    
    def trigger_event(self, event: GameEvent, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """触发事件"""
        if not event.can_trigger(game_state):
            return {"success": False, "reason": "不满足触发条件"}
        
        # 检查冷却期
        if event.id in self.last_trigger_times:
            last_trigger = self.last_trigger_times[event.id]
            cooldown_end = last_trigger + timedelta(days=event.cooldown_days)
            if datetime.now() < cooldown_end:
                return {"success": False, "reason": "仍在冷却期"}
        
        # 应用事件效果
        effects_applied = []
        for effect in event.effects:
            effect_result = self._apply_effect(effect, game_state)
            effects_applied.append(effect_result)
        
        # 记录事件
        event_record = {
            "event": event,
            "timestamp": datetime.now(),
            "effects_applied": effects_applied,
            "game_state_snapshot": game_state.copy()
        }
        
        self.event_history.append(event_record)
        self.last_trigger_times[event.id] = datetime.now()
        
        # 通知监听器
        if event.id in self.event_listeners:
            for callback in self.event_listeners[event.id]:
                try:
                    callback(event, game_state)
                except Exception as e:
                    print(f"事件监听器错误: {e}")
        
        return {
            "success": True,
            "event": event,
            "effects": effects_applied,
            "news": {
                "headline": event.news_headline,
                "content": event.news_content
            }
        }
    
    def _apply_effect(self, effect: EventEffect, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """应用单个效果"""
        target_obj = game_state.get(effect.target)
        if not target_obj:
            return {"success": False, "reason": f"目标对象 {effect.target} 不存在"}
        
        if not hasattr(target_obj, effect.attribute):
            return {"success": False, "reason": f"属性 {effect.attribute} 不存在"}
        
        old_value = getattr(target_obj, effect.attribute)
        
        if effect.change_type == "absolute":
            new_value = old_value + effect.value
        elif effect.change_type == "percentage":
            new_value = old_value * (1 + effect.value)
        elif effect.change_type == "multiplier":
            new_value = old_value * effect.value
        else:
            return {"success": False, "reason": f"未知的变化类型: {effect.change_type}"}
        
        setattr(target_obj, effect.attribute, new_value)
        
        return {
            "success": True,
            "target": effect.target,
            "attribute": effect.attribute,
            "old_value": old_value,
            "new_value": new_value,
            "change": new_value - old_value
        }
    
    def check_random_events(self, game_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查随机事件触发"""
        triggered_events = []
        
        for event in self.events_catalog:
            # 跳过冷却期内的事件
            if event.id in self.last_trigger_times:
                last_trigger = self.last_trigger_times[event.id]
                cooldown_end = last_trigger + timedelta(days=event.cooldown_days)
                if datetime.now() < cooldown_end:
                    continue
            
            # 检查触发条件
            if not event.can_trigger(game_state):
                continue
            
            # 随机触发检查
            if random.random() < event.probability:
                result = self.trigger_event(event, game_state)
                if result["success"]:
                    triggered_events.append(result)
        
        return triggered_events
    
    def get_event_by_id(self, event_id: str) -> Optional[GameEvent]:
        """根据ID获取事件"""
        for event in self.events_catalog:
            if event.id == event_id:
                return event
        return None
    
    def get_events_by_category(self, category: EventCategory) -> List[GameEvent]:
        """根据类别获取事件"""
        return [event for event in self.events_catalog if event.category == category]
    
    def get_recent_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取最近的事件"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [record for record in self.event_history 
                if record["timestamp"] >= cutoff_date]