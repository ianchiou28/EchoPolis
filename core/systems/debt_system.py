"""
负债系统 - EchoPolis
管理贷款、月供、利息计算
"""
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class LoanType(Enum):
    """贷款类型"""
    MORTGAGE = "房贷"          # 房屋贷款，利率低，期限长
    CONSUMER = "消费贷"        # 消费贷款，利率中等
    BUSINESS = "经营贷"        # 经营贷款，利率较高
    CREDIT = "信用贷"          # 信用贷款，利率最高，额度低
    MARGIN = "融资融券"        # 证券融资，随时可能被追缴


class RepaymentMethod(Enum):
    """还款方式"""
    EQUAL_INSTALLMENT = "等额本息"    # 每月固定还款
    EQUAL_PRINCIPAL = "等额本金"      # 本金固定，利息递减
    INTEREST_ONLY = "先息后本"        # 每月只还利息，到期还本
    BULLET = "到期一次性还本付息"     # 一次性还款


@dataclass
class Loan:
    """贷款记录"""
    id: str                         # 贷款ID
    loan_type: LoanType             # 贷款类型
    principal: int                  # 本金
    annual_rate: float              # 年利率 (0.05 = 5%)
    term_months: int                # 贷款期限（月）
    remaining_months: int           # 剩余期限
    remaining_principal: float      # 剩余本金
    repayment_method: RepaymentMethod  # 还款方式
    monthly_payment: float          # 月供金额
    collateral: Optional[str] = None   # 抵押物
    created_at: float = field(default_factory=time.time)
    is_overdue: bool = False        # 是否逾期
    overdue_days: int = 0           # 逾期天数
    
    @property
    def total_interest(self) -> float:
        """总利息"""
        if self.repayment_method == RepaymentMethod.EQUAL_INSTALLMENT:
            return self.monthly_payment * self.term_months - self.principal
        elif self.repayment_method == RepaymentMethod.EQUAL_PRINCIPAL:
            monthly_principal = self.principal / self.term_months
            total_interest = 0
            remaining = self.principal
            for _ in range(self.term_months):
                total_interest += remaining * (self.annual_rate / 12)
                remaining -= monthly_principal
            return total_interest
        else:
            return self.principal * self.annual_rate * (self.term_months / 12)


@dataclass 
class LoanProduct:
    """贷款产品定义"""
    loan_type: LoanType
    name: str
    min_amount: int
    max_amount: int
    min_term: int               # 最短期限（月）
    max_term: int               # 最长期限（月）
    base_rate: float            # 基准年利率
    rate_range: tuple           # 利率浮动范围 (min_multiplier, max_multiplier)
    requires_collateral: bool   # 是否需要抵押
    credit_score_required: int  # 最低信用分要求
    description: str


# 贷款产品库
LOAN_PRODUCTS = [
    LoanProduct(
        loan_type=LoanType.MORTGAGE,
        name="住房按揭贷款",
        min_amount=100000,
        max_amount=5000000,
        min_term=60,
        max_term=360,
        base_rate=0.041,
        rate_range=(0.9, 1.2),
        requires_collateral=True,
        credit_score_required=600,
        description="购房首选，利率优惠，最长30年"
    ),
    LoanProduct(
        loan_type=LoanType.CONSUMER,
        name="个人消费贷款",
        min_amount=5000,
        max_amount=300000,
        min_term=6,
        max_term=60,
        base_rate=0.078,
        rate_range=(0.8, 1.5),
        requires_collateral=False,
        credit_score_required=650,
        description="无需抵押，用于日常消费"
    ),
    LoanProduct(
        loan_type=LoanType.BUSINESS,
        name="小微企业贷款",
        min_amount=50000,
        max_amount=1000000,
        min_term=12,
        max_term=60,
        base_rate=0.065,
        rate_range=(0.9, 1.3),
        requires_collateral=True,
        credit_score_required=680,
        description="创业经营资金支持"
    ),
    LoanProduct(
        loan_type=LoanType.CREDIT,
        name="信用贷款",
        min_amount=1000,
        max_amount=100000,
        min_term=3,
        max_term=24,
        base_rate=0.15,
        rate_range=(1.0, 2.0),
        requires_collateral=False,
        credit_score_required=600,
        description="凭信用获得，利率较高"
    ),
    LoanProduct(
        loan_type=LoanType.MARGIN,
        name="证券融资",
        min_amount=10000,
        max_amount=500000,
        min_term=1,
        max_term=12,
        base_rate=0.068,
        rate_range=(1.0, 1.2),
        requires_collateral=True,
        credit_score_required=700,
        description="用于股票投资，需维持担保比例"
    ),
]


class DebtSystem:
    """负债管理系统"""
    
    def __init__(self):
        self.loans: Dict[str, Loan] = {}  # loan_id -> Loan
        self.loan_products = {p.loan_type: p for p in LOAN_PRODUCTS}
        self.credit_score = 700  # 默认信用分
        self.total_credit_limit = 100000  # 总授信额度
        
    def calculate_monthly_payment(self, 
                                  principal: int, 
                                  annual_rate: float, 
                                  term_months: int,
                                  method: RepaymentMethod) -> float:
        """计算月供
        
        Args:
            principal: 本金
            annual_rate: 年利率
            term_months: 期限（月）
            method: 还款方式
        
        Returns:
            月供金额
        """
        monthly_rate = annual_rate / 12
        
        if method == RepaymentMethod.EQUAL_INSTALLMENT:
            # 等额本息: M = P * [r(1+r)^n] / [(1+r)^n - 1]
            if monthly_rate == 0:
                return principal / term_months
            factor = (1 + monthly_rate) ** term_months
            return principal * monthly_rate * factor / (factor - 1)
        
        elif method == RepaymentMethod.EQUAL_PRINCIPAL:
            # 等额本金: 首月最高，逐月递减
            # 返回首月金额作为参考
            monthly_principal = principal / term_months
            return monthly_principal + principal * monthly_rate
        
        elif method == RepaymentMethod.INTEREST_ONLY:
            # 先息后本: 每月只还利息
            return principal * monthly_rate
        
        else:  # BULLET
            # 到期还本付息: 每月无需还款
            return 0
    
    def get_rate_for_user(self, loan_type: LoanType, credit_score: int = None) -> float:
        """根据用户信用评分获取利率"""
        product = self.loan_products.get(loan_type)
        if not product:
            return 0.10  # 默认10%
        
        score = credit_score or self.credit_score
        
        # 信用评分影响利率
        if score >= 750:
            multiplier = product.rate_range[0]  # 最优利率
        elif score >= 700:
            multiplier = (product.rate_range[0] + product.rate_range[1]) / 2
        elif score >= 650:
            multiplier = product.rate_range[1]
        else:
            multiplier = product.rate_range[1] * 1.2  # 额外加成
        
        return product.base_rate * multiplier
    
    def can_apply_loan(self, 
                       loan_type: LoanType, 
                       amount: int,
                       has_collateral: bool = False) -> tuple:
        """检查是否可以申请贷款
        
        Returns:
            (can_apply, reason)
        """
        product = self.loan_products.get(loan_type)
        if not product:
            return False, "贷款产品不存在"
        
        if amount < product.min_amount:
            return False, f"最低贷款额度为 ¥{product.min_amount:,}"
        
        if amount > product.max_amount:
            return False, f"最高贷款额度为 ¥{product.max_amount:,}"
        
        if self.credit_score < product.credit_score_required:
            return False, f"信用评分不足，需要 {product.credit_score_required} 分"
        
        if product.requires_collateral and not has_collateral:
            return False, "需要提供抵押物"
        
        # 检查总负债率
        current_debt = self.get_total_debt()
        if current_debt + amount > self.total_credit_limit * 2:
            return False, "总负债过高，暂不批准"
        
        return True, "可以申请"
    
    def apply_loan(self,
                   loan_type: LoanType,
                   amount: int,
                   term_months: int,
                   repayment_method: RepaymentMethod = RepaymentMethod.EQUAL_INSTALLMENT,
                   collateral: Optional[str] = None) -> tuple:
        """申请贷款
        
        Returns:
            (success, loan_or_error_message)
        """
        can_apply, reason = self.can_apply_loan(loan_type, amount, collateral is not None)
        if not can_apply:
            return False, reason
        
        product = self.loan_products[loan_type]
        
        if term_months < product.min_term or term_months > product.max_term:
            return False, f"贷款期限需在 {product.min_term} 到 {product.max_term} 个月之间"
        
        # 计算利率和月供
        rate = self.get_rate_for_user(loan_type)
        monthly_payment = self.calculate_monthly_payment(amount, rate, term_months, repayment_method)
        
        # 创建贷款
        loan_id = f"LOAN_{int(time.time())}_{loan_type.value[:2]}"
        loan = Loan(
            id=loan_id,
            loan_type=loan_type,
            principal=amount,
            annual_rate=rate,
            term_months=term_months,
            remaining_months=term_months,
            remaining_principal=float(amount),
            repayment_method=repayment_method,
            monthly_payment=round(monthly_payment, 2),
            collateral=collateral
        )
        
        self.loans[loan_id] = loan
        
        # 每笔新贷款轻微影响信用分
        self._adjust_credit_score(-2)
        
        return True, loan
    
    def process_monthly_payment(self, loan_id: str) -> Dict:
        """处理月度还款
        
        Returns:
            还款详情
        """
        loan = self.loans.get(loan_id)
        if not loan:
            return {"error": "贷款不存在"}
        
        if loan.remaining_months <= 0:
            return {"error": "贷款已还清"}
        
        monthly_rate = loan.annual_rate / 12
        
        # 计算本月利息
        interest_payment = loan.remaining_principal * monthly_rate
        
        if loan.repayment_method == RepaymentMethod.EQUAL_INSTALLMENT:
            principal_payment = loan.monthly_payment - interest_payment
        elif loan.repayment_method == RepaymentMethod.EQUAL_PRINCIPAL:
            principal_payment = loan.principal / loan.term_months
        elif loan.repayment_method == RepaymentMethod.INTEREST_ONLY:
            principal_payment = 0 if loan.remaining_months > 1 else loan.remaining_principal
        else:  # BULLET
            if loan.remaining_months == 1:
                principal_payment = loan.remaining_principal
                interest_payment = loan.principal * loan.annual_rate * (loan.term_months / 12)
            else:
                principal_payment = 0
                interest_payment = 0
        
        total_payment = principal_payment + interest_payment
        
        # 更新贷款状态
        loan.remaining_principal -= principal_payment
        loan.remaining_months -= 1
        
        # 还清检查
        if loan.remaining_months <= 0 or loan.remaining_principal <= 0:
            loan.remaining_principal = 0
            loan.remaining_months = 0
        
        return {
            "loan_id": loan_id,
            "loan_type": loan.loan_type.value,
            "total_payment": round(total_payment, 2),
            "principal_payment": round(principal_payment, 2),
            "interest_payment": round(interest_payment, 2),
            "remaining_principal": round(loan.remaining_principal, 2),
            "remaining_months": loan.remaining_months,
            "is_paid_off": loan.remaining_months <= 0
        }
    
    def process_all_monthly_payments(self) -> List[Dict]:
        """处理所有贷款的月度还款"""
        results = []
        for loan_id in list(self.loans.keys()):
            loan = self.loans[loan_id]
            if loan.remaining_months > 0:
                result = self.process_monthly_payment(loan_id)
                results.append(result)
        return results
    
    def get_total_monthly_payment(self) -> float:
        """获取所有贷款的总月供"""
        total = 0
        for loan in self.loans.values():
            if loan.remaining_months > 0:
                total += loan.monthly_payment
        return round(total, 2)
    
    def get_total_debt(self) -> float:
        """获取总负债"""
        return sum(loan.remaining_principal for loan in self.loans.values())
    
    def mark_overdue(self, loan_id: str, days: int = 30):
        """标记逾期"""
        loan = self.loans.get(loan_id)
        if loan:
            loan.is_overdue = True
            loan.overdue_days += days
            # 逾期严重影响信用分
            self._adjust_credit_score(-min(days // 10, 50))
    
    def early_repayment(self, loan_id: str, amount: int) -> Dict:
        """提前还款
        
        Args:
            loan_id: 贷款ID
            amount: 还款金额
        """
        loan = self.loans.get(loan_id)
        if not loan:
            return {"error": "贷款不存在"}
        
        if amount > loan.remaining_principal:
            amount = loan.remaining_principal
        
        loan.remaining_principal -= amount
        
        # 重新计算剩余期限（保持月供不变）
        if loan.remaining_principal > 0 and loan.monthly_payment > 0:
            monthly_rate = loan.annual_rate / 12
            if monthly_rate > 0:
                import math
                n = math.log(loan.monthly_payment / (loan.monthly_payment - loan.remaining_principal * monthly_rate)) / math.log(1 + monthly_rate)
                loan.remaining_months = max(1, int(n))
        else:
            loan.remaining_months = 0
        
        # 提前还款有利于信用
        self._adjust_credit_score(5)
        
        return {
            "loan_id": loan_id,
            "amount_paid": amount,
            "remaining_principal": round(loan.remaining_principal, 2),
            "remaining_months": loan.remaining_months,
            "is_paid_off": loan.remaining_principal <= 0
        }
    
    def _adjust_credit_score(self, delta: int):
        """调整信用分"""
        self.credit_score = max(300, min(850, self.credit_score + delta))
    
    def get_credit_report(self) -> Dict:
        """获取信用报告"""
        active_loans = [l for l in self.loans.values() if l.remaining_months > 0]
        overdue_loans = [l for l in active_loans if l.is_overdue]
        
        return {
            "credit_score": self.credit_score,
            "credit_level": self._get_credit_level(),
            "total_debt": round(self.get_total_debt(), 2),
            "monthly_payment": self.get_total_monthly_payment(),
            "active_loans": len(active_loans),
            "overdue_loans": len(overdue_loans),
            "credit_limit": self.total_credit_limit,
            "available_credit": max(0, self.total_credit_limit - self.get_total_debt()),
            "debt_ratio": round(self.get_total_debt() / max(1, self.total_credit_limit) * 100, 1)
        }
    
    def _get_credit_level(self) -> str:
        """获取信用等级"""
        if self.credit_score >= 750:
            return "优秀"
        elif self.credit_score >= 700:
            return "良好"
        elif self.credit_score >= 650:
            return "中等"
        elif self.credit_score >= 600:
            return "一般"
        else:
            return "较差"
    
    def get_loans_summary(self) -> List[Dict]:
        """获取贷款摘要"""
        return [
            {
                "id": loan.id,
                "type": loan.loan_type.value,
                "principal": loan.principal,
                "remaining_principal": round(loan.remaining_principal, 2),
                "annual_rate": round(loan.annual_rate * 100, 2),
                "monthly_payment": loan.monthly_payment,
                "remaining_months": loan.remaining_months,
                "is_overdue": loan.is_overdue,
                "collateral": loan.collateral
            }
            for loan in self.loans.values()
        ]


# 全局实例
debt_system = DebtSystem()
