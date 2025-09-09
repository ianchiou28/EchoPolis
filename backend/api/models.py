"""
API 数据模型定义
使用 Pydantic 进行数据验证和序列化
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


# 基础枚举类型
class InterventionTypeEnum(str, Enum):
    INSPIRATIONAL = "inspirational"
    ADVISORY = "advisory"
    DIRECTIVE = "directive"
    EMOTIONAL = "emotional"


class EventCategoryEnum(str, Enum):
    MACRO = "macro"
    INDUSTRY = "industry"
    PERSONAL = "personal"
    BLACK_SWAN = "black_swan"
    WHITE_SWAN = "white_swan"


class CurrencyTypeEnum(str, Enum):
    CREDIT_POINTS = "CP"
    INSIGHT_CRYSTALS = "IC"


# 用户认证相关
class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    is_active: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# 人格评估相关
class AssessmentQuestion(BaseModel):
    id: int
    text: str
    options: List[Dict[str, Any]]


class AssessmentResponse(BaseModel):
    questions: List[AssessmentQuestion]
    fq_questions: List[AssessmentQuestion]
    session_id: str


class AssessmentSubmission(BaseModel):
    session_id: str
    answers: List[int]
    fq_answers: List[int]


class PersonalityProfile(BaseModel):
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float


class AgentCreationResponse(BaseModel):
    agent_id: str
    personality: PersonalityProfile
    traits: List[str]
    fq_level: int
    initial_state: Dict[str, Any]


# AI化身状态相关
class AgentState(BaseModel):
    health: float
    energy: float
    credit_score: int
    happiness: float
    stress: float
    credit_points: float
    insight_crystals: int
    net_worth: float
    monthly_income: float
    monthly_expenses: float
    relationship_status: str
    social_connections: int
    job_title: str
    job_satisfaction: float
    fq_level: int
    experience_points: int


class AgentStatusResponse(BaseModel):
    agent_id: str
    state: AgentState
    personality: PersonalityProfile
    traits: List[str]
    trust_level: float
    current_age: int
    life_stage: str
    last_updated: datetime


# 干预系统相关
class InterventionRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    intervention_type: InterventionTypeEnum


class InterventionResponse(BaseModel):
    success: bool
    ai_response: str
    internal_monologue: str
    trust_change: float
    intervention_points_used: int
    remaining_points: int


class DecisionOption(BaseModel):
    id: str
    description: str
    expected_outcome: str
    risk_level: float
    keywords: List[str]


class DecisionContext(BaseModel):
    decision_type: str
    options: List[DecisionOption]
    time_pressure: float
    social_influence: float


class DecisionRecord(BaseModel):
    timestamp: datetime
    context: DecisionContext
    chosen_option: DecisionOption
    confidence: float
    explanation: str
    player_intervention: Optional[str]
    outcome: Optional[Dict[str, Any]]


# 经济系统相关
class EconomicIndicators(BaseModel):
    base_interest_rate: float
    inflation_rate: float
    unemployment_rate: float
    gdp_growth_rate: float
    consumer_price_index: float
    market_sentiment: float


class EconomicIndicatorsResponse(BaseModel):
    indicators: EconomicIndicators
    last_updated: datetime
    trend_analysis: Dict[str, str]


class MarketData(BaseModel):
    stock_index: float
    stock_index_change: float
    bond_yield: float
    commodity_prices: Dict[str, float]
    sector_performance: Dict[str, float]
    currency_rates: Dict[str, float]


class MarketDataResponse(BaseModel):
    market_data: MarketData
    last_updated: datetime
    market_status: str  # "open", "closed", "pre_market", "after_hours"


# 钱包和交易相关
class WalletBalance(BaseModel):
    credit_points: float
    insight_crystals: int
    total_assets: float
    liquid_assets: float
    invested_assets: float


class WalletResponse(BaseModel):
    balance: WalletBalance
    monthly_summary: Dict[str, float]
    investment_portfolio: List[Dict[str, Any]]


class TransactionRecord(BaseModel):
    id: str
    timestamp: datetime
    transaction_type: str
    currency_type: CurrencyTypeEnum
    amount: float
    description: str
    balance_after: float
    category: Optional[str]


# 事件系统相关
class EventEffect(BaseModel):
    target: str
    attribute: str
    change_type: str
    value: float
    duration_days: int


class EventResponse(BaseModel):
    id: str
    name: str
    description: str
    category: EventCategoryEnum
    severity: str
    effects: List[EventEffect]
    news_headline: str
    news_content: str
    timestamp: datetime
    affected_users: Optional[List[str]]


class EventTriggerRequest(BaseModel):
    event_id: str
    target_users: Optional[List[str]] = None


# 新闻系统相关
class NewsItem(BaseModel):
    id: str
    headline: str
    content: str
    category: str
    timestamp: datetime
    importance: int  # 1-5, 5最重要
    related_events: List[str]
    market_impact: Optional[Dict[str, float]]


# 社交系统相关
class RelationshipInfo(BaseModel):
    agent_id: str
    agent_name: str
    relationship_type: str  # "friend", "colleague", "spouse", "business_partner"
    relationship_strength: float  # 0-100
    interaction_history: List[Dict[str, Any]]
    mutual_investments: List[str]


# 商店系统相关
class ShopItem(BaseModel):
    id: str
    name: str
    description: str
    price: int  # IC价格
    category: str
    effect_description: str
    availability: bool
    purchase_limit: Optional[int]


class PurchaseRequest(BaseModel):
    item_id: str
    quantity: int = 1


class PurchaseResponse(BaseModel):
    success: bool
    message: str
    item: Optional[ShopItem]
    new_balance: int  # 剩余IC


# 游戏统计相关
class GameStats(BaseModel):
    total_play_time: int  # 分钟
    decisions_made: int
    interventions_sent: int
    events_experienced: int
    achievements_unlocked: List[str]
    wealth_progression: List[Dict[str, Any]]
    personality_evolution: List[Dict[str, Any]]


class GameStatsResponse(BaseModel):
    stats: GameStats
    current_session: Dict[str, Any]
    milestones: List[Dict[str, Any]]


# 成就系统相关
class Achievement(BaseModel):
    id: str
    name: str
    description: str
    category: str
    requirements: Dict[str, Any]
    reward_ic: int
    icon: str
    unlocked_at: Optional[datetime]


class AchievementProgress(BaseModel):
    achievement_id: str
    current_progress: Dict[str, Any]
    completion_percentage: float
    estimated_completion: Optional[datetime]


# 生命周期相关
class LifeStageInfo(BaseModel):
    stage_name: str
    age_range: tuple
    key_challenges: List[str]
    typical_goals: List[str]
    financial_focus: List[str]


class LifeReviewReport(BaseModel):
    agent_id: str
    life_span: Dict[str, int]  # start_age, end_age
    major_decisions: List[DecisionRecord]
    wealth_trajectory: List[Dict[str, Any]]
    relationship_summary: Dict[str, Any]
    achievement_summary: List[Achievement]
    final_net_worth: float
    life_satisfaction_score: float
    key_lessons: List[str]
    ic_reward: int


# 错误响应
class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime
    request_id: Optional[str]


# 通用响应
class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]]
    timestamp: datetime