"""
Brain模块 - 参考AIvilization的Brain结构
"""
from typing import Dict, List, Optional, TYPE_CHECKING
from enum import Enum
import random

from ..ai.deepseek_engine import deepseek_engine
from ..systems.asset_calculator import asset_calculator

if TYPE_CHECKING:
    from .person import Person

class ThoughtType(Enum):
    """思维类型"""
    LOGICAL = "logical"
    EMOTIONAL = "emotional"
    INTUITIVE = "intuitive"
    PRACTICAL = "practical"

class Brain:
    """大脑模块 - 处理思考和决策"""
    
    def __init__(self, person: 'Person'):
        self.person = person
        self.thoughts: List[Dict] = []
        self.decision_patterns: Dict = {}
        
    def process_decision(self, situation: str, options: List[str], player_echo: Optional[str] = None) -> Dict:
        """处理决策过程"""
        # 生成思维过程
        thought = self._generate_thought(situation, options, player_echo)
        self.thoughts.append(thought)
        
        # 做出决策
        if deepseek_engine:
            decision = self._ai_decision(situation, options, player_echo)
        else:
            decision = self._rule_decision(situation, options, player_echo)
        
        # 计算资产影响
        asset_change, asset_desc = asset_calculator.calculate_decision_impact(
            decision['chosen_option'], self.person.attributes.credits
        )
        
        # 更新属性
        old_credits = self.person.attributes.credits
        self.person.update_attributes({'credits': asset_change})
        
        return {
            **decision,
            'thought': thought,
            'asset_change': asset_change,
            'asset_desc': asset_desc,
            'old_credits': old_credits,
            'new_credits': self.person.attributes.credits
        }
    
    def _generate_thought(self, situation: str, options: List[str], player_echo: Optional[str]) -> Dict:
        """生成思维过程"""
        mbti = self.person.attributes.mbti_type
        
        # 根据MBTI确定思维类型
        thought_type = self._get_thought_type(mbti)
        
        # 生成思维内容
        considerations = []
        if self.person.attributes.stress > 60:
            considerations.append("当前压力较大")
        if self.person.attributes.credits < 10000:
            considerations.append("资金紧张")
        if player_echo:
            considerations.append(f"玩家建议: {player_echo}")
        
        return {
            "type": thought_type.value,
            "considerations": considerations,
            "confidence": random.uniform(0.6, 0.9)
        }
    
    def _get_thought_type(self, mbti) -> ThoughtType:
        """根据MBTI获取思维类型"""
        thinking_types = {
            "NT": ThoughtType.LOGICAL,
            "NF": ThoughtType.INTUITIVE,
            "ST": ThoughtType.PRACTICAL,
            "SF": ThoughtType.EMOTIONAL
        }
        
        mbti_str = mbti.value
        for pattern, thought_type in thinking_types.items():
            if all(char in mbti_str for char in pattern):
                return thought_type
        
        return ThoughtType.LOGICAL
    
    def _ai_decision(self, situation: str, options: List[str], player_echo: Optional[str]) -> Dict:
        """AI决策"""
        context = {
            "name": self.person.attributes.name,
            "age": self.person.attributes.age,
            "mbti": self.person.attributes.mbti_type.value,
            "credits": self.person.attributes.credits,
            "health": self.person.attributes.health,
            "happiness": self.person.attributes.happiness,
            "stress": self.person.attributes.stress,
            "trust": self.person.attributes.trust_level,
            "situation": situation,
            "options": options,
            "player_echo": player_echo
        }
        
        result = deepseek_engine.make_decision(context)
        if "error" not in result:
            return {
                "chosen_option": result["chosen_option"],
                "ai_thoughts": result["ai_thoughts"]
            }
        
        return self._rule_decision(situation, options, player_echo)
    
    def _rule_decision(self, situation: str, options: List[str], player_echo: Optional[str]) -> Dict:
        """规则决策"""
        # 简化的决策逻辑
        weights = [1.0] * len(options)
        
        # MBTI影响
        mbti = self.person.attributes.mbti_type.value
        if "T" in mbti:  # 思维型
            for i, option in enumerate(options):
                if any(word in option.lower() for word in ["分析", "计算", "理性"]):
                    weights[i] += 0.3
        
        if "F" in mbti:  # 情感型
            for i, option in enumerate(options):
                if any(word in option.lower() for word in ["感觉", "直觉", "情感"]):
                    weights[i] += 0.3
        
        # 玩家影响
        if player_echo:
            trust_factor = self.person.attributes.trust_level / 100
            for i, option in enumerate(options):
                if any(word in player_echo.lower() for word in option.lower().split()):
                    weights[i] += 0.5 * trust_factor
        
        # 选择权重最高的选项
        chosen_idx = weights.index(max(weights))
        chosen_option = options[chosen_idx]
        
        # 生成简单的思考
        thoughts = f"基于{mbti}人格特质，我选择了这个方案"
        if player_echo and self.person.attributes.trust_level > 50:
            thoughts += f"，也考虑了你的建议"
        
        return {
            "chosen_option": chosen_option,
            "ai_thoughts": thoughts[:150]
        }