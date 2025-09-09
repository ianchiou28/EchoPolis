"""
中央银行模块 - 监控和调控所有用户的经济行为
"""
from typing import Dict, List, Optional
from .person import Person
from ..systems.mbti_traits import MBTIType
import random

class CentralBank:
    """中央银行 - 监控和调控经济系统"""
    
    def __init__(self):
        self.persons: List[Person] = []
        self.economic_data: Dict = {
            "day": 1,
            "interest_rate": 3.5,
            "inflation_rate": 2.1,
            "market_index": 3000,
            "total_money_supply": 1000000000,
            "economic_indicators": []
        }
        self.intervention_points = 10
        self.transaction_log: List[Dict] = []
        
    def create_person(self, name: str, mbti_type: MBTIType) -> Person:
        """创建新人物并注册到央行系统"""
        person = Person(name, mbti_type)
        self.persons.append(person)
        self._register_account(person)
        return person
    
    def _register_account(self, person: Person):
        """为新用户注册央行账户"""
        self.transaction_log.append({
            "type": "account_creation",
            "person": person.attributes.name,
            "initial_credits": person.attributes.credits,
            "day": self.economic_data["day"]
        })
    
    def monitor_transaction(self, person: Person, amount: int, transaction_type: str, description: str):
        """监控用户交易行为"""
        transaction = {
            "person": person.attributes.name,
            "amount": amount,
            "type": transaction_type,
            "description": description,
            "day": self.economic_data["day"],
            "balance_after": person.attributes.credits
        }
        self.transaction_log.append(transaction)
        
        # 实时调控
        self._economic_regulation(transaction)
    
    def _economic_regulation(self, transaction: Dict):
        """根据交易行为进行经济调控"""
        amount = abs(transaction["amount"])
        
        # 大额交易监控
        if amount > 50000:
            self._adjust_interest_rate(0.1)
            self.economic_data["economic_indicators"].append(
                f"检测到大额交易，调整利率至{self.economic_data['interest_rate']:.1f}%"
            )
        
        # 投资行为监控
        if "投资" in transaction["description"]:
            self._adjust_market_index(random.randint(-50, 100))
        
        # 通胀控制
        total_transactions = sum(abs(t["amount"]) for t in self.transaction_log[-10:])
        if total_transactions > 200000:
            self._adjust_inflation_rate(0.1)
    
    def _adjust_interest_rate(self, change: float):
        """调整利率"""
        self.economic_data["interest_rate"] += change
        self.economic_data["interest_rate"] = max(0.1, min(10.0, self.economic_data["interest_rate"]))
    
    def _adjust_market_index(self, change: int):
        """调整市场指数"""
        self.economic_data["market_index"] += change
        self.economic_data["market_index"] = max(1000, self.economic_data["market_index"])
    
    def _adjust_inflation_rate(self, change: float):
        """调整通胀率"""
        self.economic_data["inflation_rate"] += change
        self.economic_data["inflation_rate"] = max(0.0, min(10.0, self.economic_data["inflation_rate"]))
    
    def advance_time(self):
        """推进时间并执行经济调控"""
        self.economic_data["day"] += 1
        self.intervention_points = 10
        
        # 所有人物休息恢复
        for person in self.persons:
            person.rest()
        
        # 执行日常经济调控
        self._daily_economic_adjustment()
    
    def _daily_economic_adjustment(self):
        """每日经济调控"""
        # 利率自然波动
        rate_change = random.uniform(-0.1, 0.1)
        self._adjust_interest_rate(rate_change)
        
        # 市场指数波动
        market_change = random.randint(-100, 100)
        self._adjust_market_index(market_change)
        
        # 通胀率调整
        inflation_change = random.uniform(-0.05, 0.05)
        self._adjust_inflation_rate(inflation_change)
        
        # 清理旧交易记录
        if len(self.transaction_log) > 1000:
            self.transaction_log = self.transaction_log[-500:]
    
    def get_economic_status(self) -> Dict:
        """获取经济状态"""
        total_assets = sum(p.attributes.credits for p in self.persons)
        avg_assets = total_assets / len(self.persons) if self.persons else 0
        
        return {
            "day": self.economic_data["day"],
            "interest_rate": f"{self.economic_data['interest_rate']:.1f}%",
            "inflation_rate": f"{self.economic_data['inflation_rate']:.1f}%",
            "market_index": self.economic_data["market_index"],
            "total_persons": len(self.persons),
            "total_assets": f"{total_assets:,} CP",
            "avg_assets": f"{avg_assets:,.0f} CP",
            "daily_transactions": len([t for t in self.transaction_log if t["day"] == self.economic_data["day"]]),
            "recent_indicators": self.economic_data["economic_indicators"][-3:]
        }
    
    def get_person_credit_rating(self, person: Person) -> str:
        """获取用户信用评级"""
        credits = person.attributes.credits
        transactions = [t for t in self.transaction_log if t["person"] == person.attributes.name]
        
        if credits > 100000 and len(transactions) > 10:
            return "AAA级"
        elif credits > 50000:
            return "AA级"
        elif credits > 20000:
            return "A级"
        else:
            return "B级"
    
    def issue_economic_policy(self, policy_type: str) -> str:
        """发布经济政策"""
        policies = {
            "tightening": "紧缩性货币政策：提高利率，控制通胀",
            "easing": "宽松性货币政策：降低利率，刺激经济",
            "neutral": "中性货币政策：维持当前利率水平"
        }
        
        if policy_type == "tightening":
            self._adjust_interest_rate(0.5)
        elif policy_type == "easing":
            self._adjust_interest_rate(-0.5)
        
        policy_desc = policies.get(policy_type, "未知政策")
        self.economic_data["economic_indicators"].append(f"央行政策：{policy_desc}")
        
        return policy_desc

# 全局央行实例
central_bank = CentralBank()