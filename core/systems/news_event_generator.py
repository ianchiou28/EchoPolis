"""
新闻事件生成器 - 基于真实新闻生成游戏事件
从 finai.org.cn/information 爬取金融新闻，使用 AI 生成个性化游戏事件
支持数据库持久化存储事件池
"""
import re
import json
import time
import requests
import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Selenium 导入
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("[NewsGenerator] Selenium 未安装，将使用备用数据")

# 导入数据库和AI模块
try:
    from core.database.news_event_db import news_event_db
except ImportError:
    news_event_db = None

try:
    from core.ai.deepseek_engine import deepseek_engine
except ImportError:
    deepseek_engine = None

@dataclass
class NewsItem:
    """新闻条目"""
    title: str
    title_cn: str  # 中文标题
    summary: str
    source: str
    category: str  # macro/stock/crypto/policy/global/merger
    sentiment: str  # positive/negative/neutral
    timestamp: float
    news_id: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class GeneratedEvent:
    """生成的游戏事件"""
    id: str
    title: str
    description: str
    category: str
    tags: List[str]
    options: List[Dict]
    source_news: str
    ai_analysis: str
    match_score: float = 0.0
    news_id: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)

class NewsEventGenerator:
    """新闻事件生成器 - 从 finai.org.cn 获取实时金融资讯，AI生成事件存入数据库"""
    
    def __init__(self):
        self.source_url = "http://www.finai.org.cn/information/"
        self.news_cache: List[NewsItem] = []
        self.generated_events: List[GeneratedEvent] = []
        self.last_fetch = 0
        self.cache_duration = 1800  # 30分钟缓存
        self.market_sentiment = "neutral"
        self.hot_topics: List[str] = []
        self.db = news_event_db
        self.ai = deepseek_engine
        
    async def fetch_and_generate_events(self, user_tags: List[str] = None, force_refresh: bool = False) -> List[Dict]:
        """
        主入口：获取新闻 -> AI生成事件 -> 存入数据库 -> 返回事件
        """
        # 1. 先检查数据库是否有活跃事件
        if self.db and not force_refresh:
            db_events = self.db.get_active_events(limit=20)
            if len(db_events) >= 5:
                print(f"[NewsGenerator] 从数据库返回 {len(db_events)} 条事件")
                return self._filter_by_tags(db_events, user_tags)
        
        # 2. 爬取新闻
        news_items = self.fetch_news()
        
        # 3. 保存新闻到数据库
        if self.db and news_items:
            self.db.save_news_batch([n.to_dict() for n in news_items])
            # 保存市场状态
            self.db.save_market_status({
                'sentiment': self.market_sentiment,
                'hot_topics': self.hot_topics
            })
        
        # 4. AI生成事件
        events = await self._ai_generate_events(news_items, user_tags)
        
        # 5. 保存事件到数据库
        if self.db and events:
            event_dicts = [e.to_dict() if isinstance(e, GeneratedEvent) else e for e in events]
            self.db.save_events_batch(event_dicts)
        
        # 6. 清理过期数据
        if self.db:
            self.db.cleanup_expired()
        
        return [e.to_dict() if isinstance(e, GeneratedEvent) else e for e in events]
    
    async def _ai_generate_events(self, news_items: List[NewsItem], user_tags: List[str] = None) -> List[GeneratedEvent]:
        """使用AI基于新闻生成事件"""
        events = []
        
        if not news_items:
            return events
        
        # 尝试使用AI生成
        if self.ai:
            try:
                ai_events = await self._generate_with_ai(news_items, user_tags)
                if ai_events:
                    events.extend(ai_events)
                    print(f"[NewsGenerator] AI生成了 {len(ai_events)} 条事件")
                    return events
            except Exception as e:
                print(f"[NewsGenerator] AI生成失败，使用模板: {e}")
        
        # 回退到模板生成
        for i, news in enumerate(news_items[:10]):
            event = self._news_to_event(news, i, user_tags)
            if event:
                events.append(event)
        
        return events
    
    async def _generate_with_ai(self, news_items: List[NewsItem], user_tags: List[str] = None) -> List[GeneratedEvent]:
        """调用DeepSeek AI生成事件"""
        if not self.ai:
            return []
        
        # 构建新闻摘要
        news_summary = "\n".join([
            f"- [{n.category}] {n.title_cn} (情绪:{n.sentiment}, 来源:{n.source})"
            for n in news_items[:8]
        ])
        
        user_context = f"用户关注标签: {', '.join(user_tags)}" if user_tags else "用户暂无特定标签"
        
        prompt = f"""你是一个金融游戏事件设计师。基于以下真实金融新闻，为游戏玩家生成5-8个有趣且有教育意义的投资决策事件。

【今日市场情绪】{self.market_sentiment}
【热门话题】{', '.join(self.hot_topics[:5])}
【{user_context}】

【今日新闻】
{news_summary}

请为每条相关新闻生成一个游戏事件，格式如下（JSON数组）：
[
  {{
    "title": "事件标题（带emoji，如：📈 科技股暴涨）",
    "description": "基于新闻的详细描述，说明对玩家的影响和选择背景",
    "category": "stock/crypto/policy/tech/merger/global/macro之一",
    "tags": ["标签1", "标签2"],
    "source_news": "对应的新闻标题",
    "ai_analysis": "AI对这条新闻的简短分析和投资建议",
    "options": [
      {{"text": "选项1描述", "tags": ["action_tag"], "effects": {{"cash": 数值变化, "happiness": 数值变化}}}},
      {{"text": "选项2描述", "tags": ["action_tag"], "effects": {{}}}},
      {{"text": "选项3描述", "tags": ["action_tag"], "effects": {{"cash": 数值变化}}}}
    ]
  }}
]

要求：
1. 每个事件有3个选择，体现不同投资风格（保守/稳健/激进）
2. effects中的cash用整数表示金额变化，happiness表示心情变化
3. 选项要有真实感和教育意义
4. 基于真实新闻但适当游戏化
5. 只返回JSON数组，不要其他内容"""

        try:
            response = await self.ai.generate_async(prompt, max_tokens=3000)
            
            # 解析JSON
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                events_data = json.loads(json_match.group())
                events = []
                for i, data in enumerate(events_data):
                    event = GeneratedEvent(
                        id=f"ai_news_{int(time.time())}_{i}",
                        title=data.get('title', ''),
                        description=data.get('description', ''),
                        category=data.get('category', 'macro'),
                        tags=data.get('tags', []),
                        options=data.get('options', []),
                        source_news=data.get('source_news', ''),
                        ai_analysis=data.get('ai_analysis', ''),
                        match_score=0.8,  # AI生成的事件给予较高匹配度
                        news_id=f"news_{int(time.time())}_{i}"
                    )
                    events.append(event)
                return events
        except Exception as e:
            print(f"[NewsGenerator] AI解析失败: {e}")
        
        return []
    
    def _filter_by_tags(self, events: List[Dict], user_tags: List[str] = None) -> List[Dict]:
        """根据用户标签筛选和排序事件"""
        if not user_tags:
            return events
        
        for event in events:
            event_tags = event.get('tags', [])
            match_count = len(set(user_tags) & set(event_tags))
            event['match_score'] = event.get('match_score', 0.5) + match_count * 0.1
        
        events.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        return events
    
    def _fetch_with_selenium(self) -> str:
        """使用 Selenium 爬取 SPA 页面"""
        if not SELENIUM_AVAILABLE:
            print("[NewsGenerator] Selenium 不可用")
            return ""
        
        driver = None
        try:
            print("[NewsGenerator] 启动 Chrome 浏览器...")
            
            # Chrome 选项
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # 自动下载和管理 ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print(f"[NewsGenerator] 访问 {self.source_url}")
            driver.get(self.source_url)
            
            # 等待页面加载（等待某个元素出现）
            print("[NewsGenerator] 等待页面加载...")
            WebDriverWait(driver, 15).until(
                lambda d: len(d.page_source) > 2000
            )
            
            # 额外等待 JavaScript 渲染
            time.sleep(3)
            
            content = driver.page_source
            print(f"[NewsGenerator] 获取到页面内容，长度: {len(content)}")
            
            return content
            
        except Exception as e:
            print(f"[NewsGenerator] Selenium 爬取失败: {e}")
            return ""
        finally:
            if driver:
                driver.quit()
        
    def fetch_news(self) -> List[NewsItem]:
        """从 finai.org.cn/information 爬取新闻"""
        current_time = time.time()
        
        # 检查缓存
        if self.news_cache and (current_time - self.last_fetch < self.cache_duration):
            print(f"[NewsGenerator] 使用缓存数据 ({len(self.news_cache)} 条)")
            return self.news_cache
        
        # 使用 Selenium 爬取 SPA 页面
        content = self._fetch_with_selenium()
        
        if content and len(content) > 2000:
            news_items = self._parse_finai_page(content)
            if news_items:
                self.news_cache = news_items
                self.last_fetch = current_time
                print(f"[NewsGenerator] 成功从 finai.org.cn 获取 {len(news_items)} 条新闻")
                return news_items
        
        print("[NewsGenerator] 爬取失败，使用备用数据")
        return self._get_fallback_news()
    
    def sync_fetch_and_generate(self, user_tags: List[str] = None, force_refresh: bool = False) -> List[Dict]:
        """同步版本的获取和生成方法 - 不使用AI，直接用模板生成"""
        # 1. 先检查数据库是否有活跃事件
        if self.db and not force_refresh:
            db_events = self.db.get_active_events(limit=20)
            if len(db_events) >= 5:
                print(f"[NewsGenerator] 从数据库返回 {len(db_events)} 条事件")
                return self._filter_by_tags(db_events, user_tags)
        
        # 2. 爬取新闻
        news_items = self.fetch_news()
        
        # 3. 保存新闻到数据库
        if self.db and news_items:
            self.db.save_news_batch([n.to_dict() for n in news_items])
            self.db.save_market_status({
                'sentiment': self.market_sentiment,
                'hot_topics': self.hot_topics
            })
        
        # 4. 使用模板生成事件（同步，不用AI）
        events = []
        for i, news in enumerate(news_items[:10]):
            event = self._news_to_event(news, i, user_tags)
            if event:
                events.append(event)
        
        # 5. 保存事件到数据库
        if self.db and events:
            event_dicts = [e.to_dict() if isinstance(e, GeneratedEvent) else e for e in events]
            self.db.save_events_batch(event_dicts)
        
        # 6. 清理过期数据
        if self.db:
            self.db.cleanup_expired()
        
        result = [e.to_dict() if isinstance(e, GeneratedEvent) else e for e in events]
        print(f"[NewsGenerator] 同步生成了 {len(result)} 条事件")
        return result
    
    def _parse_finai_page(self, content: str) -> List[NewsItem]:
        """解析 finai.org.cn/information 页面内容"""
        news_items = []
        
        # 清理 HTML 标签的辅助函数
        def clean_html(text):
            # 移除所有 HTML 标签
            text = re.sub(r'<[^>]+>', '', text)
            # 移除 data-v-xxx 等 Vue 属性残留
            text = re.sub(r'data-v-[a-f0-9]+', '', text)
            # 移除多余空白
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        
        # 1. 提取市场情绪
        sentiment_match = re.search(r'市场情绪[：:\s]*(积极|消极|中性)', content)
        if sentiment_match:
            self.market_sentiment = sentiment_match.group(1)
            print(f"[NewsGenerator] 市场情绪: {self.market_sentiment}")
        
        # 2. 提取热门话题 - 匹配 "话题×数字" 格式
        topic_matches = re.findall(r'([A-Za-z\u4e00-\u9fa5]{2,15})×(\d+)', content)
        if topic_matches:
            # 按出现次数排序
            sorted_topics = sorted(topic_matches, key=lambda x: int(x[1]), reverse=True)
            self.hot_topics = [t[0].strip() for t in sorted_topics[:10]]
            print(f"[NewsGenerator] 热门话题: {self.hot_topics}")
        
        # 3. 提取新闻项 - 多种模式匹配
        
        # 模式1: 匹配 "来源 类别 标题→" 格式
        pattern1 = r'(CNBC|Financial Times|Forbes|MarketWatch|雪球|Bloomberg|Reuters|WSJ)[^→]*?(财报|并购|政策|其他|宏观|科技)[^→]*?([A-Za-z][^→]{10,100}?)([\u4e00-\u9fa5][^→<]{10,80}?)(?:→|<)'
        
        for match in re.finditer(pattern1, content):
            source = match.group(1).strip()
            category = match.group(2).strip()
            title_en = clean_html(match.group(3))
            title_cn = clean_html(match.group(4))
            
            if len(title_cn) > 8 and len(title_cn) < 100:
                news_items.append(self._create_news_item(
                    title_en, title_cn, source, category, len(news_items)
                ))
        
        # 模式2: 直接匹配中文新闻标题（包含关键词）
        if len(news_items) < 5:
            # 查找可能的新闻标题区域
            cn_titles = re.findall(
                r'([\u4e00-\u9fa5]{2,8}(?:股|涨|跌|暴|创|破|突破|激增|下跌|上涨|收购|并购|发布|推出)[\u4e00-\u9fa5，、\d%]{5,50})',
                content
            )
            for idx, title in enumerate(cn_titles[:15]):
                title = clean_html(title)
                # 排除太短或已存在的
                if len(title) > 10 and not any(title in n.title_cn for n in news_items):
                    news_items.append(self._create_news_item(
                        title, title, "finai.org.cn", "宏观", len(news_items)
                    ))
        
        # 模式3: 匹配英文标题后跟中文翻译
        if len(news_items) < 5:
            pattern3 = r'([A-Z][a-zA-Z\s\',\.\$\d%]{15,80})\s*([\u4e00-\u9fa5][\u4e00-\u9fa5，、\d%]{10,60})'
            for match in re.finditer(pattern3, content):
                title_en = clean_html(match.group(1))
                title_cn = clean_html(match.group(2))
                
                if (len(title_cn) > 10 and len(title_cn) < 80 and 
                    not any(title_cn in n.title_cn for n in news_items)):
                    news_items.append(self._create_news_item(
                        title_en, title_cn, "finai.org.cn", "宏观", len(news_items)
                    ))
        
        # 去重并限制数量
        seen = set()
        unique_items = []
        for item in news_items:
            # 标准化标题用于去重
            key = item.title_cn[:20]
            if key not in seen:
                seen.add(key)
                unique_items.append(item)
        
        return unique_items[:15]
    
    def _create_news_item(self, title_en: str, title_cn: str, source: str, category: str, idx: int) -> NewsItem:
        """创建新闻条目"""
        news_category = self._map_category(category, title_cn)
        sentiment = self._analyze_sentiment(title_cn)
        news_id = f"news_{int(time.time()*1000)}_{idx}"
        
        return NewsItem(
            title=title_en[:100] if title_en else title_cn[:100],
            title_cn=title_cn[:100],
            summary=title_cn[:200],
            source=source,
            category=news_category,
            sentiment=sentiment,
            timestamp=time.time(),
            news_id=news_id
        )
    
    def _map_category(self, source_category: str, title: str) -> str:
        """映射新闻类别"""
        category_map = {
            '财报': 'stock',
            '并购': 'merger',
            '政策': 'policy',
            '宏观': 'macro',
            '科技': 'tech',
            '其他': 'global'
        }
        
        # 先用来源分类
        if source_category in category_map:
            return category_map[source_category]
        
        # 再根据内容判断
        return self._categorize_news(title)
    
    def _categorize_news(self, text: str) -> str:
        """分类新闻"""
        if any(k in text for k in ['美联储', '央行', '利率', '政策', '监管', 'Fed', 'Federal Reserve']):
            return 'policy'
        elif any(k in text for k in ['比特币', '加密', '数字货币', 'BTC', 'crypto', 'Bitcoin']):
            return 'crypto'
        elif any(k in text for k in ['美股', 'A股', '港股', '股市', '指数', '暴涨', '暴跌', 'S&P', 'Nasdaq']):
            return 'stock'
        elif any(k in text for k in ['收购', '并购', '合并', 'merger', 'acquisition']):
            return 'merger'
        elif any(k in text for k in ['AI', '人工智能', 'Nvidia', '英伟达', 'GPU', 'OpenAI']):
            return 'tech'
        elif any(k in text for k in ['全球', '国际', '贸易', '地缘', '欧洲', '亚洲']):
            return 'global'
        else:
            return 'macro'
    
    def _analyze_sentiment(self, text: str) -> str:
        """简单情感分析"""
        positive_words = ['上涨', '增长', '突破', '新高', '利好', '反弹', '回暖', '激增', '暴涨', '看涨', 
                         'surge', 'jump', 'soar', 'rise', 'gain', 'positive']
        negative_words = ['下跌', '暴跌', '下滑', '危机', '利空', '崩盘', '恐慌', '担忧', '下挫',
                         'fall', 'drop', 'crash', 'decline', 'negative', 'fear']
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text or w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text or w in text_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'
    
    def _get_fallback_news(self) -> List[NewsItem]:
        """获取备用新闻（基于热门话题生成）"""
        fallback = [
            NewsItem("AI芯片需求持续增长", "AI芯片需求持续增长，科技股受益", "英伟达等AI芯片股持续走强", "system", "tech", "positive", time.time(), "fallback_1"),
            NewsItem("美联储政策动向", "市场关注美联储下一步利率决策", "美联储政策动向影响全球市场", "system", "policy", "neutral", time.time(), "fallback_2"),
            NewsItem("科技巨头财报季", "科技巨头财报超预期，推动市场上涨", "科技股财报表现亮眼", "system", "stock", "positive", time.time(), "fallback_3"),
            NewsItem("中国市场表现", "A股市场震荡整理，等待方向", "中国市场观望情绪浓厚", "system", "macro", "neutral", time.time(), "fallback_4"),
            NewsItem("全球经济展望", "全球经济复苏势头延续", "主要经济体增长动能持续", "system", "global", "positive", time.time(), "fallback_5"),
        ]
        return fallback
    
    def generate_events_from_news(self, user_tags: List[str] = None) -> List[GeneratedEvent]:
        """基于新闻生成游戏事件"""
        news_items = self.fetch_news()
        events = []
        
        for i, news in enumerate(news_items):
            event = self._news_to_event(news, i, user_tags)
            if event:
                events.append(event)
        
        # 按匹配度排序
        events.sort(key=lambda x: x.match_score, reverse=True)
        return events[:10]  # 返回前10个事件
    
    def _news_to_event(self, news: NewsItem, index: int, user_tags: List[str] = None) -> Optional[GeneratedEvent]:
        """将新闻转换为游戏事件"""
        
        # 基于新闻类别生成事件
        event_templates = {
            'policy': {
                'title_prefix': '📜 政策风向',
                'options': [
                    {'text': '积极调整投资策略应对政策变化', 'tags': ['adaptive', 'risk_aware'], 'effects': {'happiness': 5}},
                    {'text': '保持观望，等待更明确的信号', 'tags': ['conservative', 'patient'], 'effects': {}},
                    {'text': '趁政策窗口期布局相关板块', 'tags': ['aggressive', 'opportunist'], 'effects': {'cash': -5000}},
                ]
            },
            'stock': {
                'title_prefix': '📈 股市快讯',
                'options': [
                    {'text': '跟随市场趋势，适当加仓', 'tags': ['trend_follower', 'aggressive'], 'effects': {'cash': -10000}},
                    {'text': '趁机获利了结，落袋为安', 'tags': ['profit_taker', 'conservative'], 'effects': {'cash': 5000}},
                    {'text': '按兵不动，坚持长期持有', 'tags': ['steady', 'long_term'], 'effects': {}},
                ]
            },
            'crypto': {
                'title_prefix': '₿ 加密动态',
                'options': [
                    {'text': '小额买入，感受市场脉搏', 'tags': ['crypto_curious', 'moderate'], 'effects': {'cash': -2000}},
                    {'text': '重仓押注，搏取高收益', 'tags': ['risk_taker', 'crypto_believer'], 'effects': {'cash': -20000}},
                    {'text': '敬而远之，专注传统投资', 'tags': ['conservative', 'traditional'], 'effects': {}},
                ]
            },
            'tech': {
                'title_prefix': '🤖 科技前沿',
                'options': [
                    {'text': '投资科技ETF，分享行业红利', 'tags': ['tech_investor', 'diversified'], 'effects': {'cash': -8000}},
                    {'text': '精选龙头个股，集中投资', 'tags': ['stock_picker', 'aggressive'], 'effects': {'cash': -15000}},
                    {'text': '保持关注，暂不介入', 'tags': ['cautious', 'observer'], 'effects': {}},
                ]
            },
            'merger': {
                'title_prefix': '🤝 并购重组',
                'options': [
                    {'text': '押注并购概念股', 'tags': ['event_driven', 'speculator'], 'effects': {'cash': -10000}},
                    {'text': '分析产业链机会', 'tags': ['analytical', 'value_investor'], 'effects': {'happiness': 3}},
                    {'text': '规避不确定性风险', 'tags': ['risk_averse', 'conservative'], 'effects': {}},
                ]
            },
            'global': {
                'title_prefix': '🌍 全球要闻',
                'options': [
                    {'text': '配置海外资产，分散风险', 'tags': ['diversified', 'global_investor'], 'effects': {'cash': -8000}},
                    {'text': '专注国内市场，深耕本土', 'tags': ['local_focused', 'conservative'], 'effects': {}},
                    {'text': '做好汇率对冲准备', 'tags': ['hedger', 'risk_aware'], 'effects': {'cash': -3000}},
                ]
            },
            'macro': {
                'title_prefix': '📊 宏观洞察',
                'options': [
                    {'text': '顺周期调整资产配置', 'tags': ['adaptive', 'macro_aware'], 'effects': {}},
                    {'text': '增加现金储备，保持灵活', 'tags': ['conservative', 'cash_holder'], 'effects': {'cash': 2000}},
                    {'text': '逆向布局，寻找错杀机会', 'tags': ['contrarian', 'value_hunter'], 'effects': {'cash': -5000}},
                ]
            }
        }
        
        template = event_templates.get(news.category, event_templates['macro'])
        
        # 计算与用户标签的匹配度
        match_score = 0.5  # 基础分
        if user_tags:
            all_option_tags = []
            for opt in template['options']:
                all_option_tags.extend(opt.get('tags', []))
            
            matched = len(set(user_tags) & set(all_option_tags))
            match_score = 0.5 + (matched * 0.15)
        
        # 根据情感调整
        if news.sentiment == 'positive':
            match_score += 0.1
        elif news.sentiment == 'negative':
            match_score += 0.05  # 负面新闻也有参考价值
        
        # 市场情绪加成
        if self.market_sentiment == '积极':
            match_score += 0.05
        
        # 热门话题加成
        for topic in self.hot_topics[:5]:
            if topic.lower() in news.title_cn.lower() or topic.lower() in news.title.lower():
                match_score += 0.08
                break
        
        # 构建描述
        description = f"【实时资讯】{news.title_cn}\n\n"
        description += f"来源: {news.source} | 市场情绪: {self.market_sentiment}\n\n"
        description += "这条来自真实市场的消息正在影响投资者决策。你会如何应对？"
        
        # AI分析
        sentiment_map = {'positive': '乐观', 'negative': '悲观', 'neutral': '中性'}
        ai_analysis = f"当前市场整体情绪{self.market_sentiment}，"
        ai_analysis += f"此新闻倾向{sentiment_map.get(news.sentiment, '中性')}。"
        if self.hot_topics:
            ai_analysis += f" 今日热点: {', '.join(self.hot_topics[:3])}。"
        
        event = GeneratedEvent(
            id=f"news_{int(time.time())}_{index}",
            title=f"{template['title_prefix']}: {news.title_cn[:25]}...",
            description=description,
            category=news.category,
            tags=self._get_event_tags(news),
            options=template['options'],
            source_news=news.title_cn,
            ai_analysis=ai_analysis,
            match_score=min(match_score, 1.0),
            news_id=news.news_id
        )
        
        return event
    
    def _get_event_tags(self, news: NewsItem) -> List[str]:
        """为事件生成标签"""
        tags = [news.category]
        text = news.title_cn + news.title
        
        # 基于内容添加标签
        if any(k in text for k in ['利率', '央行', 'Fed', 'Federal Reserve', '美联储']):
            tags.extend(['interest_rate', 'monetary_policy'])
        if any(k in text for k in ['股', 'stock', 'equity', 'S&P', 'Nasdaq']):
            tags.extend(['stock', 'equity'])
        if any(k in text for k in ['比特币', '加密', 'Bitcoin', 'crypto', 'BTC']):
            tags.extend(['crypto', 'digital_asset'])
        if any(k in text for k in ['黄金', 'gold', 'Gold']):
            tags.extend(['gold', 'safe_haven'])
        if any(k in text for k in ['AI', '人工智能', 'Nvidia', '英伟达', 'OpenAI']):
            tags.extend(['ai', 'tech_growth'])
        if any(k in text for k in ['房', 'real estate', 'property']):
            tags.extend(['real_estate', 'property'])
        if any(k in text for k in ['并购', '收购', 'merger', 'acquisition']):
            tags.extend(['merger', 'corporate_action'])
        if any(k in text for k in ['财报', 'earnings', 'revenue', '营收']):
            tags.extend(['earnings', 'fundamental'])
            
        return list(set(tags))[:6]
    
    def get_market_status(self) -> Dict:
        """获取当前市场状态摘要"""
        self.fetch_news()  # 确保数据是最新的
        return {
            'sentiment': self.market_sentiment,
            'hot_topics': self.hot_topics[:10],
            'news_count': len(self.news_cache),
            'last_update': datetime.fromtimestamp(self.last_fetch).strftime('%Y-%m-%d %H:%M:%S') if self.last_fetch else None
        }
    
    def get_events_as_dict(self, user_tags: List[str] = None) -> List[Dict]:
        """获取事件字典列表（用于API返回）- 同步版本"""
        events = self.generate_events_from_news(user_tags)
        return [
            {
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'category': e.category,
                'tags': e.tags,
                'options': e.options,
                'source_news': e.source_news,
                'ai_analysis': e.ai_analysis,
                'match_score': e.match_score,
                'is_real_news': True,
                'news_id': e.news_id
            }
            for e in events
        ]
    
    def get_db_events(self, user_tags: List[str] = None, limit: int = 20) -> List[Dict]:
        """从数据库获取事件"""
        if not self.db:
            return self.get_events_as_dict(user_tags)
        
        events = self.db.get_active_events(limit=limit)
        if not events:
            # 数据库为空，生成新事件
            return self.sync_fetch_and_generate(user_tags, force_refresh=True)
        
        return self._filter_by_tags(events, user_tags)
    
    def get_event_stats(self) -> Dict:
        """获取事件池统计"""
        if self.db:
            return self.db.get_event_stats()
        return {
            'active_news': len(self.news_cache),
            'active_events': len(self.generated_events),
            'total_news': len(self.news_cache),
            'total_events': len(self.generated_events)
        }

# 全局实例
news_event_generator = NewsEventGenerator()
