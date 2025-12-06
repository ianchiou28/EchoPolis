"""
动态市场引擎 - EchoPolis 核心金融系统
实现虚拟股票市场的价格波动、K线生成、市场事件联动
使用 Longbridge API 获取真实市场数据
"""
import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta

# 导入 Longbridge 客户端
try:
    from .longbridge_client import longbridge_client, STOCK_SYMBOL_MAPPING
    HAS_LONGBRIDGE = True
except ImportError:
    HAS_LONGBRIDGE = False
    longbridge_client = None
    STOCK_SYMBOL_MAPPING = {}


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
        self.current_game_date = datetime.now()  # 使用当前日期
        self.month_count = 0
        
        # 从数据库加载历史数据
        self._load_history_from_db()
    
    def _load_history_from_db(self):
        """从 stock.db 数据库加载历史 K 线数据"""
        if not HAS_LONGBRIDGE or not longbridge_client:
            print("[MarketEngine] Longbridge client not available, using default prices")
            return
        
        print("[MarketEngine] Loading historical data from stock.db...")
        loaded_count = 0
        
        for stock_code in self.stocks.keys():
            # 从数据库获取历史K线
            kline_data = longbridge_client.get_kline_from_db(stock_code, 365)
            
            if kline_data and len(kline_data) > 0:
                # 转换为 OHLCV 对象
                history = []
                for k in kline_data:
                    ohlcv = OHLCV(
                        date=k.get("date", ""),
                        open=float(k.get("open", 0)),
                        high=float(k.get("high", 0)),
                        low=float(k.get("low", 0)),
                        close=float(k.get("close", 0)),
                        volume=int(k.get("volume", 0)),
                        change_pct=float(k.get("change_pct", 0))
                    )
                    history.append(ohlcv)
                
                self.price_history[stock_code] = history
                # 设置当前价格为最新收盘价
                self.current_prices[stock_code] = history[-1].close
                loaded_count += 1
                
                # 更新游戏日期为最新数据日期
                if history[-1].date:
                    try:
                        latest_date = datetime.strptime(history[-1].date, "%Y-%m-%d")
                        if latest_date > self.current_game_date - timedelta(days=30):
                            self.current_game_date = latest_date
                    except:
                        pass
        
        print(f"[MarketEngine] Loaded {loaded_count} stocks from database")
        
        # 计算市场指数
        self._update_market_index()
    
    def _update_market_index(self):
        """根据所有股票价格更新市场指数"""
        if not self.current_prices:
            return
        
        # 计算加权平均指数
        total_value = sum(self.current_prices.values())
        self.market_state.index_value = total_value / len(self.current_prices) * 30  # 缩放到合适范围
    
    def _analyze_stock_pattern(self, stock_code: str) -> Dict:
        """分析股票历史数据的统计特征，用于生成符合历史规律的新数据"""
        history = self.price_history.get(stock_code, [])
        if len(history) < 20:
            stock = self.stocks.get(stock_code)
            return {
                "volatility": stock.volatility if stock else 0.03,
                "avg_return": 0,
                "trend": 0,
                "momentum": 0,
                "support": self.current_prices.get(stock_code, 100) * 0.9,
                "resistance": self.current_prices.get(stock_code, 100) * 1.1
            }
        
        # 计算历史收益率
        returns = []
        for i in range(1, len(history)):
            if history[i-1].close > 0:
                ret = (history[i].close - history[i-1].close) / history[i-1].close
                returns.append(ret)
        
        # 统计特征
        avg_return = sum(returns) / len(returns) if returns else 0
        volatility = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5 if returns else 0.03
        
        # 近期趋势 (最近20天)
        recent_returns = returns[-20:] if len(returns) >= 20 else returns
        trend = sum(recent_returns) / len(recent_returns) if recent_returns else 0
        
        # 动量指标 (最近5天 vs 最近20天)
        recent_5 = returns[-5:] if len(returns) >= 5 else returns
        recent_20 = returns[-20:] if len(returns) >= 20 else returns
        momentum = (sum(recent_5) / len(recent_5)) - (sum(recent_20) / len(recent_20)) if recent_5 and recent_20 else 0
        
        # 支撑位和阻力位 (最近60天的最低和最高价)
        recent_history = history[-60:] if len(history) >= 60 else history
        support = min(h.low for h in recent_history)
        resistance = max(h.high for h in recent_history)
        
        return {
            "volatility": volatility,
            "avg_return": avg_return,
            "trend": trend,
            "momentum": momentum,
            "support": support,
            "resistance": resistance
        }
    
    def generate_next_day(self, stock_code: str) -> OHLCV:
        """基于历史数据生成下一个交易日的 K 线数据"""
        stock = self.stocks.get(stock_code)
        if not stock:
            return None
        
        prev_close = self.current_prices.get(stock_code, stock.base_price)
        pattern = self._analyze_stock_pattern(stock_code)
        
        # 基于历史特征生成收益率
        # 1. 基础收益率：历史均值 + 随机波动
        base_return = pattern["avg_return"] + random.gauss(0, pattern["volatility"])
        
        # 2. 趋势效应：延续近期趋势
        trend_effect = pattern["trend"] * 0.3 * random.uniform(0.5, 1.5)
        
        # 3. 动量效应
        momentum_effect = pattern["momentum"] * 0.2
        
        # 4. 均值回归：如果价格偏离支撑/阻力位太远，会有回归趋势
        if prev_close < pattern["support"]:
            reversion = (pattern["support"] - prev_close) / prev_close * 0.1
        elif prev_close > pattern["resistance"]:
            reversion = (pattern["resistance"] - prev_close) / prev_close * 0.1
        else:
            reversion = 0
        
        # 5. 市场情绪影响
        market_effect = self.market_state.trend_strength * stock.beta * 0.005
        
        # 综合收益率
        daily_return = base_return + trend_effect + momentum_effect + reversion + market_effect
        
        # 限制单日涨跌幅 (A股限制 ±10%，科创板 ±20%)
        max_change = 0.20 if "688" in stock_code else 0.10
        daily_return = max(-max_change, min(max_change, daily_return))
        
        # 生成 OHLCV
        close = prev_close * (1 + daily_return)
        
        # 生成日内波动
        intraday_vol = pattern["volatility"] * 0.6
        high_mult = 1 + random.uniform(0, intraday_vol)
        low_mult = 1 - random.uniform(0, intraday_vol)
        
        open_price = prev_close * (1 + random.gauss(0, pattern["volatility"] * 0.3))
        high = max(open_price, close) * high_mult
        low = min(open_price, close) * low_mult
        
        # 确保逻辑正确
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        # 成交量：基于历史平均和波动
        history = self.price_history.get(stock_code, [])
        if history:
            avg_volume = sum(h.volume for h in history[-20:]) / min(20, len(history))
            volume = int(avg_volume * (1 + abs(daily_return) * 5) * random.uniform(0.7, 1.3))
        else:
            volume = int(1000000 * random.uniform(0.5, 1.5))
        
        change_pct = round(daily_return * 100, 2)
        
        # 生成日期 (当前游戏日期的下一个交易日)
        next_date = self.current_game_date + timedelta(days=1)
        while next_date.weekday() >= 5:  # 跳过周末
            next_date += timedelta(days=1)
        
        return OHLCV(
            date=next_date.strftime("%Y-%m-%d"),
            open=round(open_price, 2),
            high=round(high, 2),
            low=round(low, 2),
            close=round(close, 2),
            volume=volume,
            change_pct=change_pct
        )
    
    def advance_day(self) -> Dict[str, OHLCV]:
        """推进一天，为所有股票生成新的 K 线数据"""
        new_candles = {}
        
        for stock_code in self.stocks.keys():
            candle = self.generate_next_day(stock_code)
            if candle:
                # 更新价格历史
                self.price_history[stock_code].append(candle)
                # 更新当前价格
                self.current_prices[stock_code] = candle.close
                new_candles[stock_code] = candle
        
        # 更新游戏日期
        self.current_game_date += timedelta(days=1)
        while self.current_game_date.weekday() >= 5:  # 跳过周末
            self.current_game_date += timedelta(days=1)
        
        # 更新市场状态
        self._update_market_state()
        self._update_market_index()
        
        # 保存新数据到数据库
        self._save_new_candles_to_db(new_candles)
        
        return new_candles
    
    def advance_month(self) -> List[Dict[str, OHLCV]]:
        """推进一个月（约22个交易日）"""
        all_candles = []
        for _ in range(22):  # 一个月约22个交易日
            daily_candles = self.advance_day()
            all_candles.append(daily_candles)
        self.month_count += 1
        return all_candles
    
    def _update_market_state(self):
        """更新市场状态（趋势、波动率等）"""
        # 计算市场整体涨跌
        total_change = 0
        for stock_code, history in self.price_history.items():
            if len(history) >= 2:
                change = (history[-1].close - history[-2].close) / history[-2].close
                total_change += change
        
        avg_change = total_change / len(self.stocks) if self.stocks else 0
        
        # 更新趋势
        if avg_change > 0.005:
            if self.market_state.trend == TrendType.BULL:
                self.market_state.days_in_trend += 1
                self.market_state.trend_strength = min(1.0, self.market_state.trend_strength + 0.1)
            else:
                self.market_state.trend = TrendType.BULL
                self.market_state.days_in_trend = 1
                self.market_state.trend_strength = 0.3
        elif avg_change < -0.005:
            if self.market_state.trend == TrendType.BEAR:
                self.market_state.days_in_trend += 1
                self.market_state.trend_strength = min(1.0, self.market_state.trend_strength + 0.1)
            else:
                self.market_state.trend = TrendType.BEAR
                self.market_state.days_in_trend = 1
                self.market_state.trend_strength = -0.3
        else:
            self.market_state.trend = TrendType.SIDEWAYS
            self.market_state.trend_strength *= 0.9
        
        # 随机调整波动率
        self.market_state.volatility_multiplier = 0.8 + random.random() * 0.4
    
    def _save_new_candles_to_db(self, candles: Dict[str, OHLCV]):
        """将新生成的 K 线数据保存到数据库"""
        if not HAS_LONGBRIDGE or not longbridge_client:
            return
        
        for stock_code, candle in candles.items():
            kline_data = [{
                "date": candle.date,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
                "change_pct": candle.change_pct
            }]
            longbridge_client.save_kline_to_db(stock_code, kline_data)
        
        # 同步当前价格到数据库
        self._sync_prices_to_db()
    
    def _sync_prices_to_db(self):
        """同步当前价格到数据库"""
        if not HAS_LONGBRIDGE or not longbridge_client:
            return
        
        for code, price in self.current_prices.items():
            stock = self.stocks.get(code)
            if stock:
                history = self.price_history.get(code, [])
                high_52w = max([k.high for k in history[-252:]], default=price) if history else price
                low_52w = min([k.low for k in history[-252:]], default=price) if history else price
                volume = history[-1].volume if history else 0
                
                # 计算涨跌
                prev_close = history[-2].close if len(history) >= 2 else stock.base_price
                change = price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close else 0
                
                longbridge_client.save_stock_price(
                    code=code,
                    current_price=round(price, 2),
                    change=round(change, 2),
                    change_pct=round(change_pct, 2),
                    high_52w=round(high_52w, 2),
                    low_52w=round(low_52w, 2),
                    volume=volume,
                    data_source="ai_generated"
                )
    
    def _generate_daily_candle_deterministic(self, stock: StockInfo, prev_close: float, rng: random.Random) -> OHLCV:
        """生成单日K线 - 使用传入的随机生成器保证确定性"""
        # 基于布朗运动 + 趋势 + 随机事件
        base_return = rng.gauss(0, stock.volatility)
        
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
        high = close * (1 + rng.uniform(0, intraday_range))
        low = close * (1 - rng.uniform(0, intraday_range))
        
        # 开盘价在前收盘附近
        open_price = prev_close * (1 + rng.uniform(-0.01, 0.01))
        
        # 确保逻辑正确
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        # 成交量 (基于波动率)
        base_volume = 1000000
        volume = int(base_volume * (1 + abs(daily_return) * 10) * rng.uniform(0.5, 1.5))
        
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
    
    def advance_month_with_report(self, economic_phase: str = "expansion") -> Dict[str, any]:
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
        
        # 同步本月数据到数据库
        self._sync_prices_to_db()
        
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
        """获取股票实时报价 - 优先使用真实市场数据"""
        if stock_code not in self.stocks:
            return None
        
        stock = self.stocks[stock_code]
        
        # 尝试从 Longbridge 获取真实报价
        real_quote = None
        if HAS_LONGBRIDGE and longbridge_client:
            real_quote = longbridge_client.get_quote(stock_code)
        
        if real_quote:
            # 使用真实市场数据
            current_price = real_quote.get("price", self.current_prices[stock_code])
            change = real_quote.get("change", 0)
            change_pct = real_quote.get("change_pct", 0)
            high_52w = real_quote.get("high_52w", current_price)
            low_52w = real_quote.get("low_52w", current_price)
            volume = real_quote.get("volume", 0)
            
            # 更新本地价格缓存
            self.current_prices[stock_code] = current_price
            
            return {
                "code": stock_code,
                "name": stock.name,
                "sector": stock.sector.value,
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "high_52w": round(high_52w, 2),
                "low_52w": round(low_52w, 2),
                "volume": volume,
                "pe_ratio": stock.pe_ratio,
                "dividend_yield": stock.dividend_yield * 100,
                "volatility": stock.volatility * 100,
                "beta": stock.beta,
                "description": stock.description,
                "data_source": "realtime"  # 标记数据来源
            }
        
        # 如果无法获取真实数据，使用模拟数据
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
            "description": stock.description,
            "data_source": "simulated"  # 标记数据来源
        }
    
    def get_stock_kline(self, stock_code: str, days: int = 30) -> List[Dict]:
        """获取K线数据 - 优先使用真实市场数据"""
        # 尝试从 Longbridge 获取真实 K 线数据
        if HAS_LONGBRIDGE and longbridge_client:
            real_kline = longbridge_client.get_kline_history(stock_code, days)
            if real_kline:
                return real_kline
        
        # 如果无法获取真实数据，使用模拟数据
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


# 全局实例 - 初始化时自动从数据库加载历史数据
market_engine = MarketEngine()
