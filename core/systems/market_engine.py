"""
动态市场引擎 - EchoPolis 核心金融系统
实现虚拟股票市场的价格波动、K线生成、市场事件联动
"""
import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta


class Sector(Enum):
    """行业板块"""
    TECH = "科技"
    FINANCE = "金融"
    CONSUMER = "消费"
    HEALTHCARE = "医疗"
    ENERGY = "能源"
    REAL_ESTATE = "房地产"
    MATERIALS = "材料"
    INDUSTRIAL = "工业"


class TrendType(Enum):
    """趋势类型"""
    BULL = "牛市"
    BEAR = "熊市"
    SIDEWAYS = "震荡"


@dataclass
class StockInfo:
    """股票基本信息"""
    code: str               # 股票代码
    name: str               # 股票名称
    sector: Sector          # 所属行业
    base_price: float       # 基准价格
    volatility: float       # 波动率 (0.1 = 10%日波动)
    beta: float             # 与大盘相关性 (1.0 = 完全同步)
    dividend_yield: float   # 股息率
    pe_ratio: float         # 市盈率
    description: str        # 公司描述


@dataclass
class OHLCV:
    """K线数据 (开高低收量)"""
    date: str               # 日期 YYYY-MM-DD
    open: float             # 开盘价
    high: float             # 最高价
    low: float              # 最低价
    close: float            # 收盘价
    volume: int             # 成交量
    change_pct: float       # 涨跌幅


@dataclass
class MarketState:
    """市场状态"""
    trend: TrendType        # 当前趋势
    index_value: float      # 大盘指数
    trend_strength: float   # 趋势强度 (-1 到 1)
    days_in_trend: int      # 当前趋势持续天数
    volatility_multiplier: float  # 波动率乘数


@dataclass
class StockPosition:
    """持仓信息"""
    stock_code: str         # 股票代码
    shares: int             # 持有数量
    avg_cost: float         # 平均成本
    current_price: float    # 当前价格
    unrealized_pnl: float   # 未实现盈亏
    stop_loss: Optional[float] = None     # 止损价
    take_profit: Optional[float] = None   # 止盈价


class MarketEngine:
    """市场引擎 - 管理虚拟股票市场"""
    
    # 预定义的虚拟股票池
    STOCK_POOL: List[StockInfo] = [
        # 科技股 - 高波动高成长
        StockInfo("ECHO01", "回声科技", Sector.TECH, 45.0, 0.035, 1.3, 0.005, 35, "AI人工智能龙头企业"),
        StockInfo("ECHO02", "量子计算", Sector.TECH, 120.0, 0.045, 1.5, 0.0, 50, "量子计算前沿研发"),
        StockInfo("ECHO03", "云智能", Sector.TECH, 88.0, 0.03, 1.2, 0.01, 28, "企业云服务提供商"),
        
        # 金融股 - 与利率强相关
        StockInfo("ECHO04", "汇通银行", Sector.FINANCE, 25.0, 0.02, 0.9, 0.04, 8, "全国性股份制银行"),
        StockInfo("ECHO05", "诚信保险", Sector.FINANCE, 55.0, 0.025, 0.85, 0.025, 12, "综合保险服务商"),
        StockInfo("ECHO06", "创投资本", Sector.FINANCE, 18.0, 0.04, 1.1, 0.02, 15, "创业投资基金"),
        
        # 消费股 - 稳定增长
        StockInfo("ECHO07", "国民饮品", Sector.CONSUMER, 180.0, 0.018, 0.7, 0.025, 25, "知名饮料品牌"),
        StockInfo("ECHO08", "潮流服饰", Sector.CONSUMER, 35.0, 0.028, 0.9, 0.015, 18, "年轻时尚品牌"),
        StockInfo("ECHO09", "美味餐饮", Sector.CONSUMER, 42.0, 0.022, 0.8, 0.02, 20, "连锁餐饮龙头"),
        
        # 医疗股 - 防御性强
        StockInfo("ECHO10", "康健医药", Sector.HEALTHCARE, 95.0, 0.025, 0.6, 0.012, 30, "创新药研发企业"),
        StockInfo("ECHO11", "智慧医疗", Sector.HEALTHCARE, 68.0, 0.03, 0.75, 0.008, 35, "医疗AI解决方案"),
        StockInfo("ECHO12", "养老健康", Sector.HEALTHCARE, 28.0, 0.02, 0.5, 0.03, 15, "养老服务产业"),
        
        # 能源股 - 周期性
        StockInfo("ECHO13", "绿能科技", Sector.ENERGY, 78.0, 0.035, 1.1, 0.018, 22, "新能源发电设备"),
        StockInfo("ECHO14", "锂电未来", Sector.ENERGY, 135.0, 0.04, 1.25, 0.005, 40, "动力电池制造商"),
        StockInfo("ECHO15", "氢能先锋", Sector.ENERGY, 55.0, 0.05, 1.4, 0.0, 60, "氢能源研发"),
        
        # 房地产 - 与利率负相关
        StockInfo("ECHO16", "安居地产", Sector.REAL_ESTATE, 12.0, 0.03, 1.0, 0.05, 6, "住宅地产开发"),
        StockInfo("ECHO17", "商业广场", Sector.REAL_ESTATE, 22.0, 0.025, 0.95, 0.045, 8, "商业地产运营"),
        
        # 材料股 - 强周期
        StockInfo("ECHO18", "稀土材料", Sector.MATERIALS, 48.0, 0.038, 1.2, 0.02, 18, "稀土深加工"),
        
        # 工业股
        StockInfo("ECHO19", "智能制造", Sector.INDUSTRIAL, 65.0, 0.028, 1.0, 0.022, 16, "工业机器人"),
        StockInfo("ECHO20", "基建重工", Sector.INDUSTRIAL, 8.5, 0.022, 0.85, 0.035, 7, "基础设施建设"),
    ]
    
    def __init__(self):
        self.stocks: Dict[str, StockInfo] = {s.code: s for s in self.STOCK_POOL}
        self.current_prices: Dict[str, float] = {s.code: s.base_price for s in self.STOCK_POOL}
        self.price_history: Dict[str, List[OHLCV]] = {s.code: [] for s in self.STOCK_POOL}
        self.market_state = MarketState(
            trend=TrendType.SIDEWAYS,
            index_value=3000.0,
            trend_strength=0.0,
            days_in_trend=0,
            volatility_multiplier=1.0
        )
        self.current_game_date = datetime(2024, 1, 1)  # 游戏内日期
        self.month_count = 0
        
    def initialize_history(self, months: int = 12):
        """初始化历史K线数据"""
        start_date = self.current_game_date - timedelta(days=months * 30)
        
        for stock_code, stock_info in self.stocks.items():
            price = stock_info.base_price * random.uniform(0.7, 1.0)  # 从较低点开始
            history = []
            
            current_date = start_date
            while current_date < self.current_game_date:
                ohlcv = self._generate_daily_candle(stock_info, price)
                ohlcv.date = current_date.strftime("%Y-%m-%d")
                history.append(ohlcv)
                price = ohlcv.close
                current_date += timedelta(days=1)
                
                # 跳过周末
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=2)
            
            self.price_history[stock_code] = history
            self.current_prices[stock_code] = price
            
    def _generate_daily_candle(self, stock: StockInfo, prev_close: float) -> OHLCV:
        """生成单日K线"""
        # 基于布朗运动 + 趋势 + 随机事件
        base_return = random.gauss(0, stock.volatility)
        
        # 应用市场趋势
        trend_effect = self.market_state.trend_strength * stock.beta * 0.01
        
        # 应用波动率乘数
        base_return *= self.market_state.volatility_multiplier
        
        # 日收益率
        daily_return = base_return + trend_effect
        
        # 生成OHLC
        close = prev_close * (1 + daily_return)
        
        # 日内波动
        intraday_range = stock.volatility * 0.8
        high = close * (1 + random.uniform(0, intraday_range))
        low = close * (1 - random.uniform(0, intraday_range))
        
        # 开盘价在前收盘附近
        open_price = prev_close * (1 + random.uniform(-0.01, 0.01))
        
        # 确保逻辑正确
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        # 成交量 (基于波动率)
        base_volume = 1000000
        volume = int(base_volume * (1 + abs(daily_return) * 10) * random.uniform(0.5, 1.5))
        
        change_pct = round((close - prev_close) / prev_close * 100, 2)
        
        return OHLCV(
            date="",
            open=round(open_price, 2),
            high=round(high, 2),
            low=round(low, 2),
            close=round(close, 2),
            volume=volume,
            change_pct=change_pct
        )
    
    def advance_month(self, economic_phase: str = "expansion") -> Dict[str, any]:
        """推进一个月的市场时间
        
        Args:
            economic_phase: 经济周期阶段 (expansion/peak/contraction/trough)
        
        Returns:
            月度市场报告
        """
        self.month_count += 1
        
        # 更新市场趋势
        self._update_market_trend(economic_phase)
        
        # 生成本月每日K线 (约22个交易日)
        trading_days = random.randint(20, 23)
        month_summary = {
            "gainers": [],      # 涨幅榜
            "losers": [],       # 跌幅榜
            "sector_performance": {},  # 板块表现
            "index_change": 0,
            "market_events": []
        }
        
        sector_returns = {sector: [] for sector in Sector}
        
        for stock_code, stock_info in self.stocks.items():
            prev_price = self.current_prices[stock_code]
            month_start_price = prev_price
            
            for day in range(trading_days):
                ohlcv = self._generate_daily_candle(stock_info, prev_price)
                ohlcv.date = (self.current_game_date + timedelta(days=day)).strftime("%Y-%m-%d")
                self.price_history[stock_code].append(ohlcv)
                prev_price = ohlcv.close
                
                # 限制历史长度，保留最近365天
                if len(self.price_history[stock_code]) > 365:
                    self.price_history[stock_code] = self.price_history[stock_code][-365:]
            
            self.current_prices[stock_code] = prev_price
            
            # 计算月度涨跌幅
            month_return = (prev_price - month_start_price) / month_start_price * 100
            
            if month_return > 0:
                month_summary["gainers"].append((stock_code, stock_info.name, round(month_return, 2)))
            else:
                month_summary["losers"].append((stock_code, stock_info.name, round(month_return, 2)))
            
            sector_returns[stock_info.sector].append(month_return)
        
        # 更新游戏日期
        self.current_game_date += timedelta(days=30)
        
        # 计算板块表现
        for sector, returns in sector_returns.items():
            if returns:
                avg_return = sum(returns) / len(returns)
                month_summary["sector_performance"][sector.value] = round(avg_return, 2)
        
        # 排序
        month_summary["gainers"] = sorted(month_summary["gainers"], key=lambda x: x[2], reverse=True)[:5]
        month_summary["losers"] = sorted(month_summary["losers"], key=lambda x: x[2])[:5]
        
        # 更新大盘指数
        all_returns = [r for returns in sector_returns.values() for r in returns]
        avg_market_return = sum(all_returns) / len(all_returns) if all_returns else 0
        self.market_state.index_value *= (1 + avg_market_return / 100)
        month_summary["index_change"] = round(avg_market_return, 2)
        
        # 生成市场事件
        month_summary["market_events"] = self._generate_market_events(economic_phase)
        
        return month_summary
    
    def _update_market_trend(self, economic_phase: str):
        """根据经济周期更新市场趋势"""
        self.market_state.days_in_trend += 30
        
        # 趋势转换概率
        trend_change_prob = 0.15 + (self.market_state.days_in_trend / 365) * 0.1
        
        if random.random() < trend_change_prob:
            # 根据经济阶段决定新趋势
            if economic_phase == "expansion":
                weights = [0.5, 0.2, 0.3]  # 牛市概率高
            elif economic_phase == "peak":
                weights = [0.3, 0.3, 0.4]  # 震荡概率高
            elif economic_phase == "contraction":
                weights = [0.2, 0.5, 0.3]  # 熊市概率高
            else:  # trough
                weights = [0.4, 0.3, 0.3]  # 可能反转
            
            new_trend = random.choices(
                [TrendType.BULL, TrendType.BEAR, TrendType.SIDEWAYS],
                weights=weights
            )[0]
            
            if new_trend != self.market_state.trend:
                self.market_state.trend = new_trend
                self.market_state.days_in_trend = 0
        
        # 更新趋势强度
        if self.market_state.trend == TrendType.BULL:
            self.market_state.trend_strength = random.uniform(0.2, 0.8)
        elif self.market_state.trend == TrendType.BEAR:
            self.market_state.trend_strength = random.uniform(-0.8, -0.2)
        else:
            self.market_state.trend_strength = random.uniform(-0.2, 0.2)
        
        # 波动率调整
        if economic_phase in ["peak", "contraction"]:
            self.market_state.volatility_multiplier = random.uniform(1.2, 1.8)
        else:
            self.market_state.volatility_multiplier = random.uniform(0.8, 1.2)
    
    def _generate_market_events(self, economic_phase: str) -> List[str]:
        """生成市场事件新闻"""
        events = []
        
        bull_events = [
            "央行宣布降准，释放长期资金",
            "科技板块获政策利好支持",
            "外资持续净流入A股市场",
            "消费数据超预期，经济复苏信号明显",
            "新能源汽车销量创历史新高",
        ]
        
        bear_events = [
            "地缘政治紧张局势加剧",
            "通胀数据高于预期，加息预期升温",
            "多家上市公司业绩不及预期",
            "房地产市场持续低迷",
            "外资大幅减持A股",
        ]
        
        neutral_events = [
            "市场观望情绪浓厚，成交量萎缩",
            "板块轮动加快，热点切换频繁",
            "大盘窄幅震荡，等待方向选择",
            "机构调仓换股，风格切换明显",
        ]
        
        if self.market_state.trend == TrendType.BULL:
            events.extend(random.sample(bull_events, min(2, len(bull_events))))
        elif self.market_state.trend == TrendType.BEAR:
            events.extend(random.sample(bear_events, min(2, len(bear_events))))
        else:
            events.extend(random.sample(neutral_events, min(2, len(neutral_events))))
        
        return events
    
    def get_stock_quote(self, stock_code: str) -> Optional[Dict]:
        """获取股票实时报价"""
        if stock_code not in self.stocks:
            return None
        
        stock = self.stocks[stock_code]
        current_price = self.current_prices[stock_code]
        history = self.price_history.get(stock_code, [])
        
        prev_close = history[-2].close if len(history) >= 2 else stock.base_price
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close else 0
        
        return {
            "code": stock_code,
            "name": stock.name,
            "sector": stock.sector.value,
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "high_52w": max([k.high for k in history[-252:]] if history else [current_price]),
            "low_52w": min([k.low for k in history[-252:]] if history else [current_price]),
            "volume": history[-1].volume if history else 0,
            "pe_ratio": stock.pe_ratio,
            "dividend_yield": stock.dividend_yield * 100,
            "volatility": stock.volatility * 100,
            "beta": stock.beta,
            "description": stock.description
        }
    
    def get_stock_kline(self, stock_code: str, days: int = 30) -> List[Dict]:
        """获取K线数据"""
        if stock_code not in self.price_history:
            return []
        
        history = self.price_history[stock_code][-days:]
        return [
            {
                "date": k.date,
                "open": k.open,
                "high": k.high,
                "low": k.low,
                "close": k.close,
                "volume": k.volume,
                "change_pct": k.change_pct
            }
            for k in history
        ]
    
    def get_all_stocks(self) -> List[Dict]:
        """获取所有股票列表"""
        result = []
        for code, stock in self.stocks.items():
            quote = self.get_stock_quote(code)
            if quote:
                result.append(quote)
        return result
    
    def get_sector_stocks(self, sector: Sector) -> List[Dict]:
        """获取某板块所有股票"""
        return [
            self.get_stock_quote(code) 
            for code, stock in self.stocks.items() 
            if stock.sector == sector
        ]
    
    def get_market_overview(self) -> Dict:
        """获取市场概览"""
        all_quotes = self.get_all_stocks()
        
        gainers = sorted([q for q in all_quotes if q["change_pct"] > 0], 
                        key=lambda x: x["change_pct"], reverse=True)
        losers = sorted([q for q in all_quotes if q["change_pct"] < 0], 
                       key=lambda x: x["change_pct"])
        
        return {
            "index_value": round(self.market_state.index_value, 2),
            "trend": self.market_state.trend.value,
            "trend_strength": round(self.market_state.trend_strength, 2),
            "volatility": round(self.market_state.volatility_multiplier, 2),
            "game_date": self.current_game_date.strftime("%Y-%m-%d"),
            "month": self.month_count,
            "top_gainers": gainers[:3],
            "top_losers": losers[:3],
            "total_stocks": len(all_quotes),
            "advancing": len([q for q in all_quotes if q["change_pct"] > 0]),
            "declining": len([q for q in all_quotes if q["change_pct"] < 0]),
        }
    
    def apply_sector_event(self, sector: Sector, impact: float):
        """应用板块事件影响
        
        Args:
            sector: 受影响的板块
            impact: 影响幅度 (-0.2 到 0.2)
        """
        for code, stock in self.stocks.items():
            if stock.sector == sector:
                self.current_prices[code] *= (1 + impact)
                self.current_prices[code] = round(self.current_prices[code], 2)
    
    def apply_market_shock(self, impact: float):
        """应用全市场冲击事件（如股灾、大牛市）
        
        Args:
            impact: 影响幅度 (-0.3 到 0.3)
        """
        for code, stock in self.stocks.items():
            # 根据beta调整影响
            adjusted_impact = impact * stock.beta
            self.current_prices[code] *= (1 + adjusted_impact)
            self.current_prices[code] = round(self.current_prices[code], 2)
        
        self.market_state.index_value *= (1 + impact)


# 全局实例
market_engine = MarketEngine()
# 初始化历史数据
market_engine.initialize_history(12)
