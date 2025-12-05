"""
个性化事件生成器 - EchoPolis
基于真实新闻 + 用户画像（MBTI、职业、风险偏好、标签）生成定制化事件
"""
import re
import json
import time
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# MBTI 类型特征映射
MBTI_TRAITS = {
    # 分析师型
    "INTJ": {
        "name": "建筑师",
        "investment_style": "战略型",
        "risk_tendency": "calculated_risk",  # 计算过的风险
        "decision_speed": "slow",
        "focus": ["长期规划", "系统分析", "独立判断"],
        "bias": ["过度自信", "忽视情绪因素"],
        "event_angles": ["战略布局", "逻辑分析", "长期视角"]
    },
    "INTP": {
        "name": "逻辑学家", 
        "investment_style": "研究型",
        "risk_tendency": "moderate",
        "decision_speed": "slow",
        "focus": ["深度研究", "模式识别", "创新机会"],
        "bias": ["分析瘫痪", "犹豫不决"],
        "event_angles": ["技术分析", "理论验证", "创新视角"]
    },
    "ENTJ": {
        "name": "指挥官",
        "investment_style": "主导型",
        "risk_tendency": "high_risk",
        "decision_speed": "fast",
        "focus": ["效率优先", "掌控全局", "快速决策"],
        "bias": ["过于激进", "不听建议"],
        "event_angles": ["主动出击", "领导市场", "效率导向"]
    },
    "ENTP": {
        "name": "辩论家",
        "investment_style": "机会型",
        "risk_tendency": "high_risk", 
        "decision_speed": "fast",
        "focus": ["创新投资", "逆向思维", "多元尝试"],
        "bias": ["缺乏耐心", "频繁换仓"],
        "event_angles": ["逆向投资", "创新机会", "挑战传统"]
    },
    # 外交官型
    "INFJ": {
        "name": "提倡者",
        "investment_style": "价值型",
        "risk_tendency": "low_risk",
        "decision_speed": "slow",
        "focus": ["社会责任", "长期价值", "直觉判断"],
        "bias": ["理想主义", "错过时机"],
        "event_angles": ["ESG投资", "社会影响", "价值认同"]
    },
    "INFP": {
        "name": "调停者",
        "investment_style": "理想型",
        "risk_tendency": "low_risk",
        "decision_speed": "slow", 
        "focus": ["价值观投资", "创意产业", "情感连接"],
        "bias": ["情绪化决策", "避免冲突"],
        "event_angles": ["情感共鸣", "理想追求", "创意投资"]
    },
    "ENFJ": {
        "name": "主人公",
        "investment_style": "关系型",
        "risk_tendency": "moderate",
        "decision_speed": "medium",
        "focus": ["团队协作", "社交投资", "影响力"],
        "bias": ["过度关注他人", "决策被影响"],
        "event_angles": ["人脉投资", "社会责任", "团队视角"]
    },
    "ENFP": {
        "name": "竞选者",
        "investment_style": "灵感型",
        "risk_tendency": "moderate",
        "decision_speed": "fast",
        "focus": ["新兴趋势", "创新领域", "热情驱动"],
        "bias": ["三分钟热度", "缺乏纪律"],
        "event_angles": ["趋势追踪", "热点捕捉", "灵感投资"]
    },
    # 守护者型
    "ISTJ": {
        "name": "物流师",
        "investment_style": "保守型",
        "risk_tendency": "low_risk",
        "decision_speed": "slow",
        "focus": ["稳定收益", "规则遵循", "历史验证"],
        "bias": ["过于保守", "错失机会"],
        "event_angles": ["稳健配置", "历史参考", "规则遵循"]
    },
    "ISFJ": {
        "name": "守卫者",
        "investment_style": "保护型",
        "risk_tendency": "low_risk",
        "decision_speed": "slow",
        "focus": ["家庭保障", "安全第一", "传统投资"],
        "bias": ["过度担忧", "缺乏冒险"],
        "event_angles": ["家庭保障", "安全优先", "传统智慧"]
    },
    "ESTJ": {
        "name": "总经理",
        "investment_style": "执行型",
        "risk_tendency": "moderate",
        "decision_speed": "fast",
        "focus": ["执行力强", "目标导向", "组织管理"],
        "bias": ["过于刻板", "忽视创新"],
        "event_angles": ["执行效率", "目标达成", "管理视角"]
    },
    "ESFJ": {
        "name": "执政官",
        "investment_style": "社交型",
        "risk_tendency": "low_risk",
        "decision_speed": "medium",
        "focus": ["群体认同", "社会主流", "和谐关系"],
        "bias": ["从众心理", "缺乏独立判断"],
        "event_angles": ["主流选择", "社会认同", "和谐投资"]
    },
    # 探险家型
    "ISTP": {
        "name": "鉴赏家",
        "investment_style": "技术型",
        "risk_tendency": "calculated_risk",
        "decision_speed": "medium",
        "focus": ["技术分析", "实用主义", "冷静观察"],
        "bias": ["过于冷漠", "缺乏长期规划"],
        "event_angles": ["技术面", "实用分析", "冷静判断"]
    },
    "ISFP": {
        "name": "探险家",
        "investment_style": "感性型",
        "risk_tendency": "moderate",
        "decision_speed": "medium",
        "focus": ["艺术审美", "当下体验", "灵活适应"],
        "bias": ["冲动决策", "缺乏计划"],
        "event_angles": ["生活投资", "体验优先", "灵活应对"]
    },
    "ESTP": {
        "name": "企业家",
        "investment_style": "行动型",
        "risk_tendency": "high_risk",
        "decision_speed": "fast",
        "focus": ["快速行动", "短期机会", "实战经验"],
        "bias": ["冲动交易", "忽视风险"],
        "event_angles": ["快速行动", "短线机会", "实战出击"]
    },
    "ESFP": {
        "name": "表演者",
        "investment_style": "享乐型",
        "risk_tendency": "moderate",
        "decision_speed": "fast",
        "focus": ["即时满足", "社交投资", "乐观态度"],
        "bias": ["过度乐观", "缺乏纪律"],
        "event_angles": ["享受当下", "乐观视角", "社交投资"]
    }
}

# 职业类型对事件的影响
CAREER_INFLUENCE = {
    "tech": {
        "name": "科技行业",
        "sensitive_topics": ["AI", "芯片", "互联网", "软件", "云计算"],
        "investment_advantage": ["tech_growth", "innovation"],
        "risk_awareness": ["技术迭代风险", "竞争激烈"],
        "special_angles": ["内幕视角", "技术趋势判断", "行业前沿"]
    },
    "finance": {
        "name": "金融行业",
        "sensitive_topics": ["利率", "央行", "股市", "债券", "汇率"],
        "investment_advantage": ["market_timing", "risk_assessment"],
        "risk_awareness": ["市场波动", "监管变化"],
        "special_angles": ["专业分析", "市场敏感度", "政策解读"]
    },
    "healthcare": {
        "name": "医疗健康",
        "sensitive_topics": ["医药", "生物科技", "医疗器械", "养老"],
        "investment_advantage": ["healthcare_insight", "demographic_trend"],
        "risk_awareness": ["研发风险", "政策不确定性"],
        "special_angles": ["行业专业度", "人口趋势", "医疗创新"]
    },
    "real_estate": {
        "name": "房地产",
        "sensitive_topics": ["房价", "地产", "城市化", "租赁"],
        "investment_advantage": ["property_insight", "location_judgment"],
        "risk_awareness": ["政策调控", "市场周期"],
        "special_angles": ["地产周期", "区域判断", "政策敏感"]
    },
    "education": {
        "name": "教育行业",
        "sensitive_topics": ["教育政策", "职业培训", "在线教育"],
        "investment_advantage": ["long_term_thinking", "knowledge_economy"],
        "risk_awareness": ["政策风险", "行业变革"],
        "special_angles": ["教育趋势", "人力资本", "知识经济"]
    },
    "manufacturing": {
        "name": "制造业",
        "sensitive_topics": ["供应链", "原材料", "工业4.0", "出口"],
        "investment_advantage": ["industry_cycle", "supply_chain"],
        "risk_awareness": ["经济周期", "成本压力"],
        "special_angles": ["产业链视角", "周期判断", "成本分析"]
    },
    "default": {
        "name": "普通职业",
        "sensitive_topics": [],
        "investment_advantage": [],
        "risk_awareness": ["普遍市场风险"],
        "special_angles": ["大众视角", "常识判断"]
    }
}


@dataclass
class UserProfile:
    """用户画像"""
    session_id: str
    name: str = "玩家"
    mbti: str = "INTJ"
    career: str = "default"
    career_title: str = ""
    cash: int = 100000
    risk_preference: str = "moderate"  # low/moderate/high
    investment_experience: str = "beginner"  # beginner/intermediate/expert
    tags: List[str] = None
    tag_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.tag_weights is None:
            self.tag_weights = {}


@dataclass
class PersonalizedEvent:
    """个性化事件"""
    id: str
    title: str
    description: str
    category: str
    tags: List[str]
    options: List[Dict]
    source_news: str
    
    # 个性化字段
    personalized_intro: str  # 针对用户的开场白
    ai_analysis: str  # 基于用户画像的分析
    mbti_hint: str  # MBTI相关提示
    career_relevance: str  # 职业相关性说明
    risk_assessment: str  # 风险评估
    
    match_score: float = 0.0
    news_id: str = ""
    is_personalized: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)


class PersonalizedEventGenerator:
    """个性化事件生成器"""
    
    def __init__(self):
        self.mbti_traits = MBTI_TRAITS
        self.career_influence = CAREER_INFLUENCE
    
    def get_user_profile(self, session_id: str) -> UserProfile:
        """从数据库获取用户完整画像"""
        try:
            from core.database.database import Database
            db = Database()
            
            profile = UserProfile(session_id=session_id)
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # 获取基本信息
                cursor.execute('''
                    SELECT name, mbti, credits FROM users WHERE session_id = ?
                ''', (session_id,))
                row = cursor.fetchone()
                if row:
                    profile.name = row[0] or "玩家"
                    profile.mbti = row[1] or "INTJ"
                    profile.cash = row[2] or 100000
                
                # 获取职业信息
                cursor.execute('''
                    SELECT job_id, job_title FROM player_careers 
                    WHERE session_id = ? AND is_active = 1
                ''', (session_id,))
                row = cursor.fetchone()
                if row:
                    job_id = row[0] or ""
                    profile.career_title = row[1] or ""
                    # 映射职业类型
                    if any(k in job_id.lower() for k in ['tech', 'software', 'engineer', 'developer']):
                        profile.career = "tech"
                    elif any(k in job_id.lower() for k in ['finance', 'bank', 'invest', 'analyst']):
                        profile.career = "finance"
                    elif any(k in job_id.lower() for k in ['doctor', 'nurse', 'medical', 'health']):
                        profile.career = "healthcare"
                    elif any(k in job_id.lower() for k in ['real_estate', 'property']):
                        profile.career = "real_estate"
                    else:
                        profile.career = "default"
                
                # 获取用户标签
                cursor.execute('''
                    SELECT tag_id, weight FROM user_tags 
                    WHERE session_id = ? AND weight > 0.3
                    ORDER BY weight DESC
                ''', (session_id,))
                for row in cursor.fetchall():
                    profile.tags.append(row[0])
                    profile.tag_weights[row[0]] = row[1]
                
                # 根据标签推断风险偏好
                if 'risk_taker' in profile.tags or 'aggressive' in profile.tags:
                    profile.risk_preference = "high"
                elif 'conservative' in profile.tags or 'loss_averse' in profile.tags:
                    profile.risk_preference = "low"
                else:
                    profile.risk_preference = "moderate"
                
                # 根据投资次数推断经验
                cursor.execute('''
                    SELECT COUNT(*) FROM investments WHERE session_id = ?
                ''', (session_id,))
                inv_count = cursor.fetchone()[0] or 0
                if inv_count > 20:
                    profile.investment_experience = "expert"
                elif inv_count > 5:
                    profile.investment_experience = "intermediate"
                else:
                    profile.investment_experience = "beginner"
            
            return profile
            
        except Exception as e:
            print(f"[PersonalizedEvent] 获取用户画像失败: {e}")
            return UserProfile(session_id=session_id)
    
    def generate_personalized_events(self, 
                                     news_events: List[Dict], 
                                     session_id: str) -> List[Dict]:
        """
        将通用新闻事件转换为个性化事件
        
        Args:
            news_events: 从新闻生成的基础事件列表
            session_id: 用户session
            
        Returns:
            个性化后的事件列表
        """
        # 获取用户画像
        profile = self.get_user_profile(session_id)
        mbti_info = self.mbti_traits.get(profile.mbti, self.mbti_traits["INTJ"])
        career_info = self.career_influence.get(profile.career, self.career_influence["default"])
        
        personalized_events = []
        
        for event in news_events:
            try:
                personalized = self._personalize_event(event, profile, mbti_info, career_info)
                personalized_events.append(personalized)
            except Exception as e:
                print(f"[PersonalizedEvent] 事件个性化失败: {e}")
                # 保留原事件
                event['is_personalized'] = False
                personalized_events.append(event)
        
        # 按匹配度排序
        personalized_events.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return personalized_events
    
    def _personalize_event(self, 
                          event: Dict, 
                          profile: UserProfile,
                          mbti_info: Dict,
                          career_info: Dict) -> Dict:
        """将单个事件个性化"""
        
        # 1. 计算匹配度
        match_score = self._calculate_match_score(event, profile, mbti_info, career_info)
        
        # 2. 生成个性化开场白
        personalized_intro = self._generate_intro(event, profile, mbti_info)
        
        # 3. 生成基于画像的AI分析
        ai_analysis = self._generate_ai_analysis(event, profile, mbti_info, career_info)
        
        # 4. 生成MBTI提示
        mbti_hint = self._generate_mbti_hint(event, profile, mbti_info)
        
        # 5. 生成职业相关性
        career_relevance = self._generate_career_relevance(event, profile, career_info)
        
        # 6. 生成风险评估
        risk_assessment = self._generate_risk_assessment(event, profile)
        
        # 7. 个性化选项
        personalized_options = self._personalize_options(
            event.get('options', []), 
            profile, 
            mbti_info
        )
        
        # 构建个性化事件
        return {
            **event,
            'match_score': match_score,
            'personalized_intro': personalized_intro,
            'ai_analysis': ai_analysis,
            'mbti_hint': mbti_hint,
            'career_relevance': career_relevance,
            'risk_assessment': risk_assessment,
            'options': personalized_options,
            'is_personalized': True,
            'user_mbti': profile.mbti,
            'user_career': profile.career_title or career_info['name']
        }
    
    def _calculate_match_score(self, 
                               event: Dict, 
                               profile: UserProfile,
                               mbti_info: Dict,
                               career_info: Dict) -> float:
        """计算事件与用户的匹配度"""
        score = 0.5  # 基础分
        
        event_text = f"{event.get('title', '')} {event.get('description', '')} {event.get('source_news', '')}".lower()
        event_tags = event.get('tags', [])
        
        # 1. 标签匹配 (+0.1 each, max 0.3)
        matched_tags = len(set(profile.tags) & set(event_tags))
        score += min(matched_tags * 0.1, 0.3)
        
        # 2. 职业相关性 (+0.15)
        for topic in career_info.get('sensitive_topics', []):
            if topic.lower() in event_text:
                score += 0.15
                break
        
        # 3. MBTI投资风格匹配 (+0.1)
        if mbti_info['risk_tendency'] == 'high_risk' and event.get('category') in ['crypto', 'tech']:
            score += 0.1
        elif mbti_info['risk_tendency'] == 'low_risk' and event.get('category') in ['policy', 'macro']:
            score += 0.1
        
        # 4. 用户标签权重加成
        for tag in event_tags:
            if tag in profile.tag_weights:
                score += profile.tag_weights[tag] * 0.1
        
        return min(score, 1.0)
    
    def _generate_intro(self, event: Dict, profile: UserProfile, mbti_info: Dict) -> str:
        """生成个性化开场白"""
        intros = {
            "INTJ": f"👁️ {profile.name}，作为战略家，这条消息可能符合你的长期布局...",
            "INTP": f"🔬 {profile.name}，这里有一个值得深度分析的信息...",
            "ENTJ": f"⚡ {profile.name}，市场又有新动向，是时候做决策了...",
            "ENTP": f"💡 {profile.name}，看看这个逆向思维的机会...",
            "INFJ": f"🌱 {profile.name}，这条消息背后可能有更深的价值含义...",
            "INFP": f"✨ {profile.name}，这个机会与你的价值观可能产生共鸣...",
            "ENFJ": f"🤝 {profile.name}，这个消息可能影响到你关心的人和事...",
            "ENFP": f"🎯 {profile.name}，新的趋势来了，你的直觉怎么说？",
            "ISTJ": f"📊 {profile.name}，让我们用数据和历史来分析这条消息...",
            "ISFJ": f"🛡️ {profile.name}，这里有一条需要谨慎考虑的信息...",
            "ESTJ": f"📋 {profile.name}，新的市场信息，需要你快速评估...",
            "ESFJ": f"👥 {profile.name}，大家都在关注这条消息...",
            "ISTP": f"🔧 {profile.name}，从技术面看看这条消息...",
            "ISFP": f"🎨 {profile.name}，这可能影响你的生活规划...",
            "ESTP": f"🏃 {profile.name}，短线机会来了，快速判断！",
            "ESFP": f"🎉 {profile.name}，市场有新动静，看看热点！",
        }
        return intros.get(profile.mbti, f"📰 {profile.name}，这里有一条市场消息...")
    
    def _generate_ai_analysis(self, 
                              event: Dict, 
                              profile: UserProfile,
                              mbti_info: Dict,
                              career_info: Dict) -> str:
        """生成基于用户画像的AI分析"""
        analysis_parts = []
        
        # 基于MBTI的分析角度
        angles = mbti_info.get('event_angles', [])
        if angles:
            angle = random.choice(angles)
            analysis_parts.append(f"从{angle}角度看")
        
        # 基于职业的分析
        if profile.career != "default":
            advantages = career_info.get('investment_advantage', [])
            if advantages:
                analysis_parts.append(f"作为{career_info['name']}从业者，你在{random.choice(advantages)}方面有优势")
        
        # 风险评估
        risk = mbti_info.get('risk_tendency', 'moderate')
        if risk == 'high_risk':
            analysis_parts.append("这类机会可能符合你的激进风格")
        elif risk == 'low_risk':
            analysis_parts.append("建议你谨慎评估风险后再做决定")
        else:
            analysis_parts.append("可以适度参与，但注意仓位控制")
        
        # 潜在偏见提醒
        biases = mbti_info.get('bias', [])
        if biases:
            analysis_parts.append(f"⚠️ 提醒：注意避免{random.choice(biases)}")
        
        return "。".join(analysis_parts) + "。"
    
    def _generate_mbti_hint(self, event: Dict, profile: UserProfile, mbti_info: Dict) -> str:
        """生成MBTI相关提示"""
        style = mbti_info.get('investment_style', '稳健型')
        speed = mbti_info.get('decision_speed', 'medium')
        
        speed_hint = {
            'fast': '你倾向于快速决策，但记得考虑长期影响',
            'slow': '你习惯深思熟虑，但别错过关键时机',
            'medium': '保持你的平衡决策风格'
        }
        
        return f"💡 {mbti_info['name']}({profile.mbti}) - {style}投资者: {speed_hint.get(speed, '')}"
    
    def _generate_career_relevance(self, event: Dict, profile: UserProfile, career_info: Dict) -> str:
        """生成职业相关性说明"""
        if profile.career == "default":
            return ""
        
        event_text = f"{event.get('title', '')} {event.get('source_news', '')}".lower()
        
        # 检查是否涉及用户职业领域
        for topic in career_info.get('sensitive_topics', []):
            if topic.lower() in event_text:
                special_angles = career_info.get('special_angles', [])
                angle = random.choice(special_angles) if special_angles else "专业视角"
                return f"🎯 职业优势: 作为{career_info['name']}从业者，你可以用{angle}来判断这条消息"
        
        return f"💼 这条消息与{career_info['name']}关联度较低，建议多参考专业意见"
    
    def _generate_risk_assessment(self, event: Dict, profile: UserProfile) -> str:
        """生成风险评估"""
        category = event.get('category', 'macro')
        
        risk_levels = {
            'crypto': ('🔴 高风险', '加密货币波动剧烈，适合风险承受能力强的投资者'),
            'tech': ('🟠 中高风险', '科技股成长性强但波动较大'),
            'stock': ('🟡 中等风险', '个股投资需要仔细研究基本面'),
            'policy': ('🟢 低风险', '政策类信息更适合作为配置参考'),
            'macro': ('🟢 低风险', '宏观信息帮助理解大趋势'),
            'merger': ('🟠 中高风险', '并购事件结果不确定性高'),
            'global': ('🟡 中等风险', '全球事件影响复杂'),
        }
        
        level, desc = risk_levels.get(category, ('🟡 中等风险', '请谨慎评估'))
        
        # 根据用户风险偏好调整建议
        if profile.risk_preference == 'low' and level.startswith('🔴'):
            desc += " ⚠️ 这可能超出你的风险承受范围"
        elif profile.risk_preference == 'high' and level.startswith('🟢'):
            desc += " 💡 你可能觉得这不够刺激，但稳健也是一种智慧"
        
        return f"{level}: {desc}"
    
    def _personalize_options(self, 
                            options: List[Dict], 
                            profile: UserProfile,
                            mbti_info: Dict) -> List[Dict]:
        """个性化选项"""
        if not options:
            return options
        
        personalized = []
        
        for i, opt in enumerate(options):
            new_opt = opt.copy()
            opt_tags = opt.get('tags', [])
            
            # 计算选项与用户标签的匹配度
            match_count = len(set(profile.tags) & set(opt_tags))
            
            # 添加推荐标记
            if match_count > 0:
                new_opt['recommended'] = True
                new_opt['match_reason'] = f"符合你的 {', '.join(set(profile.tags) & set(opt_tags))} 特质"
            else:
                new_opt['recommended'] = False
            
            # 根据MBTI风格给出提示
            risk = mbti_info.get('risk_tendency', 'moderate')
            if 'aggressive' in opt_tags or 'risk_taker' in opt_tags:
                if risk == 'high_risk':
                    new_opt['mbti_fit'] = '⭐ 符合你的风格'
                elif risk == 'low_risk':
                    new_opt['mbti_fit'] = '⚠️ 可能超出你的舒适区'
            elif 'conservative' in opt_tags:
                if risk == 'low_risk':
                    new_opt['mbti_fit'] = '⭐ 符合你的风格'
                elif risk == 'high_risk':
                    new_opt['mbti_fit'] = '💡 尝试一下稳健策略?'
            
            personalized.append(new_opt)
        
        return personalized


# 全局实例
personalized_event_generator = PersonalizedEventGenerator()
