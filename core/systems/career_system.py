"""
职业与收入系统 - EchoPolis
实现职业发展、跳槽升职、副业创业、被动收入
"""
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class CareerLevel(Enum):
    """职业等级"""
    INTERN = "实习生"
    JUNIOR = "初级员工"
    MID = "中级员工"
    SENIOR = "高级员工"
    LEAD = "团队负责人"
    MANAGER = "部门经理"
    DIRECTOR = "总监"
    VP = "副总裁"
    CXO = "高管"


class Industry(Enum):
    """行业"""
    TECH = "科技互联网"
    FINANCE = "金融"
    CONSULTING = "咨询"
    HEALTHCARE = "医疗健康"
    EDUCATION = "教育"
    MANUFACTURING = "制造业"
    REAL_ESTATE = "房地产"
    RETAIL = "零售消费"
    MEDIA = "传媒娱乐"
    GOVERNMENT = "政府机构"


class SideBusinessType(Enum):
    """副业类型"""
    FREELANCE = "自由职业"
    ECOMMERCE = "电商小店"
    CONTENT_CREATOR = "自媒体"
    TUTOR = "家教培训"
    CONSULTING = "兼职顾问"
    INVESTMENT = "投资理财"
    RENTAL = "房产出租"


@dataclass
class Career:
    """职业信息"""
    industry: Industry
    level: CareerLevel
    company_size: str           # "startup", "medium", "large", "multinational"
    base_salary: int            # 月薪
    bonus_rate: float           # 年终奖系数 (月薪倍数)
    stock_options: int          # 期权价值
    years_in_position: int      # 当前职位年数
    total_experience: int       # 总工作年限 (月)
    skills: List[str] = field(default_factory=list)
    reputation: int = 50        # 职场声誉 (0-100)
    burnout: int = 0           # 倦怠值 (0-100)


@dataclass
class SideBusiness:
    """副业"""
    business_type: SideBusinessType
    name: str
    monthly_revenue: int        # 月收入
    monthly_cost: int          # 月成本
    time_required: int         # 每月需要小时数
    start_month: int           # 开始月份
    success_rate: float        # 成功概率
    is_active: bool = True


@dataclass
class PassiveIncome:
    """被动收入"""
    source: str                # 来源
    income_type: str           # "dividend", "rental", "royalty", "interest"
    monthly_amount: int
    start_month: int
    is_permanent: bool = True


# 薪资基准表 (月薪)
SALARY_TABLE = {
    Industry.TECH: {
        CareerLevel.INTERN: (3000, 6000),
        CareerLevel.JUNIOR: (8000, 15000),
        CareerLevel.MID: (15000, 25000),
        CareerLevel.SENIOR: (25000, 40000),
        CareerLevel.LEAD: (35000, 55000),
        CareerLevel.MANAGER: (45000, 70000),
        CareerLevel.DIRECTOR: (60000, 100000),
        CareerLevel.VP: (80000, 150000),
        CareerLevel.CXO: (100000, 300000),
    },
    Industry.FINANCE: {
        CareerLevel.INTERN: (4000, 8000),
        CareerLevel.JUNIOR: (10000, 20000),
        CareerLevel.MID: (20000, 35000),
        CareerLevel.SENIOR: (35000, 60000),
        CareerLevel.LEAD: (50000, 80000),
        CareerLevel.MANAGER: (70000, 120000),
        CareerLevel.DIRECTOR: (100000, 180000),
        CareerLevel.VP: (150000, 300000),
        CareerLevel.CXO: (200000, 500000),
    },
    Industry.CONSULTING: {
        CareerLevel.INTERN: (5000, 10000),
        CareerLevel.JUNIOR: (12000, 22000),
        CareerLevel.MID: (22000, 38000),
        CareerLevel.SENIOR: (38000, 65000),
        CareerLevel.LEAD: (55000, 90000),
        CareerLevel.MANAGER: (80000, 130000),
        CareerLevel.DIRECTOR: (110000, 200000),
        CareerLevel.VP: (160000, 350000),
        CareerLevel.CXO: (250000, 600000),
    },
}

# 默认薪资（其他行业）
DEFAULT_SALARY = {
    CareerLevel.INTERN: (2500, 5000),
    CareerLevel.JUNIOR: (6000, 12000),
    CareerLevel.MID: (12000, 20000),
    CareerLevel.SENIOR: (20000, 35000),
    CareerLevel.LEAD: (30000, 50000),
    CareerLevel.MANAGER: (40000, 70000),
    CareerLevel.DIRECTOR: (55000, 100000),
    CareerLevel.VP: (70000, 150000),
    CareerLevel.CXO: (90000, 250000),
}


class CareerSystem:
    """职业系统"""
    
    # 升职所需月数（最少）
    PROMOTION_MONTHS = {
        CareerLevel.INTERN: 3,
        CareerLevel.JUNIOR: 12,
        CareerLevel.MID: 18,
        CareerLevel.SENIOR: 24,
        CareerLevel.LEAD: 24,
        CareerLevel.MANAGER: 36,
        CareerLevel.DIRECTOR: 48,
        CareerLevel.VP: 60,
    }
    
    # 职级顺序
    LEVEL_ORDER = list(CareerLevel)
    
    def __init__(self):
        self.careers: Dict[str, Career] = {}
        self.side_businesses: Dict[str, List[SideBusiness]] = {}
        self.passive_incomes: Dict[str, List[PassiveIncome]] = {}
    
    def create_career(self, session_id: str, industry: Industry = None, 
                     level: CareerLevel = CareerLevel.JUNIOR) -> Career:
        """创建职业"""
        if industry is None:
            industry = random.choice(list(Industry))
        
        # 生成薪资
        salary_range = SALARY_TABLE.get(industry, DEFAULT_SALARY).get(level, (8000, 15000))
        base_salary = random.randint(salary_range[0], salary_range[1])
        
        # 公司规模影响
        company_sizes = ["startup", "medium", "large", "multinational"]
        company_size = random.choice(company_sizes)
        
        size_multipliers = {
            "startup": 0.85,
            "medium": 1.0,
            "large": 1.1,
            "multinational": 1.2
        }
        base_salary = int(base_salary * size_multipliers[company_size])
        
        # 年终奖系数
        bonus_rates = {
            "startup": random.uniform(0, 2),      # 0-2个月，不稳定
            "medium": random.uniform(1, 3),       # 1-3个月
            "large": random.uniform(2, 4),        # 2-4个月
            "multinational": random.uniform(3, 6) # 3-6个月
        }
        
        career = Career(
            industry=industry,
            level=level,
            company_size=company_size,
            base_salary=base_salary,
            bonus_rate=round(bonus_rates[company_size], 1),
            stock_options=0 if company_size != "startup" else random.randint(0, 50000),
            years_in_position=0,
            total_experience=0,
            skills=[],
            reputation=50,
            burnout=0
        )
        
        self.careers[session_id] = career
        return career
    
    def get_monthly_salary(self, session_id: str) -> Dict:
        """获取月薪信息"""
        career = self.careers.get(session_id)
        if not career:
            return {"base_salary": 0, "total": 0}
        
        # 基本工资
        base = career.base_salary
        
        # 绩效浮动 (-10% ~ +20%)
        performance = random.uniform(-0.1, 0.2)
        performance_bonus = int(base * performance)
        
        # 加班费（如果burnout高）
        overtime = int(base * 0.1 * (career.burnout / 100)) if career.burnout > 30 else 0
        
        total = base + performance_bonus + overtime
        
        return {
            "base_salary": base,
            "performance_bonus": performance_bonus,
            "overtime": overtime,
            "total": total,
            "level": career.level.value,
            "industry": career.industry.value
        }
    
    def get_annual_bonus(self, session_id: str, month: int) -> int:
        """获取年终奖（12月发放）"""
        if month != 12:
            return 0
        
        career = self.careers.get(session_id)
        if not career:
            return 0
        
        # 年终奖 = 月薪 × 系数 × 绩效调整
        performance_factor = random.uniform(0.8, 1.5)
        bonus = int(career.base_salary * career.bonus_rate * performance_factor)
        
        return bonus
    
    def check_promotion(self, session_id: str) -> Optional[Dict]:
        """检查是否有升职机会"""
        career = self.careers.get(session_id)
        if not career:
            return None
        
        # 获取当前职级索引
        current_idx = self.LEVEL_ORDER.index(career.level)
        if current_idx >= len(self.LEVEL_ORDER) - 1:
            return None  # 已经是最高级
        
        # 检查时间要求
        required_months = self.PROMOTION_MONTHS.get(career.level, 24)
        if career.years_in_position < required_months:
            return None
        
        # 计算升职概率
        base_prob = 0.15
        
        # 声誉加成
        reputation_bonus = (career.reputation - 50) / 200
        
        # 技能加成
        skill_bonus = len(career.skills) * 0.02
        
        # 倦怠惩罚
        burnout_penalty = career.burnout / 500
        
        total_prob = base_prob + reputation_bonus + skill_bonus - burnout_penalty
        total_prob = max(0.05, min(0.5, total_prob))
        
        if random.random() < total_prob:
            next_level = self.LEVEL_ORDER[current_idx + 1]
            
            # 计算新薪资
            salary_range = SALARY_TABLE.get(career.industry, DEFAULT_SALARY).get(next_level, (20000, 35000))
            new_salary = random.randint(salary_range[0], salary_range[1])
            
            # 确保涨薪
            new_salary = max(new_salary, int(career.base_salary * 1.2))
            
            return {
                "type": "promotion",
                "old_level": career.level.value,
                "new_level": next_level.value,
                "old_salary": career.base_salary,
                "new_salary": new_salary,
                "salary_increase": new_salary - career.base_salary,
                "increase_rate": round((new_salary - career.base_salary) / career.base_salary * 100, 1)
            }
        
        return None
    
    def apply_promotion(self, session_id: str, new_level: CareerLevel, new_salary: int):
        """应用升职"""
        career = self.careers.get(session_id)
        if career:
            career.level = new_level
            career.base_salary = new_salary
            career.years_in_position = 0
            career.reputation = min(100, career.reputation + 10)
    
    def check_job_opportunity(self, session_id: str) -> Optional[Dict]:
        """检查跳槽机会"""
        career = self.careers.get(session_id)
        if not career:
            return None
        
        # 每月5%概率收到猎头邀请
        if random.random() > 0.05:
            return None
        
        # 生成新机会
        new_industry = random.choice(list(Industry))
        
        # 可能升一级或平级
        current_idx = self.LEVEL_ORDER.index(career.level)
        if random.random() < 0.3 and current_idx < len(self.LEVEL_ORDER) - 1:
            new_level = self.LEVEL_ORDER[current_idx + 1]
        else:
            new_level = career.level
        
        # 新公司薪资（通常有溢价）
        salary_range = SALARY_TABLE.get(new_industry, DEFAULT_SALARY).get(new_level, (15000, 30000))
        base_offer = random.randint(salary_range[0], salary_range[1])
        
        # 跳槽溢价 10-30%
        premium = random.uniform(1.1, 1.3)
        offer_salary = int(base_offer * premium)
        
        # 确保比现在高
        offer_salary = max(offer_salary, int(career.base_salary * 1.15))
        
        company_size = random.choice(["startup", "medium", "large", "multinational"])
        
        return {
            "type": "job_offer",
            "industry": new_industry.value,
            "level": new_level.value,
            "company_size": company_size,
            "offer_salary": offer_salary,
            "current_salary": career.base_salary,
            "increase_rate": round((offer_salary - career.base_salary) / career.base_salary * 100, 1),
            "new_bonus_rate": round(random.uniform(1, 4), 1),
            "stock_options": random.randint(0, 100000) if company_size == "startup" else 0
        }
    
    def accept_job_offer(self, session_id: str, offer: Dict):
        """接受跳槽邀请"""
        career = self.careers.get(session_id)
        if not career:
            return
        
        career.industry = Industry(offer["industry"])
        career.level = CareerLevel(offer["level"])
        career.company_size = offer["company_size"]
        career.base_salary = offer["offer_salary"]
        career.bonus_rate = offer["new_bonus_rate"]
        career.stock_options = offer.get("stock_options", 0)
        career.years_in_position = 0
        career.burnout = max(0, career.burnout - 20)  # 新环境减少倦怠
    
    def check_layoff(self, session_id: str, economic_phase: str) -> Optional[Dict]:
        """检查裁员风险"""
        career = self.careers.get(session_id)
        if not career:
            return None
        
        # 基础裁员概率
        base_prob = 0.01
        
        # 经济衰退增加概率
        if economic_phase == "contraction":
            base_prob += 0.03
        elif economic_phase == "trough":
            base_prob += 0.02
        
        # 创业公司风险更高
        if career.company_size == "startup":
            base_prob += 0.02
        
        # 低声誉增加风险
        if career.reputation < 40:
            base_prob += 0.02
        
        if random.random() < base_prob:
            # 计算遣散费（N+1）
            months_worked = career.total_experience
            severance = career.base_salary * (months_worked // 12 + 1)
            severance = min(severance, career.base_salary * 12)  # 最多12个月
            
            return {
                "type": "layoff",
                "severance": severance,
                "unemployment_months": random.randint(1, 6),
                "reason": random.choice([
                    "公司业务调整",
                    "部门裁撤",
                    "经济下行裁员",
                    "公司重组"
                ])
            }
        
        return None
    
    def start_side_business(self, session_id: str, business_type: SideBusinessType,
                           investment: int, current_month: int) -> Tuple[bool, str]:
        """开始副业"""
        if session_id not in self.side_businesses:
            self.side_businesses[session_id] = []
        
        # 检查是否已有同类副业
        existing = [b for b in self.side_businesses[session_id] 
                   if b.business_type == business_type and b.is_active]
        if existing:
            return False, "已有同类型副业在运营"
        
        # 副业配置
        business_config = {
            SideBusinessType.FREELANCE: {
                "min_investment": 0,
                "revenue_range": (2000, 8000),
                "cost_range": (0, 500),
                "time_required": 20,
                "success_rate": 0.7
            },
            SideBusinessType.ECOMMERCE: {
                "min_investment": 5000,
                "revenue_range": (3000, 15000),
                "cost_range": (1000, 5000),
                "time_required": 30,
                "success_rate": 0.5
            },
            SideBusinessType.CONTENT_CREATOR: {
                "min_investment": 2000,
                "revenue_range": (500, 20000),
                "cost_range": (200, 1000),
                "time_required": 25,
                "success_rate": 0.3
            },
            SideBusinessType.TUTOR: {
                "min_investment": 0,
                "revenue_range": (3000, 10000),
                "cost_range": (0, 200),
                "time_required": 15,
                "success_rate": 0.8
            },
            SideBusinessType.CONSULTING: {
                "min_investment": 0,
                "revenue_range": (5000, 20000),
                "cost_range": (0, 500),
                "time_required": 10,
                "success_rate": 0.6
            },
        }
        
        config = business_config.get(business_type, {
            "min_investment": 1000,
            "revenue_range": (1000, 5000),
            "cost_range": (200, 1000),
            "time_required": 20,
            "success_rate": 0.5
        })
        
        if investment < config["min_investment"]:
            return False, f"启动资金不足，最少需要 ¥{config['min_investment']:,}"
        
        # 创建副业
        business = SideBusiness(
            business_type=business_type,
            name=f"我的{business_type.value}",
            monthly_revenue=0,  # 初始没有收入
            monthly_cost=random.randint(*config["cost_range"]),
            time_required=config["time_required"],
            start_month=current_month,
            success_rate=config["success_rate"],
            is_active=True
        )
        
        self.side_businesses[session_id].append(business)
        return True, f"成功启动{business_type.value}副业"
    
    def update_side_businesses(self, session_id: str, current_month: int) -> List[Dict]:
        """更新副业状态（每月调用）"""
        if session_id not in self.side_businesses:
            return []
        
        results = []
        
        for business in self.side_businesses[session_id]:
            if not business.is_active:
                continue
            
            months_running = current_month - business.start_month
            
            # 成功概率随时间增加
            adjusted_rate = min(0.9, business.success_rate + months_running * 0.02)
            
            if random.random() < adjusted_rate:
                # 副业成功，产生收入
                config = {
                    SideBusinessType.FREELANCE: (2000, 8000),
                    SideBusinessType.ECOMMERCE: (3000, 15000),
                    SideBusinessType.CONTENT_CREATOR: (500, 20000),
                    SideBusinessType.TUTOR: (3000, 10000),
                    SideBusinessType.CONSULTING: (5000, 20000),
                }
                revenue_range = config.get(business.business_type, (1000, 5000))
                
                # 收入随经验增长
                growth_factor = 1 + months_running * 0.05
                revenue = int(random.randint(*revenue_range) * growth_factor)
                business.monthly_revenue = revenue
                
                net_income = revenue - business.monthly_cost
                
                results.append({
                    "business_type": business.business_type.value,
                    "name": business.name,
                    "revenue": revenue,
                    "cost": business.monthly_cost,
                    "net_income": net_income,
                    "status": "success"
                })
            else:
                # 副业遇到困难
                business.monthly_revenue = 0
                results.append({
                    "business_type": business.business_type.value,
                    "name": business.name,
                    "revenue": 0,
                    "cost": business.monthly_cost,
                    "net_income": -business.monthly_cost,
                    "status": "struggling"
                })
        
        return results
    
    def add_passive_income(self, session_id: str, source: str, income_type: str,
                          monthly_amount: int, start_month: int):
        """添加被动收入"""
        if session_id not in self.passive_incomes:
            self.passive_incomes[session_id] = []
        
        income = PassiveIncome(
            source=source,
            income_type=income_type,
            monthly_amount=monthly_amount,
            start_month=start_month
        )
        self.passive_incomes[session_id].append(income)
    
    def get_passive_income(self, session_id: str) -> List[Dict]:
        """获取被动收入列表"""
        if session_id not in self.passive_incomes:
            return []
        
        return [
            {
                "source": p.source,
                "income_type": p.income_type,
                "monthly_amount": p.monthly_amount
            }
            for p in self.passive_incomes[session_id]
            if p.is_permanent
        ]
    
    def get_total_monthly_income(self, session_id: str, month: int) -> Dict:
        """获取总月收入"""
        # 工资收入
        salary_info = self.get_monthly_salary(session_id)
        salary = salary_info.get("total", 0)
        
        # 年终奖
        bonus = self.get_annual_bonus(session_id, month)
        
        # 副业收入
        side_income = 0
        if session_id in self.side_businesses:
            for b in self.side_businesses[session_id]:
                if b.is_active:
                    side_income += b.monthly_revenue - b.monthly_cost
        
        # 被动收入
        passive = 0
        if session_id in self.passive_incomes:
            for p in self.passive_incomes[session_id]:
                passive += p.monthly_amount
        
        total = salary + bonus + side_income + passive
        
        return {
            "salary": salary,
            "bonus": bonus,
            "side_business": side_income,
            "passive": passive,
            "total": total
        }
    
    def advance_month(self, session_id: str):
        """月度更新"""
        career = self.careers.get(session_id)
        if career:
            career.years_in_position += 1
            career.total_experience += 1
            
            # 倦怠累积
            if career.burnout < 80:
                career.burnout += random.randint(0, 3)
            
            # 休假可以降低倦怠（简化处理）
            if random.random() < 0.1:
                career.burnout = max(0, career.burnout - 10)
    
    def get_career_summary(self, session_id: str) -> Dict:
        """获取职业摘要"""
        career = self.careers.get(session_id)
        if not career:
            return {"status": "unemployed"}
        
        return {
            "status": "employed",
            "industry": career.industry.value,
            "level": career.level.value,
            "company_size": career.company_size,
            "base_salary": career.base_salary,
            "bonus_rate": career.bonus_rate,
            "stock_options": career.stock_options,
            "months_in_position": career.years_in_position,
            "total_experience_months": career.total_experience,
            "skills": career.skills,
            "reputation": career.reputation,
            "burnout": career.burnout,
            "side_businesses": len(self.side_businesses.get(session_id, [])),
            "passive_income_sources": len(self.passive_incomes.get(session_id, []))
        }
    
    def get_available_jobs(self) -> List[Dict]:
        """获取所有可用职位"""
        jobs = []
        for industry in Industry:
            for level in CareerLevel:
                base_salary = self._calculate_base_salary(industry, level)
                jobs.append({
                    "id": f"{industry.value}_{level.value}",
                    "title": self._get_job_title(industry, level),
                    "industry": industry.value,
                    "level": level.value,
                    "level_name": self._get_level_name(level),
                    "base_salary": base_salary,
                    "requirements": self._get_job_requirements(level)
                })
        return jobs
    
    def _get_job_title(self, industry: Industry, level: CareerLevel) -> str:
        """获取职位名称"""
        titles = {
            Industry.TECH: {
                CareerLevel.INTERN: "技术实习生",
                CareerLevel.JUNIOR: "初级程序员",
                CareerLevel.SENIOR: "高级程序员",
                CareerLevel.LEAD: "技术主管",
                CareerLevel.MANAGER: "技术经理",
                CareerLevel.DIRECTOR: "技术总监",
                CareerLevel.VP: "技术VP",
                CareerLevel.CXO: "CTO"
            },
            Industry.FINANCE: {
                CareerLevel.INTERN: "金融实习生",
                CareerLevel.JUNIOR: "银行柜员",
                CareerLevel.SENIOR: "投资分析师",
                CareerLevel.LEAD: "高级分析师",
                CareerLevel.MANAGER: "基金经理",
                CareerLevel.DIRECTOR: "投资总监",
                CareerLevel.VP: "副总裁",
                CareerLevel.CXO: "CFO"
            },
            Industry.MANUFACTURING: {
                CareerLevel.INTERN: "生产实习生",
                CareerLevel.JUNIOR: "生产专员",
                CareerLevel.SENIOR: "生产工程师",
                CareerLevel.LEAD: "生产主管",
                CareerLevel.MANAGER: "生产经理",
                CareerLevel.DIRECTOR: "生产总监",
                CareerLevel.VP: "运营VP",
                CareerLevel.CXO: "COO"
            },
            Industry.HEALTHCARE: {
                CareerLevel.INTERN: "医疗实习生",
                CareerLevel.JUNIOR: "医疗助理",
                CareerLevel.SENIOR: "医疗顾问",
                CareerLevel.LEAD: "科室主管",
                CareerLevel.MANAGER: "部门经理",
                CareerLevel.DIRECTOR: "医疗总监",
                CareerLevel.VP: "副院长",
                CareerLevel.CXO: "院长"
            },
            Industry.RETAIL: {
                CareerLevel.INTERN: "零售实习生",
                CareerLevel.JUNIOR: "销售专员",
                CareerLevel.SENIOR: "销售主管",
                CareerLevel.LEAD: "区域主管",
                CareerLevel.MANAGER: "门店经理",
                CareerLevel.DIRECTOR: "区域总监",
                CareerLevel.VP: "销售VP",
                CareerLevel.CXO: "CEO"
            }
        }
        return titles.get(industry, {}).get(level, f"{industry.value}员工")
    
    def _get_level_name(self, level: CareerLevel) -> str:
        """获取级别名称"""
        names = {
            CareerLevel.INTERN: "实习",
            CareerLevel.JUNIOR: "初级",
            CareerLevel.SENIOR: "高级",
            CareerLevel.LEAD: "主管",
            CareerLevel.MANAGER: "经理",
            CareerLevel.DIRECTOR: "总监",
            CareerLevel.VP: "副总裁",
            CareerLevel.CXO: "C级高管"
        }
        return names.get(level, "员工")
    
    def _get_job_requirements(self, level: CareerLevel) -> str:
        """获取职位要求"""
        reqs = {
            CareerLevel.INTERN: "无",
            CareerLevel.JUNIOR: "无",
            CareerLevel.SENIOR: "2年经验",
            CareerLevel.LEAD: "4年经验",
            CareerLevel.MANAGER: "管理技能",
            CareerLevel.DIRECTOR: "6年经验+管理",
            CareerLevel.VP: "10年经验",
            CareerLevel.CXO: "15年经验"
        }
        return reqs.get(level, "无")
    
    def _calculate_base_salary(self, industry: Industry, level: CareerLevel) -> int:
        """计算基础薪资"""
        base = {
            Industry.TECH: 12000,
            Industry.FINANCE: 15000,
            Industry.MANUFACTURING: 8000,
            Industry.HEALTHCARE: 10000,
            Industry.RETAIL: 6000
        }.get(industry, 8000)
        
        multiplier = {
            CareerLevel.INTERN: 0.4,
            CareerLevel.JUNIOR: 1.0,
            CareerLevel.SENIOR: 1.8,
            CareerLevel.LEAD: 2.5,
            CareerLevel.MANAGER: 3.5,
            CareerLevel.DIRECTOR: 5.0,
            CareerLevel.VP: 8.0,
            CareerLevel.CXO: 15.0
        }.get(level, 1.0)
        
        return int(base * multiplier)
    
    def get_career_status(self, session_id: str) -> Dict:
        """获取玩家当前职业状态"""
        career = self.careers.get(session_id)
        if not career:
            # 返回空职业状态而不是 None，避免调用方出错
            return {
                "job_id": None,
                "title": None,
                "industry": None,
                "level": None,
                "level_name": None,
                "salary": 0,
                "months": 0,
                "performance": None
            }
        
        return {
            "job_id": f"{career.industry.value}_{career.level.value}",
            "title": self._get_job_title(career.industry, career.level),
            "industry": career.industry.value,
            "level": career.level.value,
            "level_name": self._get_level_name(career.level),
            "salary": career.base_salary,
            "months": career.years_in_position,
            "performance": "A" if career.reputation > 80 else "B" if career.reputation > 50 else "C"
        }
    
    def apply_for_job(self, session_id: str, job_id: str, player_skills: Dict = None) -> Dict:
        """申请职位"""
        try:
            parts = job_id.split("_")
            industry = Industry(parts[0])
            level = CareerLevel(parts[1])
            
            # 创建新职业
            career = Career(
                industry=industry,
                level=level,
                company_size=random.choice(["small", "medium", "large"]),
                base_salary=self._calculate_base_salary(industry, level)
            )
            self.careers[session_id] = career
            
            return {"success": True, "message": "入职成功！"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def resign(self, session_id: str) -> Dict:
        """辞职"""
        if session_id in self.careers:
            del self.careers[session_id]
            return {"success": True, "message": "已辞职"}
        return {"success": False, "message": "当前没有工作"}
    
    def get_all_skills(self) -> List[Dict]:
        """获取所有可学习技能"""
        return [
            {"id": "programming", "name": "编程", "icon": "💻", "cost": 5000, "description": "软件开发能力"},
            {"id": "investing", "name": "投资", "icon": "📈", "cost": 8000, "description": "投资分析能力"},
            {"id": "management", "name": "管理", "icon": "👔", "cost": 10000, "description": "团队管理能力"},
            {"id": "marketing", "name": "营销", "icon": "📣", "cost": 6000, "description": "市场推广能力"},
            {"id": "finance", "name": "财务", "icon": "💰", "cost": 7000, "description": "财务分析能力"},
            {"id": "design", "name": "设计", "icon": "🎨", "cost": 5000, "description": "创意设计能力"},
            {"id": "communication", "name": "沟通", "icon": "🗣️", "cost": 3000, "description": "人际沟通能力"},
            {"id": "leadership", "name": "领导力", "icon": "👑", "cost": 12000, "description": "领导团队能力"}
        ]
    
    def learn_skill(self, session_id: str, skill_id: str) -> Dict:
        """学习技能"""
        skills = {s["id"]: s for s in self.get_all_skills()}
        if skill_id not in skills:
            return {"success": False, "message": "技能不存在"}
        
        # 简化：直接返回成功（实际应扣钱并记录）
        return {"success": True, "message": f"成功学习 {skills[skill_id]['name']}！"}
    
    def get_available_side_businesses(self) -> List[Dict]:
        """获取可用副业列表"""
        return [
            {
                "id": "content",
                "name": "自媒体",
                "icon": "📱",
                "description": "运营短视频/公众号",
                "startup_cost": 2000,
                "min_income": 500,
                "max_income": 5000,
                "time_required": 25
            },
            {
                "id": "freelance",
                "name": "接单设计",
                "icon": "🎨",
                "description": "平面设计/UI设计",
                "startup_cost": 5000,
                "min_income": 2000,
                "max_income": 8000,
                "time_required": 20
            },
            {
                "id": "tutor",
                "name": "家教辅导",
                "icon": "📚",
                "description": "辅导学生功课",
                "startup_cost": 0,
                "min_income": 1000,
                "max_income": 4000,
                "time_required": 15
            },
            {
                "id": "ecommerce",
                "name": "电商代购",
                "icon": "🛒",
                "description": "开网店/做代购",
                "startup_cost": 10000,
                "min_income": 3000,
                "max_income": 15000,
                "time_required": 30
            },
            {
                "id": "consulting",
                "name": "咨询顾问",
                "icon": "💼",
                "description": "提供专业咨询",
                "startup_cost": 0,
                "min_income": 5000,
                "max_income": 20000,
                "time_required": 10
            },
            {
                "id": "driver",
                "name": "网约车",
                "icon": "🚗",
                "description": "兼职开网约车",
                "startup_cost": 0,
                "min_income": 2000,
                "max_income": 6000,
                "time_required": 20
            }
        ]


# 全局实例
career_system = CareerSystem()
