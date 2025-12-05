"""
用户标签系统 - EchoPolis
基于用户行为动态生成和更新标签，用于个性化事件推荐
"""
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import sqlite3
import json


class TagCategory(Enum):
    """标签分类"""
    INVESTMENT = "investment"      # 投资偏好
    RISK = "risk"                  # 风险态度
    LIFESTYLE = "lifestyle"        # 生活方式
    CAREER = "career"              # 职业倾向
    SOCIAL = "social"              # 社交特征
    OTHER = "other"                # 其他


@dataclass
class UserTag:
    """用户标签"""
    id: str
    name: str
    category: str
    icon: str
    weight: float = 0.5           # 权重 0-1
    is_recent: bool = False       # 是否最近获得
    source: str = "behavior"      # 来源: behavior/preset/custom


# 预设标签库
PRESET_TAGS = {
    # 投资偏好
    "tech_investor": UserTag("tech_investor", "科技投资者", "investment", "💻"),
    "value_investor": UserTag("value_investor", "价值投资者", "investment", "📊"),
    "growth_investor": UserTag("growth_investor", "成长投资者", "investment", "📈"),
    "dividend_seeker": UserTag("dividend_seeker", "分红爱好者", "investment", "💰"),
    "diversified": UserTag("diversified", "分散投资", "investment", "🎨"),
    "long_term": UserTag("long_term", "长期主义", "investment", "⏰"),
    "short_term": UserTag("short_term", "短线操作", "investment", "⚡"),
    "real_estate": UserTag("real_estate", "房产偏好", "investment", "🏠"),
    
    # 风险态度
    "risk_taker": UserTag("risk_taker", "风险偏好者", "risk", "🎲"),
    "conservative": UserTag("conservative", "保守型", "risk", "🛡️"),
    "moderate": UserTag("moderate", "稳健型", "risk", "⚖️"),
    "aggressive": UserTag("aggressive", "激进型", "risk", "🔥"),
    "loss_averse": UserTag("loss_averse", "厌恶损失", "risk", "😰"),
    
    # 生活方式
    "health_conscious": UserTag("health_conscious", "注重健康", "lifestyle", "🏃"),
    "work_life_balance": UserTag("work_life_balance", "平衡生活", "lifestyle", "🧘"),
    "minimalist": UserTag("minimalist", "极简主义", "lifestyle", "✨"),
    "materialist": UserTag("materialist", "物质追求", "lifestyle", "🛍️"),
    "experience_seeker": UserTag("experience_seeker", "体验至上", "lifestyle", "🌍"),
    "frugal": UserTag("frugal", "节俭生活", "lifestyle", "💵"),
    
    # 职业倾向
    "career_focused": UserTag("career_focused", "事业导向", "career", "💼"),
    "entrepreneur": UserTag("entrepreneur", "创业精神", "career", "🚀"),
    "steady_job": UserTag("steady_job", "稳定工作", "career", "🏢"),
    "side_hustle": UserTag("side_hustle", "副业达人", "career", "🌙"),
    "skill_learner": UserTag("skill_learner", "技能学习者", "career", "📚"),
    
    # 社交特征
    "social_active": UserTag("social_active", "社交活跃", "social", "👥"),
    "introvert": UserTag("introvert", "内向独处", "social", "🏠"),
    "networker": UserTag("networker", "人脉积累", "social", "🤝"),
    "generous": UserTag("generous", "慷慨大方", "social", "🎁"),
    "cautious_lender": UserTag("cautious_lender", "谨慎借贷", "social", "🔐"),
}


# 行为到标签的映射规则
BEHAVIOR_TAG_RULES = {
    # 投资行为
    "buy_tech_stock": [("tech_investor", 0.15)],
    "buy_value_stock": [("value_investor", 0.15)],
    "buy_growth_stock": [("growth_investor", 0.15)],
    "hold_long_term": [("long_term", 0.1), ("value_investor", 0.05)],
    "sell_quick": [("short_term", 0.15)],
    "diversify_portfolio": [("diversified", 0.2)],
    "buy_real_estate": [("real_estate", 0.2)],
    
    # 风险行为
    "high_risk_investment": [("risk_taker", 0.15), ("aggressive", 0.1)],
    "low_risk_investment": [("conservative", 0.15), ("moderate", 0.05)],
    "panic_sell": [("loss_averse", 0.2)],
    "buy_dip": [("risk_taker", 0.1)],
    
    # 生活行为
    "gym_expense": [("health_conscious", 0.15)],
    "vacation_expense": [("experience_seeker", 0.15)],
    "luxury_purchase": [("materialist", 0.15)],
    "save_money": [("frugal", 0.1)],
    
    # 职业行为
    "apply_job": [("career_focused", 0.1)],
    "start_business": [("entrepreneur", 0.2)],
    "learn_skill": [("skill_learner", 0.15)],
    "side_business": [("side_hustle", 0.15)],
    
    # 社交行为
    "lend_money": [("generous", 0.1)],
    "refuse_lend": [("cautious_lender", 0.1)],
    "social_event": [("social_active", 0.1)],
    "stay_home": [("introvert", 0.1)],
}


class UserTagSystem:
    """用户标签系统"""
    
    def __init__(self, db_path: str = "echopolis.db"):
        self.db_path = db_path
        self.init_tables()
    
    def init_tables(self):
        """初始化标签相关表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 用户标签表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    tag_id TEXT NOT NULL,
                    tag_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    icon TEXT NOT NULL,
                    weight REAL DEFAULT 0.5,
                    source TEXT DEFAULT 'behavior',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, tag_id)
                )
            ''')
            
            # 标签历史表（记录标签变化）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tag_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    tag_id TEXT NOT NULL,
                    old_weight REAL,
                    new_weight REAL,
                    reason TEXT,
                    month INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def get_user_tags(self, session_id: str) -> List[Dict]:
        """获取用户所有标签"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tag_id, tag_name, category, icon, weight, source,
                       datetime(updated_at) > datetime('now', '-7 days') as is_recent
                FROM user_tags
                WHERE session_id = ?
                ORDER BY weight DESC
            ''', (session_id,))
            
            tags = []
            for row in cursor.fetchall():
                tags.append({
                    "id": row[0],
                    "name": row[1],
                    "category": row[2],
                    "icon": row[3],
                    "weight": row[4],
                    "source": row[5],
                    "isRecent": bool(row[6])
                })
            return tags
    
    def add_or_update_tag(self, session_id: str, tag_id: str, weight_delta: float = 0.1, 
                          source: str = "behavior", reason: str = None):
        """添加或更新用户标签"""
        if tag_id not in PRESET_TAGS:
            return False
        
        tag = PRESET_TAGS[tag_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查标签是否存在
            cursor.execute('''
                SELECT weight FROM user_tags WHERE session_id = ? AND tag_id = ?
            ''', (session_id, tag_id))
            row = cursor.fetchone()
            
            if row:
                old_weight = row[0]
                new_weight = min(1.0, max(0.0, old_weight + weight_delta))
                
                cursor.execute('''
                    UPDATE user_tags 
                    SET weight = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = ? AND tag_id = ?
                ''', (new_weight, session_id, tag_id))
            else:
                old_weight = 0
                new_weight = min(1.0, max(0.0, 0.5 + weight_delta))
                
                cursor.execute('''
                    INSERT INTO user_tags (session_id, tag_id, tag_name, category, icon, weight, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, tag_id, tag.name, tag.category, tag.icon, new_weight, source))
            
            # 记录历史
            cursor.execute('''
                INSERT INTO tag_history (session_id, tag_id, old_weight, new_weight, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, tag_id, old_weight, new_weight, reason))
            
            conn.commit()
            return True
    
    def process_behavior(self, session_id: str, behavior: str, context: Dict = None):
        """根据用户行为更新标签"""
        if behavior not in BEHAVIOR_TAG_RULES:
            return []
        
        updated_tags = []
        for tag_id, weight_delta in BEHAVIOR_TAG_RULES[behavior]:
            if self.add_or_update_tag(session_id, tag_id, weight_delta, "behavior", f"行为: {behavior}"):
                updated_tags.append(tag_id)
        
        return updated_tags
    
    def decay_tags(self, session_id: str, decay_rate: float = 0.02):
        """标签自然衰减（每月调用）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_tags 
                SET weight = MAX(0.1, weight - ?)
                WHERE session_id = ? AND weight > 0.1
            ''', (decay_rate, session_id))
            conn.commit()
    
    def get_top_tags(self, session_id: str, limit: int = 5) -> List[str]:
        """获取用户权重最高的标签ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tag_id FROM user_tags
                WHERE session_id = ?
                ORDER BY weight DESC
                LIMIT ?
            ''', (session_id, limit))
            return [row[0] for row in cursor.fetchall()]
    
    def init_preset_tags(self, session_id: str, tag_ids: List[str]):
        """初始化预设标签（角色创建时）"""
        for tag_id in tag_ids:
            if tag_id.startswith("custom:"):
                # 处理自定义标签
                custom_name = tag_id.replace("custom:", "")
                self._add_custom_tag(session_id, custom_name)
            else:
                self.add_or_update_tag(session_id, tag_id, 0.3, "preset", "角色初始化")
    
    def _add_custom_tag(self, session_id: str, tag_name: str):
        """添加自定义标签"""
        tag_id = f"custom_{tag_name}_{session_id[:8]}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_tags 
                (session_id, tag_id, tag_name, category, icon, weight, source)
                VALUES (?, ?, ?, 'other', '🏷️', 0.6, 'custom')
            ''', (session_id, tag_id, tag_name))
            conn.commit()
    
    def get_tag_definition(self, tag_id: str) -> Optional[Dict]:
        """获取标签定义"""
        if tag_id in PRESET_TAGS:
            tag = PRESET_TAGS[tag_id]
            return {
                "id": tag_id,
                "name": tag.name,
                "icon": tag.icon,
                "category": tag.category
            }
        return None
    
    def get_all_tag_definitions(self) -> List[Dict]:
        """获取所有可用标签定义"""
        return [
            {
                "id": tag_id,
                "name": tag.name,
                "icon": tag.icon,
                "category": tag.category,
                "base_weight": tag.weight
            }
            for tag_id, tag in PRESET_TAGS.items()
        ]
    
    def tag_to_dict(self, tag: UserTag) -> Dict:
        """将标签对象转换为字典"""
        return {
            "id": tag.id,
            "name": tag.name,
            "icon": tag.icon,
            "category": tag.category,
            "weight": tag.weight,
            "is_recent": tag.is_recent,
            "source": tag.source
        }
    
    def initialize_user_tags(self, session_id: str) -> List[UserTag]:
        """为新用户初始化默认标签"""
        default_tag_ids = ["moderate", "work_life_balance", "steady_job", "frugal"]
        tags = []
        
        for tag_id in default_tag_ids:
            if tag_id in PRESET_TAGS:
                base_tag = PRESET_TAGS[tag_id]
                tags.append(UserTag(
                    id=tag_id,
                    name=base_tag.name,
                    category=base_tag.category,
                    icon=base_tag.icon,
                    weight=0.5,
                    is_recent=True,
                    source="系统初始化"
                ))
        
        return tags
    
    def get_event_pool(self) -> List[Dict]:
        """获取事件池"""
        return self._generate_expanded_event_pool()
    
    def _generate_expanded_event_pool(self) -> List[Dict]:
        """生成扩展的事件池（模拟1000+事件）"""
        base_events = [
            # ============ 财务决策类 ============
            {
                "id": "financial_001",
                "category": "financial",
                "title": "投资理财产品",
                "description": "银行推出一款年化收益5%的理财产品，锁定期1年。",
                "tags": ["conservative", "value_investor"],
                "icon": "💰",
                "options": [
                    {"text": "投入50%积蓄", "tags": ["value_investor"], "effects": {"cash": -0.5, "assets": 0.025}},
                    {"text": "小额尝试", "tags": ["moderate"], "effects": {"cash": -0.1}},
                    {"text": "观望不投", "tags": ["conservative"], "effects": {}}
                ]
            },
            {
                "id": "financial_002",
                "category": "financial",
                "title": "基金定投计划",
                "description": "财务顾问建议你开始每月定投指数基金。",
                "tags": ["long_term", "diversified"],
                "icon": "📊",
                "options": [
                    {"text": "每月定投2000元", "tags": ["long_term", "diversified"], "effects": {"monthly_expense": 2000}},
                    {"text": "一次性投入", "tags": ["aggressive"], "effects": {"cash": -24000}},
                    {"text": "暂时不考虑", "tags": [], "effects": {}}
                ]
            },
            {
                "id": "financial_003",
                "category": "financial",
                "title": "加密货币诱惑",
                "description": "朋友炫耀他的加密货币翻了5倍，邀你入场。",
                "tags": ["risk_taker", "aggressive", "tech_investor"],
                "icon": "₿",
                "options": [
                    {"text": "投入10万试水", "tags": ["risk_taker", "aggressive"], "effects": {"cash": -100000}},
                    {"text": "投1万感受下", "tags": ["moderate"], "effects": {"cash": -10000}},
                    {"text": "谨慎拒绝", "tags": ["conservative"], "effects": {}}
                ]
            },
            {
                "id": "financial_004",
                "category": "financial",
                "title": "股票分红通知",
                "description": "你持有的蓝筹股宣布高额分红，收到一笔意外之财。",
                "tags": ["dividend_seeker", "value_investor"],
                "icon": "💵",
                "options": [
                    {"text": "继续加仓该股", "tags": ["dividend_seeker", "value_investor"], "effects": {"cash": 5000}},
                    {"text": "将分红存入储蓄", "tags": ["conservative", "frugal"], "effects": {"cash": 5000}},
                    {"text": "犒劳自己一下", "tags": ["materialist"], "effects": {"cash": 5000, "happiness": 10}}
                ]
            },
            {
                "id": "financial_005",
                "category": "financial",
                "title": "黄金投资机会",
                "description": "国际局势动荡，黄金价格波动加剧。",
                "tags": ["conservative", "diversified"],
                "icon": "🥇",
                "options": [
                    {"text": "配置10%黄金资产", "tags": ["conservative", "diversified"], "effects": {"cash": -0.1}},
                    {"text": "大量买入避险", "tags": ["loss_averse"], "effects": {"cash": -0.3}},
                    {"text": "不感兴趣", "tags": [], "effects": {}}
                ]
            },
            
            # ============ 职业发展类 ============
            {
                "id": "career_001",
                "category": "career",
                "title": "跳槽机会",
                "description": "猎头联系你，一家知名企业提供比现在高30%的薪资。",
                "tags": ["career_focused", "risk_taker"],
                "icon": "💼",
                "options": [
                    {"text": "果断跳槽", "tags": ["career_focused", "risk_taker"], "effects": {"income": 0.3}},
                    {"text": "用offer谈加薪", "tags": ["career_focused"], "effects": {"income": 0.15}},
                    {"text": "婉拒，稳定为主", "tags": ["steady_job", "conservative"], "effects": {}}
                ]
            },
            {
                "id": "career_002",
                "category": "career",
                "title": "创业合伙邀请",
                "description": "大学同学创业成功，邀你作为合伙人加入新项目。",
                "tags": ["entrepreneur", "risk_taker"],
                "icon": "🚀",
                "options": [
                    {"text": "辞职加入创业", "tags": ["entrepreneur", "risk_taker"], "effects": {"income": -1, "happiness": 15}},
                    {"text": "作为投资人参与", "tags": ["entrepreneur"], "effects": {"cash": -50000}},
                    {"text": "祝福但不参与", "tags": ["steady_job"], "effects": {}}
                ]
            },
            {
                "id": "career_003",
                "category": "career",
                "title": "海外工作机会",
                "description": "公司提供海外派遣机会，薪资翻倍但要离开家人朋友。",
                "tags": ["career_focused", "experience_seeker"],
                "icon": "✈️",
                "options": [
                    {"text": "接受外派", "tags": ["career_focused", "experience_seeker"], "effects": {"income": 1, "happiness": -10}},
                    {"text": "要求更好条件", "tags": ["career_focused"], "effects": {}},
                    {"text": "拒绝，家人优先", "tags": ["work_life_balance"], "effects": {}}
                ]
            },
            {
                "id": "career_004",
                "category": "career",
                "title": "副业机会",
                "description": "发现一个周末兼职机会，每月能多赚5000但会牺牲休息时间。",
                "tags": ["side_hustle", "career_focused"],
                "icon": "🌙",
                "options": [
                    {"text": "接下副业", "tags": ["side_hustle"], "effects": {"income": 5000, "happiness": -5}},
                    {"text": "先试一个月", "tags": ["moderate"], "effects": {"income": 5000}},
                    {"text": "休息更重要", "tags": ["work_life_balance"], "effects": {}}
                ]
            },
            {
                "id": "career_005",
                "category": "career",
                "title": "技能培训认证",
                "description": "行业权威认证考试报名开始，通过后可大幅提升竞争力。",
                "tags": ["skill_learner", "career_focused"],
                "icon": "📜",
                "options": [
                    {"text": "报名并全力备考", "tags": ["skill_learner", "career_focused"], "effects": {"cash": -5000, "happiness": -5}},
                    {"text": "自学不考证", "tags": ["skill_learner", "frugal"], "effects": {}},
                    {"text": "工作经验更重要", "tags": [], "effects": {}}
                ]
            },
            
            # ============ 生活选择类 ============
            {
                "id": "life_001",
                "category": "life",
                "title": "购房抉择",
                "description": "看中一套心仪的房子，首付需要掏空积蓄并背负30年房贷。",
                "tags": ["real_estate", "long_term"],
                "icon": "🏠",
                "options": [
                    {"text": "咬牙买下", "tags": ["real_estate", "long_term"], "effects": {"cash": -0.8, "monthly_expense": 8000}},
                    {"text": "再等等看", "tags": ["conservative"], "effects": {}},
                    {"text": "继续租房", "tags": ["minimalist", "experience_seeker"], "effects": {}}
                ]
            },
            {
                "id": "life_002",
                "category": "life",
                "title": "健身房会员",
                "description": "小区新开了一家高端健身房，年卡优惠只有今天。",
                "tags": ["health_conscious"],
                "icon": "🏋️",
                "options": [
                    {"text": "办3年卡更划算", "tags": ["health_conscious", "long_term"], "effects": {"cash": -15000, "health": 10}},
                    {"text": "先办1年试试", "tags": ["health_conscious", "moderate"], "effects": {"cash": -6000, "health": 5}},
                    {"text": "在家锻炼就行", "tags": ["frugal", "minimalist"], "effects": {}}
                ]
            },
            {
                "id": "life_003",
                "category": "life",
                "title": "奢侈品诱惑",
                "description": "心仪已久的包包/手表正在打折，但价格仍是月薪的一半。",
                "tags": ["materialist"],
                "icon": "👜",
                "options": [
                    {"text": "犒赏自己", "tags": ["materialist"], "effects": {"cash": -15000, "happiness": 15}},
                    {"text": "等更大折扣", "tags": ["frugal"], "effects": {}},
                    {"text": "理性消费", "tags": ["minimalist", "frugal"], "effects": {"happiness": -3}}
                ]
            },
            {
                "id": "life_004",
                "category": "life",
                "title": "旅行计划",
                "description": "工作压力大，朋友邀请你一起出国旅行放松。",
                "tags": ["experience_seeker", "work_life_balance"],
                "icon": "🌴",
                "options": [
                    {"text": "来一场说走就走的旅行", "tags": ["experience_seeker"], "effects": {"cash": -20000, "happiness": 25}},
                    {"text": "国内短途就好", "tags": ["moderate", "frugal"], "effects": {"cash": -3000, "happiness": 10}},
                    {"text": "工作太忙走不开", "tags": ["career_focused"], "effects": {"happiness": -5}}
                ]
            },
            {
                "id": "life_005",
                "category": "life",
                "title": "宠物领养",
                "description": "朋友家的猫生了一窝小猫，问你要不要领养一只。",
                "tags": ["experience_seeker", "social_active"],
                "icon": "🐱",
                "options": [
                    {"text": "领养小猫", "tags": ["experience_seeker"], "effects": {"monthly_expense": 500, "happiness": 10}},
                    {"text": "考虑养狗", "tags": [], "effects": {}},
                    {"text": "暂时不养", "tags": ["minimalist"], "effects": {}}
                ]
            },
            
            # ============ 社交关系类 ============
            {
                "id": "social_001",
                "category": "social",
                "title": "朋友借钱",
                "description": "多年好友急需借钱周转，金额不小。",
                "tags": ["generous", "cautious_lender", "social_active"],
                "icon": "🤝",
                "options": [
                    {"text": "全力帮助", "tags": ["generous", "social_active"], "effects": {"cash": -30000}},
                    {"text": "借一部分", "tags": ["generous", "moderate"], "effects": {"cash": -10000}},
                    {"text": "婉言拒绝", "tags": ["cautious_lender"], "effects": {"happiness": -5}}
                ]
            },
            {
                "id": "social_002",
                "category": "social",
                "title": "份子钱季节",
                "description": "这个月有3个朋友结婚，份子钱是个不小的开支。",
                "tags": ["social_active", "generous"],
                "icon": "💒",
                "options": [
                    {"text": "每家都包大红包", "tags": ["generous", "social_active"], "effects": {"cash": -6000}},
                    {"text": "按亲疏远近给", "tags": ["moderate"], "effects": {"cash": -3000}},
                    {"text": "找理由不去", "tags": ["introvert", "frugal"], "effects": {"happiness": -10}}
                ]
            },
            {
                "id": "social_003",
                "category": "social",
                "title": "同学聚会",
                "description": "大学同学组织聚会，好多年没见的老同学都会来。",
                "tags": ["social_active", "networker"],
                "icon": "🎓",
                "options": [
                    {"text": "积极参与组织", "tags": ["social_active", "networker"], "effects": {"cash": -1000, "happiness": 10}},
                    {"text": "参加但低调", "tags": ["moderate"], "effects": {"cash": -500, "happiness": 5}},
                    {"text": "找借口不去", "tags": ["introvert"], "effects": {}}
                ]
            },
            {
                "id": "social_004",
                "category": "social",
                "title": "家庭聚餐AA",
                "description": "亲戚聚餐，表哥提议这次你请客。",
                "tags": ["generous", "social_active"],
                "icon": "🍽️",
                "options": [
                    {"text": "大方买单", "tags": ["generous"], "effects": {"cash": -2000, "happiness": 5}},
                    {"text": "提议AA制", "tags": ["moderate"], "effects": {"cash": -300}},
                    {"text": "找理由推脱", "tags": ["cautious_lender", "frugal"], "effects": {"happiness": -5}}
                ]
            },
            {
                "id": "social_005",
                "category": "social",
                "title": "社群活动邀请",
                "description": "被邀请加入一个高端人脉社群，入会费不菲。",
                "tags": ["networker", "career_focused"],
                "icon": "🎭",
                "options": [
                    {"text": "加入拓展人脉", "tags": ["networker", "career_focused"], "effects": {"cash": -20000}},
                    {"text": "先观察一下", "tags": ["moderate", "cautious_lender"], "effects": {}},
                    {"text": "不感兴趣", "tags": ["introvert"], "effects": {}}
                ]
            },
            
            # ============ 投资机会类 ============
            {
                "id": "investment_001",
                "category": "investment",
                "title": "科技股暴涨",
                "description": "AI概念大热，科技股集体飙升！",
                "tags": ["tech_investor", "growth_investor", "risk_taker"],
                "icon": "🚀",
                "options": [
                    {"text": "重仓追高", "tags": ["tech_investor", "risk_taker", "aggressive"], "effects": {"cash": -0.5}},
                    {"text": "适度配置", "tags": ["tech_investor", "moderate"], "effects": {"cash": -0.2}},
                    {"text": "不追热点", "tags": ["value_investor", "conservative"], "effects": {}}
                ]
            },
            {
                "id": "investment_002",
                "category": "investment",
                "title": "IPO打新机会",
                "description": "一家明星公司即将上市，人人都想打新股。",
                "tags": ["growth_investor", "risk_taker"],
                "icon": "🎯",
                "options": [
                    {"text": "全力打新", "tags": ["growth_investor", "risk_taker"], "effects": {"cash": -50000}},
                    {"text": "小资金参与", "tags": ["moderate"], "effects": {"cash": -10000}},
                    {"text": "等上市后再看", "tags": ["conservative"], "effects": {}}
                ]
            },
            {
                "id": "investment_003",
                "category": "investment",
                "title": "REITs投资",
                "description": "一款优质REITs基金正在发行，投资商业地产。",
                "tags": ["real_estate", "dividend_seeker", "diversified"],
                "icon": "🏢",
                "options": [
                    {"text": "大额认购", "tags": ["real_estate", "dividend_seeker"], "effects": {"cash": -100000}},
                    {"text": "小额配置", "tags": ["diversified", "moderate"], "effects": {"cash": -20000}},
                    {"text": "直接买房更好", "tags": ["real_estate"], "effects": {}}
                ]
            },
            {
                "id": "investment_004",
                "category": "investment",
                "title": "债券市场机会",
                "description": "利率下行周期，债券价格可能上涨。",
                "tags": ["conservative", "value_investor"],
                "icon": "📃",
                "options": [
                    {"text": "增配债券基金", "tags": ["conservative", "diversified"], "effects": {"cash": -50000}},
                    {"text": "买国债稳妥", "tags": ["conservative", "loss_averse"], "effects": {"cash": -30000}},
                    {"text": "股票收益更高", "tags": ["growth_investor", "risk_taker"], "effects": {}}
                ]
            },
            {
                "id": "investment_005",
                "category": "investment",
                "title": "私募基金门票",
                "description": "朋友介绍一只私募基金，过往业绩亮眼，门槛100万。",
                "tags": ["risk_taker", "aggressive"],
                "icon": "🎫",
                "options": [
                    {"text": "凑够门槛投资", "tags": ["risk_taker", "aggressive"], "effects": {"cash": -1000000}},
                    {"text": "找人合投", "tags": ["moderate", "networker"], "effects": {"cash": -300000}},
                    {"text": "风险太大", "tags": ["conservative", "loss_averse"], "effects": {}}
                ]
            },
            
            # ============ 突发事件类 ============
            {
                "id": "emergency_001",
                "category": "emergency",
                "title": "车祸理赔",
                "description": "停在路边的车被撞，对方逃逸，修车需要一笔钱。",
                "tags": ["loss_averse"],
                "icon": "🚗",
                "options": [
                    {"text": "走保险理赔", "tags": ["moderate"], "effects": {"time": -5, "happiness": -5}},
                    {"text": "自己承担", "tags": ["frugal"], "effects": {"cash": -8000, "happiness": -10}},
                    {"text": "报警追查", "tags": ["aggressive"], "effects": {"time": -10, "happiness": -5}}
                ]
            },
            {
                "id": "emergency_002",
                "category": "emergency",
                "title": "家人住院",
                "description": "亲人突发疾病住院，需要一大笔医疗费。",
                "tags": ["loss_averse"],
                "icon": "🏥",
                "options": [
                    {"text": "全力救治不惜代价", "tags": ["generous"], "effects": {"cash": -100000, "happiness": -20}},
                    {"text": "走医保尽力而为", "tags": ["moderate"], "effects": {"cash": -30000, "happiness": -15}},
                    {"text": "发起众筹", "tags": ["social_active"], "effects": {"cash": -20000, "happiness": -10}}
                ]
            },
            {
                "id": "emergency_003",
                "category": "emergency",
                "title": "失业风波",
                "description": "公司裁员，你在名单上，能获得N+1赔偿。",
                "tags": ["loss_averse", "career_focused"],
                "icon": "📦",
                "options": [
                    {"text": "接受赔偿重新找工作", "tags": ["moderate"], "effects": {"cash": 50000, "income": -1}},
                    {"text": "争取更多赔偿", "tags": ["aggressive"], "effects": {"time": -10}},
                    {"text": "主动请缨留下", "tags": ["career_focused", "steady_job"], "effects": {}}
                ]
            },
            {
                "id": "emergency_004",
                "category": "emergency",
                "title": "诈骗电话",
                "description": "接到自称银行的电话说账户异常，要求转账验证。",
                "tags": ["cautious_lender"],
                "icon": "📱",
                "options": [
                    {"text": "挂断并报警", "tags": ["cautious_lender", "conservative"], "effects": {}},
                    {"text": "先核实再说", "tags": ["moderate"], "effects": {}},
                    {"text": "配合对方操作", "tags": [], "effects": {"cash": -50000, "happiness": -30}}
                ]
            },
            {
                "id": "emergency_005",
                "category": "emergency",
                "title": "房屋漏水",
                "description": "楼上漏水把你家泡了，损失不小。",
                "tags": ["loss_averse"],
                "icon": "💧",
                "options": [
                    {"text": "找楼上协商赔偿", "tags": ["moderate", "social_active"], "effects": {"time": -5}},
                    {"text": "直接走法律程序", "tags": ["aggressive"], "effects": {"cash": -5000, "time": -15}},
                    {"text": "自认倒霉修一修", "tags": ["conservative", "frugal"], "effects": {"cash": -10000, "happiness": -10}}
                ]
            },
            
            # ============ 个人成长类 ============
            {
                "id": "growth_001",
                "category": "growth",
                "title": "读MBA机会",
                "description": "获得知名商学院MBA录取通知，学费不菲但人脉价值高。",
                "tags": ["skill_learner", "career_focused", "networker"],
                "icon": "🎓",
                "options": [
                    {"text": "全日制深造", "tags": ["skill_learner", "career_focused"], "effects": {"cash": -300000, "income": -1}},
                    {"text": "在职MBA", "tags": ["skill_learner", "work_life_balance"], "effects": {"cash": -200000, "happiness": -10}},
                    {"text": "工作经验更重要", "tags": [], "effects": {}}
                ]
            },
            {
                "id": "growth_002",
                "category": "growth",
                "title": "健康体检预警",
                "description": "年度体检发现一些小问题，医生建议改善生活习惯。",
                "tags": ["health_conscious", "work_life_balance"],
                "icon": "🩺",
                "options": [
                    {"text": "立即调整作息运动", "tags": ["health_conscious", "work_life_balance"], "effects": {"health": 15, "happiness": 5}},
                    {"text": "买份重疾险", "tags": ["conservative", "loss_averse"], "effects": {"monthly_expense": 500}},
                    {"text": "年轻不用太在意", "tags": [], "effects": {"health": -5}}
                ]
            },
            {
                "id": "growth_003",
                "category": "growth",
                "title": "心理咨询",
                "description": "最近压力很大，朋友建议你尝试心理咨询。",
                "tags": ["health_conscious", "work_life_balance"],
                "icon": "🧠",
                "options": [
                    {"text": "开始定期咨询", "tags": ["health_conscious"], "effects": {"monthly_expense": 800, "happiness": 10}},
                    {"text": "先自己调整", "tags": ["frugal"], "effects": {}},
                    {"text": "没什么大不了", "tags": [], "effects": {"happiness": -5}}
                ]
            },
            {
                "id": "growth_004",
                "category": "growth",
                "title": "兴趣班报名",
                "description": "一直想学的技能（乐器/绘画/编程）开班招生了。",
                "tags": ["skill_learner", "experience_seeker"],
                "icon": "🎨",
                "options": [
                    {"text": "报名系统学习", "tags": ["skill_learner"], "effects": {"cash": -5000, "happiness": 10}},
                    {"text": "网上自学", "tags": ["frugal", "skill_learner"], "effects": {}},
                    {"text": "没时间", "tags": ["career_focused"], "effects": {}}
                ]
            },
            {
                "id": "growth_005",
                "category": "growth",
                "title": "冥想训练营",
                "description": "朋友推荐一个正念冥想课程，说对减压很有帮助。",
                "tags": ["health_conscious", "work_life_balance", "minimalist"],
                "icon": "🧘",
                "options": [
                    {"text": "报名参加", "tags": ["health_conscious", "minimalist"], "effects": {"cash": -2000, "happiness": 8}},
                    {"text": "用app自学", "tags": ["frugal"], "effects": {"happiness": 3}},
                    {"text": "不感兴趣", "tags": [], "effects": {}}
                ]
            },
            
            # ============ 消费抉择类 ============
            {
                "id": "consumption_001",
                "category": "consumption",
                "title": "换手机时刻",
                "description": "手机用了三年有点卡，新款旗舰机很诱人。",
                "tags": ["materialist", "tech_investor", "frugal"],
                "icon": "📱",
                "options": [
                    {"text": "买最新旗舰", "tags": ["materialist", "tech_investor"], "effects": {"cash": -8000, "happiness": 8}},
                    {"text": "买性价比款", "tags": ["moderate", "frugal"], "effects": {"cash": -3000, "happiness": 5}},
                    {"text": "能用就继续用", "tags": ["frugal", "minimalist"], "effects": {}}
                ]
            },
            {
                "id": "consumption_002",
                "category": "consumption",
                "title": "双十一购物",
                "description": "购物车里囤了一大堆，算下来能省不少。",
                "tags": ["materialist", "frugal"],
                "icon": "🛒",
                "options": [
                    {"text": "全部买买买", "tags": ["materialist"], "effects": {"cash": -5000, "happiness": 10}},
                    {"text": "只买必需品", "tags": ["frugal", "moderate"], "effects": {"cash": -1000, "happiness": 3}},
                    {"text": "一件不买", "tags": ["minimalist", "frugal"], "effects": {}}
                ]
            },
            {
                "id": "consumption_003",
                "category": "consumption",
                "title": "换车诱惑",
                "description": "现在的车还能开，但新能源车补贴很诱人。",
                "tags": ["materialist", "tech_investor"],
                "icon": "🚙",
                "options": [
                    {"text": "换新能源车", "tags": ["tech_investor", "experience_seeker"], "effects": {"cash": -200000, "happiness": 15}},
                    {"text": "等技术更成熟", "tags": ["moderate", "conservative"], "effects": {}},
                    {"text": "旧车挺好", "tags": ["frugal", "minimalist"], "effects": {}}
                ]
            },
            {
                "id": "consumption_004",
                "category": "consumption",
                "title": "装修升级",
                "description": "房子住了几年，想重新装修提升生活品质。",
                "tags": ["materialist", "experience_seeker"],
                "icon": "🏡",
                "options": [
                    {"text": "全屋翻新", "tags": ["materialist"], "effects": {"cash": -150000, "happiness": 20}},
                    {"text": "局部改造", "tags": ["moderate"], "effects": {"cash": -30000, "happiness": 10}},
                    {"text": "维持现状", "tags": ["frugal", "minimalist"], "effects": {}}
                ]
            },
            {
                "id": "consumption_005",
                "category": "consumption",
                "title": "订阅服务泛滥",
                "description": "发现每月各种订阅加起来花了不少钱。",
                "tags": ["frugal", "minimalist"],
                "icon": "💳",
                "options": [
                    {"text": "全部保留，值得", "tags": ["materialist", "experience_seeker"], "effects": {"monthly_expense": 500}},
                    {"text": "精简到必要的", "tags": ["frugal", "moderate"], "effects": {"monthly_expense": -300}},
                    {"text": "全部取消", "tags": ["minimalist", "frugal"], "effects": {"monthly_expense": -500, "happiness": -5}}
                ]
            }
        ]
        
        return base_events


class PersonalizedEventSystem:
    """个性化事件推荐系统"""
    
    def __init__(self, tag_system: UserTagSystem):
        self.tag_system = tag_system
        self.event_pool = self._load_event_pool()
    
    def _load_event_pool(self) -> List[Dict]:
        """加载事件池（模拟1000+事件）"""
        # 这里应该从数据库或文件加载，暂时使用模拟数据
        events = [
            {
                "id": "invest_tech_boom",
                "category": "投资机会",
                "title": "科技股暴涨 🚀",
                "description": "AI概念大热，科技股集体飙升！这波行情你准备如何操作？",
                "tags": ["tech_investor", "growth_investor", "risk_taker"],
                "options": [
                    {"text": "重仓科技股", "impacts": [{"type": "资产", "value": 0.25, "is_pct": True}]},
                    {"text": "适度配置", "impacts": [{"type": "资产", "value": 0.08, "is_pct": True}]},
                    {"text": "不跟风", "impacts": []}
                ],
                "tag_updates": {"重仓科技股": ["tech_investor", "risk_taker"], "适度配置": ["moderate"]}
            },
            {
                "id": "career_promotion",
                "category": "职业事件",
                "title": "晋升机会 💼",
                "description": "公司有一个管理岗位空缺，你的上司问你是否有意愿竞争这个职位。",
                "tags": ["career_focused", "skill_learner"],
                "options": [
                    {"text": "积极争取，全力竞争", "impacts": [{"type": "收入", "value": 3000}]},
                    {"text": "保持现状，专注技术", "impacts": []},
                    {"text": "提出条件，协商薪资", "impacts": [{"type": "收入", "value": 2000}]}
                ],
                "tag_updates": {"积极争取，全力竞争": ["career_focused", "aggressive"]}
            },
            {
                "id": "health_warning",
                "category": "个人事件",
                "title": "健康警报 ⚠️",
                "description": "最近体检发现一些小问题，医生建议你调整作息和运动习惯。",
                "tags": ["health_conscious", "work_life_balance"],
                "options": [
                    {"text": "立即改变，健康优先", "impacts": [{"type": "健康", "value": 15}]},
                    {"text": "稍后调整，工作第一", "impacts": [{"type": "健康", "value": -5}]},
                    {"text": "购买保险，以防万一", "impacts": [{"type": "现金", "value": -500}]}
                ],
                "tag_updates": {"立即改变，健康优先": ["health_conscious"], "购买保险，以防万一": ["conservative"]}
            },
            {
                "id": "macro_rate_cut",
                "category": "宏观事件",
                "title": "央行降息 🏦",
                "description": "央行宣布降息25个基点，市场流动性增加，资产价格波动加大。",
                "tags": ["value_investor", "real_estate"],
                "options": [
                    {"text": "增加股票配置", "impacts": [{"type": "资产", "value": 0.05, "is_pct": True}]},
                    {"text": "增加房产投资", "impacts": []},
                    {"text": "保持现金观望", "impacts": []}
                ],
                "tag_updates": {"增加股票配置": ["growth_investor"], "保持现金观望": ["conservative"]}
            },
            {
                "id": "friend_borrow",
                "category": "社交事件",
                "title": "朋友借钱 👥",
                "description": "一位多年好友向你借一笔钱周转，金额是你现金的20%。",
                "tags": ["generous", "social_active", "cautious_lender"],
                "options": [
                    {"text": "全额借出，信任朋友", "impacts": [{"type": "现金", "value": -0.2, "is_pct": True}]},
                    {"text": "借一半，保护自己", "impacts": [{"type": "现金", "value": -0.1, "is_pct": True}]},
                    {"text": "婉言拒绝，有借无还", "impacts": []}
                ],
                "tag_updates": {"全额借出，信任朋友": ["generous", "social_active"], "婉言拒绝，有借无还": ["cautious_lender"]}
            },
            {
                "id": "startup_opportunity",
                "category": "投资机会",
                "title": "创业邀请 🚀",
                "description": "前同事邀请你加入他的创业公司，需要投入一部分资金并可能辞去现有工作。",
                "tags": ["entrepreneur", "risk_taker", "career_focused"],
                "options": [
                    {"text": "全力投入，辞职创业", "impacts": [{"type": "现金", "value": -50000}, {"type": "幸福", "value": 20}]},
                    {"text": "小额投资，观望为主", "impacts": [{"type": "现金", "value": -10000}]},
                    {"text": "婉拒邀请，稳定优先", "impacts": []}
                ],
                "tag_updates": {"全力投入，辞职创业": ["entrepreneur", "risk_taker"], "婉拒邀请，稳定优先": ["steady_job", "conservative"]}
            },
            {
                "id": "luxury_temptation",
                "category": "个人事件",
                "title": "奢侈品诱惑 🛍️",
                "description": "你心仪已久的限量版商品正在打折，但价格仍然不菲。",
                "tags": ["materialist", "frugal"],
                "options": [
                    {"text": "果断入手，犒劳自己", "impacts": [{"type": "现金", "value": -15000}, {"type": "幸福", "value": 10}]},
                    {"text": "等等看，可能更便宜", "impacts": []},
                    {"text": "理性消费，不为所动", "impacts": [{"type": "幸福", "value": -5}]}
                ],
                "tag_updates": {"果断入手，犒劳自己": ["materialist"], "理性消费，不为所动": ["frugal", "minimalist"]}
            },
            {
                "id": "skill_course",
                "category": "职业事件",
                "title": "进修机会 📚",
                "description": "发现一个高质量的专业课程，可能对职业发展有帮助，但需要投入时间和金钱。",
                "tags": ["skill_learner", "career_focused"],
                "options": [
                    {"text": "报名学习，投资自己", "impacts": [{"type": "现金", "value": -8000}]},
                    {"text": "自学替代，省钱为主", "impacts": []},
                    {"text": "暂时搁置，工作优先", "impacts": []}
                ],
                "tag_updates": {"报名学习，投资自己": ["skill_learner"], "自学替代，省钱为主": ["frugal"]}
            },
            {
                "id": "market_crash",
                "category": "宏观事件",
                "title": "市场暴跌 📉",
                "description": "全球股市突发暴跌，你的投资组合损失惨重。",
                "tags": ["loss_averse", "conservative", "risk_taker"],
                "options": [
                    {"text": "恐慌抛售，止损出局", "impacts": [{"type": "资产", "value": -0.15, "is_pct": True}]},
                    {"text": "逢低加仓，逆势而为", "impacts": []},
                    {"text": "持有不动，等待反弹", "impacts": [{"type": "资产", "value": -0.08, "is_pct": True}]}
                ],
                "tag_updates": {"恐慌抛售，止损出局": ["loss_averse"], "逢低加仓，逆势而为": ["risk_taker", "aggressive"]}
            },
            {
                "id": "social_gathering",
                "category": "社交事件",
                "title": "社交邀约 🎉",
                "description": "朋友邀请你参加一个行业聚会，可能拓展人脉，但需要花费时间和社交精力。",
                "tags": ["social_active", "networker", "introvert"],
                "options": [
                    {"text": "欣然赴约，拓展人脉", "impacts": [{"type": "幸福", "value": 5}]},
                    {"text": "选择性参加，适度社交", "impacts": []},
                    {"text": "婉拒邀请，独处休息", "impacts": [{"type": "精力", "value": 10}]}
                ],
                "tag_updates": {"欣然赴约，拓展人脉": ["social_active", "networker"], "婉拒邀请，独处休息": ["introvert"]}
            }
        ]
        return events
    
    def get_personalized_events(self, session_id: str, count: int = 5) -> List[Dict]:
        """获取个性化推荐的事件"""
        user_tags = self.tag_system.get_user_tags(session_id)
        user_tag_ids = {t["id"]: t["weight"] for t in user_tags}
        
        # 计算每个事件的匹配分数
        scored_events = []
        for event in self.event_pool:
            score = self._calculate_match_score(event, user_tag_ids)
            event_copy = event.copy()
            event_copy["matchScore"] = score
            scored_events.append(event_copy)
        
        # 按分数排序并选择
        scored_events.sort(key=lambda x: x["matchScore"], reverse=True)
        
        # 混合高分和随机事件，避免过度推荐
        top_events = scored_events[:count * 2]
        random.shuffle(top_events)
        return top_events[:count]
    
    def _calculate_match_score(self, event: Dict, user_tags: Dict[str, float]) -> float:
        """计算事件与用户标签的匹配分数"""
        event_tags = event.get("tags", [])
        if not event_tags:
            return 0.5  # 无标签事件给基础分
        
        total_score = 0
        matched_count = 0
        
        for tag_id in event_tags:
            if tag_id in user_tags:
                total_score += user_tags[tag_id]
                matched_count += 1
        
        if matched_count == 0:
            return 0.3  # 无匹配给低分
        
        # 平均分 + 匹配率加成
        avg_score = total_score / matched_count
        match_rate = matched_count / len(event_tags)
        
        return avg_score * 0.7 + match_rate * 0.3
    
    def process_choice(self, session_id: str, event_id: str, option_index: int) -> Dict:
        """处理用户的事件选择"""
        # 找到事件
        event = None
        for e in self.event_pool:
            if e["id"] == event_id:
                event = e
                break
        
        if not event or option_index >= len(event["options"]):
            return {"success": False, "message": "事件或选项不存在"}
        
        option = event["options"][option_index]
        option_text = option["text"]
        
        # 更新用户标签
        new_tags = []
        tag_updates = event.get("tag_updates", {})
        if option_text in tag_updates:
            for tag_id in tag_updates[option_text]:
                if self.tag_system.add_or_update_tag(session_id, tag_id, 0.1, "event", f"事件选择: {event['title']}"):
                    new_tags.append(PRESET_TAGS[tag_id].name if tag_id in PRESET_TAGS else tag_id)
        
        # 返回结果
        return {
            "success": True,
            "message": f"你选择了「{option_text}」",
            "impacts": option.get("impacts", []),
            "newTags": new_tags
        }
