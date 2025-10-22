"""
Unity客户端专用数据模型
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class UnityResponse(BaseModel):
    """Unity统一响应格式"""
    status: ResponseStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None

class MBTIType(str, Enum):
    INTJ = "INTJ"
    INTP = "INTP"
    ENTJ = "ENTJ"
    ENTP = "ENTP"
    INFJ = "INFJ"
    INFP = "INFP"
    ENFJ = "ENFJ"
    ENFP = "ENFP"
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    ESTP = "ESTP"
    ESFP = "ESFP"

class EmotionType(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    WORRIED = "worried"
    CONFIDENT = "confident"
    CONFUSED = "confused"
    NEUTRAL = "neutral"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class AvatarData(BaseModel):
    """AI化身数据"""
    name: str
    mbti_type: MBTIType
    trust_level: int
    current_emotion: EmotionType
    health: int
    energy: int
    stress: int

class FinancialData(BaseModel):
    """财务数据"""
    cash: float
    total_assets: float
    monthly_income: float
    monthly_expenses: float
    investment_value: float
    debt: float

class DecisionOption(BaseModel):
    """决策选项"""
    id: int
    title: str
    description: str
    consequence: str
    risk_level: RiskLevel
    financial_impact: float

class SituationData(BaseModel):
    """当前情况数据"""
    id: str
    title: str
    description: str
    context: str
    options: List[DecisionOption]
    time_limit: Optional[int] = None  # 秒数，None表示无限制

class DecisionRequest(BaseModel):
    """决策请求"""
    situation_id: str
    option_id: int
    user_input: Optional[str] = None

class DecisionResult(BaseModel):
    """决策结果"""
    success: bool
    result_description: str
    financial_change: Dict[str, float]
    avatar_change: Dict[str, Any]
    trust_change: int
    new_situation: Optional[SituationData] = None

class GameState(BaseModel):
    """完整游戏状态"""
    user_id: str
    avatar: AvatarData
    finances: FinancialData
    current_situation: Optional[SituationData] = None
    game_month: int
    is_game_over: bool
    game_over_reason: Optional[str] = None

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str

class CreateAvatarRequest(BaseModel):
    """创建化身请求"""
    name: str
    mbti_type: MBTIType

class WebSocketMessage(BaseModel):
    """WebSocket消息格式"""
    type: str  # "situation", "decision_result", "status_update", etc.
    data: Dict[str, Any]
    timestamp: float