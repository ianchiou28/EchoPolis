"""
Action模块 - 参考AIvilization的Action结构
"""
from typing import Dict, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass
import random

if TYPE_CHECKING:
    from .person import Person

class ActionType(Enum):
    """行动类型"""
    INVEST = "invest"
    WORK = "work"
    REST = "rest"
    STUDY = "study"
    SOCIALIZE = "socialize"
    PURCHASE = "purchase"
    SAVE = "save"

@dataclass
class ActionResult:
    """行动结果"""
    success: bool
    message: str
    attribute_changes: Dict[str, int]
    asset_change: int = 0

class Action:
    """行动类 - 类似AIvilization的Action"""
    
    def __init__(self, action_type: ActionType, target: str, context: Dict):
        self.action_type = action_type
        self.target = target
        self.context = context
        self.executed = False
        self.result: ActionResult = None
    
    def execute(self, person: 'Person') -> Dict:
        """执行行动"""
        if self.executed:
            return {"error": "Action already executed"}
        
        self.executed = True
        
        # 根据行动类型执行不同逻辑
        if self.action_type == ActionType.INVEST:
            self.result = self._execute_invest(person)
        elif self.action_type == ActionType.WORK:
            self.result = self._execute_work(person)
        elif self.action_type == ActionType.REST:
            self.result = self._execute_rest(person)
        elif self.action_type == ActionType.STUDY:
            self.result = self._execute_study(person)
        elif self.action_type == ActionType.SOCIALIZE:
            self.result = self._execute_socialize(person)
        elif self.action_type == ActionType.PURCHASE:
            self.result = self._execute_purchase(person)
        elif self.action_type == ActionType.SAVE:
            self.result = self._execute_save(person)
        else:
            self.result = ActionResult(False, "Unknown action type", {})
        
        # 应用属性变化
        person.update_attributes(self.result.attribute_changes)
        
        return {
            "success": self.result.success,
            "message": self.result.message,
            "attribute_changes": self.result.attribute_changes,
            "asset_change": self.result.asset_change
        }
    
    def _execute_invest(self, person: 'Person') -> ActionResult:
        """执行投资"""
        amount = self.context.get('amount', 10000)
        risk_level = self.context.get('risk', 'medium')
        
        if person.attributes.credits < amount:
            return ActionResult(False, "资金不足", {})
        
        # 投资成功率
        success_rates = {'low': 0.8, 'medium': 0.6, 'high': 0.4}
        success_rate = success_rates.get(risk_level, 0.6)
        
        if random.random() < success_rate:
            return_rate = random.uniform(0.05, 0.3)
            profit = int(amount * return_rate)
            return ActionResult(
                True, 
                f"投资成功，获得{profit:,}收益",
                {"happiness": 10, "stress": -5},
                profit
            )
        else:
            loss = int(amount * random.uniform(0.1, 0.5))
            return ActionResult(
                False,
                f"投资失败，损失{loss:,}",
                {"happiness": -10, "stress": 15},
                -loss
            )
    
    def _execute_work(self, person: 'Person') -> ActionResult:
        """执行工作"""
        work_type = self.context.get('type', 'normal')
        
        income_ranges = {
            'normal': (3000, 8000),
            'overtime': (5000, 12000),
            'parttime': (1000, 4000)
        }
        
        min_income, max_income = income_ranges.get(work_type, (3000, 8000))
        income = random.randint(min_income, max_income)
        
        stress_change = 5 if work_type == 'overtime' else 2
        energy_change = -10 if work_type == 'overtime' else -5
        
        return ActionResult(
            True,
            f"工作获得{income:,}收入",
            {"stress": stress_change, "energy": energy_change},
            income
        )
    
    def _execute_rest(self, person: 'Person') -> ActionResult:
        """执行休息"""
        return ActionResult(
            True,
            "充分休息，状态恢复",
            {"energy": 20, "stress": -10, "health": 5}
        )
    
    def _execute_study(self, person: 'Person') -> ActionResult:
        """执行学习"""
        return ActionResult(
            True,
            "学习提升了能力",
            {"happiness": 5, "stress": 3, "energy": -5}
        )
    
    def _execute_socialize(self, person: 'Person') -> ActionResult:
        """执行社交"""
        return ActionResult(
            True,
            "社交活动很愉快",
            {"happiness": 15, "stress": -5, "energy": -3}
        )
    
    def _execute_purchase(self, person: 'Person') -> ActionResult:
        """执行购买"""
        cost = self.context.get('cost', 1000)
        
        if person.attributes.credits < cost:
            return ActionResult(False, "资金不足", {})
        
        return ActionResult(
            True,
            f"购买成功，花费{cost:,}",
            {"happiness": 8},
            -cost
        )
    
    def _execute_save(self, person: 'Person') -> ActionResult:
        """执行储蓄"""
        amount = self.context.get('amount', 5000)
        interest_rate = 0.03
        interest = int(amount * interest_rate)
        
        return ActionResult(
            True,
            f"储蓄获得{interest:,}利息",
            {"happiness": 3},
            interest
        )