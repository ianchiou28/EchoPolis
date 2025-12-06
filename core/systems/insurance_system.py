"""
保险系统 - EchoPolis
提供各类保险产品，抵御风险事件
"""
import time
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class InsuranceType(Enum):
    """保险类型"""
    HEALTH = "医疗险"
    LIFE = "寿险"
    ACCIDENT = "意外险"
    PROPERTY = "财产险"
    UNEMPLOYMENT = "失业险"
    INVESTMENT = "投资保险"


class ClaimStatus(Enum):
    """理赔状态"""
    PENDING = "审核中"
    APPROVED = "已批准"
    REJECTED = "已拒绝"
    PAID = "已赔付"


@dataclass
class InsuranceProduct:
    """保险产品"""
    id: str
    name: str
    insurance_type: InsuranceType
    monthly_premium: int            # 月保费
    coverage_amount: int            # 保额
    deductible: int                 # 免赔额
    coverage_ratio: float           # 赔付比例 (0.8 = 80%)
    min_term_months: int            # 最短保障期
    max_claim_times: int            # 最大理赔次数
    waiting_days: int               # 等待期（天）
    description: str
    covers: List[str]               # 保障内容列表


@dataclass
class InsurancePolicy:
    """保单"""
    id: str
    product_id: str
    product_name: str
    insurance_type: InsuranceType
    monthly_premium: int
    coverage_amount: int
    deductible: int
    coverage_ratio: float
    start_month: int                # 生效月份
    remaining_months: int           # 剩余月数，-1表示长期
    claim_count: int = 0            # 已理赔次数
    max_claims: int = 1             # 最大理赔次数
    is_active: bool = True
    created_at: float = field(default_factory=time.time)


@dataclass
class InsuranceClaim:
    """理赔记录"""
    id: str
    policy_id: str
    event_type: str                 # 事件类型
    event_description: str
    claim_amount: int               # 申请金额
    approved_amount: int = 0        # 批准金额
    status: ClaimStatus = ClaimStatus.PENDING
    created_at: float = field(default_factory=time.time)


# 保险产品库
INSURANCE_PRODUCTS = [
    # 医疗险
    InsuranceProduct(
        id="INS_HEALTH_BASIC",
        name="基础医疗险",
        insurance_type=InsuranceType.HEALTH,
        monthly_premium=200,
        coverage_amount=100000,
        deductible=1000,
        coverage_ratio=0.7,
        min_term_months=12,
        max_claim_times=3,
        waiting_days=30,
        description="基础医疗保障，覆盖门诊和住院费用",
        covers=["门诊费用", "住院费用", "手术费用"]
    ),
    InsuranceProduct(
        id="INS_HEALTH_PRO",
        name="尊享医疗险",
        insurance_type=InsuranceType.HEALTH,
        monthly_premium=500,
        coverage_amount=500000,
        deductible=0,
        coverage_ratio=0.9,
        min_term_months=12,
        max_claim_times=5,
        waiting_days=15,
        description="高端医疗保障，0免赔，覆盖更广",
        covers=["门诊费用", "住院费用", "手术费用", "重疾保障", "海外就医"]
    ),
    
    # 意外险
    InsuranceProduct(
        id="INS_ACCIDENT",
        name="综合意外险",
        insurance_type=InsuranceType.ACCIDENT,
        monthly_premium=50,
        coverage_amount=500000,
        deductible=0,
        coverage_ratio=1.0,
        min_term_months=12,
        max_claim_times=1,
        waiting_days=0,
        description="意外伤害保障，包含意外身故和伤残",
        covers=["意外身故", "意外伤残", "意外医疗"]
    ),
    
    # 财产险
    InsuranceProduct(
        id="INS_PROPERTY_HOME",
        name="家庭财产险",
        insurance_type=InsuranceType.PROPERTY,
        monthly_premium=100,
        coverage_amount=300000,
        deductible=500,
        coverage_ratio=0.8,
        min_term_months=12,
        max_claim_times=2,
        waiting_days=7,
        description="保障房屋及室内财产损失",
        covers=["火灾", "水灾", "盗窃", "自然灾害"]
    ),
    InsuranceProduct(
        id="INS_PROPERTY_INVESTMENT",
        name="投资保障险",
        insurance_type=InsuranceType.INVESTMENT,
        monthly_premium=300,
        coverage_amount=200000,
        deductible=5000,
        coverage_ratio=0.5,
        min_term_months=6,
        max_claim_times=1,
        waiting_days=30,
        description="保障投资亏损，降低极端损失",
        covers=["股票暴跌", "基金清盘", "P2P暴雷"]
    ),
    
    # 失业险
    InsuranceProduct(
        id="INS_UNEMPLOYMENT",
        name="失业收入保障险",
        insurance_type=InsuranceType.UNEMPLOYMENT,
        monthly_premium=150,
        coverage_amount=10000,  # 每月赔付上限
        deductible=0,
        coverage_ratio=0.6,     # 赔付原工资60%
        min_term_months=12,
        max_claim_times=1,
        waiting_days=60,
        description="失业后最长赔付3个月基本收入",
        covers=["非自愿失业", "公司倒闭"]
    ),
    
    # 寿险
    InsuranceProduct(
        id="INS_LIFE_TERM",
        name="定期寿险",
        insurance_type=InsuranceType.LIFE,
        monthly_premium=100,
        coverage_amount=1000000,
        deductible=0,
        coverage_ratio=1.0,
        min_term_months=120,
        max_claim_times=1,
        waiting_days=90,
        description="定期寿险，身故赔付百万保额",
        covers=["身故赔付", "全残赔付"]
    ),
]


class InsuranceSystem:
    """保险管理系统"""
    
    def __init__(self):
        self.products = {p.id: p for p in INSURANCE_PRODUCTS}
        self.policies: Dict[str, InsurancePolicy] = {}  # policy_id -> InsurancePolicy
        self.claims: List[InsuranceClaim] = []
        self.current_month = 0
    
    def get_available_products(self) -> List[InsuranceProduct]:
        """获取所有可购买的保险产品"""
        return list(self.products.values())
    
    def get_products_by_type(self, insurance_type: InsuranceType) -> List[InsuranceProduct]:
        """按类型获取保险产品"""
        return [p for p in self.products.values() if p.insurance_type == insurance_type]
    
    def purchase_insurance(self, product_id: str, term_months: int = -1) -> tuple:
        """购买保险
        
        Args:
            product_id: 产品ID
            term_months: 保障期限，-1表示长期
        
        Returns:
            (success, policy_or_error)
        """
        product = self.products.get(product_id)
        if not product:
            return False, "保险产品不存在"
        
        if term_months > 0 and term_months < product.min_term_months:
            return False, f"最短保障期为 {product.min_term_months} 个月"
        
        # 检查是否已有同类型保险
        existing = [p for p in self.policies.values() 
                   if p.is_active and p.insurance_type == product.insurance_type]
        if existing:
            return False, f"已有{product.insurance_type.value}在保，不可重复购买"
        
        policy_id = f"POL_{int(time.time())}_{product_id[-4:]}"
        policy = InsurancePolicy(
            id=policy_id,
            product_id=product_id,
            product_name=product.name,
            insurance_type=product.insurance_type,
            monthly_premium=product.monthly_premium,
            coverage_amount=product.coverage_amount,
            deductible=product.deductible,
            coverage_ratio=product.coverage_ratio,
            start_month=self.current_month,
            remaining_months=term_months,
            max_claims=product.max_claim_times
        )
        
        self.policies[policy_id] = policy
        return True, policy
    
    def cancel_insurance(self, policy_id: str) -> tuple:
        """退保"""
        policy = self.policies.get(policy_id)
        if not policy:
            return False, "保单不存在"
        
        if not policy.is_active:
            return False, "保单已失效"
        
        policy.is_active = False
        # 简化：不计算退保金额
        return True, "退保成功"
    
    def process_monthly(self) -> Dict:
        """月度处理"""
        self.current_month += 1
        result = {
            "total_premium": 0,
            "expired_policies": [],
            "active_policies": []
        }
        
        for policy in list(self.policies.values()):
            if not policy.is_active:
                continue
            
            # 扣除保费
            result["total_premium"] += policy.monthly_premium
            
            # 更新剩余期限
            if policy.remaining_months > 0:
                policy.remaining_months -= 1
                if policy.remaining_months <= 0:
                    policy.is_active = False
                    result["expired_policies"].append(policy.product_name)
                else:
                    result["active_policies"].append({
                        "name": policy.product_name,
                        "remaining": policy.remaining_months
                    })
            else:
                result["active_policies"].append({
                    "name": policy.product_name,
                    "remaining": "长期"
                })
        
        return result
    
    def check_coverage(self, event_type: str, amount: int) -> Dict:
        """检查是否有保障覆盖某事件
        
        Args:
            event_type: 事件类型（如"疾病"、"意外"、"财产损失"、"失业"）
            amount: 损失金额
        
        Returns:
            保障详情
        """
        coverage_map = {
            "疾病": [InsuranceType.HEALTH],
            "重疾": [InsuranceType.HEALTH],
            "意外": [InsuranceType.ACCIDENT],
            "财产损失": [InsuranceType.PROPERTY],
            "房屋损坏": [InsuranceType.PROPERTY],
            "失业": [InsuranceType.UNEMPLOYMENT],
            "投资亏损": [InsuranceType.INVESTMENT],
            "身故": [InsuranceType.LIFE, InsuranceType.ACCIDENT]
        }
        
        applicable_types = coverage_map.get(event_type, [])
        if not applicable_types:
            return {
                "covered": False,
                "message": "此类事件无保险覆盖"
            }
        
        # 查找有效保单
        for policy in self.policies.values():
            if not policy.is_active:
                continue
            if policy.insurance_type not in applicable_types:
                continue
            if policy.claim_count >= policy.max_claims:
                continue
            
            # 检查等待期
            product = self.products.get(policy.product_id)
            if product and self.current_month - policy.start_month < (product.waiting_days // 30):
                continue
            
            # 计算可赔付金额
            claimable = min(amount, policy.coverage_amount)
            after_deductible = max(0, claimable - policy.deductible)
            payout = int(after_deductible * policy.coverage_ratio)
            
            return {
                "covered": True,
                "policy_id": policy.id,
                "policy_name": policy.product_name,
                "loss_amount": amount,
                "deductible": policy.deductible,
                "coverage_ratio": policy.coverage_ratio,
                "estimated_payout": payout,
                "remaining_claims": policy.max_claims - policy.claim_count
            }
        
        return {
            "covered": False,
            "message": f"无有效{event_type}保障，需自行承担全部损失"
        }
    
    def file_claim(self, policy_id: str, event_type: str, 
                   event_description: str, amount: int) -> tuple:
        """提交理赔
        
        Returns:
            (success, claim_result)
        """
        policy = self.policies.get(policy_id)
        if not policy:
            return False, "保单不存在"
        
        if not policy.is_active:
            return False, "保单已失效"
        
        if policy.claim_count >= policy.max_claims:
            return False, "已达最大理赔次数"
        
        # 计算赔付
        claimable = min(amount, policy.coverage_amount)
        after_deductible = max(0, claimable - policy.deductible)
        payout = int(after_deductible * policy.coverage_ratio)
        
        # 模拟理赔审核（90%通过率）
        approved = random.random() < 0.9
        
        claim = InsuranceClaim(
            id=f"CLM_{int(time.time())}",
            policy_id=policy_id,
            event_type=event_type,
            event_description=event_description,
            claim_amount=amount,
            approved_amount=payout if approved else 0,
            status=ClaimStatus.APPROVED if approved else ClaimStatus.REJECTED
        )
        
        self.claims.append(claim)
        
        if approved:
            policy.claim_count += 1
            return True, {
                "claim_id": claim.id,
                "status": "approved",
                "payout": payout,
                "message": f"理赔成功，获得赔付 ¥{payout:,}"
            }
        else:
            return False, {
                "claim_id": claim.id,
                "status": "rejected",
                "payout": 0,
                "message": "理赔被拒绝，请联系客服申诉"
            }
    
    def get_total_premium(self) -> int:
        """获取当前月总保费"""
        return sum(p.monthly_premium for p in self.policies.values() if p.is_active)
    
    def get_total_coverage(self) -> Dict[str, int]:
        """获取总保额"""
        coverage = {}
        for policy in self.policies.values():
            if policy.is_active:
                type_name = policy.insurance_type.value
                coverage[type_name] = coverage.get(type_name, 0) + policy.coverage_amount
        return coverage
    
    def get_policies_summary(self) -> List[Dict]:
        """获取保单摘要"""
        return [
            {
                "id": p.id,
                "name": p.product_name,
                "type": p.insurance_type.value,
                "premium": p.monthly_premium,
                "coverage": p.coverage_amount,
                "remaining_months": p.remaining_months if p.remaining_months > 0 else "长期",
                "claims_used": f"{p.claim_count}/{p.max_claims}",
                "is_active": p.is_active
            }
            for p in self.policies.values()
        ]
    
    def get_insurance_advice(self, cash: int, monthly_income: int, 
                            has_family: bool = False) -> List[str]:
        """获取保险配置建议"""
        advice = []
        active_types = {p.insurance_type for p in self.policies.values() if p.is_active}
        
        # 基础保障检查
        if InsuranceType.HEALTH not in active_types:
            advice.append("💊 建议购买医疗险，应对疾病风险")
        
        if InsuranceType.ACCIDENT not in active_types:
            advice.append("🚑 建议购买意外险，保费低保额高")
        
        # 根据资产状况建议
        if cash > 500000 and InsuranceType.PROPERTY not in active_types:
            advice.append("🏠 资产较多，建议购买财产险保障")
        
        if monthly_income > 15000 and InsuranceType.UNEMPLOYMENT not in active_types:
            advice.append("💼 收入较高，建议购买失业险对冲风险")
        
        if has_family and InsuranceType.LIFE not in active_types:
            advice.append("👨‍👩‍👧 有家庭责任，建议购买定期寿险")
        
        # 保费占比检查
        total_premium = self.get_total_premium()
        if monthly_income > 0:
            ratio = total_premium / monthly_income
            if ratio > 0.1:
                advice.append(f"⚠️ 保费占收入 {ratio*100:.1f}%，建议控制在10%以内")
            elif ratio < 0.03 and monthly_income > 8000:
                advice.append("📈 保障配置偏低，建议适当增加保险覆盖")
        
        if not advice:
            advice.append("✅ 当前保险配置合理")
        
        return advice


# 全局实例
insurance_system = InsuranceSystem()
