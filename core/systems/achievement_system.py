"""
成就系统 - EchoPolis
记录玩家里程碑，提供成就感和游戏目标
"""
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum


class AchievementCategory(Enum):
    """成就类别"""
    WEALTH = "财富里程碑"
    INVESTMENT = "投资成就"
    SAVING = "储蓄成就"
    DEBT = "债务管理"
    CAREER = "职业发展"
    LIFESTYLE = "生活方式"
    SKILL = "技能解锁"
    SPECIAL = "特殊成就"


class AchievementRarity(Enum):
    """成就稀有度"""
    COMMON = "普通"
    UNCOMMON = "稀有"
    RARE = "史诗"
    LEGENDARY = "传说"
    MYTHIC = "神话"


@dataclass
class Achievement:
    """成就定义"""
    id: str
    name: str
    description: str
    category: AchievementCategory
    rarity: AchievementRarity
    icon: str                           # emoji图标
    condition_desc: str                 # 解锁条件描述
    reward_coins: int = 0               # 奖励金币
    reward_exp: int = 0                 # 奖励经验
    reward_title: Optional[str] = None  # 奖励称号
    hidden: bool = False                # 是否隐藏成就
    prerequisite: Optional[str] = None  # 前置成就ID


@dataclass
class UnlockedAchievement:
    """已解锁的成就"""
    achievement_id: str
    unlocked_at: float = field(default_factory=time.time)
    unlocked_month: int = 0             # 游戏月份


# 成就库
ACHIEVEMENTS: List[Achievement] = [
    # ============ 财富里程碑 ============
    Achievement(
        id="WEALTH_10K",
        name="小有积蓄",
        description="总资产达到1万元",
        category=AchievementCategory.WEALTH,
        rarity=AchievementRarity.COMMON,
        icon="💰",
        condition_desc="总资产 ≥ ¥10,000",
        reward_coins=100,
        reward_exp=50
    ),
    Achievement(
        id="WEALTH_100K",
        name="十万俱乐部",
        description="总资产达到10万元",
        category=AchievementCategory.WEALTH,
        rarity=AchievementRarity.UNCOMMON,
        icon="💎",
        condition_desc="总资产 ≥ ¥100,000",
        reward_coins=500,
        reward_exp=200,
        prerequisite="WEALTH_10K"
    ),
    Achievement(
        id="WEALTH_1M",
        name="百万富翁",
        description="总资产突破100万",
        category=AchievementCategory.WEALTH,
        rarity=AchievementRarity.RARE,
        icon="🏆",
        condition_desc="总资产 ≥ ¥1,000,000",
        reward_coins=2000,
        reward_exp=1000,
        reward_title="百万富翁",
        prerequisite="WEALTH_100K"
    ),
    Achievement(
        id="WEALTH_10M",
        name="千万大佬",
        description="总资产突破1000万",
        category=AchievementCategory.WEALTH,
        rarity=AchievementRarity.LEGENDARY,
        icon="👑",
        condition_desc="总资产 ≥ ¥10,000,000",
        reward_coins=10000,
        reward_exp=5000,
        reward_title="财富自由者",
        prerequisite="WEALTH_1M"
    ),
    Achievement(
        id="WEALTH_100M",
        name="亿万富豪",
        description="总资产突破1亿",
        category=AchievementCategory.WEALTH,
        rarity=AchievementRarity.MYTHIC,
        icon="🌟",
        condition_desc="总资产 ≥ ¥100,000,000",
        reward_coins=50000,
        reward_exp=20000,
        reward_title="传奇富豪",
        prerequisite="WEALTH_10M"
    ),
    
    # ============ 投资成就 ============
    Achievement(
        id="FIRST_STOCK",
        name="初入股市",
        description="第一次购买股票",
        category=AchievementCategory.INVESTMENT,
        rarity=AchievementRarity.COMMON,
        icon="📈",
        condition_desc="购买第一只股票",
        reward_coins=50,
        reward_exp=30
    ),
    Achievement(
        id="STOCK_PROFIT_10K",
        name="股市小赢家",
        description="股票累计盈利1万元",
        category=AchievementCategory.INVESTMENT,
        rarity=AchievementRarity.UNCOMMON,
        icon="📊",
        condition_desc="股票累计盈利 ≥ ¥10,000",
        reward_coins=300,
        reward_exp=150,
        prerequisite="FIRST_STOCK"
    ),
    Achievement(
        id="STOCK_PROFIT_100K",
        name="股市高手",
        description="股票累计盈利10万元",
        category=AchievementCategory.INVESTMENT,
        rarity=AchievementRarity.RARE,
        icon="🎯",
        condition_desc="股票累计盈利 ≥ ¥100,000",
        reward_coins=1000,
        reward_exp=500,
        reward_title="股市高手",
        prerequisite="STOCK_PROFIT_10K"
    ),
    Achievement(
        id="DIVERSIFIED",
        name="分散投资者",
        description="同时持有5种以上不同类型资产",
        category=AchievementCategory.INVESTMENT,
        rarity=AchievementRarity.UNCOMMON,
        icon="🎨",
        condition_desc="持有5种以上不同类型资产",
        reward_coins=500,
        reward_exp=200,
        hidden=True  # 功能暂未实现
    ),
    Achievement(
        id="DIVIDEND_COLLECTOR",
        name="股息收割机",
        description="累计获得1万元股息",
        category=AchievementCategory.INVESTMENT,
        rarity=AchievementRarity.RARE,
        icon="💵",
        condition_desc="累计股息收入 ≥ ¥10,000",
        reward_coins=800,
        reward_exp=400,
        hidden=True  # 股息发放功能暂未实现
    ),
    Achievement(
        id="TEN_BAGGER",
        name="十倍股神话",
        description="单只股票盈利超过10倍",
        category=AchievementCategory.INVESTMENT,
        rarity=AchievementRarity.LEGENDARY,
        icon="🚀",
        condition_desc="单只股票回报率 ≥ 1000%",
        reward_coins=5000,
        reward_exp=2000,
        reward_title="十倍股猎手",
        hidden=True
    ),
    Achievement(
        id="FUND_MASTER",
        name="基金达人",
        description="基金投资累计盈利5万元",
        category=AchievementCategory.INVESTMENT,
        rarity=AchievementRarity.UNCOMMON,
        icon="📦",
        condition_desc="基金累计盈利 ≥ ¥50,000",
        reward_coins=400,
        reward_exp=200,
        hidden=True  # 基金购买功能暂未实现
    ),
    
    # ============ 储蓄成就 ============
    Achievement(
        id="FIRST_DEPOSIT",
        name="存款第一步",
        description="开设第一个定期存款",
        category=AchievementCategory.SAVING,
        rarity=AchievementRarity.COMMON,
        icon="🏦",
        condition_desc="开设定期存款",
        reward_coins=50,
        reward_exp=30
    ),
    Achievement(
        id="EMERGENCY_FUND",
        name="应急储备金",
        description="储蓄账户余额超过6个月支出",
        category=AchievementCategory.SAVING,
        rarity=AchievementRarity.UNCOMMON,
        icon="🛡️",
        condition_desc="储蓄 ≥ 6个月支出",
        reward_coins=300,
        reward_exp=150,
        hidden=True  # 月支出追踪功能暂未实现
    ),
    Achievement(
        id="SAVING_RATE_30",
        name="储蓄达人",
        description="连续6个月储蓄率超过30%",
        category=AchievementCategory.SAVING,
        rarity=AchievementRarity.RARE,
        icon="📥",
        condition_desc="连续6个月储蓄率 ≥ 30%",
        reward_coins=600,
        reward_exp=300,
        hidden=True  # 储蓄率追踪功能暂未实现
    ),
    
    # ============ 债务管理 ============
    Achievement(
        id="FIRST_LOAN",
        name="信用初体验",
        description="获得第一笔贷款",
        category=AchievementCategory.DEBT,
        rarity=AchievementRarity.COMMON,
        icon="📋",
        condition_desc="申请第一笔贷款",
        reward_coins=30,
        reward_exp=20
    ),
    Achievement(
        id="DEBT_FREE",
        name="无债一身轻",
        description="还清所有贷款",
        category=AchievementCategory.DEBT,
        rarity=AchievementRarity.UNCOMMON,
        icon="🎊",
        condition_desc="无任何贷款",
        reward_coins=500,
        reward_exp=250
    ),
    Achievement(
        id="PERFECT_CREDIT",
        name="完美信用",
        description="信用分达到800分",
        category=AchievementCategory.DEBT,
        rarity=AchievementRarity.RARE,
        icon="⭐",
        condition_desc="信用分 ≥ 800",
        reward_coins=800,
        reward_exp=400,
        reward_title="信用达人"
    ),
    Achievement(
        id="MORTGAGE_OWNER",
        name="房奴成就",
        description="成功申请房贷",
        category=AchievementCategory.DEBT,
        rarity=AchievementRarity.COMMON,
        icon="🏠",
        condition_desc="持有房贷",
        reward_coins=200,
        reward_exp=100,
        hidden=True  # 房贷系统暂未实现
    ),
    Achievement(
        id="HOUSE_PAID_OFF",
        name="房产解放",
        description="还清房贷",
        category=AchievementCategory.DEBT,
        rarity=AchievementRarity.LEGENDARY,
        icon="🏡",
        condition_desc="还清房贷",
        reward_coins=3000,
        reward_exp=1500,
        reward_title="房产自由者",
        prerequisite="MORTGAGE_OWNER",
        hidden=True  # 房贷系统暂未实现
    ),
    
    # ============ 职业发展 ============
    Achievement(
        id="FIRST_JOB",
        name="职场新人",
        description="获得第一份工作",
        category=AchievementCategory.CAREER,
        rarity=AchievementRarity.COMMON,
        icon="👔",
        condition_desc="开始工作",
        reward_coins=50,
        reward_exp=30
    ),
    Achievement(
        id="SALARY_15K",
        name="月入过万",
        description="月薪达到15000元",
        category=AchievementCategory.CAREER,
        rarity=AchievementRarity.UNCOMMON,
        icon="💼",
        condition_desc="月薪 ≥ ¥15,000",
        reward_coins=300,
        reward_exp=150
    ),
    Achievement(
        id="SALARY_50K",
        name="高薪精英",
        description="月薪达到50000元",
        category=AchievementCategory.CAREER,
        rarity=AchievementRarity.RARE,
        icon="🎖️",
        condition_desc="月薪 ≥ ¥50,000",
        reward_coins=1000,
        reward_exp=500,
        reward_title="高薪精英",
        prerequisite="SALARY_15K"
    ),
    Achievement(
        id="SIDE_HUSTLE",
        name="斜杠青年",
        description="拥有额外收入来源",
        category=AchievementCategory.CAREER,
        rarity=AchievementRarity.UNCOMMON,
        icon="🔀",
        condition_desc="有副业收入",
        reward_coins=200,
        reward_exp=100,
        hidden=True  # 副业系统暂未实现
    ),
    Achievement(
        id="PASSIVE_INCOME",
        name="被动收入达人",
        description="被动收入超过主动收入",
        category=AchievementCategory.CAREER,
        rarity=AchievementRarity.LEGENDARY,
        icon="🌊",
        condition_desc="被动收入 > 主动收入",
        reward_coins=5000,
        reward_exp=2000,
        reward_title="财务自由者",
        hidden=True  # 收入分类功能暂未实现
    ),
    
    # ============ 生活方式 ============
    Achievement(
        id="INSURED",
        name="保障先行",
        description="购买第一份保险",
        category=AchievementCategory.LIFESTYLE,
        rarity=AchievementRarity.COMMON,
        icon="🛡️",
        condition_desc="购买保险",
        reward_coins=50,
        reward_exp=30
    ),
    Achievement(
        id="FULL_INSURANCE",
        name="全面保障",
        description="同时持有医疗险、意外险、财产险",
        category=AchievementCategory.LIFESTYLE,
        rarity=AchievementRarity.UNCOMMON,
        icon="🏥",
        condition_desc="持有3种以上保险",
        reward_coins=400,
        reward_exp=200,
        hidden=True  # 保险购买UI暂未实现
    ),
    Achievement(
        id="SURVIVOR",
        name="危机幸存者",
        description="成功度过一次经济危机",
        category=AchievementCategory.LIFESTYLE,
        rarity=AchievementRarity.RARE,
        icon="💪",
        condition_desc="经历并存活于经济危机",
        reward_coins=1000,
        reward_exp=500,
        hidden=True
    ),
    Achievement(
        id="CLAIM_SUCCESS",
        name="理赔成功",
        description="成功获得保险理赔",
        category=AchievementCategory.LIFESTYLE,
        rarity=AchievementRarity.UNCOMMON,
        icon="✅",
        condition_desc="获得保险理赔",
        reward_coins=200,
        reward_exp=100,
        hidden=True  # 保险理赔功能暂未实现
    ),
    
    # ============ 技能解锁 ============
    Achievement(
        id="SKILL_BUDGETING",
        name="预算大师",
        description="连续3个月支出低于预算",
        category=AchievementCategory.SKILL,
        rarity=AchievementRarity.UNCOMMON,
        icon="📊",
        condition_desc="连续3个月控制支出",
        reward_coins=300,
        reward_exp=150,
        hidden=True  # 预算功能暂未实现
    ),
    Achievement(
        id="SKILL_TIMING",
        name="择时高手",
        description="成功抄底并在高点卖出",
        category=AchievementCategory.SKILL,
        rarity=AchievementRarity.RARE,
        icon="⏰",
        condition_desc="低买高卖获利50%以上",
        reward_coins=800,
        reward_exp=400,
        hidden=True
    ),
    Achievement(
        id="SKILL_ANALYSIS",
        name="分析师",
        description="查看过50次市场分析报告",
        category=AchievementCategory.SKILL,
        rarity=AchievementRarity.COMMON,
        icon="🔍",
        condition_desc="查看50次报告",
        reward_coins=100,
        reward_exp=50,
        hidden=True  # 报告查看计数功能暂未实现
    ),
    
    # ============ 特殊成就 ============
    Achievement(
        id="EARLY_BIRD",
        name="早起的鸟儿",
        description="在游戏首月就开始投资",
        category=AchievementCategory.SPECIAL,
        rarity=AchievementRarity.UNCOMMON,
        icon="🐦",
        condition_desc="第一个月开始投资",
        reward_coins=200,
        reward_exp=100,
        hidden=True
    ),
    Achievement(
        id="COMEBACK_KING",
        name="绝地反击",
        description="从负债状态恢复到正资产",
        category=AchievementCategory.SPECIAL,
        rarity=AchievementRarity.LEGENDARY,
        icon="🔥",
        condition_desc="从负资产恢复",
        reward_coins=3000,
        reward_exp=1500,
        reward_title="逆袭王者",
        hidden=True
    ),
    Achievement(
        id="LONG_TERM_HOLDER",
        name="长期主义者",
        description="持有某只股票超过24个月",
        category=AchievementCategory.SPECIAL,
        rarity=AchievementRarity.RARE,
        icon="🕰️",
        condition_desc="持股超过24个月",
        reward_coins=1000,
        reward_exp=500,
        hidden=True  # 持股时间追踪功能暂未实现
    ),
    Achievement(
        id="BLACK_SWAN",
        name="黑天鹅幸存者",
        description="在一次暴跌中损失超过50%但最终翻盘",
        category=AchievementCategory.SPECIAL,
        rarity=AchievementRarity.MYTHIC,
        icon="🦢",
        condition_desc="从暴跌中翻盘",
        reward_coins=10000,
        reward_exp=5000,
        reward_title="黑天鹅猎手",
        hidden=True
    ),
    Achievement(
        id="GAME_MASTER",
        name="人生赢家",
        description="解锁50个成就",
        category=AchievementCategory.SPECIAL,
        rarity=AchievementRarity.MYTHIC,
        icon="🎮",
        condition_desc="解锁50个成就",
        reward_coins=20000,
        reward_exp=10000,
        reward_title="人生赢家",
        hidden=True  # 当前可解锁成就不足50个
    ),
    
    # ============ 行为洞察成就 ============
    Achievement(
        id="BEHAVIOR_RATIONAL",
        name="理性投资者",
        description="连续保持高理性决策评分",
        category=AchievementCategory.SKILL,
        rarity=AchievementRarity.RARE,
        icon="🧠",
        condition_desc="平均理性评分 ≥ 80%",
        reward_coins=1000,
        reward_exp=500,
        reward_title="理性投资者"
    ),
    Achievement(
        id="BEHAVIOR_DIVERSE",
        name="多元配置师",
        description="展现出色的资产多元化能力",
        category=AchievementCategory.SKILL,
        rarity=AchievementRarity.UNCOMMON,
        icon="🎨",
        condition_desc="持有3类以上不同资产",
        reward_coins=500,
        reward_exp=250
    ),
    Achievement(
        id="BEHAVIOR_STABLE",
        name="稳健派",
        description="风险偏好稳定，不受市场情绪影响",
        category=AchievementCategory.SKILL,
        rarity=AchievementRarity.RARE,
        icon="⚖️",
        condition_desc="风险偏好波动率 < 10%",
        reward_coins=800,
        reward_exp=400
    ),
    Achievement(
        id="BEHAVIOR_PLANNER",
        name="财务规划师",
        description="展现出色的财务规划能力",
        category=AchievementCategory.SKILL,
        rarity=AchievementRarity.UNCOMMON,
        icon="📋",
        condition_desc="规划能力评分 ≥ 70%",
        reward_coins=600,
        reward_exp=300
    ),
    Achievement(
        id="BEHAVIOR_NO_HERD",
        name="独立思考者",
        description="不盲目跟风，保持独立判断",
        category=AchievementCategory.SKILL,
        rarity=AchievementRarity.RARE,
        icon="🦅",
        condition_desc="羊群倾向 < 30%",
        reward_coins=1000,
        reward_exp=500,
        reward_title="独行侠"
    ),
    Achievement(
        id="BEHAVIOR_LOW_RISK",
        name="风控达人",
        description="持续保持低风险行为",
        category=AchievementCategory.SKILL,
        rarity=AchievementRarity.UNCOMMON,
        icon="🛡️",
        condition_desc="平均风险评分 < 30%",
        reward_coins=500,
        reward_exp=250
    ),
    Achievement(
        id="BEHAVIOR_CONSISTENT",
        name="一致性大师",
        description="决策风格保持高度一致",
        category=AchievementCategory.SKILL,
        rarity=AchievementRarity.LEGENDARY,
        icon="🎯",
        condition_desc="决策一致性 ≥ 90%",
        reward_coins=2000,
        reward_exp=1000,
        reward_title="始终如一",
        hidden=True
    ),
    Achievement(
        id="BEHAVIOR_IMPROVED",
        name="自我提升者",
        description="行为评分持续改善",
        category=AchievementCategory.SPECIAL,
        rarity=AchievementRarity.UNCOMMON,
        icon="📈",
        condition_desc="3个月内理性评分提升20%",
        reward_coins=600,
        reward_exp=300,
        hidden=True
    ),
]


class AchievementSystem:
    """成就管理系统"""
    
    def __init__(self):
        self.achievements = {a.id: a for a in ACHIEVEMENTS}
        self.unlocked: Dict[str, UnlockedAchievement] = {}
        self.progress: Dict[str, Dict] = {}  # 成就进度追踪
        self.total_coins_earned = 0
        self.total_exp_earned = 0
        self.current_title: Optional[str] = None
        self.available_titles: List[str] = []
        
    def check_and_unlock(self, achievement_id: str, game_month: int = 0) -> Optional[Dict]:
        """检查并解锁成就
        
        Returns:
            解锁信息 或 None
        """
        if achievement_id in self.unlocked:
            return None
        
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            return None
        
        # 检查前置成就
        if achievement.prerequisite and achievement.prerequisite not in self.unlocked:
            return None
        
        # 解锁成就
        self.unlocked[achievement_id] = UnlockedAchievement(
            achievement_id=achievement_id,
            unlocked_month=game_month
        )
        
        # 发放奖励
        self.total_coins_earned += achievement.reward_coins
        self.total_exp_earned += achievement.reward_exp
        
        if achievement.reward_title:
            self.available_titles.append(achievement.reward_title)
        
        return {
            "achievement": {
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "rarity": achievement.rarity.value
            },
            "rewards": {
                "coins": achievement.reward_coins,
                "exp": achievement.reward_exp,
                "title": achievement.reward_title
            }
        }
    
    def load_unlocked_from_list(self, unlocked_list: List[Dict]):
        """从已解锁成就列表加载到内存中，避免重复解锁
        
        Args:
            unlocked_list: 数据库中已解锁成就的列表，每项包含 achievement_id 和 unlocked_month
        """
        self.unlocked = {}
        for item in unlocked_list:
            ach_id = item.get("achievement_id")
            if ach_id:
                self.unlocked[ach_id] = UnlockedAchievement(
                    achievement_id=ach_id,
                    unlocked_month=item.get("unlocked_month", 0)
                )
    
    def check_wealth_achievements(self, total_assets: int, game_month: int) -> List[Dict]:
        """检查财富成就"""
        unlocked = []
        
        thresholds = [
            ("WEALTH_10K", 10000),
            ("WEALTH_100K", 100000),
            ("WEALTH_1M", 1000000),
            ("WEALTH_10M", 10000000),
            ("WEALTH_100M", 100000000),
        ]
        
        for ach_id, threshold in thresholds:
            if total_assets >= threshold:
                result = self.check_and_unlock(ach_id, game_month)
                if result:
                    unlocked.append(result)
        
        return unlocked
    
    def check_investment_achievements(self, 
                                      stock_profit: int,
                                      fund_profit: int,
                                      dividend_income: int,
                                      asset_types: int,
                                      best_stock_return: float,
                                      game_month: int) -> List[Dict]:
        """检查投资成就"""
        unlocked = []
        
        # 股票盈利
        if stock_profit >= 10000:
            r = self.check_and_unlock("STOCK_PROFIT_10K", game_month)
            if r: unlocked.append(r)
        if stock_profit >= 100000:
            r = self.check_and_unlock("STOCK_PROFIT_100K", game_month)
            if r: unlocked.append(r)
        
        # 分散投资
        if asset_types >= 5:
            r = self.check_and_unlock("DIVERSIFIED", game_month)
            if r: unlocked.append(r)
        
        # 股息收入
        if dividend_income >= 10000:
            r = self.check_and_unlock("DIVIDEND_COLLECTOR", game_month)
            if r: unlocked.append(r)
        
        # 十倍股
        if best_stock_return >= 10.0:
            r = self.check_and_unlock("TEN_BAGGER", game_month)
            if r: unlocked.append(r)
        
        # 基金盈利
        if fund_profit >= 50000:
            r = self.check_and_unlock("FUND_MASTER", game_month)
            if r: unlocked.append(r)
        
        return unlocked
    
    def check_career_achievements(self, 
                                  monthly_salary: int,
                                  passive_income: int,
                                  has_side_job: bool,
                                  game_month: int) -> List[Dict]:
        """检查职业成就"""
        unlocked = []
        
        if monthly_salary >= 15000:
            r = self.check_and_unlock("SALARY_15K", game_month)
            if r: unlocked.append(r)
        
        if monthly_salary >= 50000:
            r = self.check_and_unlock("SALARY_50K", game_month)
            if r: unlocked.append(r)
        
        if has_side_job:
            r = self.check_and_unlock("SIDE_HUSTLE", game_month)
            if r: unlocked.append(r)
        
        if passive_income > monthly_salary > 0:
            r = self.check_and_unlock("PASSIVE_INCOME", game_month)
            if r: unlocked.append(r)
        
        return unlocked
    
    def check_saving_achievements(self,
                                  savings: int,
                                  monthly_expense: int,
                                  saving_rate_history: List[float],
                                  game_month: int) -> List[Dict]:
        """检查储蓄成就"""
        unlocked = []
        
        # 应急储备金
        if monthly_expense > 0 and savings >= monthly_expense * 6:
            r = self.check_and_unlock("EMERGENCY_FUND", game_month)
            if r: unlocked.append(r)
        
        # 高储蓄率
        if len(saving_rate_history) >= 6:
            if all(r >= 0.3 for r in saving_rate_history[-6:]):
                r = self.check_and_unlock("SAVING_RATE_30", game_month)
                if r: unlocked.append(r)
        
        return unlocked
    
    def check_debt_achievements(self,
                                has_loans: bool,
                                credit_score: int,
                                has_mortgage: bool,
                                mortgage_paid: bool,
                                game_month: int) -> List[Dict]:
        """检查债务成就"""
        unlocked = []
        
        if not has_loans:
            r = self.check_and_unlock("DEBT_FREE", game_month)
            if r: unlocked.append(r)
        
        if credit_score >= 800:
            r = self.check_and_unlock("PERFECT_CREDIT", game_month)
            if r: unlocked.append(r)
        
        if has_mortgage:
            r = self.check_and_unlock("MORTGAGE_OWNER", game_month)
            if r: unlocked.append(r)
        
        if mortgage_paid:
            r = self.check_and_unlock("HOUSE_PAID_OFF", game_month)
            if r: unlocked.append(r)
        
        return unlocked
    
    def check_insurance_achievements(self,
                                     insurance_count: int,
                                     has_claim: bool,
                                     game_month: int) -> List[Dict]:
        """检查保险成就"""
        unlocked = []
        
        if insurance_count >= 1:
            r = self.check_and_unlock("INSURED", game_month)
            if r: unlocked.append(r)
        
        if insurance_count >= 3:
            r = self.check_and_unlock("FULL_INSURANCE", game_month)
            if r: unlocked.append(r)
        
        if has_claim:
            r = self.check_and_unlock("CLAIM_SUCCESS", game_month)
            if r: unlocked.append(r)
        
        return unlocked
    
    def check_behavior_achievements(self, behavior_profile: Dict, game_month: int) -> List[Dict]:
        """基于行为洞察检查成就
        
        Args:
            behavior_profile: 行为画像数据
            game_month: 游戏月份
            
        Returns:
            新解锁的成就列表
        """
        unlocked = []
        
        if not behavior_profile:
            return unlocked
        
        # 理性投资者 - 平均理性评分 >= 80%
        avg_rationality = behavior_profile.get('avg_rationality', 0)
        if avg_rationality >= 0.8:
            r = self.check_and_unlock("BEHAVIOR_RATIONAL", game_month)
            if r: unlocked.append(r)
        
        # 规划能力评分 >= 70%
        planning_ability = behavior_profile.get('planning_ability', 0)
        if planning_ability >= 0.7:
            r = self.check_and_unlock("BEHAVIOR_PLANNER", game_month)
            if r: unlocked.append(r)
        
        # 独立思考者 - 羊群倾向 < 30%
        herding_tendency = behavior_profile.get('herding_tendency', 1)
        if herding_tendency < 0.3:
            r = self.check_and_unlock("BEHAVIOR_NO_HERD", game_month)
            if r: unlocked.append(r)
        
        # 风控达人 - 平均风险评分 < 30%
        avg_risk = behavior_profile.get('avg_risk_score', 1)
        if avg_risk < 0.3:
            r = self.check_and_unlock("BEHAVIOR_LOW_RISK", game_month)
            if r: unlocked.append(r)
        
        return unlocked
    
    def check_behavior_diversity(self, portfolio: Dict, game_month: int) -> Optional[Dict]:
        """检查资产多元化成就
        
        Args:
            portfolio: 投资组合
            game_month: 游戏月份
        """
        asset_types = set()
        
        # 检查各类资产
        if portfolio.get('stocks') and len(portfolio['stocks']) > 0:
            asset_types.add('stocks')
        if portfolio.get('deposits') and any(d.get('amount', 0) > 0 for d in portfolio.get('deposits', [])):
            asset_types.add('deposits')
        if portfolio.get('bonds') and len(portfolio.get('bonds', [])) > 0:
            asset_types.add('bonds')
        if portfolio.get('funds') and len(portfolio.get('funds', [])) > 0:
            asset_types.add('funds')
        if portfolio.get('real_estate') and len(portfolio.get('real_estate', [])) > 0:
            asset_types.add('real_estate')
        if portfolio.get('insurance') and len(portfolio.get('insurance', [])) > 0:
            asset_types.add('insurance')
        
        if len(asset_types) >= 3:
            return self.check_and_unlock("BEHAVIOR_DIVERSE", game_month)
        return None
    
    def check_behavior_improvement(self, 
                                   current_rationality: float, 
                                   history: List[float],
                                   game_month: int) -> Optional[Dict]:
        """检查行为改善成就
        
        Args:
            current_rationality: 当前理性评分
            history: 历史理性评分
            game_month: 游戏月份
        """
        if len(history) >= 3:
            # 3个月前的评分
            old_score = history[-3] if len(history) >= 3 else history[0]
            improvement = current_rationality - old_score
            
            # 提升超过20%
            if improvement >= 0.2:
                return self.check_and_unlock("BEHAVIOR_IMPROVED", game_month)
        return None

    def record_first_action(self, action: str, game_month: int) -> Optional[Dict]:
        """记录首次行动"""
        action_map = {
            "stock_buy": "FIRST_STOCK",
            "deposit": "FIRST_DEPOSIT",
            "loan": "FIRST_LOAN",
            "job": "FIRST_JOB",
            "insurance": "INSURED",
        }
        
        ach_id = action_map.get(action)
        if ach_id:
            return self.check_and_unlock(ach_id, game_month)
        return None
    
    def record_special_event(self, event: str, game_month: int) -> Optional[Dict]:
        """记录特殊事件"""
        event_map = {
            "early_invest": "EARLY_BIRD",
            "comeback": "COMEBACK_KING",
            "survive_crisis": "SURVIVOR",
            "black_swan": "BLACK_SWAN",
            "timing_success": "SKILL_TIMING",
        }
        
        ach_id = event_map.get(event)
        if ach_id:
            return self.check_and_unlock(ach_id, game_month)
        return None
    
    def set_title(self, title: str) -> bool:
        """设置称号"""
        if title in self.available_titles:
            self.current_title = title
            return True
        return False
    
    def get_progress_stats(self) -> Dict:
        """获取成就进度统计"""
        total = len(self.achievements)
        unlocked = len(self.unlocked)
        
        by_category = {}
        by_rarity = {}
        
        for ach in self.achievements.values():
            cat = ach.category.value
            rar = ach.rarity.value
            
            if cat not in by_category:
                by_category[cat] = {"total": 0, "unlocked": 0}
            by_category[cat]["total"] += 1
            
            if rar not in by_rarity:
                by_rarity[rar] = {"total": 0, "unlocked": 0}
            by_rarity[rar]["total"] += 1
            
            if ach.id in self.unlocked:
                by_category[cat]["unlocked"] += 1
                by_rarity[rar]["unlocked"] += 1
        
        return {
            "total": total,
            "unlocked": unlocked,
            "completion_rate": f"{unlocked/total*100:.1f}%",
            "by_category": by_category,
            "by_rarity": by_rarity,
            "total_coins": self.total_coins_earned,
            "total_exp": self.total_exp_earned,
            "current_title": self.current_title,
            "available_titles": self.available_titles
        }
    
    def get_unlocked_list(self) -> List[Dict]:
        """获取已解锁成就列表"""
        result = []
        for unlocked in self.unlocked.values():
            ach = self.achievements.get(unlocked.achievement_id)
            if ach:
                result.append({
                    "id": ach.id,
                    "name": ach.name,
                    "description": ach.description,
                    "icon": ach.icon,
                    "category": ach.category.value,
                    "rarity": ach.rarity.value,
                    "unlocked_month": unlocked.unlocked_month
                })
        return sorted(result, key=lambda x: x["unlocked_month"], reverse=True)
    
    def get_locked_list(self, show_hidden: bool = False) -> List[Dict]:
        """获取未解锁成就列表"""
        result = []
        for ach in self.achievements.values():
            if ach.id in self.unlocked:
                continue
            if ach.hidden and not show_hidden:
                continue
            
            result.append({
                "id": ach.id,
                "name": ach.name if not ach.hidden else "???",
                "description": ach.description if not ach.hidden else "隐藏成就",
                "icon": ach.icon if not ach.hidden else "❓",
                "category": ach.category.value,
                "rarity": ach.rarity.value,
                "condition": ach.condition_desc if not ach.hidden else "???"
            })
        return result
    
    def get_recent_unlocks(self, count: int = 5) -> List[Dict]:
        """获取最近解锁的成就"""
        sorted_unlocks = sorted(
            self.unlocked.values(),
            key=lambda x: x.unlocked_at,
            reverse=True
        )[:count]
        
        result = []
        for unlocked in sorted_unlocks:
            ach = self.achievements.get(unlocked.achievement_id)
            if ach:
                result.append({
                    "id": ach.id,
                    "name": ach.name,
                    "icon": ach.icon,
                    "rarity": ach.rarity.value
                })
        return result


# 全局实例
achievement_system = AchievementSystem()
