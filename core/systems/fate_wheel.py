"""
命运轮盘系统 - Echopolis核心模块
决定AI化身的初始出身背景和特殊特质
"""
import random
from enum import Enum
from typing import Dict, List, Tuple
from dataclasses import dataclass

class FateType(Enum):
    """命运类型枚举"""
    BILLIONAIRE = "billionaire"      # 亿万富豪
    SCHOLAR_FAMILY = "scholar_family" # 书香门第  
    FALLEN_NOBLE = "fallen_noble"     # 家道中落
    SELF_MADE = "self_made"          # 白手起家
    MIDDLE_CLASS = "middle_class"     # 中产家庭
    WORKING_CLASS = "working_class"   # 工薪阶层
    RURAL_ORIGIN = "rural_origin"     # 农村出身
    LOW_INCOME = "low_income"         # 低收入户

@dataclass
class FateOutcome:
    """命运结果"""
    fate_type: FateType
    name: str
    description: str
    initial_credits: int
    initial_attributes: Dict[str, int]
    special_traits: List[str]
    background_story: str
    probability: float  # 出现概率

class FateWheelSystem:
    """命运轮盘系统"""
    
    def __init__(self):
        self.fate_outcomes = self._initialize_fates()
    
    def _initialize_fates(self) -> List[FateOutcome]:
        """初始化所有命运结果"""
        return [
            FateOutcome(
                fate_type=FateType.BILLIONAIRE,
                name="🏆 亿万富豪",
                description="含着金汤匙出生，家族企业遍布全球",
                initial_credits=100_000_000,
                initial_attributes={
                    "happiness": 80,
                    "stress": 20,
                    "health": 90,
                    "energy": 100,
                    "credit_score": 800
                },
                special_traits=["挥霍倾向", "社交达人", "投资嗅觉"],
                background_story="你出生在一个商业帝国家族，从小接受最好的教育，但也承受着巨大的期望压力。",
                probability=0.05  # 5%
            ),
            
            FateOutcome(
                fate_type=FateType.SCHOLAR_FAMILY,
                name="📚 书香门第", 
                description="知识分子家庭，重视教育和文化传承",
                initial_credits=1_000_000,
                initial_attributes={
                    "happiness": 70,
                    "stress": 30,
                    "health": 85,
                    "energy": 90,
                    "credit_score": 750
                },
                special_traits=["学习能力强", "理性决策", "风险厌恶"],
                background_story="你的家族几代都是知识分子，父母都是大学教授，家中藏书万卷。",
                probability=0.15  # 15%
            ),
            
            FateOutcome(
                fate_type=FateType.FALLEN_NOBLE,
                name="💔 家道中落",
                description="曾经辉煌的家族如今衰落，但保留着贵族的品味",
                initial_credits=10_000,
                initial_attributes={
                    "happiness": 40,
                    "stress": 70,
                    "health": 75,
                    "energy": 80,
                    "credit_score": 650
                },
                special_traits=["商业嗅觉敏锐", "压力抗性", "复仇心理"],
                background_story="你的家族曾经显赫一时，但因为投资失败而破产，你发誓要重振家族荣光。",
                probability=0.10  # 10%
            ),
            
            FateOutcome(
                fate_type=FateType.SELF_MADE,
                name="💪 白手起家",
                description="普通家庭出身，凭借自己的努力奋斗",
                initial_credits=50_000,
                initial_attributes={
                    "happiness": 60,
                    "stress": 50,
                    "health": 90,
                    "energy": 95,
                    "credit_score": 700
                },
                special_traits=["坚韧不拔", "机会敏感", "节俭习惯"],
                background_story="你出生在一个普通的工薪家庭，父母辛勤工作供你上学，你深知成功来之不易。",
                probability=0.25  # 25%
            ),
            
            FateOutcome(
                fate_type=FateType.MIDDLE_CLASS,
                name="🏠 中产家庭",
                description="标准的中产阶级家庭，生活稳定舒适",
                initial_credits=200_000,
                initial_attributes={
                    "happiness": 75,
                    "stress": 35,
                    "health": 85,
                    "energy": 85,
                    "credit_score": 720
                },
                special_traits=["稳健投资", "生活品质追求", "社交活跃"],
                background_story="你的家庭属于典型的中产阶级，父母都有稳定的工作，生活质量不错。",
                probability=0.30  # 30%
            ),
            
            FateOutcome(
                fate_type=FateType.WORKING_CLASS,
                name="🔧 工薪阶层",
                description="蓝领工人家庭，勤劳朴实",
                initial_credits=30_000,
                initial_attributes={
                    "happiness": 65,
                    "stress": 45,
                    "health": 80,
                    "energy": 90,
                    "credit_score": 680
                },
                special_traits=["勤劳节俭", "实用主义", "风险规避"],
                background_story="你的父母都是普通的工人，虽然收入不高，但一家人其乐融融。",
                probability=0.10  # 10%
            ),
            
            FateOutcome(
                fate_type=FateType.LOW_INCOME,
                name="💰 低收入户",
                description="家庭收入微薄，生活拮据但充满希望",
                initial_credits=25_000,
                initial_attributes={
                    "happiness": 50,
                    "stress": 60,
                    "health": 75,
                    "energy": 85,
                    "credit_score": 650
                },
                special_traits=["节俭意识", "奋斗精神", "珍惜机会"],
                background_story="你的家庭收入微薄，父母为了生计辛苦工作，这让你深知金钱的珍贵和奋斗的意义。",
                probability=0.05  # 5%
            )
        ]
    
    def spin_wheel(self) -> FateOutcome:
        """转动命运轮盘，随机选择一个命运"""
        # 根据概率权重随机选择
        weights = [fate.probability for fate in self.fate_outcomes]
        chosen_fate = random.choices(self.fate_outcomes, weights=weights)[0]
        return chosen_fate
    
    def get_fate_by_type(self, fate_type: FateType) -> FateOutcome:
        """根据类型获取特定命运"""
        for fate in self.fate_outcomes:
            if fate.fate_type == fate_type:
                return fate
        return self.fate_outcomes[0]  # 默认返回第一个
    
    def get_all_fates(self) -> List[FateOutcome]:
        """获取所有可能的命运"""
        return self.fate_outcomes
    
    def calculate_fate_influence(self, fate_type: FateType, decision_context: str) -> Dict[str, float]:
        """计算命运对决策的影响"""
        fate = self.get_fate_by_type(fate_type)
        influence = {}
        
        # 根据特殊特质计算影响
        for trait in fate.special_traits:
            if trait == "挥霍倾向" and "消费" in decision_context:
                influence["spend_tendency"] = 0.3
            elif trait == "商业嗅觉敏锐" and "投资" in decision_context:
                influence["investment_insight"] = 0.4
            elif trait == "风险厌恶" and "风险" in decision_context:
                influence["risk_aversion"] = 0.5
            elif trait == "坚韧不拔" and "困难" in decision_context:
                influence["resilience"] = 0.6
            elif trait == "节俭习惯" and "消费" in decision_context:
                influence["frugality"] = -0.4
        
        return influence

class FateWheel:
    """FateWheel兼容性类"""
    
    @staticmethod
    def get_fate_info(fate_type):
        """获取命运信息"""
        fate_map = {
            FateType.BILLIONAIRE: {'initial_money': 100_000_000, 'description': '含着金汤匙出生，家族企业遍布全球'},
            FateType.SCHOLAR_FAMILY: {'initial_money': 1_000_000, 'description': '知识分子家庭，重视教育和文化传承'},
            FateType.FALLEN_NOBLE: {'initial_money': 10_000, 'description': '曾经辉煌的家族如今衰落，但保留着贵族的品味'},
            FateType.SELF_MADE: {'initial_money': 50_000, 'description': '普通家庭出身，凭借自己的努力奋斗'},
            FateType.MIDDLE_CLASS: {'initial_money': 200_000, 'description': '标准的中产阶级家庭，生活稳定舒适'},
            FateType.WORKING_CLASS: {'initial_money': 30_000, 'description': '蓝领工人家庭，勤劳朴实'},
            FateType.LOW_INCOME: {'initial_money': 25_000, 'description': '家庭收入微薄，生活拮据但充满希望'}
        }
        return fate_map.get(fate_type, {'initial_money': 50000, 'description': '普通家庭'})

# 全局实例
fate_wheel = FateWheelSystem()