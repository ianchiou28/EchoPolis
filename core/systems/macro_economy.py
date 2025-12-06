"""
宏观经济系统 - EchoPolis 增强版
模拟经济周期、通胀影响、利率变化，联动税收系统
"""
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from copy import deepcopy


class EconomicPhase(Enum):
    """经济周期阶段"""
    EXPANSION = "expansion"      # 扩张期
    PEAK = "peak"               # 顶峰期
    CONTRACTION = "contraction"  # 收缩期
    TROUGH = "trough"           # 谷底期


class PolicyType(Enum):
    """政策类型"""
    RATE_CUT = "降息"
    RATE_HIKE = "加息"
    QE = "量化宽松"
    TIGHTENING = "紧缩政策"
    TAX_CUT = "减税"
    TAX_HIKE = "加税"
    STIMULUS = "经济刺激"


@dataclass
class EconomicState:
    """经济状态"""
    gdp_growth: float           # GDP增长率 (%)
    inflation: float            # 通胀率 (%)
    interest_rate: float        # 基准利率 (%)
    market_sentiment: float     # 市场情绪 (0-100)
    phase: str                  # 经济周期阶段
    unemployment: float = 5.0   # 失业率 (%)
    cpi_index: float = 100.0    # 消费价格指数 (基准100)
    house_price_index: float = 100.0  # 房价指数
    stock_index: float = 3000.0      # 股票指数


@dataclass
class EconomicEvent:
    """经济事件"""
    name: str
    description: str
    impact: Dict[str, float]    # 对各指标的影响
    probability: float          # 发生概率
    duration: int = 1           # 持续月数


class MacroEconomy:
    """宏观经济系统"""
    
    # 经济事件库
    ECONOMIC_EVENTS = [
        EconomicEvent("央行降息", "央行宣布下调基准利率25个基点", 
                     {"interest_rate": -0.25, "market_sentiment": 5, "stock_index": 50}, 0.08),
        EconomicEvent("央行加息", "央行宣布上调基准利率25个基点",
                     {"interest_rate": 0.25, "market_sentiment": -3, "stock_index": -30}, 0.08),
        EconomicEvent("通胀超预期", "CPI数据高于预期",
                     {"inflation": 0.3, "market_sentiment": -5}, 0.10),
        EconomicEvent("就业数据向好", "新增就业岗位超预期",
                     {"unemployment": -0.2, "market_sentiment": 3, "gdp_growth": 0.1}, 0.12),
        EconomicEvent("国际油价上涨", "地缘政治导致油价飙升",
                     {"inflation": 0.2, "market_sentiment": -3}, 0.08),
        EconomicEvent("科技股暴跌", "科技巨头业绩不及预期",
                     {"stock_index": -100, "market_sentiment": -8}, 0.05),
        EconomicEvent("房地产政策放松", "多地放宽购房限制",
                     {"house_price_index": 2, "market_sentiment": 2}, 0.06),
        EconomicEvent("出口数据强劲", "贸易顺差创新高",
                     {"gdp_growth": 0.2, "market_sentiment": 4}, 0.10),
        EconomicEvent("消费刺激政策", "政府发放消费券",
                     {"gdp_growth": 0.15, "inflation": 0.1, "market_sentiment": 3}, 0.05),
        EconomicEvent("金融危机预警", "银行坏账率上升引发担忧",
                     {"market_sentiment": -15, "stock_index": -150}, 0.02),
    ]
    
    # 个税税率阶梯
    INCOME_TAX_BRACKETS = [
        (0, 5000, 0),
        (5000, 8000, 0.03),
        (8000, 17000, 0.10),
        (17000, 30000, 0.20),
        (30000, 40000, 0.25),
        (40000, 60000, 0.30),
        (60000, 85000, 0.35),
        (85000, float('inf'), 0.45)
    ]
    
    # 资本利得税率
    CAPITAL_GAINS_TAX = 0.20
    
    # 股息税率
    DIVIDEND_TAX = 0.20
    
    def __init__(self):
        self.state = EconomicState(
            gdp_growth=3.0,
            inflation=2.0,
            interest_rate=3.5,
            market_sentiment=50.0,
            phase="expansion",
            unemployment=5.0,
            cpi_index=100.0,
            house_price_index=100.0,
            stock_index=3000.0
        )
        self.history: List[EconomicState] = []
        self.months_in_phase = 0
        self.active_events: List[Dict] = []
        self.recent_policies: List[str] = []
        
    def advance_month(self) -> Dict[str, any]:
        """推进一个月，更新经济指标"""
        # 保存历史
        self.history.append(deepcopy(self.state))
        
        prev_state = self.state
        self.months_in_phase += 1
        
        # 基础经济周期逻辑
        result = self._process_economic_cycle(prev_state)
        
        # 处理随机经济事件
        events = self._process_random_events()
        result["events"] = events
        
        # 更新CPI指数（基于通胀累积）
        self.state.cpi_index *= (1 + self.state.inflation / 100 / 12)
        
        # 更新股票指数（基于市场情绪和经济周期）
        sentiment_factor = (self.state.market_sentiment - 50) / 500
        cycle_factor = self._get_cycle_stock_factor()
        self.state.stock_index *= (1 + sentiment_factor + cycle_factor + random.uniform(-0.02, 0.02))
        self.state.stock_index = max(1000, self.state.stock_index)
        
        # 更新房价指数
        self._update_house_price_index()
        
        result.update({
            "gdp_growth": round(self.state.gdp_growth, 2),
            "inflation": round(self.state.inflation, 2),
            "interest_rate": round(self.state.interest_rate, 2),
            "market_sentiment": round(self.state.market_sentiment, 1),
            "phase": self.state.phase,
            "phase_name": self._get_phase_name(),
            "unemployment": round(self.state.unemployment, 1),
            "cpi_index": round(self.state.cpi_index, 1),
            "house_price_index": round(self.state.house_price_index, 1),
            "stock_index": round(self.state.stock_index, 0),
            "months_in_phase": self.months_in_phase
        })
        
        return result
    
    def _process_economic_cycle(self, prev_state: EconomicState) -> Dict:
        """处理经济周期逻辑"""
        new_sentiment = prev_state.market_sentiment
        volatility = random.uniform(-2.0, 2.0)
        phase_changed = False
        
        if prev_state.phase == "expansion":
            new_gdp = min(8.0, prev_state.gdp_growth + 0.1 + random.uniform(-0.1, 0.2))
            new_inflation = min(10.0, prev_state.inflation + 0.05 + random.uniform(0, 0.1))
            new_interest = prev_state.interest_rate + (0.02 if new_inflation > 3.0 else 0)
            new_unemployment = max(3.0, prev_state.unemployment - 0.1)
            new_sentiment += 1.0
            
            if (new_gdp > 6.0 and new_inflation > 4.0) or self.months_in_phase > 24:
                self.state.phase = "peak"
                self.months_in_phase = 0
                phase_changed = True
                
        elif prev_state.phase == "peak":
            new_gdp = prev_state.gdp_growth - 0.2 + random.uniform(-0.2, 0.1)
            new_inflation = prev_state.inflation + 0.1
            new_interest = prev_state.interest_rate + 0.1
            new_unemployment = prev_state.unemployment + 0.05
            new_sentiment -= 2.0
            
            if new_gdp < 2.0 or self.months_in_phase > 12:
                self.state.phase = "contraction"
                self.months_in_phase = 0
                phase_changed = True
                
        elif prev_state.phase == "contraction":
            new_gdp = max(-3.0, prev_state.gdp_growth - 0.3 + random.uniform(-0.2, 0.1))
            new_inflation = max(-1.0, prev_state.inflation - 0.2)
            new_interest = max(0.0, prev_state.interest_rate - 0.1)
            new_unemployment = min(15.0, prev_state.unemployment + 0.2)
            new_sentiment -= 3.0
            
            if new_gdp < 0 or self.months_in_phase > 18:
                self.state.phase = "trough"
                self.months_in_phase = 0
                phase_changed = True
                
        else:  # trough
            new_gdp = prev_state.gdp_growth + 0.2 + random.uniform(0, 0.2)
            new_inflation = max(0.0, prev_state.inflation - 0.1)
            new_interest = max(0.0, prev_state.interest_rate - 0.05)
            new_unemployment = max(3.5, prev_state.unemployment - 0.1)
            new_sentiment += 0.5
            
            if new_gdp > 1.0 or self.months_in_phase > 12:
                self.state.phase = "expansion"
                self.months_in_phase = 0
                phase_changed = True

        # 更新状态
        self.state.gdp_growth = round(new_gdp, 2)
        self.state.inflation = round(max(-2, min(15, new_inflation)), 2)
        self.state.interest_rate = round(max(0, min(15, new_interest)), 2)
        self.state.market_sentiment = max(0, min(100, round(new_sentiment + volatility, 1)))
        self.state.unemployment = round(new_unemployment, 1)
        
        return {"phase_changed": phase_changed}
    
    def _process_random_events(self) -> List[Dict]:
        """处理随机经济事件"""
        triggered_events = []
        
        for event in self.ECONOMIC_EVENTS:
            if random.random() < event.probability:
                # 应用事件影响
                for key, value in event.impact.items():
                    if hasattr(self.state, key):
                        current = getattr(self.state, key)
                        setattr(self.state, key, current + value)
                
                triggered_events.append({
                    "name": event.name,
                    "description": event.description
                })
        
        return triggered_events
    
    def _get_cycle_stock_factor(self) -> float:
        """获取经济周期对股市的影响因子"""
        factors = {
            "expansion": 0.01,
            "peak": 0.005,
            "contraction": -0.02,
            "trough": -0.005
        }
        return factors.get(self.state.phase, 0)
    
    def _update_house_price_index(self):
        """更新房价指数"""
        # 房价与利率负相关，与GDP正相关
        rate_effect = -0.1 * (self.state.interest_rate - 3.5)
        gdp_effect = 0.05 * (self.state.gdp_growth - 3.0)
        
        change = (rate_effect + gdp_effect + random.uniform(-0.5, 0.5)) / 100
        self.state.house_price_index *= (1 + change)
        self.state.house_price_index = max(50, min(200, self.state.house_price_index))
    
    def _get_phase_name(self) -> str:
        """获取周期阶段中文名"""
        names = {
            "expansion": "扩张期 📈",
            "peak": "顶峰期 🔝",
            "contraction": "收缩期 📉",
            "trough": "谷底期 ⬇️"
        }
        return names.get(self.state.phase, "未知")
    
    def get_asset_impact(self) -> Dict[str, float]:
        """获取当前经济状态对各类资产的影响系数"""
        impact = {
            "cash": 1.0 - (self.state.inflation / 100.0 / 12.0),
            "stock": 1.0,
            "bond": 1.0,
            "real_estate": 1.0,
            "gold": 1.0,
            "crypto": 1.0
        }
        
        if self.state.phase == "expansion":
            impact["stock"] = 1.02 + (self.state.gdp_growth / 100.0)
            impact["real_estate"] = 1.01
            impact["bond"] = 0.99
            impact["gold"] = 0.98
            impact["crypto"] = 1.03
        elif self.state.phase == "peak":
            impact["stock"] = 1.00
            impact["real_estate"] = 1.02
            impact["bond"] = 0.98
            impact["gold"] = 1.01
            impact["crypto"] = 1.05
        elif self.state.phase == "contraction":
            impact["stock"] = 0.95
            impact["real_estate"] = 0.98
            impact["bond"] = 1.02
            impact["gold"] = 1.03
            impact["crypto"] = 0.90
        elif self.state.phase == "trough":
            impact["stock"] = 0.98
            impact["real_estate"] = 0.99
            impact["bond"] = 1.02
            impact["gold"] = 1.02
            impact["crypto"] = 0.95
            
        return impact
    
    def calculate_inflation_erosion(self, cash: int) -> int:
        """计算通胀对现金的侵蚀
        
        Args:
            cash: 当前现金
        
        Returns:
            侵蚀后的现金值
        """
        monthly_inflation = self.state.inflation / 100 / 12
        return int(cash * (1 - monthly_inflation))
    
    def calculate_income_tax(self, monthly_income: int) -> Dict:
        """计算个人所得税
        
        Args:
            monthly_income: 月收入
        
        Returns:
            税务详情
        """
        taxable = monthly_income
        total_tax = 0
        
        for lower, upper, rate in self.INCOME_TAX_BRACKETS:
            if taxable <= 0:
                break
            bracket_income = min(taxable, upper - lower)
            if taxable > lower:
                tax_in_bracket = bracket_income * rate
                total_tax += tax_in_bracket
                taxable -= bracket_income
        
        effective_rate = total_tax / monthly_income if monthly_income > 0 else 0
        
        return {
            "gross_income": monthly_income,
            "tax": int(total_tax),
            "net_income": monthly_income - int(total_tax),
            "effective_rate": round(effective_rate * 100, 2)
        }
    
    def calculate_capital_gains_tax(self, profit: int) -> Dict:
        """计算资本利得税
        
        Args:
            profit: 投资收益（可为负）
        
        Returns:
            税务详情
        """
        if profit <= 0:
            return {
                "profit": profit,
                "tax": 0,
                "net_profit": profit,
                "loss_carryforward": abs(profit) if profit < 0 else 0
            }
        
        tax = int(profit * self.CAPITAL_GAINS_TAX)
        return {
            "profit": profit,
            "tax": tax,
            "net_profit": profit - tax,
            "tax_rate": self.CAPITAL_GAINS_TAX * 100
        }
    
    def calculate_dividend_tax(self, dividend: int, holding_months: int) -> Dict:
        """计算股息税（持有时间影响税率）
        
        Args:
            dividend: 股息金额
            holding_months: 持有月数
        
        Returns:
            税务详情
        """
        # 持有超过12个月，股息税减半
        if holding_months >= 12:
            tax_rate = self.DIVIDEND_TAX / 2
        else:
            tax_rate = self.DIVIDEND_TAX
        
        tax = int(dividend * tax_rate)
        return {
            "dividend": dividend,
            "tax": tax,
            "net_dividend": dividend - tax,
            "tax_rate": tax_rate * 100,
            "holding_bonus": holding_months >= 12
        }
    
    def get_economic_summary(self) -> Dict:
        """获取经济状况摘要"""
        # 综合评估经济健康度
        health_score = 50
        health_score += (self.state.gdp_growth - 3) * 5
        health_score += (50 - abs(self.state.market_sentiment - 50)) / 2
        health_score -= abs(self.state.inflation - 2) * 3
        health_score -= (self.state.unemployment - 5) * 2
        health_score = max(0, min(100, health_score))
        
        if health_score >= 70:
            outlook = "经济向好 🌟"
        elif health_score >= 50:
            outlook = "经济平稳 📊"
        elif health_score >= 30:
            outlook = "经济疲软 ⚠️"
        else:
            outlook = "经济衰退 🔻"
        
        return {
            "phase": self.state.phase,
            "phase_name": self._get_phase_name(),
            "gdp_growth": self.state.gdp_growth,
            "inflation": self.state.inflation,
            "interest_rate": self.state.interest_rate,
            "unemployment": self.state.unemployment,
            "market_sentiment": self.state.market_sentiment,
            "cpi_index": round(self.state.cpi_index, 1),
            "stock_index": round(self.state.stock_index, 0),
            "house_price_index": round(self.state.house_price_index, 1),
            "health_score": round(health_score, 0),
            "outlook": outlook,
            "months_in_phase": self.months_in_phase,
            "investment_advice": self._get_investment_advice()
        }
    
    def _get_investment_advice(self) -> str:
        """根据经济状况给出投资建议"""
        if self.state.phase == "expansion":
            return "扩张期适合增持股票类资产，可适当提高风险敞口"
        elif self.state.phase == "peak":
            return "市场处于高位，建议逐步减仓股票，增加现金和债券比例"
        elif self.state.phase == "contraction":
            return "经济收缩期应防守为主，持有现金和避险资产如黄金、国债"
        else:  # trough
            return "谷底期可能是布局优质股票的好时机，但需分批建仓"
    
    def get_sector_outlook(self) -> Dict[str, str]:
        """获取各板块前景"""
        outlooks = {}
        
        if self.state.phase == "expansion":
            outlooks = {
                "科技": "🌟 强烈看好",
                "金融": "📈 看好",
                "消费": "📈 看好",
                "医疗": "➡️ 中性",
                "能源": "📈 看好",
                "房地产": "📈 看好"
            }
        elif self.state.phase == "peak":
            outlooks = {
                "科技": "⚠️ 谨慎",
                "金融": "➡️ 中性",
                "消费": "📈 看好",
                "医疗": "📈 看好",
                "能源": "⚠️ 谨慎",
                "房地产": "⚠️ 谨慎"
            }
        elif self.state.phase == "contraction":
            outlooks = {
                "科技": "📉 回避",
                "金融": "📉 回避",
                "消费": "➡️ 中性（必需消费）",
                "医疗": "📈 看好（防御）",
                "能源": "📉 回避",
                "房地产": "📉 回避"
            }
        else:  # trough
            outlooks = {
                "科技": "🔍 关注布局",
                "金融": "🔍 关注布局",
                "消费": "📈 逐步加仓",
                "医疗": "📈 看好",
                "能源": "➡️ 中性",
                "房地产": "🔍 关注优质标的"
            }
        
        return outlooks


# 全局实例
macro_economy = MacroEconomy()
