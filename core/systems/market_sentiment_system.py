"""
市场情绪分析系统 - Echopolis核心模块
爬取外部数据分析市场情绪，影响游戏内的事件和成功率
"""
import re
import requests
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

@dataclass
class MarketSentiment:
    """市场情绪数据"""
    overall_sentiment: str  # 积极/消极/中性
    global_score: float     # 全球市场分数
    china_score: float      # 中国市场分数
    us_score: float         # 美国市场分数
    outlook: str            # 市场展望 (震荡/上涨/下跌)
    hot_topics: list[str]   # 热门话题
    real_events: list[str]  # 真实事件
    timestamp: float        # 数据获取时间

class MarketSentimentSystem:
    """市场情绪分析系统"""
    
    def __init__(self):
        self.source_url = "http://www.finai.org.cn/"
        self.current_sentiment: Optional[MarketSentiment] = None
        self.last_update = 0
        self.cache_duration = 3600  # 缓存1小时
    
    def get_sentiment(self) -> MarketSentiment:
        """获取当前市场情绪，如果缓存过期则重新获取"""
        import time
        if self.current_sentiment and (time.time() - self.last_update < self.cache_duration):
            return self.current_sentiment
        
        try:
            return self.fetch_and_analyze()
        except Exception as e:
            print(f"[WARN] Failed to fetch market sentiment: {e}")
            # 返回默认中性数据
            return MarketSentiment(
                overall_sentiment="中性",
                global_score=0.0,
                china_score=0.0,
                us_score=0.0,
                outlook="震荡",
                hot_topics=[],
                real_events=[],
                timestamp=time.time()
            )

    def fetch_and_analyze(self) -> MarketSentiment:
        """爬取并分析数据"""
        import time
        
        # 模拟浏览器头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(self.source_url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            content = response.text
            
            # 解析数据
            sentiment_data = self._parse_content(content)
            self.current_sentiment = sentiment_data
            self.last_update = time.time()
            return sentiment_data
            
        except Exception as e:
            raise Exception(f"Error fetching data: {str(e)}")

    def _parse_content(self, content: str) -> MarketSentiment:
        """解析网页内容"""
        import time
        
        # 移除HTML标签以简化解析
        clean_content = re.sub(r'<[^>]+>', ' ', content)
        clean_content = re.sub(r'\s+', ' ', clean_content)
        
        # 1. 提取总体情绪
        # 寻找 "市场情绪 消极" 或类似结构
        overall_sentiment = "中性"
        if "市场情绪 积极" in clean_content:
            overall_sentiment = "积极"
        elif "市场情绪 消极" in clean_content:
            overall_sentiment = "消极"
        
        # 2. 提取具体分数
        # 格式: 全球市场 -0.12 消极
        global_score = 0.0
        china_score = 0.0
        us_score = 0.0
        
        # 更新正则以匹配清理后的文本
        global_match = re.search(r"全球市场\s*([+-]?\d+\.?\d*)", clean_content)
        if global_match:
            global_score = float(global_match.group(1))
            
        china_match = re.search(r"中国市场\s*([+-]?\d+\.?\d*)", clean_content)
        if china_match:
            china_score = float(china_match.group(1))
            
        us_match = re.search(r"美国市场\s*([+-]?\d+\.?\d*)", clean_content)
        if us_match:
            us_score = float(us_match.group(1))
            
        # 3. 提取展望
        # 格式: 全球→ 震荡
        outlook = "震荡"
        outlook_match = re.search(r"全球→\s*(\w+)", clean_content)
        if outlook_match:
            outlook = outlook_match.group(1)
            
        # 4. 提取热门话题
        # 简单提取一些关键词
        hot_topics = []
        # 尝试匹配 "热门话题 ... 市场展望" 之间的内容
        topic_pattern = re.search(r"热门话题(.*?)(?:市场展望|$)", clean_content)
        if topic_pattern:
            raw_topics = topic_pattern.group(1)
            # 简单的清理和分割
            topics = re.findall(r"[\u4e00-\u9fa5]+", raw_topics)
            # 过滤掉一些非话题词
            filtered_topics = [t for t in topics if len(t) > 1 and t not in ["美股", "铜", "白银", "伦敦金属交易所"]] 
            hot_topics = filtered_topics[:5]

        # 5. 提取关键事件
        real_events = []
        # 尝试匹配 "关键事件 ... 热门话题" 之间的内容
        events_pattern = re.search(r"关键事件\s*\d*\s*条?(.*?)(?:热门话题|市场展望|$)", clean_content)
        if events_pattern:
            raw_events = events_pattern.group(1).strip()
            if raw_events:
                # 简单的清理，移除多余的标签或来源标识
                cleaned_event = re.sub(r'Financial Times|Bloomberg|Reuters', '', raw_events)
                real_events.append(cleaned_event.strip())

        return MarketSentiment(
            overall_sentiment=overall_sentiment,
            global_score=global_score,
            china_score=china_score,
            us_score=us_score,
            outlook=outlook,
            hot_topics=hot_topics,
            real_events=real_events,
            timestamp=time.time()
        )

    def get_influence_modifier(self) -> float:
        """获取基于情绪的成功率修正值 (-0.2 到 +0.2)"""
        sentiment = self.get_sentiment()
        
        # 基础修正
        modifier = sentiment.global_score * 0.5  # 假设分数在 -1 到 1 之间
        
        # 限制范围
        return max(min(modifier, 0.2), -0.2)

# 全局实例
market_sentiment_system = MarketSentimentSystem()
