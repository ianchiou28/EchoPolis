"""
现金流系统 - EchoPolis
管理收入、支出、现金流预警
"""
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class IncomeType(Enum):
    """收入类型"""
    SALARY = "工资收入"
    INVESTMENT = "投资收益"
    DIVIDEND = "股息分红"
    RENTAL = "租金收入"
    BUSINESS = "经营收入"
    BONUS = "奖金"
    SIDE_JOB = "副业收入"
    OTHER = "其他收入"


class ExpenseType(Enum):
    """支出类型"""
    LIVING = "生活开支"          # 日常生活必需
    HOUSING = "住房支出"          # 房租/房贷
    FOOD = "餐饮支出"
    TRANSPORT = "交通出行"
    ENTERTAINMENT = "娱乐消费"
    EDUCATION = "教育培训"
    HEALTHCARE = "医疗健康"
    INSURANCE = "保险费用"
    TAX = "税费"
    LOAN = "贷款还款"
    INVESTMENT = "投资支出"
    OTHER = "其他支出"


class ExpenseNecessity(Enum):
    """支出必要性"""
    ESSENTIAL = "必需"          # 不可削减
    IMPORTANT = "重要"          # 可适当削减
    OPTIONAL = "可选"           # 可大幅削减
    LUXURY = "奢侈"             # 可完全取消


@dataclass
class IncomeItem:
    """收入项"""
    id: str
    income_type: IncomeType
    name: str
    amount: int
    is_recurring: bool = True       # 是否每月循环
    months_remaining: int = -1      # 剩余月数，-1表示永久
    tax_rate: float = 0             # 适用税率
    source: str = ""                # 收入来源描述
    
    def get_after_tax(self) -> int:
        """获取税后金额"""
        return int(self.amount * (1 - self.tax_rate))


@dataclass
class ExpenseItem:
    """支出项"""
    id: str
    expense_type: ExpenseType
    name: str
    amount: int
    is_recurring: bool = True
    months_remaining: int = -1
    necessity: ExpenseNecessity = ExpenseNecessity.IMPORTANT
    can_defer: bool = False         # 是否可延期
    

@dataclass
class CashFlowWarning:
    """现金流预警"""
    level: str                      # critical/warning/info
    message: str
    suggestion: str
    projected_shortfall: int = 0


class CashFlowSystem:
    """现金流管理系统"""
    
    # 基础生活费参考（按城市等级）
    BASE_LIVING_COST = {
        "一线城市": 5000,
        "二线城市": 3500,
        "三线城市": 2500,
        "其他": 2000
    }
    
    # 收入税率阶梯（简化版个税）
    TAX_BRACKETS = [
        (0, 5000, 0),           # 5000以下免税
        (5000, 8000, 0.03),     # 3%
        (8000, 17000, 0.10),    # 10%
        (17000, 30000, 0.20),   # 20%
        (30000, 40000, 0.25),   # 25%
        (40000, 60000, 0.30),   # 30%
        (60000, 85000, 0.35),   # 35%
        (85000, float('inf'), 0.45)  # 45%
    ]
    
    def __init__(self, city_level: str = "二线城市"):
        self.city_level = city_level
        self.incomes: Dict[str, IncomeItem] = {}
        self.expenses: Dict[str, ExpenseItem] = {}
        self.history: List[Dict] = []  # 月度现金流记录
        
        # 初始化基础生活支出
        self._init_basic_expenses()
    
    def _init_basic_expenses(self):
        """初始化基础生活支出"""
        base_cost = self.BASE_LIVING_COST.get(self.city_level, 2500)
        
        # 必要生活开支
        self.add_expense(ExpenseItem(
            id="EXP_LIVING_BASIC",
            expense_type=ExpenseType.LIVING,
            name="日常生活费",
            amount=int(base_cost * 0.5),
            necessity=ExpenseNecessity.ESSENTIAL
        ))
        
        self.add_expense(ExpenseItem(
            id="EXP_FOOD",
            expense_type=ExpenseType.FOOD,
            name="餐饮费用",
            amount=int(base_cost * 0.3),
            necessity=ExpenseNecessity.ESSENTIAL
        ))
        
        self.add_expense(ExpenseItem(
            id="EXP_TRANSPORT",
            expense_type=ExpenseType.TRANSPORT,
            name="交通出行",
            amount=int(base_cost * 0.15),
            necessity=ExpenseNecessity.IMPORTANT
        ))
        
        self.add_expense(ExpenseItem(
            id="EXP_TELECOM",
            expense_type=ExpenseType.LIVING,
            name="通讯费用",
            amount=int(base_cost * 0.05),
            necessity=ExpenseNecessity.IMPORTANT
        ))
    
    def calculate_income_tax(self, monthly_income: int) -> Tuple[int, float]:
        """计算个人所得税
        
        Returns:
            (税额, 实际税率)
        """
        taxable_income = monthly_income
        total_tax = 0
        
        for lower, upper, rate in self.TAX_BRACKETS:
            if taxable_income <= 0:
                break
            bracket_income = min(taxable_income, upper - lower)
            if taxable_income > lower:
                tax_in_bracket = bracket_income * rate
                total_tax += tax_in_bracket
                taxable_income -= bracket_income
        
        effective_rate = total_tax / monthly_income if monthly_income > 0 else 0
        return int(total_tax), round(effective_rate, 4)
    
    def add_income(self, income: IncomeItem):
        """添加收入项"""
        # 自动计算税率（工资收入）
        if income.income_type == IncomeType.SALARY and income.tax_rate == 0:
            _, tax_rate = self.calculate_income_tax(income.amount)
            income.tax_rate = tax_rate
        
        self.incomes[income.id] = income
    
    def remove_income(self, income_id: str):
        """移除收入项"""
        if income_id in self.incomes:
            del self.incomes[income_id]
    
    def add_expense(self, expense: ExpenseItem):
        """添加支出项"""
        self.expenses[expense.id] = expense
    
    def remove_expense(self, expense_id: str):
        """移除支出项"""
        if expense_id in self.expenses:
            del self.expenses[expense_id]
    
    def add_housing_expense(self, is_rent: bool, amount: int):
        """添加住房支出（房租或房贷）"""
        expense_id = "EXP_HOUSING"
        name = "房租" if is_rent else "房贷月供"
        
        self.add_expense(ExpenseItem(
            id=expense_id,
            expense_type=ExpenseType.HOUSING,
            name=name,
            amount=amount,
            necessity=ExpenseNecessity.ESSENTIAL,
            can_defer=False
        ))
    
    def add_loan_payment(self, loan_id: str, loan_name: str, amount: int):
        """添加贷款还款"""
        self.add_expense(ExpenseItem(
            id=f"EXP_LOAN_{loan_id}",
            expense_type=ExpenseType.LOAN,
            name=f"{loan_name}还款",
            amount=amount,
            necessity=ExpenseNecessity.ESSENTIAL,
            can_defer=False
        ))
    
    def add_insurance_payment(self, insurance_id: str, insurance_name: str, amount: int):
        """添加保险费"""
        self.add_expense(ExpenseItem(
            id=f"EXP_INS_{insurance_id}",
            expense_type=ExpenseType.INSURANCE,
            name=insurance_name,
            amount=amount,
            necessity=ExpenseNecessity.IMPORTANT,
            can_defer=True
        ))
    
    def get_total_income(self, include_tax: bool = False) -> int:
        """获取总收入
        
        Args:
            include_tax: True返回税前，False返回税后
        """
        total = 0
        for income in self.incomes.values():
            if income.months_remaining != 0:
                if include_tax:
                    total += income.amount
                else:
                    total += income.get_after_tax()
        return total
    
    def get_total_expense(self) -> int:
        """获取总支出"""
        total = 0
        for expense in self.expenses.values():
            if expense.months_remaining != 0:
                total += expense.amount
        return total
    
    def get_monthly_cashflow(self) -> int:
        """获取月度净现金流（税后收入 - 支出）"""
        return self.get_total_income(include_tax=False) - self.get_total_expense()
    
    def get_essential_expenses(self) -> int:
        """获取必要支出总额"""
        return sum(
            e.amount for e in self.expenses.values()
            if e.necessity in [ExpenseNecessity.ESSENTIAL, ExpenseNecessity.IMPORTANT]
            and e.months_remaining != 0
        )
    
    def get_savings_rate(self) -> float:
        """获取储蓄率"""
        income = self.get_total_income()
        if income == 0:
            return 0
        return (self.get_monthly_cashflow() / income)
    
    def check_cashflow_health(self, current_cash: int) -> List[CashFlowWarning]:
        """检查现金流健康状况
        
        Args:
            current_cash: 当前现金余额
        
        Returns:
            预警列表
        """
        warnings = []
        
        monthly_cashflow = self.get_monthly_cashflow()
        total_income = self.get_total_income()
        total_expense = self.get_total_expense()
        essential_expense = self.get_essential_expenses()
        
        # 1. 收不抵支
        if monthly_cashflow < 0:
            months_until_broke = current_cash / abs(monthly_cashflow) if monthly_cashflow < 0 else float('inf')
            
            if months_until_broke <= 1:
                warnings.append(CashFlowWarning(
                    level="critical",
                    message="⚠️ 严重警告：下个月将入不敷出！",
                    suggestion="立即削减非必要开支或寻求额外收入来源",
                    projected_shortfall=abs(monthly_cashflow)
                ))
            elif months_until_broke <= 3:
                warnings.append(CashFlowWarning(
                    level="warning",
                    message=f"⚠️ 警告：按当前支出，约{int(months_until_broke)}个月后将耗尽现金",
                    suggestion="建议减少消费或增加收入",
                    projected_shortfall=abs(monthly_cashflow)
                ))
        
        # 2. 现金储备不足
        emergency_fund = essential_expense * 6  # 建议6个月应急金
        if current_cash < emergency_fund:
            if current_cash < essential_expense * 3:
                warnings.append(CashFlowWarning(
                    level="warning",
                    message="💰 应急储备金不足3个月支出",
                    suggestion=f"建议积累至少 ¥{emergency_fund:,} 作为应急金"
                ))
            else:
                warnings.append(CashFlowWarning(
                    level="info",
                    message="💰 应急储备金未达到6个月目标",
                    suggestion="继续积累应急金，提高财务安全性"
                ))
        
        # 3. 储蓄率过低
        savings_rate = self.get_savings_rate()
        if savings_rate < 0.1 and monthly_cashflow >= 0:
            warnings.append(CashFlowWarning(
                level="info",
                message="📊 储蓄率较低（<10%）",
                suggestion="建议提高储蓄率至收入的20%以上"
            ))
        
        # 4. 住房支出过高
        housing_expense = sum(
            e.amount for e in self.expenses.values()
            if e.expense_type == ExpenseType.HOUSING
        )
        if total_income > 0 and housing_expense / total_income > 0.4:
            warnings.append(CashFlowWarning(
                level="warning",
                message="🏠 住房支出占比过高（>40%）",
                suggestion="住房支出建议控制在收入的30%以内"
            ))
        
        # 5. 负债支出过高
        loan_expense = sum(
            e.amount for e in self.expenses.values()
            if e.expense_type == ExpenseType.LOAN
        )
        if total_income > 0 and loan_expense / total_income > 0.5:
            warnings.append(CashFlowWarning(
                level="critical",
                message="📉 负债率过高（>50%）",
                suggestion="尝试提前还款或整合债务，降低利息支出"
            ))
        
        return warnings
    
    def project_future_cashflow(self, months: int = 12, current_cash: int = 0) -> List[Dict]:
        """预测未来现金流
        
        Args:
            months: 预测月数
            current_cash: 当前现金
        
        Returns:
            每月现金流预测
        """
        projections = []
        cash = current_cash
        
        # 复制收支项用于模拟
        temp_incomes = {k: IncomeItem(**vars(v)) for k, v in self.incomes.items()}
        temp_expenses = {k: ExpenseItem(**vars(v)) for k, v in self.expenses.items()}
        
        for month in range(1, months + 1):
            month_income = 0
            month_expense = 0
            
            # 计算收入
            for income in temp_incomes.values():
                if income.months_remaining != 0:
                    month_income += income.get_after_tax()
                    if income.months_remaining > 0:
                        income.months_remaining -= 1
            
            # 计算支出
            for expense in temp_expenses.values():
                if expense.months_remaining != 0:
                    month_expense += expense.amount
                    if expense.months_remaining > 0:
                        expense.months_remaining -= 1
            
            net_flow = month_income - month_expense
            cash += net_flow
            
            projections.append({
                "month": month,
                "income": month_income,
                "expense": month_expense,
                "net_flow": net_flow,
                "ending_cash": cash,
                "status": "positive" if cash > 0 else "negative"
            })
        
        return projections
    
    def process_monthly(self) -> Dict:
        """处理月度现金流"""
        month_record = {
            "timestamp": time.time(),
            "incomes": [],
            "expenses": [],
            "total_income": 0,
            "total_expense": 0,
            "net_flow": 0
        }
        
        # 处理收入
        for income in list(self.incomes.values()):
            if income.months_remaining != 0:
                after_tax = income.get_after_tax()
                month_record["incomes"].append({
                    "name": income.name,
                    "type": income.income_type.value,
                    "gross": income.amount,
                    "tax": income.amount - after_tax,
                    "net": after_tax
                })
                month_record["total_income"] += after_tax
                
                if income.months_remaining > 0:
                    income.months_remaining -= 1
                    if income.months_remaining == 0:
                        del self.incomes[income.id]
        
        # 处理支出
        for expense in list(self.expenses.values()):
            if expense.months_remaining != 0:
                month_record["expenses"].append({
                    "name": expense.name,
                    "type": expense.expense_type.value,
                    "amount": expense.amount,
                    "necessity": expense.necessity.value
                })
                month_record["total_expense"] += expense.amount
                
                if expense.months_remaining > 0:
                    expense.months_remaining -= 1
                    if expense.months_remaining == 0:
                        del self.expenses[expense.id]
        
        month_record["net_flow"] = month_record["total_income"] - month_record["total_expense"]
        self.history.append(month_record)
        
        return month_record
    
    def get_expense_breakdown(self) -> Dict[str, int]:
        """获取支出分类汇总"""
        breakdown = {}
        for expense in self.expenses.values():
            if expense.months_remaining != 0:
                category = expense.expense_type.value
                breakdown[category] = breakdown.get(category, 0) + expense.amount
        return breakdown
    
    def get_income_breakdown(self) -> Dict[str, int]:
        """获取收入分类汇总"""
        breakdown = {}
        for income in self.incomes.values():
            if income.months_remaining != 0:
                category = income.income_type.value
                breakdown[category] = breakdown.get(category, 0) + income.get_after_tax()
        return breakdown
    
    def get_summary(self) -> Dict:
        """获取现金流摘要"""
        return {
            "total_income": self.get_total_income(),
            "total_income_pretax": self.get_total_income(include_tax=True),
            "total_expense": self.get_total_expense(),
            "monthly_cashflow": self.get_monthly_cashflow(),
            "savings_rate": round(self.get_savings_rate() * 100, 1),
            "essential_expense": self.get_essential_expenses(),
            "income_breakdown": self.get_income_breakdown(),
            "expense_breakdown": self.get_expense_breakdown(),
            "income_sources": len([i for i in self.incomes.values() if i.months_remaining != 0]),
            "expense_items": len([e for e in self.expenses.values() if e.months_remaining != 0])
        }


# 全局实例
cashflow_system = CashFlowSystem()
