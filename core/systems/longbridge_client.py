"""
Longbridge API 客户端 - 获取真实股票行情数据
用于 EchoPolis 游戏的股票价格和K线同步
使用 Longbridge 官方 Python SDK
"""
import os
import json
import time
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib
import hmac
import requests

# 尝试导入 Longbridge SDK
try:
    from longbridge.openapi import QuoteContext, Config, Period, AdjustType
    HAS_LONGBRIDGE_SDK = True
except ImportError:
    HAS_LONGBRIDGE_SDK = False
    print("[Longbridge] SDK not installed. Run: pip install longbridge")


def get_project_root() -> str:
    """获取项目根目录"""
    current_dir = os.path.dirname(__file__)
    while current_dir != os.path.dirname(current_dir):
        if os.path.exists(os.path.join(current_dir, 'README.md')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


# Longbridge API 配置
LONGBRIDGE_CONFIG = {
    "app_key": os.getenv("LONGBRIDGE_APP_KEY", "c11f9edb62576c25f9af35c3341d3b12"),
    "app_secret": os.getenv("LONGBRIDGE_APP_SECRET", "c4194bb057625fd4cd322b92894feed0fc62ab02c0c3bdb9e9f52df1fb14565c"),
    "access_token": os.getenv("LONGBRIDGE_ACCESS_TOKEN", "m_eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJsb25nYnJpZGdlIiwic3ViIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzcyNDQ3NDQ1LCJpYXQiOjE3NjQ2NzE0NDEsImFrIjoiYzExZjllZGI2MjU3NmMyNWY5YWYzNWMzMzQxZDNiMTIiLCJhYWlkIjoyMTAwMzc4NiwiYWMiOiJsYl9wYXBlcnRyYWRpbmciLCJtaWQiOjI0NzQxODI3LCJzaWQiOiJHdVliK081bTE0QlFVczlNWUpHRXd3PT0iLCJibCI6MCwidWwiOjAsImlrIjoibGJfcGFwZXJ0cmFkaW5nXzIxMDAzNzg2In0.oANThbBvbOftrrRc4RXqqWlBbfBCbJtXBVscmTr5wa0x7P5qEt1BRK9_Q8JyXUetQFp71NmYE0CyvUtcGJs9ti9R5tjV8WnQRGPL-DxaKVs9TdLDXmIYP9cpZGm7tgfA-Lx8jAWIfTjIdpTryIXaSg5DmBRME0Vqi0Hqhuylx16p7i6g5viG4YZReLdLCCB1JUQgA7YfJZNGtsvhG4OpMy_hvur0-d20eWTPY8tp8mvI0_6EPWdvR9UXbbAieuaqTWsafO_9pb2HNWb_eUGyWJyipCkFNtKd4VqXepVCGWdrA_YHzfh9RzihHbUwUYFAERAUwly4RfmQKejXSTFRp6AZ2w3Vp4dg414mFbtyjY-Ch6AV2XLLNmkPZf42rxcHwbXlNcOqMyZctNpmUNWxhc9D9sn87fVNJzww9qw7xdESC0mfcESdOjx-GpCtcKInfa-8_Mbvo9_Q5ju2EDY7AQfO2p-srWRNUoa6ACkQLjxz34gIT7CE4MjERz7QQil3PFyxkPFkUDNSiGQYbbjH__prw_z6X-8XhmNz_m6_5sNvzjUC2B6teWVylxcPlnZVsOc2T5EgO10sBy_OYqe_uI0dFxYP2fXSZHf4CgzWb_1gpz_nTEH181CXPMpDYwYvFq828-JFWPA5C-4bdDzQcnCyjVCgX-2ENpfSntcW2TU"),
    "base_url": "https://openapi.longbridgeapp.com"
}

# 游戏股票与真实股票的映射关系
# 全部对应 A 股市场，使用 Longbridge 格式
STOCK_MAPPING = {
    # 游戏代码 -> (真实代码, 市场, 缩放因子, 真实名称, 映射理由)
    
    # 科技股 - 高波动高成长
    "ECHO01": ("002230.SZ", "CN", 1.0, "科大讯飞", "A股人工智能语音龙头，典型的高波动科技股"),
    "ECHO02": ("688027.SH", "CN", 1.0, "国盾量子", "科创板量子通信第一股，具有极高的研发投入和不确定性"),
    "ECHO03": ("688111.SH", "CN", 1.0, "金山办公", "国产软件/云服务龙头，高市盈率，高成长"),
    
    # 金融股 - 与利率强相关
    "ECHO04": ("600036.SH", "CN", 1.0, "招商银行", "股份制银行之王，股价弹性优于国有大行"),
    "ECHO05": ("601318.SH", "CN", 1.0, "中国平安", "综合金融巨头，包含保险、银行、投资，A股核心资产"),
    "ECHO06": ("300059.SZ", "CN", 1.0, "东方财富", "券茅，主要靠流量和基金销售，不仅是金融也是互联网成长股"),
    
    # 消费股 - 稳定增长
    "ECHO07": ("600809.SH", "CN", 1.0, "山西汾酒", "相比茅台，汾酒的股价和弹性更符合描述"),
    "ECHO08": ("002832.SZ", "CN", 1.0, "比音勒芬", "A股高端服饰代表，业绩稳健"),
    "ECHO09": ("605108.SH", "CN", 1.0, "同庆楼", "A股稀缺的纯正餐饮老字号，符合餐饮龙头的描述"),
    
    # 医疗股 - 防御性强
    "ECHO10": ("600276.SH", "CN", 1.0, "恒瑞医药", "医药一哥，创新药转型的代表，防御性与成长性兼备"),
    "ECHO11": ("688271.SH", "CN", 1.0, "联影医疗", "高端医疗影像设备，医疗+硬科技的结合"),
    "ECHO12": ("002223.SZ", "CN", 1.0, "鱼跃医疗", "家用医疗器械（制氧机等），典型的养老概念"),
    
    # 能源股 - 周期性
    "ECHO13": ("300274.SZ", "CN", 1.0, "阳光电源", "光伏逆变器龙头，价格和波动性都非常符合"),
    "ECHO14": ("300750.SZ", "CN", 1.0, "宁德时代", "宁王，创业板一哥，动力电池龙头"),
    "ECHO15": ("688339.SH", "CN", 1.0, "亿华通", "氢燃料电池系统龙头，科创板硬科技"),
    
    # 房地产 - 与利率负相关
    "ECHO16": ("600048.SH", "CN", 1.0, "保利发展", "央企地产龙头，在地产下行周期中韧性最强"),
    "ECHO17": ("600007.SH", "CN", 1.0, "中国国贸", "核心地段商业地产运营，现金流稳定，收租股"),
    
    # 材料股 - 强周期
    "ECHO18": ("600111.SH", "CN", 1.0, "北方稀土", "全球最大的轻稀土供应商，典型的强周期资源股"),
    
    # 工业股
    "ECHO19": ("300124.SZ", "CN", 1.0, "汇川技术", "工业自动化龙头，被称为工控界的小华为"),
    "ECHO20": ("601668.SH", "CN", 1.0, "中国建筑", "全球最大工程承包商，低估值、低股价、高分红"),
}

# 为兼容性提供别名
STOCK_SYMBOL_MAPPING = STOCK_MAPPING


@dataclass
class RealQuote:
    """真实行情数据"""
    symbol: str
    name: str
    price: float
    prev_close: float
    open: float
    high: float
    low: float
    volume: int
    change: float
    change_pct: float
    timestamp: int


class LongbridgeClient:
    """Longbridge API 客户端"""
    
    def __init__(self, db_path: str = None):
        self.config = LONGBRIDGE_CONFIG
        # 使用单独的 stock.db 存储所有股票数据
        if db_path is None:
            project_root = get_project_root()
            self.db_path = os.path.join(project_root, "stock.db")
        else:
            self.db_path = db_path
        print(f"[Longbridge] Stock database path: {self.db_path}")
        self.cache: Dict[str, RealQuote] = {}
        self.cache_time: Dict[str, float] = {}
        self.cache_ttl = 60  # 缓存60秒
        self._init_db()
        self._init_stock_info()  # 初始化股票基础信息
        
    def _init_db(self):
        """初始化股票数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 股票基础信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stocks (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    sector TEXT NOT NULL,
                    base_price REAL NOT NULL,
                    volatility REAL NOT NULL,
                    beta REAL NOT NULL,
                    dividend_yield REAL NOT NULL,
                    pe_ratio REAL NOT NULL,
                    description TEXT,
                    real_symbol TEXT,
                    real_market TEXT,
                    scale_factor REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 股票价格缓存表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_price_cache (
                    symbol TEXT PRIMARY KEY,
                    game_code TEXT,
                    price REAL,
                    prev_close REAL,
                    open_price REAL,
                    high REAL,
                    low REAL,
                    volume INTEGER,
                    change_pct REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # K线数据缓存表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_kline_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_code TEXT,
                    date TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    change_pct REAL,
                    UNIQUE(game_code, date)
                )
            ''')
            
            # 股票实时价格表（存储当前价格）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_current_prices (
                    code TEXT PRIMARY KEY,
                    current_price REAL NOT NULL,
                    change REAL DEFAULT 0,
                    change_pct REAL DEFAULT 0,
                    high_52w REAL,
                    low_52w REAL,
                    volume INTEGER DEFAULT 0,
                    data_source TEXT DEFAULT 'simulated',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def _init_stock_info(self):
        """初始化所有股票基础信息到数据库"""
        # 从 market_engine 导入股票池定义
        from .market_engine import MarketEngine
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for stock in MarketEngine.STOCK_POOL:
                # 获取真实股票映射信息
                mapping = STOCK_MAPPING.get(stock.code)
                real_symbol = mapping[0] if mapping else None
                real_market = mapping[1] if mapping else None
                scale_factor = mapping[2] if mapping else 1.0
                
                cursor.execute('''
                    INSERT OR REPLACE INTO stocks 
                    (code, name, sector, base_price, volatility, beta, 
                     dividend_yield, pe_ratio, description, 
                     real_symbol, real_market, scale_factor, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    stock.code,
                    stock.name,
                    stock.sector.value,
                    stock.base_price,
                    stock.volatility,
                    stock.beta,
                    stock.dividend_yield,
                    stock.pe_ratio,
                    stock.description,
                    real_symbol,
                    real_market,
                    scale_factor
                ))
            
            conn.commit()
            print(f"[Longbridge] Initialized {len(MarketEngine.STOCK_POOL)} stocks in database")
    
    def save_stock_price(self, code: str, current_price: float, change: float = 0, 
                         change_pct: float = 0, high_52w: float = None, 
                         low_52w: float = None, volume: int = 0, 
                         data_source: str = "simulated"):
        """保存股票当前价格到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO stock_current_prices 
                (code, current_price, change, change_pct, high_52w, low_52w, volume, data_source, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (code, current_price, change, change_pct, high_52w, low_52w, volume, data_source))
            conn.commit()
    
    def get_stock_price_from_db(self, code: str) -> Optional[Dict]:
        """从数据库获取股票当前价格"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT current_price, change, change_pct, high_52w, low_52w, volume, data_source, updated_at
                FROM stock_current_prices WHERE code = ?
            ''', (code,))
            row = cursor.fetchone()
            if row:
                return {
                    "code": code,
                    "current_price": row[0],
                    "change": row[1],
                    "change_pct": row[2],
                    "high_52w": row[3],
                    "low_52w": row[4],
                    "volume": row[5],
                    "data_source": row[6],
                    "updated_at": row[7]
                }
        return None
    
    def get_all_stocks_from_db(self) -> List[Dict]:
        """从数据库获取所有股票信息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.*, p.current_price, p.change, p.change_pct, p.high_52w, p.low_52w, p.volume, p.data_source
                FROM stocks s
                LEFT JOIN stock_current_prices p ON s.code = p.code
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def save_kline_to_db(self, game_code: str, kline_data: List[Dict]):
        """保存K线数据到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for k in kline_data:
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_kline_cache 
                    (game_code, date, open, high, low, close, volume, change_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    game_code,
                    k.get("date", ""),
                    k.get("open", 0),
                    k.get("high", 0),
                    k.get("low", 0),
                    k.get("close", 0),
                    k.get("volume", 0),
                    k.get("change_pct", 0)
                ))
            conn.commit()
    
    def get_kline_from_db(self, game_code: str, days: int = 60) -> List[Dict]:
        """从数据库获取K线数据"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, open, high, low, close, volume, change_pct
                FROM stock_kline_cache 
                WHERE game_code = ?
                ORDER BY date DESC
                LIMIT ?
            ''', (game_code, days))
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]
    
    def _init_quote_context(self):
        """初始化 Longbridge QuoteContext"""
        if not HAS_LONGBRIDGE_SDK:
            return None
        
        if hasattr(self, '_quote_ctx') and self._quote_ctx:
            return self._quote_ctx
        
        try:
            config = Config(
                app_key=self.config["app_key"],
                app_secret=self.config["app_secret"],
                access_token=self.config["access_token"]
            )
            self._quote_ctx = QuoteContext(config)
            print("[Longbridge] QuoteContext initialized successfully")
            return self._quote_ctx
        except Exception as e:
            print(f"[Longbridge] Failed to initialize QuoteContext: {e}")
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """生成 API 请求头"""
        timestamp = str(int(time.time()))
        return {
            "X-Api-Key": self.config["app_key"],
            "Authorization": f"Bearer {self.config['access_token']}",
            "X-Timestamp": timestamp,
            "Content-Type": "application/json"
        }
    
    def get_quote(self, symbol: str) -> Optional[RealQuote]:
        """获取单只股票实时行情
        
        Args:
            symbol: 股票代码，如 "700.HK", "AAPL.US"
        """
        # 检查缓存
        cache_key = symbol
        if cache_key in self.cache:
            if time.time() - self.cache_time.get(cache_key, 0) < self.cache_ttl:
                return self.cache[cache_key]
        
        # 使用 SDK 获取实时行情
        ctx = self._init_quote_context()
        if ctx:
            try:
                resp = ctx.quote([symbol])
                if resp:
                    q = resp[0]
                    quote = RealQuote(
                        symbol=symbol,
                        name=q.symbol,
                        price=float(q.last_done),
                        prev_close=float(q.prev_close),
                        open=float(q.open),
                        high=float(q.high),
                        low=float(q.low),
                        volume=int(q.volume),
                        change=float(q.last_done) - float(q.prev_close),
                        change_pct=((float(q.last_done) - float(q.prev_close)) / float(q.prev_close) * 100) if q.prev_close else 0,
                        timestamp=int(time.time())
                    )
                    self.cache[cache_key] = quote
                    self.cache_time[cache_key] = time.time()
                    self._save_to_db(symbol, quote)
                    return quote
            except Exception as e:
                print(f"[Longbridge] SDK failed to get quote for {symbol}: {e}")
        
        # 从数据库获取缓存
        return self._get_from_db(symbol)
    
    def get_kline(self, symbol: str, period: str = "day", count: int = 60) -> List[Dict]:
        """使用 SDK 获取K线数据
        
        Args:
            symbol: 股票代码
            period: 周期 (day/week/month)
            count: 数量
        """
        ctx = self._init_quote_context()
        if not ctx:
            print(f"[Longbridge] QuoteContext not available for {symbol}")
            return []
        
        try:
            # 映射周期
            period_map = {
                "day": Period.Day,
                "week": Period.Week,
                "month": Period.Month,
            }
            lb_period = period_map.get(period, Period.Day)
            
            print(f"[Longbridge] Fetching K-line for {symbol}, count={count}")
            resp = ctx.candlesticks(symbol, lb_period, count, AdjustType.ForwardAdjust)
            
            if resp:
                klines = []
                for candle in resp:
                    klines.append({
                        "timestamp": candle.timestamp.timestamp() if hasattr(candle.timestamp, 'timestamp') else candle.timestamp,
                        "open": float(candle.open),
                        "high": float(candle.high),
                        "low": float(candle.low),
                        "close": float(candle.close),
                        "volume": int(candle.volume),
                        "turnover": float(candle.turnover) if hasattr(candle, 'turnover') else 0
                    })
                print(f"[Longbridge] Got {len(klines)} K-lines for {symbol}")
                return klines
        except Exception as e:
            print(f"[Longbridge] Failed to get kline for {symbol}: {e}")
        
        return []
    
    def _save_to_db(self, symbol: str, quote: RealQuote):
        """保存行情到数据库"""
        game_code = None
        for gc, (real_symbol, _, _) in STOCK_MAPPING.items():
            if real_symbol == symbol:
                game_code = gc
                break
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO stock_price_cache 
                (symbol, game_code, price, prev_close, open_price, high, low, volume, change_pct, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (symbol, game_code, quote.price, quote.prev_close, quote.open, 
                  quote.high, quote.low, quote.volume, quote.change_pct))
            conn.commit()
    
    def _get_from_db(self, symbol: str) -> Optional[RealQuote]:
        """从数据库获取缓存的行情"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT price, prev_close, open_price, high, low, volume, change_pct
                FROM stock_price_cache WHERE symbol = ?
            ''', (symbol,))
            row = cursor.fetchone()
            if row:
                return RealQuote(
                    symbol=symbol,
                    name=symbol,
                    price=row[0],
                    prev_close=row[1],
                    open=row[2],
                    high=row[3],
                    low=row[4],
                    volume=row[5],
                    change=row[0] - row[1],
                    change_pct=row[6],
                    timestamp=int(time.time())
                )
        return None
    
    def get_game_stock_price(self, game_code: str) -> Optional[Tuple[float, float]]:
        """获取游戏股票的真实价格（经过缩放）
        
        Returns:
            (当前价格, 涨跌幅) 或 None
        """
        mapping = STOCK_MAPPING.get(game_code)
        if not mapping:
            return None
        
        real_symbol = mapping[0]  # 真实股票代码
        scale = mapping[2]  # 缩放因子
        quote = self.get_quote(real_symbol)
        
        if quote and quote.price > 0:
            scaled_price = quote.price * scale
            return (round(scaled_price, 2), quote.change_pct)
        
        return None
    
    def sync_all_game_stocks(self) -> Dict[str, Tuple[float, float]]:
        """同步所有游戏股票价格
        
        Returns:
            {game_code: (price, change_pct)}
        """
        results = {}
        for game_code in STOCK_MAPPING.keys():
            price_data = self.get_game_stock_price(game_code)
            if price_data:
                results[game_code] = price_data
        return results
    
    def get_game_stock_kline(self, game_code: str, days: int = 60, force_refresh: bool = False) -> List[Dict]:
        """获取游戏股票的K线数据（经过缩放）
        
        优先从数据库读取，如果数据不足或强制刷新则从API获取
        """
        # 先尝试从数据库获取
        if not force_refresh:
            cached_klines = self.get_kline_from_db(game_code, days)
            if len(cached_klines) >= days * 0.8:  # 如果有80%以上的数据，使用缓存
                return cached_klines
        
        mapping = STOCK_MAPPING.get(game_code)
        if not mapping:
            return self.get_kline_from_db(game_code, days)  # 返回缓存数据
        
        real_symbol = mapping[0]  # 真实股票代码
        scale = mapping[2]  # 缩放因子
        klines = self.get_kline(real_symbol, "day", days)
        
        if not klines:
            # API 获取失败，返回缓存数据
            return self.get_kline_from_db(game_code, days)
        
        # 缩放价格并转换格式
        scaled_klines = []
        for k in klines:
            timestamp = k.get("timestamp", "")
            # 转换时间戳为日期字符串
            if isinstance(timestamp, (int, float)):
                date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            else:
                date_str = str(timestamp)[:10] if timestamp else ""
            
            open_price = float(k.get("open", 0)) * scale
            close_price = float(k.get("close", 0)) * scale
            prev_close = float(k.get("close", open_price))
            change_pct = ((close_price - open_price) / open_price * 100) if open_price > 0 else 0
            
            scaled_klines.append({
                "date": date_str,
                "open": round(open_price, 2),
                "high": round(float(k.get("high", 0)) * scale, 2),
                "low": round(float(k.get("low", 0)) * scale, 2),
                "close": round(close_price, 2),
                "volume": int(k.get("volume", 0)),
                "change_pct": round(change_pct, 2)
            })
        
        # 保存到数据库
        if scaled_klines:
            self.save_kline_to_db(game_code, scaled_klines)
        
        return scaled_klines
    
    def fetch_and_store_all_klines(self, days: int = 365) -> Dict[str, int]:
        """从 Longbridge 获取所有股票的K线数据并存入数据库
        
        Args:
            days: 获取多少天的历史数据，默认365天
            
        Returns:
            {game_code: 获取到的K线数量}
        """
        results = {}
        
        print(f"[Longbridge] Starting to fetch K-line data for {len(STOCK_MAPPING)} stocks...")
        
        for game_code, mapping in STOCK_MAPPING.items():
            real_symbol = mapping[0]  # 真实股票代码
            scale = mapping[2]  # 缩放因子
            real_name = mapping[3] if len(mapping) > 3 else real_symbol  # 真实名称
            try:
                print(f"[Longbridge] Fetching {game_code} -> {real_name} ({real_symbol})...")
                klines = self.get_kline(real_symbol, "day", days)
                
                if klines:
                    # 缩放价格并转换格式
                    scaled_klines = []
                    for k in klines:
                        timestamp = k.get("timestamp", "")
                        if isinstance(timestamp, (int, float)):
                            date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                        else:
                            date_str = str(timestamp)[:10] if timestamp else ""
                        
                        open_price = float(k.get("open", 0)) * scale
                        close_price = float(k.get("close", 0)) * scale
                        change_pct = ((close_price - open_price) / open_price * 100) if open_price > 0 else 0
                        
                        scaled_klines.append({
                            "date": date_str,
                            "open": round(open_price, 2),
                            "high": round(float(k.get("high", 0)) * scale, 2),
                            "low": round(float(k.get("low", 0)) * scale, 2),
                            "close": round(close_price, 2),
                            "volume": int(k.get("volume", 0)),
                            "change_pct": round(change_pct, 2)
                        })
                    
                    # 保存到数据库
                    self.save_kline_to_db(game_code, scaled_klines)
                    results[game_code] = len(scaled_klines)
                    print(f"[Longbridge] {game_code}: Stored {len(scaled_klines)} K-lines")
                else:
                    results[game_code] = 0
                    print(f"[Longbridge] {game_code}: No data received")
                
                # 避免 API 限流，稍微延迟
                time.sleep(0.5)
                
            except Exception as e:
                print(f"[Longbridge] Error fetching {game_code}: {e}")
                results[game_code] = 0
        
        print(f"[Longbridge] Finished fetching K-line data. Total: {sum(results.values())} K-lines")
        return results
    
    def get_stock_kline_count(self, game_code: str) -> int:
        """获取数据库中某只股票的K线数量"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM stock_kline_cache WHERE game_code = ?
            ''', (game_code,))
            return cursor.fetchone()[0]
    
    def get_all_kline_counts(self) -> Dict[str, int]:
        """获取所有股票的K线数量"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT game_code, COUNT(*) as count 
                FROM stock_kline_cache 
                GROUP BY game_code
            ''')
            return {row[0]: row[1] for row in cursor.fetchall()}


# 全局客户端实例
longbridge_client = LongbridgeClient()


def get_real_stock_price(game_code: str) -> Optional[Tuple[float, float]]:
    """获取游戏股票真实价格的便捷函数"""
    return longbridge_client.get_game_stock_price(game_code)


def sync_all_prices() -> Dict[str, Tuple[float, float]]:
    """同步所有股票价格的便捷函数"""
    return longbridge_client.sync_all_game_stocks()


def fetch_all_klines(days: int = 365) -> Dict[str, int]:
    """获取所有股票K线数据并存入数据库的便捷函数"""
    return longbridge_client.fetch_and_store_all_klines(days)


def init_stock_database():
    """初始化股票数据库，从 Longbridge 获取所有历史K线数据"""
    print("[Longbridge] Initializing stock database with historical K-line data...")
    
    # 检查现有数据
    counts = longbridge_client.get_all_kline_counts()
    total_existing = sum(counts.values())
    
    if total_existing < len(STOCK_MAPPING) * 30:  # 如果数据量不足
        print(f"[Longbridge] Found {total_existing} existing K-lines, fetching more data...")
        fetch_all_klines(365)
    else:
        print(f"[Longbridge] Found {total_existing} existing K-lines, database is ready.")
    
    return counts
