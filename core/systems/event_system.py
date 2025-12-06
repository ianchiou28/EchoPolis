"""
事件系统 - EchoPolis
丰富的随机事件：宏观事件、个人事件、投资机会事件
"""
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum


class EventCategory(Enum):
    """事件类别"""
    MACRO = "宏观事件"
    PERSONAL = "个人事件"
    INVESTMENT = "投资机会"
    CAREER = "职业事件"
    SOCIAL = "社交事件"
    RANDOM = "随机事件"


class EventImpactType(Enum):
    """影响类型"""
    CASH = "现金"
    ASSET = "资产"
    INCOME = "收入"
    EXPENSE = "支出"
    HEALTH = "健康"
    HAPPINESS = "幸福"
    REPUTATION = "声誉"
    SKILL = "技能"


@dataclass
class EventImpact:
    """事件影响"""
    impact_type: EventImpactType
    value: int                      # 具体数值（可正可负）
    is_percentage: bool = False     # 是否百分比
    duration: int = 0               # 持续月数（0表示一次性）
    

@dataclass
class EventOption:
    """事件选项"""
    text: str
    impacts: List[EventImpact]
    success_rate: float = 1.0       # 成功概率
    fail_impacts: List[EventImpact] = field(default_factory=list)
    unlock_condition: Optional[str] = None
    

@dataclass
class GameEvent:
    """游戏事件"""
    id: str
    category: EventCategory
    title: str
    description: str
    options: List[EventOption]
    probability: float              # 发生概率
    min_month: int = 1              # 最早发生月份
    max_month: int = 999            # 最晚发生月份
    min_assets: int = 0             # 最低资产要求
    max_assets: int = 999999999     # 最高资产限制
    once_only: bool = False         # 是否只触发一次
    prerequisite_events: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


# ============ 宏观事件库 ============
MACRO_EVENTS = [
    GameEvent(
        id="MACRO_BULL_MARKET",
        category=EventCategory.MACRO,
        title="牛市来临 📈",
        description="市场情绪高涨，股票普涨！这波行情你怎么把握？",
        options=[
            EventOption("加仓追涨", [
                EventImpact(EventImpactType.ASSET, 15, is_percentage=True)
            ], success_rate=0.6, fail_impacts=[
                EventImpact(EventImpactType.ASSET, -10, is_percentage=True)
            ]),
            EventOption("逢高减仓", [
                EventImpact(EventImpactType.CASH, 10, is_percentage=True)
            ]),
            EventOption("保持观望", [])
        ],
        probability=0.03,
        tags=["market", "opportunity"]
    ),
    GameEvent(
        id="MACRO_BEAR_MARKET",
        category=EventCategory.MACRO,
        title="熊市降临 📉",
        description="市场恐慌蔓延，股价跳水！如何应对？",
        options=[
            EventOption("恐慌抛售", [
                EventImpact(EventImpactType.ASSET, -20, is_percentage=True)
            ]),
            EventOption("逢低加仓", [
                EventImpact(EventImpactType.ASSET, -10, is_percentage=True)
            ], success_rate=0.4, fail_impacts=[
                EventImpact(EventImpactType.ASSET, -25, is_percentage=True)
            ]),
            EventOption("持有不动", [
                EventImpact(EventImpactType.ASSET, -8, is_percentage=True)
            ])
        ],
        probability=0.03,
        tags=["market", "crisis"]
    ),
    GameEvent(
        id="MACRO_RATE_CUT",
        category=EventCategory.MACRO,
        title="央行降息 🏦",
        description="央行宣布降息25个基点，释放流动性。",
        options=[
            EventOption("增加股票配置", [
                EventImpact(EventImpactType.ASSET, 5, is_percentage=True)
            ]),
            EventOption("增加房产配置", []),
            EventOption("保持现状", [])
        ],
        probability=0.04,
        tags=["policy", "positive"]
    ),
    GameEvent(
        id="MACRO_RATE_HIKE",
        category=EventCategory.MACRO,
        title="央行加息 📊",
        description="为抑制通胀，央行宣布加息。存款利率上升，贷款成本增加。",
        options=[
            EventOption("增加存款", [
                EventImpact(EventImpactType.CASH, 2, is_percentage=True, duration=6)
            ]),
            EventOption("提前还贷", [
                EventImpact(EventImpactType.EXPENSE, -500, duration=12)
            ]),
            EventOption("保持现状", [])
        ],
        probability=0.04,
        tags=["policy"]
    ),
    GameEvent(
        id="MACRO_INFLATION",
        category=EventCategory.MACRO,
        title="通胀加剧 💸",
        description="物价持续上涨，购买力下降。",
        options=[
            EventOption("购买抗通胀资产", [
                EventImpact(EventImpactType.ASSET, 3, is_percentage=True)
            ]),
            EventOption("减少消费", [
                EventImpact(EventImpactType.HAPPINESS, -5),
                EventImpact(EventImpactType.EXPENSE, -1000)
            ]),
            EventOption("不做调整", [
                EventImpact(EventImpactType.CASH, -3, is_percentage=True)
            ])
        ],
        probability=0.05,
        tags=["economy", "negative"]
    ),
    GameEvent(
        id="MACRO_TECH_BOOM",
        category=EventCategory.MACRO,
        title="科技股暴涨 🚀",
        description="AI概念大热，科技股集体飙升！",
        options=[
            EventOption("重仓科技股", [
                EventImpact(EventImpactType.ASSET, 25, is_percentage=True)
            ], success_rate=0.5, fail_impacts=[
                EventImpact(EventImpactType.ASSET, -15, is_percentage=True)
            ]),
            EventOption("适度配置", [
                EventImpact(EventImpactType.ASSET, 8, is_percentage=True)
            ]),
            EventOption("不跟风", [])
        ],
        probability=0.02,
        tags=["sector", "opportunity"]
    ),
    GameEvent(
        id="MACRO_HOUSING_POLICY",
        category=EventCategory.MACRO,
        title="楼市新政 🏠",
        description="政府出台房地产刺激政策，购房门槛降低。",
        options=[
            EventOption("趁机购房", [
                EventImpact(EventImpactType.ASSET, 50000),
                EventImpact(EventImpactType.CASH, -100000),
                EventImpact(EventImpactType.EXPENSE, 3000, duration=360)
            ]),
            EventOption("观望等待", []),
            EventOption("投资REITs", [
                EventImpact(EventImpactType.ASSET, 5, is_percentage=True)
            ])
        ],
        probability=0.03,
        min_assets=50000,
        tags=["policy", "housing"]
    ),
]

# ============ 个人事件库 ============
PERSONAL_EVENTS = [
    GameEvent(
        id="PERSONAL_SICK",
        category=EventCategory.PERSONAL,
        title="生病住院 🏥",
        description="突发疾病需要住院治疗，医疗费用不菲。",
        options=[
            EventOption("住院治疗", [
                EventImpact(EventImpactType.CASH, -15000),
                EventImpact(EventImpactType.HEALTH, 20),
            ]),
            EventOption("门诊保守治疗", [
                EventImpact(EventImpactType.CASH, -3000),
                EventImpact(EventImpactType.HEALTH, 5),
            ]),
            EventOption("硬扛不治", [
                EventImpact(EventImpactType.HEALTH, -20),
                EventImpact(EventImpactType.HAPPINESS, -10),
            ])
        ],
        probability=0.04,
        tags=["health", "expense"]
    ),
    GameEvent(
        id="PERSONAL_MARRIAGE",
        category=EventCategory.PERSONAL,
        title="步入婚姻 💒",
        description="恭喜！你即将步入婚姻殿堂。婚礼怎么办？",
        options=[
            EventOption("豪华婚礼", [
                EventImpact(EventImpactType.CASH, -80000),
                EventImpact(EventImpactType.HAPPINESS, 30),
                EventImpact(EventImpactType.EXPENSE, 5000, duration=999)
            ]),
            EventOption("简约婚礼", [
                EventImpact(EventImpactType.CASH, -20000),
                EventImpact(EventImpactType.HAPPINESS, 20),
                EventImpact(EventImpactType.EXPENSE, 3000, duration=999)
            ]),
            EventOption("旅行结婚", [
                EventImpact(EventImpactType.CASH, -30000),
                EventImpact(EventImpactType.HAPPINESS, 25),
                EventImpact(EventImpactType.EXPENSE, 3000, duration=999)
            ])
        ],
        probability=0.02,
        min_month=24,
        once_only=True,
        tags=["life", "milestone"]
    ),
    GameEvent(
        id="PERSONAL_BABY",
        category=EventCategory.PERSONAL,
        title="喜得贵子 👶",
        description="恭喜升级为父母！养育孩子的开支也随之而来。",
        options=[
            EventOption("全力培养", [
                EventImpact(EventImpactType.HAPPINESS, 20),
                EventImpact(EventImpactType.EXPENSE, 8000, duration=216)  # 18年
            ]),
            EventOption("量力而行", [
                EventImpact(EventImpactType.HAPPINESS, 15),
                EventImpact(EventImpactType.EXPENSE, 4000, duration=216)
            ]),
        ],
        probability=0.015,
        min_month=36,
        prerequisite_events=["PERSONAL_MARRIAGE"],
        once_only=True,
        tags=["life", "milestone"]
    ),
    GameEvent(
        id="PERSONAL_PARENT_SICK",
        category=EventCategory.PERSONAL,
        title="父母生病 👨‍👩‍👧",
        description="父母生病需要照顾和医疗费用。",
        options=[
            EventOption("全力救治", [
                EventImpact(EventImpactType.CASH, -50000),
                EventImpact(EventImpactType.HAPPINESS, -5),
            ]),
            EventOption("医保+自费", [
                EventImpact(EventImpactType.CASH, -20000),
            ]),
            EventOption("保守治疗", [
                EventImpact(EventImpactType.CASH, -8000),
                EventImpact(EventImpactType.HAPPINESS, -15),
            ])
        ],
        probability=0.03,
        min_month=12,
        tags=["family", "expense"]
    ),
    GameEvent(
        id="PERSONAL_INHERITANCE",
        category=EventCategory.PERSONAL,
        title="获得遗产 📜",
        description="远方亲戚留下了一笔遗产给你。",
        options=[
            EventOption("接受遗产", [
                EventImpact(EventImpactType.CASH, 100000),
            ]),
            EventOption("捐给慈善", [
                EventImpact(EventImpactType.HAPPINESS, 20),
                EventImpact(EventImpactType.REPUTATION, 15),
            ])
        ],
        probability=0.01,
        once_only=True,
        tags=["windfall", "positive"]
    ),
    GameEvent(
        id="PERSONAL_CAR_ACCIDENT",
        category=EventCategory.PERSONAL,
        title="交通事故 🚗",
        description="发生了一起交通事故，需要处理。",
        options=[
            EventOption("走保险理赔", [
                EventImpact(EventImpactType.CASH, -2000),
            ]),
            EventOption("私了解决", [
                EventImpact(EventImpactType.CASH, -8000),
            ]),
            EventOption("法律途径", [
                EventImpact(EventImpactType.CASH, -5000),
                EventImpact(EventImpactType.HAPPINESS, -5),
            ])
        ],
        probability=0.02,
        tags=["accident", "expense"]
    ),
    GameEvent(
        id="PERSONAL_VACATION",
        category=EventCategory.PERSONAL,
        title="旅行机会 ✈️",
        description="朋友邀请你一起出国旅行，放松身心。",
        options=[
            EventOption("豪华游", [
                EventImpact(EventImpactType.CASH, -30000),
                EventImpact(EventImpactType.HAPPINESS, 25),
                EventImpact(EventImpactType.HEALTH, 10),
            ]),
            EventOption("经济游", [
                EventImpact(EventImpactType.CASH, -10000),
                EventImpact(EventImpactType.HAPPINESS, 15),
                EventImpact(EventImpactType.HEALTH, 5),
            ]),
            EventOption("婉拒邀请", [
                EventImpact(EventImpactType.HAPPINESS, -5),
            ])
        ],
        probability=0.05,
        tags=["leisure", "choice"]
    ),
    GameEvent(
        id="PERSONAL_SKILL_COURSE",
        category=EventCategory.PERSONAL,
        title="进修机会 📚",
        description="有一个提升专业技能的培训课程。",
        options=[
            EventOption("报名学习", [
                EventImpact(EventImpactType.CASH, -15000),
                EventImpact(EventImpactType.SKILL, 1),
                EventImpact(EventImpactType.INCOME, 2000, duration=999),
            ]),
            EventOption("自学替代", [
                EventImpact(EventImpactType.SKILL, 1),
            ], success_rate=0.4),
            EventOption("暂时不学", [])
        ],
        probability=0.04,
        tags=["career", "growth"]
    ),
]

# ============ 投资机会事件库 ============
INVESTMENT_EVENTS = [
    GameEvent(
        id="INVEST_IPO",
        category=EventCategory.INVESTMENT,
        title="新股申购 🎯",
        description="热门科技公司即将上市，你获得了打新机会！",
        options=[
            EventOption("全力申购", [
                EventImpact(EventImpactType.CASH, 30000)
            ], success_rate=0.3, fail_impacts=[
                EventImpact(EventImpactType.CASH, 0)
            ]),
            EventOption("小额尝试", [
                EventImpact(EventImpactType.CASH, 5000)
            ], success_rate=0.3),
            EventOption("放弃机会", [])
        ],
        probability=0.03,
        min_assets=10000,
        tags=["stock", "opportunity"]
    ),
    GameEvent(
        id="INVEST_PRIVATE_EQUITY",
        category=EventCategory.INVESTMENT,
        title="私募邀请 💼",
        description="朋友的创业公司需要融资，邀请你投资。",
        options=[
            EventOption("大额投资", [
                EventImpact(EventImpactType.CASH, -100000),
                EventImpact(EventImpactType.ASSET, 300000)
            ], success_rate=0.2, fail_impacts=[
                EventImpact(EventImpactType.CASH, -100000),
            ]),
            EventOption("小额支持", [
                EventImpact(EventImpactType.CASH, -20000),
                EventImpact(EventImpactType.ASSET, 60000)
            ], success_rate=0.2, fail_impacts=[
                EventImpact(EventImpactType.CASH, -20000),
            ]),
            EventOption("婉拒邀请", [
                EventImpact(EventImpactType.REPUTATION, -5)
            ])
        ],
        probability=0.02,
        min_assets=50000,
        tags=["venture", "high-risk"]
    ),
    GameEvent(
        id="INVEST_CRYPTO_SURGE",
        category=EventCategory.INVESTMENT,
        title="加密货币暴涨 ₿",
        description="比特币暴涨50%，朋友都在讨论。",
        options=[
            EventOption("跟风入场", [
                EventImpact(EventImpactType.ASSET, 40, is_percentage=True)
            ], success_rate=0.35, fail_impacts=[
                EventImpact(EventImpactType.ASSET, -30, is_percentage=True)
            ]),
            EventOption("小仓位试水", [
                EventImpact(EventImpactType.ASSET, 10, is_percentage=True)
            ], success_rate=0.35, fail_impacts=[
                EventImpact(EventImpactType.ASSET, -8, is_percentage=True)
            ]),
            EventOption("保持理性", [])
        ],
        probability=0.02,
        tags=["crypto", "high-risk"]
    ),
    GameEvent(
        id="INVEST_REAL_ESTATE",
        category=EventCategory.INVESTMENT,
        title="笋盘出现 🏠",
        description="发现一处低于市场价20%的房产，急售！",
        options=[
            EventOption("全款购买", [
                EventImpact(EventImpactType.CASH, -800000),
                EventImpact(EventImpactType.ASSET, 1000000),
            ]),
            EventOption("贷款购买", [
                EventImpact(EventImpactType.CASH, -200000),
                EventImpact(EventImpactType.ASSET, 1000000),
                EventImpact(EventImpactType.EXPENSE, 5000, duration=360)
            ]),
            EventOption("错过机会", [])
        ],
        probability=0.01,
        min_assets=200000,
        once_only=True,
        tags=["realestate", "opportunity"]
    ),
    GameEvent(
        id="INVEST_FUND_RECOMMEND",
        category=EventCategory.INVESTMENT,
        title="基金推荐 📊",
        description="理财经理推荐了一只近三年业绩优秀的基金。",
        options=[
            EventOption("大额买入", [
                EventImpact(EventImpactType.ASSET, 12, is_percentage=True)
            ], success_rate=0.6, fail_impacts=[
                EventImpact(EventImpactType.ASSET, -8, is_percentage=True)
            ]),
            EventOption("定投开始", [
                EventImpact(EventImpactType.ASSET, 5, is_percentage=True)
            ]),
            EventOption("谢绝推荐", [])
        ],
        probability=0.04,
        min_assets=5000,
        tags=["fund", "moderate"]
    ),
    GameEvent(
        id="INVEST_INSIDER_TIP",
        category=EventCategory.INVESTMENT,
        title="内幕消息 🤫",
        description="有人透露某股票即将有重大利好...",
        options=[
            EventOption("相信消息买入", [
                EventImpact(EventImpactType.ASSET, 50, is_percentage=True)
            ], success_rate=0.25, fail_impacts=[
                EventImpact(EventImpactType.ASSET, -40, is_percentage=True),
                EventImpact(EventImpactType.REPUTATION, -10)
            ]),
            EventOption("小仓位试探", [
                EventImpact(EventImpactType.ASSET, 15, is_percentage=True)
            ], success_rate=0.25, fail_impacts=[
                EventImpact(EventImpactType.ASSET, -12, is_percentage=True)
            ]),
            EventOption("拒绝内幕交易", [
                EventImpact(EventImpactType.REPUTATION, 5)
            ])
        ],
        probability=0.02,
        tags=["stock", "high-risk", "ethical"]
    ),
]

# ============ 职业事件库 ============
CAREER_EVENTS = [
    GameEvent(
        id="CAREER_PROMOTION",
        category=EventCategory.CAREER,
        title="晋升机会 🎉",
        description="老板暗示有晋升机会，但需要更多付出。",
        options=[
            EventOption("全力争取", [
                EventImpact(EventImpactType.INCOME, 5000, duration=999),
                EventImpact(EventImpactType.HAPPINESS, -10),
            ], success_rate=0.7, fail_impacts=[
                EventImpact(EventImpactType.HAPPINESS, -15),
            ]),
            EventOption("顺其自然", [
                EventImpact(EventImpactType.INCOME, 2000, duration=999),
            ], success_rate=0.4),
            EventOption("保持现状", [])
        ],
        probability=0.03,
        min_month=12,
        tags=["career", "growth"]
    ),
    GameEvent(
        id="CAREER_STARTUP",
        category=EventCategory.CAREER,
        title="创业邀请 🚀",
        description="朋友邀请你一起创业，需要投入资金和时间。",
        options=[
            EventOption("全职加入", [
                EventImpact(EventImpactType.CASH, -50000),
                EventImpact(EventImpactType.INCOME, -10000, duration=12),
            ], success_rate=0.3, fail_impacts=[
                EventImpact(EventImpactType.CASH, -50000),
                EventImpact(EventImpactType.HAPPINESS, -20),
            ]),
            EventOption("兼职参与", [
                EventImpact(EventImpactType.CASH, -20000),
                EventImpact(EventImpactType.HAPPINESS, -5),
            ], success_rate=0.3, fail_impacts=[
                EventImpact(EventImpactType.CASH, -20000),
            ]),
            EventOption("婉拒邀请", [])
        ],
        probability=0.02,
        min_assets=30000,
        tags=["career", "high-risk"]
    ),
    GameEvent(
        id="CAREER_HEADHUNTER",
        category=EventCategory.CAREER,
        title="猎头电话 📞",
        description="猎头带来了一个新机会，薪资涨幅30%。",
        options=[
            EventOption("接受offer", [
                EventImpact(EventImpactType.INCOME, 8000, duration=999),
                EventImpact(EventImpactType.REPUTATION, -5),
            ]),
            EventOption("谈判加薪", [
                EventImpact(EventImpactType.INCOME, 3000, duration=999),
            ], success_rate=0.5),
            EventOption("拒绝跳槽", [
                EventImpact(EventImpactType.REPUTATION, 5),
            ])
        ],
        probability=0.03,
        min_month=6,
        tags=["career", "opportunity"]
    ),
]


class EventSystem:
    """事件系统管理器"""
    
    def __init__(self):
        self.all_events = MACRO_EVENTS + PERSONAL_EVENTS + INVESTMENT_EVENTS + CAREER_EVENTS
        self.triggered_events: Dict[str, List[str]] = {}  # session_id -> triggered event ids
        self.active_effects: Dict[str, List[Dict]] = {}   # session_id -> active duration effects
    
    def get_random_events(self, session_id: str, current_month: int, 
                         total_assets: int, economic_phase: str = "expansion") -> List[GameEvent]:
        """获取本月可能触发的事件"""
        available_events = []
        triggered = self.triggered_events.get(session_id, [])
        
        for event in self.all_events:
            # 检查是否已触发过（一次性事件）
            if event.once_only and event.id in triggered:
                continue
            
            # 检查月份限制
            if current_month < event.min_month or current_month > event.max_month:
                continue
            
            # 检查资产限制
            if total_assets < event.min_assets or total_assets > event.max_assets:
                continue
            
            # 检查前置事件
            if event.prerequisite_events:
                if not all(e in triggered for e in event.prerequisite_events):
                    continue
            
            # 根据经济周期调整概率
            adjusted_prob = event.probability
            if "crisis" in event.tags and economic_phase in ["contraction", "trough"]:
                adjusted_prob *= 1.5
            elif "opportunity" in event.tags and economic_phase in ["expansion", "peak"]:
                adjusted_prob *= 1.3
            
            # 随机决定是否触发
            if random.random() < adjusted_prob:
                available_events.append(event)
        
        # 限制每月最多3个事件
        if len(available_events) > 3:
            available_events = random.sample(available_events, 3)
        
        return available_events
    
    def apply_event_choice(self, session_id: str, event: GameEvent, 
                          option_index: int, current_month: int) -> Dict:
        """应用事件选择的结果"""
        if option_index < 0 or option_index >= len(event.options):
            return {"success": False, "error": "无效选项"}
        
        option = event.options[option_index]
        
        # 判断成功/失败
        is_success = random.random() < option.success_rate
        impacts = option.impacts if is_success else option.fail_impacts
        
        # 记录触发
        if session_id not in self.triggered_events:
            self.triggered_events[session_id] = []
        self.triggered_events[session_id].append(event.id)
        
        # 处理影响
        result = {
            "success": is_success,
            "event_id": event.id,
            "event_title": event.title,
            "chosen_option": option.text,
            "impacts": []
        }
        
        for impact in impacts:
            impact_result = {
                "type": impact.impact_type.value,
                "value": impact.value,
                "is_percentage": impact.is_percentage,
                "duration": impact.duration
            }
            result["impacts"].append(impact_result)
            
            # 如果是持续效果，记录到活跃效果中
            if impact.duration > 0:
                if session_id not in self.active_effects:
                    self.active_effects[session_id] = []
                self.active_effects[session_id].append({
                    "type": impact.impact_type.value,
                    "value": impact.value,
                    "remaining_months": impact.duration,
                    "source": event.title
                })
        
        return result
    
    def get_active_effects(self, session_id: str) -> List[Dict]:
        """获取当前活跃的持续效果"""
        return self.active_effects.get(session_id, [])
    
    def update_active_effects(self, session_id: str) -> List[Dict]:
        """更新活跃效果（每月调用），返回本月生效的效果"""
        if session_id not in self.active_effects:
            return []
        
        active = []
        remaining = []
        
        for effect in self.active_effects[session_id]:
            if effect["remaining_months"] > 0:
                active.append(effect.copy())
                effect["remaining_months"] -= 1
                if effect["remaining_months"] > 0:
                    remaining.append(effect)
        
        self.active_effects[session_id] = remaining
        return active
    
    def get_event_by_id(self, event_id: str) -> Optional[GameEvent]:
        """根据ID获取事件"""
        for event in self.all_events:
            if event.id == event_id:
                return event
        return None
    
    def get_events_by_category(self, category: EventCategory) -> List[GameEvent]:
        """按类别获取事件"""
        return [e for e in self.all_events if e.category == category]
    
    def get_event_history(self, session_id: str) -> List[str]:
        """获取已触发事件历史"""
        return self.triggered_events.get(session_id, [])


# 全局实例
event_system = EventSystem()
