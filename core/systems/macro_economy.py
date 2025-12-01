import random
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class EconomicState:
    gdp_growth: float  # GDP增长率 (%)
    inflation: float   # 通胀率 (%)
    interest_rate: float # 基准利率 (%)
    market_sentiment: float # 市场情绪 (0-100)
    phase: str # 经济周期阶段: expansion, peak, contraction, trough

class MacroEconomy:
    def __init__(self):
        self.state = EconomicState(
            gdp_growth=3.0,
            inflation=2.0,
            interest_rate=3.5,
            market_sentiment=50.0,
            phase="expansion"
        )
        self.history: List[EconomicState] = []

    def advance_month(self) -> Dict[str, any]:
        """推进一个月，更新经济指标"""
        # 简单的经济周期模拟
        # 扩张 -> 顶峰 -> 衰退 -> 谷底 -> 扩张
        
        prev_state = self.state
        new_sentiment = prev_state.market_sentiment
        
        # 随机波动
        volatility = random.uniform(-2.0, 2.0)
        
        if prev_state.phase == "expansion":
            new_gdp = min(8.0, prev_state.gdp_growth + 0.1 + random.uniform(-0.1, 0.2))
            new_inflation = min(10.0, prev_state.inflation + 0.05)
            new_interest = prev_state.interest_rate + 0.02 if new_inflation > 3.0 else prev_state.interest_rate
            new_sentiment += 1.0
            
            if new_gdp > 6.0 and new_inflation > 4.0:
                self.state.phase = "peak"
                
        elif prev_state.phase == "peak":
            new_gdp = prev_state.gdp_growth - 0.2
            new_inflation = prev_state.inflation + 0.1
            new_interest = prev_state.interest_rate + 0.1 # 加息抑制通胀
            new_sentiment -= 2.0
            
            if new_gdp < 2.0:
                self.state.phase = "contraction"
                
        elif prev_state.phase == "contraction":
            new_gdp = max(-2.0, prev_state.gdp_growth - 0.3)
            new_inflation = max(0.0, prev_state.inflation - 0.2)
            new_interest = max(0.0, prev_state.interest_rate - 0.1) # 降息刺激经济
            new_sentiment -= 3.0
            
            if new_gdp < 0:
                self.state.phase = "trough"
                
        else: # trough
            new_gdp = prev_state.gdp_growth + 0.2
            new_inflation = max(0.0, prev_state.inflation - 0.1)
            new_interest = max(0.0, prev_state.interest_rate - 0.05)
            new_sentiment += 0.5
            
            if new_gdp > 1.0:
                self.state.phase = "expansion"

        # 限制范围
        self.state.gdp_growth = round(new_gdp, 2)
        self.state.inflation = round(new_inflation, 2)
        self.state.interest_rate = round(new_interest, 2)
        self.state.market_sentiment = max(0, min(100, round(new_sentiment + volatility, 1)))
        
        self.history.append(self.state)
        
        return {
            "gdp_growth": self.state.gdp_growth,
            "inflation": self.state.inflation,
            "interest_rate": self.state.interest_rate,
            "market_sentiment": self.state.market_sentiment,
            "phase": self.state.phase
        }

    def get_asset_impact(self) -> Dict[str, float]:
        """获取当前经济状态对各类资产的影响系数"""
        # 基础系数为 1.0
        impact = {
            "cash": 1.0 - (self.state.inflation / 100.0 / 12.0), # 现金受通胀贬值
            "stock": 1.0,
            "bond": 1.0,
            "real_estate": 1.0
        }
        
        if self.state.phase == "expansion":
            impact["stock"] = 1.02 + (self.state.gdp_growth / 100.0)
            impact["real_estate"] = 1.01
            impact["bond"] = 0.99 # 利率上升，债券价格下跌
        elif self.state.phase == "peak":
            impact["stock"] = 1.00
            impact["real_estate"] = 1.02 # 资产泡沫
            impact["bond"] = 0.98
        elif self.state.phase == "contraction":
            impact["stock"] = 0.95
            impact["real_estate"] = 0.98
            impact["bond"] = 1.01 # 避险
        elif self.state.phase == "trough":
            impact["stock"] = 0.98
            impact["real_estate"] = 0.99
            impact["bond"] = 1.02
            
        return impact

macro_economy = MacroEconomy()
