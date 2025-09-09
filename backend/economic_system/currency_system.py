"""
Echopolis 货币系统
实现双轨制货币体系：信用点(CP) + 启示结晶(IC)
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import math


class CurrencyType(Enum):
    """货币类型"""
    CREDIT_POINTS = "CP"  # 信用点
    INSIGHT_CRYSTALS = "IC"  # 启示结晶


class TransactionType(Enum):
    """交易类型"""
    INCOME = "income"  # 收入
    EXPENSE = "expense"  # 支出
    INVESTMENT = "investment"  # 投资
    LOAN = "loan"  # 贷款
    INTEREST = "interest"  # 利息
    DIVIDEND = "dividend"  # 股息
    SALARY = "salary"  # 工资
    BONUS = "bonus"  # 奖金
    TAX = "tax"  # 税收
    FINE = "fine"  # 罚款


@dataclass
class Transaction:
    """交易记录"""
    id: str
    user_id: str
    transaction_type: TransactionType
    currency_type: CurrencyType
    amount: float
    description: str
    timestamp: datetime
    balance_after: float
    metadata: Dict = None


@dataclass
class EconomicIndicators:
    """经济指标"""
    base_interest_rate: float  # 基准利率
    inflation_rate: float  # 通胀率
    unemployment_rate: float  # 失业率
    gdp_growth_rate: float  # GDP增长率
    consumer_price_index: float  # 消费者价格指数
    market_sentiment: float  # 市场情绪 (-1到1)
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "base_interest_rate": self.base_interest_rate,
            "inflation_rate": self.inflation_rate,
            "unemployment_rate": self.unemployment_rate,
            "gdp_growth_rate": self.gdp_growth_rate,
            "consumer_price_index": self.consumer_price_index,
            "market_sentiment": self.market_sentiment
        }


class CentralBank:
    """中央银行 - 货币政策制定者"""
    
    def __init__(self):
        self.indicators = EconomicIndicators(
            base_interest_rate=0.025,  # 2.5%
            inflation_rate=0.02,      # 2%
            unemployment_rate=0.05,   # 5%
            gdp_growth_rate=0.03,     # 3%
            consumer_price_index=100.0,
            market_sentiment=0.0
        )
        self.policy_history = []
        self.money_supply = 1000000000.0  # 10亿CP的货币供应量
    
    def adjust_interest_rate(self, new_rate: float, reason: str):
        """调整基准利率"""
        old_rate = self.indicators.base_interest_rate
        self.indicators.base_interest_rate = max(0.0, min(0.20, new_rate))  # 0-20%限制
        
        policy_change = {
            "timestamp": datetime.now(),
            "type": "interest_rate_change",
            "old_value": old_rate,
            "new_value": self.indicators.base_interest_rate,
            "reason": reason
        }
        self.policy_history.append(policy_change)
    
    def quantitative_easing(self, amount: float):
        """量化宽松 - 增加货币供应量"""
        self.money_supply += amount
        
        # 量化宽松会推高通胀和资产价格
        inflation_impact = amount / self.money_supply * 0.1
        self.indicators.inflation_rate += inflation_impact
        self.indicators.market_sentiment += 0.1  # 市场通常对QE反应积极
        
        policy_change = {
            "timestamp": datetime.now(),
            "type": "quantitative_easing",
            "amount": amount,
            "new_money_supply": self.money_supply,
            "reason": "刺激经济增长"
        }
        self.policy_history.append(policy_change)
    
    def update_economic_cycle(self, cycle_phase: str):
        """根据经济周期更新指标"""
        if cycle_phase == "recession":
            self.indicators.gdp_growth_rate = max(-0.05, self.indicators.gdp_growth_rate - 0.02)
            self.indicators.unemployment_rate = min(0.15, self.indicators.unemployment_rate + 0.01)
            self.indicators.market_sentiment = max(-1.0, self.indicators.market_sentiment - 0.2)
            
        elif cycle_phase == "recovery":
            self.indicators.gdp_growth_rate = min(0.08, self.indicators.gdp_growth_rate + 0.01)
            self.indicators.unemployment_rate = max(0.02, self.indicators.unemployment_rate - 0.005)
            self.indicators.market_sentiment = min(1.0, self.indicators.market_sentiment + 0.1)
            
        elif cycle_phase == "boom":
            self.indicators.gdp_growth_rate = min(0.10, self.indicators.gdp_growth_rate + 0.005)
            self.indicators.inflation_rate = min(0.08, self.indicators.inflation_rate + 0.005)
            self.indicators.market_sentiment = min(1.0, self.indicators.market_sentiment + 0.05)
    
    def get_deposit_rate(self) -> float:
        """获取存款利率"""
        return self.indicators.base_interest_rate * 0.8  # 通常低于基准利率
    
    def get_loan_rate(self, credit_score: int, loan_type: str = "personal") -> float:
        """获取贷款利率"""
        base_rate = self.indicators.base_interest_rate
        
        # 信用评分影响
        credit_premium = max(0, (700 - credit_score) / 1000)  # 信用分越低，利率越高
        
        # 贷款类型影响
        type_premium = {
            "personal": 0.05,      # 个人贷款
            "mortgage": 0.01,      # 房贷
            "business": 0.03,      # 商业贷款
            "credit_card": 0.15    # 信用卡
        }.get(loan_type, 0.05)
        
        return base_rate + credit_premium + type_premium


class WealthManager:
    """财富管理系统"""
    
    def __init__(self, central_bank: CentralBank):
        self.central_bank = central_bank
        self.user_accounts = {}  # user_id -> account_data
        self.transaction_history = {}  # user_id -> [transactions]
    
    def create_account(self, user_id: str, initial_cp: float = 50000.0) -> Dict:
        """创建用户账户"""
        account = {
            "user_id": user_id,
            "credit_points": initial_cp,
            "insight_crystals": 0,
            "created_at": datetime.now(),
            "last_updated": datetime.now()
        }
        
        self.user_accounts[user_id] = account
        self.transaction_history[user_id] = []
        
        # 记录初始交易
        self._record_transaction(
            user_id=user_id,
            transaction_type=TransactionType.INCOME,
            currency_type=CurrencyType.CREDIT_POINTS,
            amount=initial_cp,
            description="账户初始资金"
        )
        
        return account
    
    def get_balance(self, user_id: str, currency_type: CurrencyType) -> float:
        """获取余额"""
        if user_id not in self.user_accounts:
            return 0.0
        
        account = self.user_accounts[user_id]
        if currency_type == CurrencyType.CREDIT_POINTS:
            return account["credit_points"]
        elif currency_type == CurrencyType.INSIGHT_CRYSTALS:
            return account["insight_crystals"]
        
        return 0.0
    
    def transfer(self, user_id: str, currency_type: CurrencyType, 
                amount: float, description: str, 
                transaction_type: TransactionType = TransactionType.EXPENSE) -> bool:
        """转账/支付"""
        if user_id not in self.user_accounts:
            return False
        
        current_balance = self.get_balance(user_id, currency_type)
        
        # 检查余额是否足够
        if transaction_type in [TransactionType.EXPENSE, TransactionType.INVESTMENT] and current_balance < amount:
            return False
        
        # 更新余额
        if currency_type == CurrencyType.CREDIT_POINTS:
            if transaction_type in [TransactionType.EXPENSE, TransactionType.INVESTMENT, TransactionType.TAX]:
                self.user_accounts[user_id]["credit_points"] -= amount
            else:
                self.user_accounts[user_id]["credit_points"] += amount
        elif currency_type == CurrencyType.INSIGHT_CRYSTALS:
            if transaction_type == TransactionType.EXPENSE:
                self.user_accounts[user_id]["insight_crystals"] -= amount
            else:
                self.user_accounts[user_id]["insight_crystals"] += amount
        
        # 记录交易
        self._record_transaction(user_id, transaction_type, currency_type, amount, description)
        
        return True
    
    def calculate_interest(self, user_id: str, deposit_amount: float, days: int) -> float:
        """计算存款利息"""
        annual_rate = self.central_bank.get_deposit_rate()
        daily_rate = annual_rate / 365
        return deposit_amount * daily_rate * days
    
    def calculate_loan_payment(self, principal: float, annual_rate: float, 
                             term_months: int) -> Tuple[float, float]:
        """计算贷款月供和总利息"""
        monthly_rate = annual_rate / 12
        num_payments = term_months
        
        if monthly_rate == 0:
            monthly_payment = principal / num_payments
            total_interest = 0
        else:
            monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                            ((1 + monthly_rate) ** num_payments - 1)
            total_interest = monthly_payment * num_payments - principal
        
        return monthly_payment, total_interest
    
    def apply_inflation(self, user_id: str):
        """应用通胀影响"""
        if user_id not in self.user_accounts:
            return
        
        inflation_rate = self.central_bank.indicators.inflation_rate
        current_cp = self.user_accounts[user_id]["credit_points"]
        
        # 现金的购买力下降
        purchasing_power_loss = current_cp * (inflation_rate / 365)  # 日通胀影响
        
        # 记录通胀影响（不实际扣除，但影响实际购买力）
        self._record_transaction(
            user_id=user_id,
            transaction_type=TransactionType.EXPENSE,
            currency_type=CurrencyType.CREDIT_POINTS,
            amount=0,  # 不实际扣除
            description=f"通胀影响：购买力下降 {purchasing_power_loss:.2f} CP"
        )
    
    def award_insight_crystals(self, user_id: str, amount: int, reason: str):
        """奖励启示结晶"""
        self.transfer(
            user_id=user_id,
            currency_type=CurrencyType.INSIGHT_CRYSTALS,
            amount=amount,
            description=f"获得启示结晶：{reason}",
            transaction_type=TransactionType.BONUS
        )
    
    def get_financial_summary(self, user_id: str) -> Dict:
        """获取财务摘要"""
        if user_id not in self.user_accounts:
            return {}
        
        account = self.user_accounts[user_id]
        transactions = self.transaction_history.get(user_id, [])
        
        # 计算本月收支
        current_month = datetime.now().replace(day=1)
        monthly_transactions = [t for t in transactions if t.timestamp >= current_month]
        
        monthly_income = sum(t.amount for t in monthly_transactions 
                           if t.transaction_type in [TransactionType.INCOME, TransactionType.SALARY, 
                                                   TransactionType.BONUS, TransactionType.DIVIDEND])
        monthly_expenses = sum(t.amount for t in monthly_transactions 
                             if t.transaction_type in [TransactionType.EXPENSE, TransactionType.TAX])
        
        return {
            "credit_points": account["credit_points"],
            "insight_crystals": account["insight_crystals"],
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "net_monthly": monthly_income - monthly_expenses,
            "transaction_count": len(transactions),
            "account_age_days": (datetime.now() - account["created_at"]).days
        }
    
    def _record_transaction(self, user_id: str, transaction_type: TransactionType,
                          currency_type: CurrencyType, amount: float, description: str):
        """记录交易"""
        if user_id not in self.transaction_history:
            self.transaction_history[user_id] = []
        
        balance_after = self.get_balance(user_id, currency_type)
        
        transaction = Transaction(
            id=f"{user_id}_{datetime.now().timestamp()}",
            user_id=user_id,
            transaction_type=transaction_type,
            currency_type=currency_type,
            amount=amount,
            description=description,
            timestamp=datetime.now(),
            balance_after=balance_after
        )
        
        self.transaction_history[user_id].append(transaction)
        self.user_accounts[user_id]["last_updated"] = datetime.now()


class InsightCrystalShop:
    """启示结晶商店"""
    
    def __init__(self):
        self.catalog = {
            "echo_lens": {
                "name": "回响透镜",
                "price": 1,
                "description": "查看AI化身的决策逻辑",
                "effect": "reveal_decision_process"
            },
            "market_insight": {
                "name": "市场洞察",
                "price": 3,
                "description": "获得未来一周的市场趋势预测",
                "effect": "market_prediction"
            },
            "financial_report": {
                "name": "深度财报分析",
                "price": 5,
                "description": "获得专业分析师的股票深度报告",
                "effect": "professional_analysis"
            },
            "trait_modifier": {
                "name": "性格调节器",
                "price": 10,
                "description": "临时调整AI化身的某个性格特质",
                "effect": "temporary_trait_change"
            },
            "new_life_bonus": {
                "name": "新生祝福",
                "price": 15,
                "description": "为下一个化身购买初始正面特质",
                "effect": "next_life_trait"
            }
        }
    
    def purchase_item(self, wealth_manager: WealthManager, user_id: str, 
                     item_id: str) -> Tuple[bool, str]:
        """购买物品"""
        if item_id not in self.catalog:
            return False, "物品不存在"
        
        item = self.catalog[item_id]
        price = item["price"]
        
        current_ic = wealth_manager.get_balance(user_id, CurrencyType.INSIGHT_CRYSTALS)
        
        if current_ic < price:
            return False, f"启示结晶不足，需要 {price} IC，当前只有 {current_ic} IC"
        
        # 扣除费用
        success = wealth_manager.transfer(
            user_id=user_id,
            currency_type=CurrencyType.INSIGHT_CRYSTALS,
            amount=price,
            description=f"购买：{item['name']}",
            transaction_type=TransactionType.EXPENSE
        )
        
        if success:
            return True, f"成功购买 {item['name']}"
        else:
            return False, "购买失败"