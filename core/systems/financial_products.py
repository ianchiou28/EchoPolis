"""
金融产品体系 - EchoPolis
定义各类金融产品的风险收益特性
"""
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    VERY_LOW = "极低风险"
    LOW = "低风险"
    MEDIUM = "中等风险"
    HIGH = "高风险"
    VERY_HIGH = "极高风险"


class ProductCategory(Enum):
    """产品类别"""
    DEPOSIT = "存款"
    BOND = "债券"
    FUND = "基金"
    STOCK = "股票"
    DERIVATIVE = "衍生品"
    INSURANCE = "保险"
    REAL_ESTATE = "房产"
    ALTERNATIVE = "另类投资"


@dataclass
class ReturnProfile:
    """收益特性"""
    expected_annual_return: float   # 预期年化收益 (0.05 = 5%)
    volatility: float               # 波动率 (标准差)
    min_return: float              # 最低可能收益 (年化)
    max_return: float              # 最高可能收益 (年化)
    is_fixed: bool = False         # 是否固定收益
    
    def calculate_monthly_return(self, market_modifier: float = 0) -> float:
        """计算月度收益率"""
        if self.is_fixed:
            return self.expected_annual_return / 12
        
        # 基于正态分布的月度收益
        monthly_vol = self.volatility / (12 ** 0.5)
        monthly_expected = self.expected_annual_return / 12
        
        raw_return = random.gauss(monthly_expected, monthly_vol)
        raw_return += market_modifier
        
        # 限制在合理范围内
        annual_equivalent = raw_return * 12
        annual_equivalent = max(self.min_return, min(self.max_return, annual_equivalent))
        
        return annual_equivalent / 12


@dataclass
class FinancialProduct:
    """金融产品定义"""
    id: str                         # 产品ID
    name: str                       # 产品名称
    category: ProductCategory       # 产品类别
    risk_level: RiskLevel          # 风险等级
    return_profile: ReturnProfile  # 收益特性
    min_investment: int            # 最低投资额
    min_holding_months: int        # 最短持有期 (月)
    max_holding_months: int        # 最长持有期 (月), 0表示无限制
    early_redemption_fee: float    # 提前赎回费率
    management_fee: float          # 管理费率 (年化)
    description: str               # 产品描述
    unlock_condition: Optional[str] = None  # 解锁条件
    leverage: float = 1.0          # 杠杆倍数
    can_margin_call: bool = False  # 是否可能爆仓
    margin_call_threshold: float = 0.0  # 爆仓阈值 (亏损比例)


# ============ 产品库定义 ============

# 存款类产品
DEPOSIT_PRODUCTS = [
    FinancialProduct(
        id="DEP_CURRENT",
        name="活期存款",
        category=ProductCategory.DEPOSIT,
        risk_level=RiskLevel.VERY_LOW,
        return_profile=ReturnProfile(0.003, 0, 0.003, 0.003, is_fixed=True),
        min_investment=1,
        min_holding_months=0,
        max_holding_months=0,
        early_redemption_fee=0,
        management_fee=0,
        description="随存随取，流动性最强，收益最低"
    ),
    FinancialProduct(
        id="DEP_3M",
        name="3个月定期",
        category=ProductCategory.DEPOSIT,
        risk_level=RiskLevel.VERY_LOW,
        return_profile=ReturnProfile(0.015, 0, 0.015, 0.015, is_fixed=True),
        min_investment=1000,
        min_holding_months=3,
        max_holding_months=3,
        early_redemption_fee=0,
        management_fee=0,
        description="三个月定期存款，保本保息"
    ),
    FinancialProduct(
        id="DEP_1Y",
        name="1年定期",
        category=ProductCategory.DEPOSIT,
        risk_level=RiskLevel.VERY_LOW,
        return_profile=ReturnProfile(0.022, 0, 0.022, 0.022, is_fixed=True),
        min_investment=1000,
        min_holding_months=12,
        max_holding_months=12,
        early_redemption_fee=0,
        management_fee=0,
        description="一年定期存款，收益略高"
    ),
    FinancialProduct(
        id="DEP_3Y",
        name="3年定期",
        category=ProductCategory.DEPOSIT,
        risk_level=RiskLevel.VERY_LOW,
        return_profile=ReturnProfile(0.028, 0, 0.028, 0.028, is_fixed=True),
        min_investment=5000,
        min_holding_months=36,
        max_holding_months=36,
        early_redemption_fee=0,
        management_fee=0,
        description="三年定期存款，锁定较高收益"
    ),
]

# 债券类产品
BOND_PRODUCTS = [
    FinancialProduct(
        id="BOND_TREASURY",
        name="国债",
        category=ProductCategory.BOND,
        risk_level=RiskLevel.VERY_LOW,
        return_profile=ReturnProfile(0.032, 0.005, 0.025, 0.04, is_fixed=False),
        min_investment=1000,
        min_holding_months=12,
        max_holding_months=60,
        early_redemption_fee=0.005,
        management_fee=0,
        description="国家信用背书，安全性最高"
    ),
    FinancialProduct(
        id="BOND_CORP_AAA",
        name="AAA级企业债",
        category=ProductCategory.BOND,
        risk_level=RiskLevel.LOW,
        return_profile=ReturnProfile(0.045, 0.02, 0.02, 0.08, is_fixed=False),
        min_investment=5000,
        min_holding_months=6,
        max_holding_months=36,
        early_redemption_fee=0.01,
        management_fee=0.002,
        description="高评级企业债券，收益稳定"
    ),
    FinancialProduct(
        id="BOND_HIGH_YIELD",
        name="高收益债券",
        category=ProductCategory.BOND,
        risk_level=RiskLevel.MEDIUM,
        return_profile=ReturnProfile(0.08, 0.06, -0.1, 0.15, is_fixed=False),
        min_investment=10000,
        min_holding_months=6,
        max_holding_months=24,
        early_redemption_fee=0.02,
        management_fee=0.005,
        description="高收益伴随高风险，可能违约",
        unlock_condition="完成债券投资课程"
    ),
]

# 基金类产品
FUND_PRODUCTS = [
    FinancialProduct(
        id="FUND_MONEY",
        name="货币基金",
        category=ProductCategory.FUND,
        risk_level=RiskLevel.VERY_LOW,
        return_profile=ReturnProfile(0.025, 0.003, 0.015, 0.035, is_fixed=False),
        min_investment=100,
        min_holding_months=0,
        max_holding_months=0,
        early_redemption_fee=0,
        management_fee=0.003,
        description="类现金管理工具，T+1赎回"
    ),
    FinancialProduct(
        id="FUND_BOND",
        name="债券基金",
        category=ProductCategory.FUND,
        risk_level=RiskLevel.LOW,
        return_profile=ReturnProfile(0.05, 0.04, -0.05, 0.12, is_fixed=False),
        min_investment=1000,
        min_holding_months=1,
        max_holding_months=0,
        early_redemption_fee=0.005,
        management_fee=0.006,
        description="主要投资债券，波动较小"
    ),
    FinancialProduct(
        id="FUND_BALANCED",
        name="平衡型基金",
        category=ProductCategory.FUND,
        risk_level=RiskLevel.MEDIUM,
        return_profile=ReturnProfile(0.08, 0.10, -0.15, 0.25, is_fixed=False),
        min_investment=1000,
        min_holding_months=3,
        max_holding_months=0,
        early_redemption_fee=0.01,
        management_fee=0.012,
        description="股债混合配置，攻守兼备"
    ),
    FinancialProduct(
        id="FUND_INDEX",
        name="沪深300指数基金",
        category=ProductCategory.FUND,
        risk_level=RiskLevel.MEDIUM,
        return_profile=ReturnProfile(0.10, 0.18, -0.30, 0.40, is_fixed=False),
        min_investment=100,
        min_holding_months=0,
        max_holding_months=0,
        early_redemption_fee=0.005,
        management_fee=0.005,
        description="跟踪大盘指数，费率低廉"
    ),
    FinancialProduct(
        id="FUND_TECH",
        name="科技主题基金",
        category=ProductCategory.FUND,
        risk_level=RiskLevel.HIGH,
        return_profile=ReturnProfile(0.15, 0.28, -0.40, 0.60, is_fixed=False),
        min_investment=1000,
        min_holding_months=6,
        max_holding_months=0,
        early_redemption_fee=0.015,
        management_fee=0.015,
        description="聚焦科技板块，高弹性"
    ),
    FinancialProduct(
        id="FUND_HEALTHCARE",
        name="医疗健康基金",
        category=ProductCategory.FUND,
        risk_level=RiskLevel.MEDIUM,
        return_profile=ReturnProfile(0.12, 0.22, -0.30, 0.50, is_fixed=False),
        min_investment=1000,
        min_holding_months=6,
        max_holding_months=0,
        early_redemption_fee=0.015,
        management_fee=0.015,
        description="长期看好医疗产业"
    ),
    FinancialProduct(
        id="FUND_NEW_ENERGY",
        name="新能源基金",
        category=ProductCategory.FUND,
        risk_level=RiskLevel.HIGH,
        return_profile=ReturnProfile(0.18, 0.35, -0.50, 0.80, is_fixed=False),
        min_investment=1000,
        min_holding_months=6,
        max_holding_months=0,
        early_redemption_fee=0.015,
        management_fee=0.015,
        description="碳中和大趋势下的热门赛道"
    ),
]

# 衍生品
DERIVATIVE_PRODUCTS = [
    FinancialProduct(
        id="DER_FUTURES_INDEX",
        name="股指期货",
        category=ProductCategory.DERIVATIVE,
        risk_level=RiskLevel.VERY_HIGH,
        return_profile=ReturnProfile(0.0, 0.50, -1.0, 2.0, is_fixed=False),
        min_investment=50000,
        min_holding_months=0,
        max_holding_months=3,
        early_redemption_fee=0,
        management_fee=0.0005,
        description="10倍杠杆，可做多做空",
        unlock_condition="完成期货交易课程",
        leverage=10.0,
        can_margin_call=True,
        margin_call_threshold=0.8  # 亏损80%强平
    ),
    FinancialProduct(
        id="DER_OPTIONS_CALL",
        name="认购期权",
        category=ProductCategory.DERIVATIVE,
        risk_level=RiskLevel.VERY_HIGH,
        return_profile=ReturnProfile(0.0, 1.0, -1.0, 5.0, is_fixed=False),
        min_investment=5000,
        min_holding_months=0,
        max_holding_months=3,
        early_redemption_fee=0,
        management_fee=0.001,
        description="看涨期权，最大损失为权利金",
        unlock_condition="完成期权交易课程",
        leverage=5.0,
        can_margin_call=False
    ),
    FinancialProduct(
        id="DER_OPTIONS_PUT",
        name="认沽期权",
        category=ProductCategory.DERIVATIVE,
        risk_level=RiskLevel.VERY_HIGH,
        return_profile=ReturnProfile(0.0, 1.0, -1.0, 5.0, is_fixed=False),
        min_investment=5000,
        min_holding_months=0,
        max_holding_months=3,
        early_redemption_fee=0,
        management_fee=0.001,
        description="看跌期权，用于对冲风险",
        unlock_condition="完成期权交易课程",
        leverage=5.0,
        can_margin_call=False
    ),
]

# 房产投资
REAL_ESTATE_PRODUCTS = [
    FinancialProduct(
        id="RE_REITS",
        name="房地产信托基金(REITs)",
        category=ProductCategory.REAL_ESTATE,
        risk_level=RiskLevel.MEDIUM,
        return_profile=ReturnProfile(0.08, 0.15, -0.20, 0.30, is_fixed=False),
        min_investment=10000,
        min_holding_months=12,
        max_holding_months=0,
        early_redemption_fee=0.02,
        management_fee=0.01,
        description="享受房产收益，无需巨额首付"
    ),
    FinancialProduct(
        id="RE_APARTMENT",
        name="住宅公寓",
        category=ProductCategory.REAL_ESTATE,
        risk_level=RiskLevel.MEDIUM,
        return_profile=ReturnProfile(0.05, 0.08, -0.10, 0.15, is_fixed=False),
        min_investment=500000,
        min_holding_months=24,
        max_holding_months=0,
        early_redemption_fee=0.03,
        management_fee=0,
        description="长期持有，租金+增值"
    ),
    FinancialProduct(
        id="RE_COMMERCIAL",
        name="商业地产",
        category=ProductCategory.REAL_ESTATE,
        risk_level=RiskLevel.HIGH,
        return_profile=ReturnProfile(0.07, 0.12, -0.20, 0.25, is_fixed=False),
        min_investment=1000000,
        min_holding_months=36,
        max_holding_months=0,
        early_redemption_fee=0.05,
        management_fee=0,
        description="商铺/写字楼，收益波动大",
        unlock_condition="总资产超过200万"
    ),
]

# 另类投资
ALTERNATIVE_PRODUCTS = [
    FinancialProduct(
        id="ALT_GOLD",
        name="黄金ETF",
        category=ProductCategory.ALTERNATIVE,
        risk_level=RiskLevel.MEDIUM,
        return_profile=ReturnProfile(0.05, 0.15, -0.20, 0.30, is_fixed=False),
        min_investment=1000,
        min_holding_months=0,
        max_holding_months=0,
        early_redemption_fee=0.005,
        management_fee=0.004,
        description="避险资产，对冲通胀"
    ),
    FinancialProduct(
        id="ALT_CRYPTO",
        name="数字货币基金",
        category=ProductCategory.ALTERNATIVE,
        risk_level=RiskLevel.VERY_HIGH,
        return_profile=ReturnProfile(0.0, 0.80, -0.80, 2.0, is_fixed=False),
        min_investment=10000,
        min_holding_months=0,
        max_holding_months=0,
        early_redemption_fee=0.02,
        management_fee=0.02,
        description="高波动高风险，非主流资产",
        unlock_condition="完成数字资产课程"
    ),
    FinancialProduct(
        id="ALT_PRIVATE_EQUITY",
        name="私募股权",
        category=ProductCategory.ALTERNATIVE,
        risk_level=RiskLevel.HIGH,
        return_profile=ReturnProfile(0.15, 0.25, -0.50, 1.0, is_fixed=False),
        min_investment=100000,
        min_holding_months=36,
        max_holding_months=60,
        early_redemption_fee=0.10,
        management_fee=0.02,
        description="长期锁定，潜在高回报",
        unlock_condition="总资产超过50万"
    ),
]


class FinancialProductLibrary:
    """金融产品库管理器"""
    
    def __init__(self):
        self.products: Dict[str, FinancialProduct] = {}
        self._load_all_products()
    
    def _load_all_products(self):
        """加载所有产品"""
        all_products = (
            DEPOSIT_PRODUCTS + 
            BOND_PRODUCTS + 
            FUND_PRODUCTS + 
            DERIVATIVE_PRODUCTS + 
            REAL_ESTATE_PRODUCTS + 
            ALTERNATIVE_PRODUCTS
        )
        
        for product in all_products:
            self.products[product.id] = product
    
    def get_product(self, product_id: str) -> Optional[FinancialProduct]:
        """获取产品"""
        return self.products.get(product_id)
    
    def get_products_by_category(self, category: ProductCategory) -> List[FinancialProduct]:
        """按类别获取产品"""
        return [p for p in self.products.values() if p.category == category]
    
    def get_products_by_risk(self, risk_level: RiskLevel) -> List[FinancialProduct]:
        """按风险等级获取产品"""
        return [p for p in self.products.values() if p.risk_level == risk_level]
    
    def get_available_products(self, 
                               cash: int, 
                               total_assets: int,
                               completed_courses: List[str]) -> List[FinancialProduct]:
        """获取用户可购买的产品
        
        Args:
            cash: 可用现金
            total_assets: 总资产
            completed_courses: 已完成的课程列表
        """
        available = []
        
        for product in self.products.values():
            # 检查最低投资额
            if cash < product.min_investment:
                continue
            
            # 检查解锁条件
            if product.unlock_condition:
                # 检查是否是课程条件
                if "课程" in product.unlock_condition:
                    course_name = product.unlock_condition.replace("完成", "").strip()
                    if course_name not in completed_courses:
                        continue
                
                # 检查是否是资产条件
                if "总资产超过" in product.unlock_condition:
                    import re
                    match = re.search(r'(\d+)', product.unlock_condition)
                    if match:
                        required_assets = int(match.group(1)) * 10000  # 假设单位是万
                        if total_assets < required_assets:
                            continue
            
            available.append(product)
        
        return available
    
    def calculate_product_return(self, 
                                 product_id: str, 
                                 amount: int,
                                 months: int,
                                 market_modifier: float = 0) -> Dict:
        """计算产品收益
        
        Args:
            product_id: 产品ID
            amount: 投资金额
            months: 持有月数
            market_modifier: 市场影响因子
        
        Returns:
            包含收益详情的字典
        """
        product = self.get_product(product_id)
        if not product:
            return {"error": "Product not found"}
        
        total_return_rate = 0
        monthly_returns = []
        
        for _ in range(months):
            monthly_rate = product.return_profile.calculate_monthly_return(market_modifier)
            
            # 应用杠杆
            if product.leverage > 1:
                monthly_rate *= product.leverage
            
            monthly_returns.append(monthly_rate)
            total_return_rate += monthly_rate
        
        # 扣除管理费
        management_fee_total = product.management_fee * (months / 12)
        net_return_rate = total_return_rate - management_fee_total
        
        final_value = amount * (1 + net_return_rate)
        profit = final_value - amount
        
        # 检查是否爆仓
        margin_called = False
        if product.can_margin_call:
            cumulative = 0
            for mr in monthly_returns:
                cumulative += mr
                if cumulative <= -product.margin_call_threshold:
                    margin_called = True
                    final_value = 0
                    profit = -amount
                    break
        
        return {
            "product_id": product_id,
            "product_name": product.name,
            "initial_amount": amount,
            "months": months,
            "total_return_rate": round(net_return_rate * 100, 2),
            "final_value": round(final_value, 2),
            "profit": round(profit, 2),
            "margin_called": margin_called,
            "monthly_returns": [round(r * 100, 2) for r in monthly_returns]
        }
    
    def get_product_summary(self) -> Dict:
        """获取产品库摘要"""
        summary = {
            "total_products": len(self.products),
            "by_category": {},
            "by_risk": {}
        }
        
        for cat in ProductCategory:
            products = self.get_products_by_category(cat)
            summary["by_category"][cat.value] = len(products)
        
        for risk in RiskLevel:
            products = self.get_products_by_risk(risk)
            summary["by_risk"][risk.value] = len(products)
        
        return summary


# 全局实例
product_library = FinancialProductLibrary()
