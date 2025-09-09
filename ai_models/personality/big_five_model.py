"""
大五人格模型实现
基于心理学研究的人格特质评估和建模
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np


class PersonalityDimension(Enum):
    """人格维度枚举"""
    OPENNESS = "openness"  # 开放性
    CONSCIENTIOUSNESS = "conscientiousness"  # 责任心
    EXTRAVERSION = "extraversion"  # 外倾性
    AGREEABLENESS = "agreeableness"  # 宜人性
    NEUROTICISM = "neuroticism"  # 神经质


@dataclass
class PersonalityProfile:
    """人格档案"""
    openness: float  # 0-100
    conscientiousness: float  # 0-100
    extraversion: float  # 0-100
    agreeableness: float  # 0-100
    neuroticism: float  # 0-100
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism
        }
    
    def get_radar_data(self) -> List[float]:
        """获取雷达图数据"""
        return [
            self.openness,
            self.conscientiousness,
            self.extraversion,
            self.agreeableness,
            self.neuroticism
        ]


class PersonalityAssessment:
    """人格评估系统"""
    
    def __init__(self):
        self.questions = self._load_assessment_questions()
    
    def _load_assessment_questions(self) -> List[Dict]:
        """加载评估问题"""
        return [
            # 开放性相关问题
            {
                "id": 1,
                "text": "面对新的投资机会时，你更倾向于：",
                "options": [
                    {"text": "深入研究创新产品和新兴市场", "dimension": "openness", "score": 5},
                    {"text": "选择传统稳健的投资方式", "dimension": "openness", "score": 1},
                    {"text": "适度尝试，但以稳健为主", "dimension": "openness", "score": 3}
                ]
            },
            # 责任心相关问题
            {
                "id": 2,
                "text": "制定财务计划时，你通常：",
                "options": [
                    {"text": "制定详细的长期规划并严格执行", "dimension": "conscientiousness", "score": 5},
                    {"text": "大概有个想法，随机应变", "dimension": "conscientiousness", "score": 1},
                    {"text": "有基本规划，但会根据情况调整", "dimension": "conscientiousness", "score": 3}
                ]
            },
            # 外倾性相关问题
            {
                "id": 3,
                "text": "在投资决策中，你更愿意：",
                "options": [
                    {"text": "与朋友讨论，听取多方意见", "dimension": "extraversion", "score": 5},
                    {"text": "独自分析，相信自己的判断", "dimension": "extraversion", "score": 1},
                    {"text": "主要靠自己，偶尔征求意见", "dimension": "extraversion", "score": 3}
                ]
            },
            # 宜人性相关问题
            {
                "id": 4,
                "text": "选择金融产品时，你会考虑：",
                "options": [
                    {"text": "产品的社会责任和环保因素", "dimension": "agreeableness", "score": 5},
                    {"text": "主要关注收益率和风险", "dimension": "agreeableness", "score": 1},
                    {"text": "收益优先，但也会考虑社会影响", "dimension": "agreeableness", "score": 3}
                ]
            },
            # 神经质相关问题
            {
                "id": 5,
                "text": "市场波动时，你的反应是：",
                "options": [
                    {"text": "感到焦虑，频繁查看账户", "dimension": "neuroticism", "score": 5},
                    {"text": "保持冷静，按计划执行", "dimension": "neuroticism", "score": 1},
                    {"text": "有些担心，但能控制情绪", "dimension": "neuroticism", "score": 3}
                ]
            }
        ]
    
    def calculate_personality(self, answers: List[int]) -> PersonalityProfile:
        """根据答案计算人格档案"""
        scores = {
            "openness": [],
            "conscientiousness": [],
            "extraversion": [],
            "agreeableness": [],
            "neuroticism": []
        }
        
        for i, answer_idx in enumerate(answers):
            question = self.questions[i]
            selected_option = question["options"][answer_idx]
            dimension = selected_option["dimension"]
            score = selected_option["score"]
            scores[dimension].append(score)
        
        # 计算各维度平均分并转换为0-100范围
        personality_scores = {}
        for dimension, dimension_scores in scores.items():
            if dimension_scores:
                avg_score = np.mean(dimension_scores)
                # 将1-5分转换为0-100分
                personality_scores[dimension] = (avg_score - 1) * 25
            else:
                personality_scores[dimension] = 50  # 默认中等水平
        
        return PersonalityProfile(**personality_scores)


class PersonalityTraits:
    """人格特质系统"""
    
    @staticmethod
    def derive_traits(personality: PersonalityProfile) -> List[str]:
        """根据人格档案推导特质"""
        traits = []
        
        # 基于开放性的特质
        if personality.openness > 80:
            traits.append("创新探索者")
        elif personality.openness < 20:
            traits.append("保守稳健")
        
        # 基于责任心的特质
        if personality.conscientiousness > 80:
            traits.append("严格自律")
        elif personality.conscientiousness < 20:
            traits.append("随性自由")
        
        # 基于外倾性的特质
        if personality.extraversion > 80:
            traits.append("社交达人")
        elif personality.extraversion < 20:
            traits.append("独立思考")
        
        # 基于宜人性的特质
        if personality.agreeableness > 80:
            traits.append("利他主义")
        elif personality.agreeableness < 20:
            traits.append("理性至上")
        
        # 基于神经质的特质
        if personality.neuroticism > 80:
            traits.append("情绪敏感")
        elif personality.neuroticism < 20:
            traits.append("情绪稳定")
        
        # 组合特质
        if personality.conscientiousness > 70 and personality.neuroticism > 70:
            traits.append("分析瘫痪")
        
        if personality.openness > 70 and personality.neuroticism < 30:
            traits.append("价值投资者")
        
        if personality.extraversion > 70 and personality.openness > 70:
            traits.append("FOMO易感")
        
        if personality.conscientiousness < 30 and personality.neuroticism > 70:
            traits.append("天生赌徒")
        
        return traits
    
    @staticmethod
    def get_trait_effects(traits: List[str]) -> Dict[str, Dict]:
        """获取特质对行为的影响"""
        trait_effects = {
            "创新探索者": {
                "investment_preference": "high_risk_high_return",
                "decision_speed": "fast",
                "market_sensitivity": "high"
            },
            "保守稳健": {
                "investment_preference": "low_risk_stable",
                "decision_speed": "slow",
                "market_sensitivity": "low"
            },
            "严格自律": {
                "budget_adherence": "high",
                "long_term_planning": "excellent",
                "impulse_control": "high"
            },
            "随性自由": {
                "budget_adherence": "low",
                "long_term_planning": "poor",
                "impulse_control": "low"
            },
            "分析瘫痪": {
                "decision_delay": "high",
                "information_gathering": "excessive",
                "opportunity_cost": "high"
            },
            "天生赌徒": {
                "risk_tolerance": "extreme",
                "leverage_usage": "high",
                "emotional_trading": "high"
            },
            "FOMO易感": {
                "trend_following": "high",
                "social_influence": "high",
                "timing_issues": "frequent"
            }
        }
        
        effects = {}
        for trait in traits:
            if trait in trait_effects:
                effects[trait] = trait_effects[trait]
        
        return effects