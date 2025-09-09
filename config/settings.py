"""
Echopolis 配置设置
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用程序设置"""
    
    # 应用基础配置
    APP_NAME: str = "Echopolis"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost/echopolis"
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI模型配置
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    MODEL_NAME: str = "deepseek-chat"
    MAX_TOKENS: int = 1000
    
    # 游戏核心参数
    GAME_TIME_MULTIPLIER: int = 168  # 1小时现实时间 = 1周游戏时间
    MAX_INTERVENTION_POINTS: int = 10
    INITIAL_CREDIT_POINTS: int = 50000
    INITIAL_TRUST_LEVEL: int = 50
    
    # 经济系统参数
    BASE_INTEREST_RATE: float = 0.025  # 2.5%基准利率
    INFLATION_RATE: float = 0.02  # 2%通胀率
    MARKET_VOLATILITY: float = 0.15  # 15%市场波动率
    
    # 生命周期阶段
    LIFE_STAGES = {
        "startup": (18, 22),    # 启航期
        "exploration": (23, 30), # 探索期
        "growth": (31, 45),     # 奋斗期
        "accumulation": (46, 60), # 沉淀期
        "retirement": (60, 100)  # 黄昏期
    }
    
    # 人格特质权重
    PERSONALITY_WEIGHTS = {
        "openness": 0.2,
        "conscientiousness": 0.25,
        "extraversion": 0.15,
        "agreeableness": 0.15,
        "neuroticism": 0.25
    }
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/echopolis.log"
    
    class Config:
        env_file = ".env"


# 全局设置实例
settings = Settings()


# 游戏常量
class GameConstants:
    """游戏常量定义"""
    
    # 货币系统
    CURRENCY_SYMBOL = "CP"  # Credit Points
    INSIGHT_CRYSTAL_SYMBOL = "IC"  # Insight Crystal
    
    # 区域定义
    DISTRICTS = {
        "launchpad": "启航区",
        "cbd": "中央商务区", 
        "silicon_valley": "硅芯谷",
        "lakeside": "湖畔居",
        "old_town": "旧城区"
    }
    
    # 资产类型
    ASSET_TYPES = {
        "financial": ["stocks", "bonds", "funds", "deposits"],
        "real_estate": ["residential", "commercial", "land"],
        "intangible": ["patents", "copyrights", "brands"]
    }
    
    # 事件类型
    EVENT_TYPES = {
        "macro": ["economic_crisis", "policy_change", "market_boom"],
        "industry": ["tech_breakthrough", "regulation_change", "market_shift"],
        "personal": ["job_change", "health_issue", "windfall", "family_event"]
    }
    
    # FQ等级定义
    FQ_LEVELS = {
        1: "新手",
        2: "学徒", 
        3: "从业者",
        4: "专家",
        5: "大师"
    }


# 数据库表名
class TableNames:
    """数据库表名定义"""
    USERS = "users"
    AGENTS = "agents"
    TRANSACTIONS = "transactions"
    ASSETS = "assets"
    EVENTS = "events"
    MARKET_DATA = "market_data"
    INTERVENTIONS = "interventions"
    RELATIONSHIPS = "relationships"