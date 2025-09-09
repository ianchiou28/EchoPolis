"""
AI化身决策引擎 - "行为皮层"
实现复杂的多因子决策逻辑
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
import random
from datetime import datetime

from ai_models.personality.big_five_model import PersonalityProfile, PersonalityTraits


class DecisionType(Enum):
    """决策类型"""
    INVESTMENT = "investment"
    CONSUMPTION = "consumption"
    CAREER = "career"
    SOCIAL = "social"
    EMERGENCY = "emergency"


class InterventionType(Enum):
    """干预类型"""
    INSPIRATIONAL = "inspirational"  # 启发式
    ADVISORY = "advisory"  # 建议式
    DIRECTIVE = "directive"  # 指令式
    EMOTIONAL = "emotional"  # 鼓励/警告式


@dataclass
class AgentState:
    """AI化身状态"""
    # 核心属性
    health: float = 100.0  # 健康值 0-100
    energy: float = 100.0  # 精力值 0-100
    credit_score: int = 500  # 信用分 300-850
    happiness: float = 50.0  # 幸福感 0-100
    stress: float = 0.0  # 压力值 0-100
    
    # 财务状态
    credit_points: float = 50000.0  # 信用点
    insight_crystals: int = 0  # 启示结晶
    net_worth: float = 50000.0  # 净资产
    monthly_income: float = 5000.0  # 月收入
    monthly_expenses: float = 3000.0  # 月支出
    
    # 社交状态
    relationship_status: str = "single"  # 感情状态
    social_connections: int = 10  # 社交连接数
    
    # 职业状态
    job_title: str = "entry_level"  # 职位
    job_satisfaction: float = 50.0  # 工作满意度
    
    # 学习状态
    fq_level: int = 1  # 金融素养等级
    experience_points: int = 0  # 经验值
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "health": self.health,
            "energy": self.energy,
            "credit_score": self.credit_score,
            "happiness": self.happiness,
            "stress": self.stress,
            "credit_points": self.credit_points,
            "insight_crystals": self.insight_crystals,
            "net_worth": self.net_worth,
            "monthly_income": self.monthly_income,
            "monthly_expenses": self.monthly_expenses,
            "relationship_status": self.relationship_status,
            "social_connections": self.social_connections,
            "job_title": self.job_title,
            "job_satisfaction": self.job_satisfaction,
            "fq_level": self.fq_level,
            "experience_points": self.experience_points
        }


@dataclass
class DecisionContext:
    """决策上下文"""
    decision_type: DecisionType
    options: List[Dict[str, Any]]
    market_conditions: Dict[str, float]
    personal_goals: List[str]
    time_pressure: float  # 0-1, 1表示非常紧急
    social_influence: float  # 0-1, 社交影响程度
    
    
@dataclass
class PlayerIntervention:
    """玩家干预"""
    intervention_type: InterventionType
    message: str
    timestamp: datetime
    trust_modifier: float = 0.0  # 对信任度的影响


class AgentBrain:
    """AI化身大脑 - 核心决策引擎"""
    
    def __init__(self, personality: PersonalityProfile, traits: List[str]):
        self.personality = personality
        self.traits = traits
        self.trait_effects = PersonalityTraits.get_trait_effects(traits)
        self.state = AgentState()
        self.trust_level = 50.0  # 对玩家的信任度
        self.decision_history = []
        self.intervention_history = []
        
    def make_decision(self, context: DecisionContext, 
                     player_intervention: Optional[PlayerIntervention] = None) -> Dict[str, Any]:
        """核心决策方法"""
        
        # 1. 计算各选项的基础得分
        option_scores = []
        for option in context.options:
            score = self._calculate_base_score(option, context)
            option_scores.append(score)
        
        # 2. 应用人格特质影响
        option_scores = self._apply_personality_effects(option_scores, context)
        
        # 3. 应用当前状态影响
        option_scores = self._apply_state_effects(option_scores, context)
        
        # 4. 处理玩家干预
        if player_intervention:
            option_scores = self._apply_player_intervention(
                option_scores, context, player_intervention
            )
        
        # 5. 添加随机扰动
        option_scores = self._add_random_noise(option_scores)
        
        # 6. 选择最高得分的选项
        best_option_idx = np.argmax(option_scores)
        chosen_option = context.options[best_option_idx]
        
        # 7. 生成决策解释
        explanation = self._generate_explanation(
            chosen_option, context, player_intervention
        )
        
        # 8. 记录决策
        decision_record = {
            "timestamp": datetime.now(),
            "context": context,
            "chosen_option": chosen_option,
            "option_scores": option_scores,
            "explanation": explanation,
            "player_intervention": player_intervention
        }
        self.decision_history.append(decision_record)
        
        return {
            "chosen_option": chosen_option,
            "confidence": option_scores[best_option_idx],
            "explanation": explanation,
            "internal_monologue": self._generate_internal_monologue(
                chosen_option, context, player_intervention
            )
        }
    
    def _calculate_base_score(self, option: Dict[str, Any], 
                            context: DecisionContext) -> float:
        """计算选项的基础得分"""
        score = 0.0
        
        # 基于选项的基础属性
        if "expected_return" in option:
            score += option["expected_return"] * 0.3
        
        if "risk_level" in option:
            # 风险偏好基于人格特质
            risk_preference = self._get_risk_preference()
            if risk_preference == "high":
                score += (option["risk_level"] - 0.5) * 0.2
            else:
                score -= (option["risk_level"] - 0.5) * 0.2
        
        if "time_commitment" in option:
            # 时间承诺偏好基于责任心
            time_preference = self.personality.conscientiousness / 100
            score += (1 - abs(option["time_commitment"] - time_preference)) * 0.1
        
        return score
    
    def _apply_personality_effects(self, scores: List[float], 
                                 context: DecisionContext) -> List[float]:
        """应用人格特质效应"""
        modified_scores = scores.copy()
        
        for i, option in enumerate(context.options):
            # 开放性影响
            if "innovation_level" in option:
                openness_effect = (self.personality.openness / 100 - 0.5) * 0.3
                modified_scores[i] += option["innovation_level"] * openness_effect
            
            # 责任心影响
            if "planning_required" in option:
                conscientiousness_effect = self.personality.conscientiousness / 100
                modified_scores[i] += option["planning_required"] * conscientiousness_effect * 0.2
            
            # 外倾性影响
            if "social_component" in option:
                extraversion_effect = self.personality.extraversion / 100
                modified_scores[i] += option["social_component"] * extraversion_effect * 0.15
        
        return modified_scores
    
    def _apply_state_effects(self, scores: List[float], 
                           context: DecisionContext) -> List[float]:
        """应用当前状态效应"""
        modified_scores = scores.copy()
        
        # 压力影响决策质量
        stress_penalty = self.state.stress / 100 * 0.2
        modified_scores = [score - stress_penalty for score in modified_scores]
        
        # 幸福感影响风险偏好
        if self.state.happiness < 40:
            # 低幸福感时可能做出冲动决策
            for i, option in enumerate(context.options):
                if option.get("immediate_gratification", False):
                    modified_scores[i] += 0.3
        
        # 健康状况影响
        if self.state.health < 50:
            # 健康不佳时更保守
            for i, option in enumerate(context.options):
                if option.get("risk_level", 0) > 0.7:
                    modified_scores[i] -= 0.2
        
        return modified_scores
    
    def _apply_player_intervention(self, scores: List[float], 
                                 context: DecisionContext,
                                 intervention: PlayerIntervention) -> List[float]:
        """应用玩家干预效应"""
        modified_scores = scores.copy()
        
        # 信任度影响干预效果
        trust_multiplier = self.trust_level / 100
        
        # 根据干预类型调整效果
        intervention_strength = {
            InterventionType.INSPIRATIONAL: 0.1,
            InterventionType.ADVISORY: 0.2,
            InterventionType.DIRECTIVE: 0.4,
            InterventionType.EMOTIONAL: 0.15
        }
        
        base_effect = intervention_strength[intervention.intervention_type] * trust_multiplier
        
        # 简化的NLP处理 - 实际应用中需要更复杂的语言理解
        message_sentiment = self._analyze_intervention_sentiment(intervention.message)
        
        # 根据消息内容调整特定选项的得分
        # 这里需要更复杂的逻辑来匹配消息内容和选项
        for i, option in enumerate(context.options):
            if self._message_supports_option(intervention.message, option):
                modified_scores[i] += base_effect
            elif self._message_opposes_option(intervention.message, option):
                modified_scores[i] -= base_effect
        
        # 更新信任度
        self._update_trust_level(intervention)
        
        return modified_scores
    
    def _add_random_noise(self, scores: List[float]) -> List[float]:
        """添加随机扰动模拟现实中的不确定性"""
        noise_level = 0.1  # 10%的随机性
        return [score + random.gauss(0, noise_level) for score in scores]
    
    def _generate_explanation(self, chosen_option: Dict[str, Any],
                            context: DecisionContext,
                            intervention: Optional[PlayerIntervention]) -> str:
        """生成决策解释"""
        explanations = []
        
        # 基于人格特质的解释
        if "严格自律" in self.traits:
            explanations.append("基于我的谨慎性格")
        if "创新探索者" in self.traits:
            explanations.append("这符合我探索新机会的天性")
        
        # 基于当前状态的解释
        if self.state.stress > 70:
            explanations.append("当前压力较大，需要稳妥的选择")
        if self.state.happiness < 30:
            explanations.append("希望这能改善我的心情")
        
        # 基于玩家干预的解释
        if intervention and self.trust_level > 60:
            explanations.append("考虑了你的建议")
        elif intervention and self.trust_level < 40:
            explanations.append("虽然听到了你的建议，但我有不同的看法")
        
        return "我选择这个方案，因为" + "，".join(explanations) + "。"
    
    def _generate_internal_monologue(self, chosen_option: Dict[str, Any],
                                   context: DecisionContext,
                                   intervention: Optional[PlayerIntervention]) -> str:
        """生成内心独白"""
        monologue_parts = []
        
        # 决策过程的内心活动
        if context.decision_type == DecisionType.INVESTMENT:
            monologue_parts.append("让我仔细考虑这个投资机会...")
        
        # 人格特质的内心声音
        if "分析瘫痪" in self.traits:
            monologue_parts.append("我需要更多信息才能确定...")
        if "天生赌徒" in self.traits:
            monologue_parts.append("这看起来很刺激，值得一试！")
        
        # 对玩家干预的内心反应
        if intervention:
            if self.trust_level > 70:
                monologue_parts.append(f"'{intervention.message}' - 这个建议很有道理")
            elif self.trust_level < 30:
                monologue_parts.append(f"'{intervention.message}' - 我不太确定这个建议是否适合我")
        
        return " ".join(monologue_parts)
    
    def _get_risk_preference(self) -> str:
        """获取风险偏好"""
        risk_score = (
            self.personality.openness * 0.3 +
            (100 - self.personality.neuroticism) * 0.4 +
            (100 - self.personality.conscientiousness) * 0.3
        )
        
        if risk_score > 70:
            return "high"
        elif risk_score < 30:
            return "low"
        else:
            return "medium"
    
    def _analyze_intervention_sentiment(self, message: str) -> float:
        """分析干预消息的情感倾向 (简化版)"""
        positive_words = ["好", "棒", "推荐", "建议", "应该", "值得"]
        negative_words = ["不", "别", "避免", "危险", "风险", "不要"]
        
        positive_count = sum(1 for word in positive_words if word in message)
        negative_count = sum(1 for word in negative_words if word in message)
        
        return (positive_count - negative_count) / max(len(message.split()), 1)
    
    def _message_supports_option(self, message: str, option: Dict[str, Any]) -> bool:
        """判断消息是否支持某个选项 (简化版)"""
        # 实际应用中需要更复杂的NLP处理
        option_keywords = option.get("keywords", [])
        return any(keyword in message for keyword in option_keywords)
    
    def _message_opposes_option(self, message: str, option: Dict[str, Any]) -> bool:
        """判断消息是否反对某个选项 (简化版)"""
        negative_indicators = ["不要", "别", "避免", "不建议"]
        option_keywords = option.get("keywords", [])
        
        has_negative = any(neg in message for neg in negative_indicators)
        mentions_option = any(keyword in message for keyword in option_keywords)
        
        return has_negative and mentions_option
    
    def _update_trust_level(self, intervention: PlayerIntervention):
        """更新对玩家的信任度"""
        # 基于干预类型和历史表现调整信任度
        trust_change = intervention.trust_modifier
        
        # 考虑人格特质对信任的影响
        if self.personality.agreeableness > 70:
            trust_change *= 1.2  # 更容易信任
        if self.personality.neuroticism > 70:
            trust_change *= 0.8  # 更难建立信任
        
        self.trust_level = max(0, min(100, self.trust_level + trust_change))
    
    def update_state(self, state_changes: Dict[str, float]):
        """更新化身状态"""
        for attribute, change in state_changes.items():
            if hasattr(self.state, attribute):
                current_value = getattr(self.state, attribute)
                new_value = current_value + change
                
                # 应用边界限制
                if attribute in ["health", "energy", "happiness"]:
                    new_value = max(0, min(100, new_value))
                elif attribute == "stress":
                    new_value = max(0, min(100, new_value))
                elif attribute == "credit_score":
                    new_value = max(300, min(850, new_value))
                
                setattr(self.state, attribute, new_value)