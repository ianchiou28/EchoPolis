"""
事件池系统 - EchoPolis
从真实世界信息系统(Wide-Research)获取事件，结合用户画像进行智能筛选
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
import json
import requests
import os


# Wide-Research API配置
# 优先使用环境变量，否则使用公网地址（本地开发也能用）
# 服务器部署时可以设置 WIDE_RESEARCH_API_URL=http://127.0.0.1:5000 使用内网
WIDE_RESEARCH_API_BASE = os.getenv("WIDE_RESEARCH_API_URL", "http://finai.org.cn")
WIDE_RESEARCH_PUBLIC_URL = "http://finai.org.cn"


class RealEventCategory(Enum):
    """真实事件类别"""
    MARKET = "市场行情"
    POLICY = "政策法规"
    INDUSTRY = "行业动态"
    ECONOMY = "宏观经济"
    TECHNOLOGY = "科技创新"
    SOCIAL = "社会民生"
    GLOBAL = "国际形势"


class EventSentiment(Enum):
    """事件情绪倾向"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class RealWorldEvent:
    """真实世界事件"""
    id: str
    title: str
    summary: str
    category: RealEventCategory
    sentiment: EventSentiment
    sentiment_score: float  # -1.0 到 1.0
    source: str
    source_url: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    relevance_keywords: List[str] = field(default_factory=list)
    impact_sectors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "category": self.category.value,
            "sentiment": self.sentiment.value,
            "sentiment_score": self.sentiment_score,
            "source": self.source,
            "source_url": self.source_url,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
            "relevance_keywords": self.relevance_keywords,
            "impact_sectors": self.impact_sectors
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "RealWorldEvent":
        return cls(
            id=data["id"],
            title=data["title"],
            summary=data["summary"],
            category=RealEventCategory(data["category"]),
            sentiment=EventSentiment(data["sentiment"]),
            sentiment_score=data["sentiment_score"],
            source=data["source"],
            source_url=data.get("source_url"),
            published_at=datetime.fromisoformat(data["published_at"]) if data.get("published_at") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            tags=data.get("tags", []),
            relevance_keywords=data.get("relevance_keywords", []),
            impact_sectors=data.get("impact_sectors", [])
        )


@dataclass 
class GameEventFromPool:
    """从事件池生成的游戏事件"""
    id: str
    real_event_id: str  # 关联的真实事件ID
    title: str
    description: str
    category: RealEventCategory
    options: List[Dict]  # 游戏选项
    relevance_score: float  # 与用户的相关度 0-1
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "real_event_id": self.real_event_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "options": self.options,
            "relevance_score": self.relevance_score,
            "created_at": self.created_at.isoformat()
        }


class EventPoolManager:
    """事件池管理器"""
    
    def __init__(self, database=None, ai_engine=None):
        self.db = database
        self.ai_engine = ai_engine
        self.event_pool: List[RealWorldEvent] = []
        self.user_event_cache: Dict[str, List[GameEventFromPool]] = {}
        self._last_fetch_time: Optional[datetime] = None
        self._fetch_cache_minutes = 30  # 缓存30分钟
    
    def set_database(self, database):
        """设置数据库"""
        self.db = database
    
    def set_ai_engine(self, ai_engine):
        """设置AI引擎"""
        self.ai_engine = ai_engine
    
    def fetch_from_wide_research(self, force: bool = False) -> int:
        """从Wide-Research API获取真实事件"""
        # 检查缓存
        if not force and self._last_fetch_time:
            from datetime import timedelta
            if datetime.now() - self._last_fetch_time < timedelta(minutes=self._fetch_cache_minutes):
                print(f"[EventPool] 使用缓存数据，上次更新: {self._last_fetch_time}")
                return 0
        
        added_count = 0
        
        # 尝试不同的API端点获取事件
        try:
            # 1. 从结构化报告获取事件
            added_count += self._fetch_from_structured_report()
            
            # 2. 从每日摘要获取事件  
            added_count += self._fetch_from_daily_summary()
            
            # 3. 从实时快讯获取
            added_count += self._fetch_from_realtime()
            
            self._last_fetch_time = datetime.now()
            print(f"[EventPool] 从Wide-Research获取了 {added_count} 个事件")
            
        except Exception as e:
            print(f"[EventPool] 获取Wide-Research数据失败: {e}")
        
        return added_count
    
    def _fetch_from_structured_report(self) -> int:
        """从结构化报告API获取事件"""
        added = 0
        try:
            # 先尝试内网地址
            url = f"{WIDE_RESEARCH_API_BASE}/api/report/structured"
            print(f"[EventPool] 尝试获取: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                # 尝试公网地址
                url = f"{WIDE_RESEARCH_PUBLIC_URL}/api/report/structured"
                print(f"[EventPool] 尝试备用地址: {url}")
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[EventPool] API返回keys: {list(data.keys())}")
                
                # 优先从 news_list 获取事件（这是主要数据源）
                news_list = data.get("news_list", [])
                print(f"[EventPool] news_list 数量: {len(news_list)}")
                
                for item in news_list:
                    event = self._parse_news_item(item)
                    if event and self.add_event(event):
                        added += 1
                
                # 也尝试从 events 字段获取（如果有的话）
                events = data.get("events", {})
                if isinstance(events, dict):
                    # 高影响事件
                    for item in events.get("high_impact", []):
                        event = self._parse_wide_research_event(item, "high_impact")
                        if event and self.add_event(event):
                            added += 1
                    
                    # 热搜事件
                    for item in events.get("hot_search", []):
                        event = self._parse_wide_research_event(item, "hot_search")
                        if event and self.add_event(event):
                            added += 1
                    
                    # 其他事件
                    for item in events.get("other", []):
                        event = self._parse_wide_research_event(item, "other")
                        if event and self.add_event(event):
                            added += 1
                        
        except Exception as e:
            print(f"[EventPool] 结构化报告获取失败: {e}")
            import traceback
            traceback.print_exc()
        
        return added
    
    def _parse_news_item(self, item: Dict) -> Optional[RealWorldEvent]:
        """解析news_list中的新闻项"""
        import uuid
        
        title = item.get("title", "")
        summary = item.get("summary", "")
        
        if not title:
            return None
        
        # 解析情绪
        sentiment_data = item.get("sentiment", {})
        if isinstance(sentiment_data, dict):
            overall = sentiment_data.get("overall", 0)
        elif isinstance(sentiment_data, (int, float)):
            overall = sentiment_data
        else:
            overall = 0
        
        if overall > 0.2:
            sentiment = EventSentiment.POSITIVE
        elif overall < -0.2:
            sentiment = EventSentiment.NEGATIVE
        else:
            sentiment = EventSentiment.NEUTRAL
        
        # 从 event_type 判断类别
        event_type = item.get("event_type", "")
        category = self._infer_category(title, summary, event_type)
        
        return RealWorldEvent(
            id=f"WR_{item.get('ref_id', uuid.uuid4().hex[:8])}",
            title=title,
            summary=summary[:500] if summary else title,
            category=category,
            sentiment=sentiment,
            sentiment_score=float(overall) if isinstance(overall, (int, float)) else 0,
            source=item.get("source", "Wide-Research"),
            source_url=item.get("url", ""),
            published_at=datetime.now(),
            tags=self._extract_tags(title, summary),
            relevance_keywords=self._extract_keywords(title),
            impact_sectors=self._infer_sectors(title, summary)
        )
    
    def _fetch_from_daily_summary(self) -> int:
        """从每日摘要API获取事件"""
        added = 0
        try:
            url = f"{WIDE_RESEARCH_API_BASE}/api/daily_summary"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                url = f"{WIDE_RESEARCH_PUBLIC_URL}/api/daily_summary"
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 解析最新的摘要内容
                content = data.get("content", "")
                if content:
                    # 简单解析摘要中的事件
                    events = self._parse_summary_content(content)
                    for event in events:
                        if self.add_event(event):
                            added += 1
                            
        except Exception as e:
            print(f"[EventPool] 每日摘要获取失败: {e}")
        
        return added
    
    def _fetch_from_realtime(self) -> int:
        """从实时快讯API获取事件"""
        added = 0
        try:
            url = f"{WIDE_RESEARCH_API_BASE}/api/realtime"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                url = f"{WIDE_RESEARCH_PUBLIC_URL}/api/realtime"
                response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", [])
                
                for item in items[:20]:  # 只取最新20条
                    event = self._parse_realtime_item(item)
                    if event and self.add_event(event):
                        added += 1
                        
        except Exception as e:
            print(f"[EventPool] 实时快讯获取失败: {e}")
        
        return added
    
    def _parse_wide_research_event(self, item: Dict, event_type: str) -> Optional[RealWorldEvent]:
        """解析Wide-Research事件数据"""
        import uuid
        
        title = item.get("title", "")
        summary = item.get("summary", item.get("content", ""))
        
        if not title:
            return None
        
        # 判断情绪
        sentiment_str = item.get("sentiment", {})
        if isinstance(sentiment_str, dict):
            overall = sentiment_str.get("overall", 0)
        else:
            overall = 0
        
        if overall > 0.2:
            sentiment = EventSentiment.POSITIVE
        elif overall < -0.2:
            sentiment = EventSentiment.NEGATIVE
        else:
            sentiment = EventSentiment.NEUTRAL
        
        # 判断类别
        category = self._infer_category(title, summary, event_type)
        
        return RealWorldEvent(
            id=f"WR_{uuid.uuid4().hex[:8]}",
            title=title,
            summary=summary[:500] if summary else title,
            category=category,
            sentiment=sentiment,
            sentiment_score=overall if isinstance(overall, (int, float)) else 0,
            source=item.get("source", "Wide-Research"),
            source_url=item.get("url", ""),
            published_at=datetime.now(),
            tags=self._extract_tags(title, summary),
            relevance_keywords=self._extract_keywords(title),
            impact_sectors=self._infer_sectors(title, summary)
        )
    
    def _parse_realtime_item(self, item: Dict) -> Optional[RealWorldEvent]:
        """解析实时快讯"""
        import uuid
        
        title = item.get("title", item.get("content", ""))
        if not title or len(title) < 10:
            return None
        
        # 实时新闻默认为中性
        return RealWorldEvent(
            id=f"RT_{uuid.uuid4().hex[:8]}",
            title=title[:100],
            summary=title,
            category=self._infer_category(title, "", "realtime"),
            sentiment=EventSentiment.NEUTRAL,
            sentiment_score=0,
            source=item.get("source", "实时快讯"),
            published_at=datetime.now(),
            tags=self._extract_tags(title, ""),
            relevance_keywords=self._extract_keywords(title),
            impact_sectors=[]
        )
    
    def _parse_summary_content(self, content: str) -> List[RealWorldEvent]:
        """解析摘要内容中的事件"""
        import uuid
        events = []
        
        # 简单按行分割，寻找事件
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if len(line) > 20 and ("：" in line or ":" in line or line.startswith("-")):
                events.append(RealWorldEvent(
                    id=f"SUM_{uuid.uuid4().hex[:8]}",
                    title=line[:80],
                    summary=line,
                    category=self._infer_category(line, "", "summary"),
                    sentiment=EventSentiment.NEUTRAL,
                    sentiment_score=0,
                    source="每日摘要",
                    published_at=datetime.now(),
                    tags=self._extract_tags(line, ""),
                    relevance_keywords=self._extract_keywords(line),
                    impact_sectors=[]
                ))
        
        return events[:10]  # 最多返回10条
    
    def _infer_category(self, title: str, summary: str, event_type: str) -> RealEventCategory:
        """推断事件类别"""
        text = (title + " " + summary).lower()
        
        if any(kw in text for kw in ["股市", "股票", "涨", "跌", "指数", "a股", "美股", "港股", "stock"]):
            return RealEventCategory.MARKET
        elif any(kw in text for kw in ["政策", "央行", "监管", "法规", "政府", "国务院", "fed", "利率"]):
            return RealEventCategory.POLICY
        elif any(kw in text for kw in ["ai", "科技", "芯片", "技术", "openai", "人工智能", "创新"]):
            return RealEventCategory.TECHNOLOGY
        elif any(kw in text for kw in ["gdp", "通胀", "经济", "增长", "消费", "零售", "pce", "cpi"]):
            return RealEventCategory.ECONOMY
        elif any(kw in text for kw in ["汽车", "房地产", "电商", "医药", "能源", "行业"]):
            return RealEventCategory.INDUSTRY
        elif any(kw in text for kw in ["美国", "欧洲", "全球", "国际", "俄", "乌", "中东"]):
            return RealEventCategory.GLOBAL
        else:
            return RealEventCategory.SOCIAL
    
    def _extract_tags(self, title: str, summary: str) -> List[str]:
        """提取标签"""
        tags = []
        text = title + " " + summary
        
        keywords = {
            "股票": ["股票", "股市", "A股", "美股", "港股"],
            "科技": ["AI", "科技", "芯片", "技术"],
            "房地产": ["房地产", "楼市", "房价"],
            "新能源": ["新能源", "电动车", "光伏"],
            "消费": ["消费", "零售", "电商"],
            "政策": ["政策", "央行", "监管"],
            "金融": ["银行", "保险", "基金"],
        }
        
        for tag, kws in keywords.items():
            if any(kw in text for kw in kws):
                tags.append(tag)
        
        return tags[:5]
    
    def _extract_keywords(self, title: str) -> List[str]:
        """提取关键词"""
        # 简单分词
        import re
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', title)
        return [w for w in words if len(w) >= 2][:10]
    
    def _infer_sectors(self, title: str, summary: str) -> List[str]:
        """推断影响行业"""
        sectors = []
        text = title + " " + summary
        
        sector_keywords = {
            "科技": ["科技", "AI", "芯片", "软件"],
            "金融": ["银行", "保险", "券商", "金融"],
            "消费": ["消费", "零售", "电商"],
            "新能源": ["新能源", "电动车", "锂电"],
            "房地产": ["房地产", "地产", "楼市"],
            "医药": ["医药", "医疗", "生物"],
        }
        
        for sector, kws in sector_keywords.items():
            if any(kw in text for kw in kws):
                sectors.append(sector)
        
        return sectors
    
    def add_event(self, event: RealWorldEvent) -> bool:
        """添加事件到池中"""
        # 检查重复
        for e in self.event_pool:
            if e.id == event.id:
                return False
        self.event_pool.append(event)
        
        # 保存到数据库
        if self.db:
            self.db.save_pool_event(event.to_dict())
        return True
    
    def add_events_batch(self, events: List[RealWorldEvent]) -> int:
        """批量添加事件"""
        added = 0
        for event in events:
            if self.add_event(event):
                added += 1
        return added
    
    def get_pool_size(self) -> int:
        """获取事件池大小"""
        return len(self.event_pool)
    
    def get_events_by_category(self, category: RealEventCategory) -> List[RealWorldEvent]:
        """按类别获取事件"""
        return [e for e in self.event_pool if e.category == category]
    
    def get_recent_events(self, hours: int = 24) -> List[RealWorldEvent]:
        """获取最近N小时的事件"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        return [e for e in self.event_pool if e.created_at >= cutoff]
    
    def clear_old_events(self, days: int = 7) -> int:
        """清理超过N天的旧事件"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        old_count = len(self.event_pool)
        self.event_pool = [e for e in self.event_pool if e.created_at >= cutoff]
        return old_count - len(self.event_pool)
    
    def filter_events_for_user(self, user_profile: Dict, limit: int = 5) -> List[RealWorldEvent]:
        """根据用户画像筛选相关事件（规则匹配）"""
        user_tags = user_profile.get("tags", [])
        user_mbti = user_profile.get("mbti", "")
        risk_preference = user_profile.get("risk_preference", "moderate")
        
        scored_events = []
        for event in self.event_pool:
            score = self._calculate_relevance(event, user_tags, user_mbti, risk_preference)
            if score > 0.3:  # 相关度阈值
                scored_events.append((event, score))
        
        # 按相关度排序
        scored_events.sort(key=lambda x: x[1], reverse=True)
        return [e[0] for e in scored_events[:limit]]
    
    def _calculate_relevance(self, event: RealWorldEvent, 
                            user_tags: List[str], mbti: str, 
                            risk_pref: str) -> float:
        """计算事件与用户的相关度"""
        score = 0.0
        
        # 标签匹配
        tag_matches = len(set(event.tags) & set(user_tags))
        score += tag_matches * 0.15
        
        # 关键词匹配
        for tag in user_tags:
            if tag.lower() in [k.lower() for k in event.relevance_keywords]:
                score += 0.1
        
        # MBTI倾向匹配
        if mbti:
            if mbti[0] == 'E' and event.category == RealEventCategory.SOCIAL:
                score += 0.1
            if mbti[1] == 'N' and event.category == RealEventCategory.TECHNOLOGY:
                score += 0.1
            if mbti[2] == 'T' and event.category == RealEventCategory.MARKET:
                score += 0.1
            if mbti[3] == 'J' and event.category == RealEventCategory.POLICY:
                score += 0.1
        
        # 风险偏好匹配
        if risk_pref == "aggressive" and event.sentiment == EventSentiment.POSITIVE:
            score += 0.1
        elif risk_pref == "conservative" and event.sentiment == EventSentiment.NEGATIVE:
            score += 0.1
        
        return min(score, 1.0)
    
    def ai_filter_events(self, user_profile: Dict, limit: int = 3) -> List[GameEventFromPool]:
        """使用AI智能筛选并转化为游戏事件"""
        if not self.ai_engine:
            # 回退到规则筛选
            events = self.filter_events_for_user(user_profile, limit)
            return [self._convert_to_game_event(e, 0.5) for e in events]
        
        # 先用规则预筛选
        candidates = self.filter_events_for_user(user_profile, limit * 3)
        if not candidates:
            return []
        
        # 构建AI筛选prompt
        prompt = self._build_filter_prompt(user_profile, candidates)
        
        try:
            response = self.ai_engine._call_api(prompt)
            selected_ids = self._parse_filter_response(response)
            
            result = []
            for event in candidates:
                if event.id in selected_ids:
                    game_event = self._generate_game_event_with_ai(event, user_profile)
                    if game_event:
                        result.append(game_event)
                    if len(result) >= limit:
                        break
            return result
        except Exception as e:
            print(f"[WARN] AI filter failed: {e}, using rule-based")
            events = candidates[:limit]
            return [self._convert_to_game_event(e, 0.5) for e in events]
    
    def _build_filter_prompt(self, user_profile: Dict, events: List[RealWorldEvent]) -> str:
        """构建AI筛选提示词"""
        events_text = "\n".join([
            f"- ID: {e.id}, 标题: {e.title}, 类别: {e.category.value}"
            for e in events
        ])
        
        return f"""你是一个金融事件筛选助手。请根据用户画像，从以下事件中选择最相关的3个。

用户画像:
- MBTI: {user_profile.get('mbti', '未知')}
- 标签: {', '.join(user_profile.get('tags', []))}
- 风险偏好: {user_profile.get('risk_preference', 'moderate')}
- 关注领域: {', '.join(user_profile.get('interests', []))}

候选事件:
{events_text}

请只返回选中事件的ID，用逗号分隔，例如: event_001,event_002,event_003"""
    
    def _parse_filter_response(self, response: str) -> List[str]:
        """解析AI筛选响应"""
        ids = []
        for part in response.split(','):
            part = part.strip()
            if part.startswith('event_') or part.startswith('EVT_'):
                ids.append(part)
        return ids
    
    def _convert_to_game_event(self, event: RealWorldEvent, relevance: float) -> GameEventFromPool:
        """将真实事件转换为游戏事件"""
        import uuid
        options = self._generate_default_options(event)
        return GameEventFromPool(
            id=f"GAME_{uuid.uuid4().hex[:8]}",
            real_event_id=event.id,
            title=event.title,
            description=event.summary,
            category=event.category,
            options=options,
            relevance_score=relevance
        )
    
    def _generate_default_options(self, event: RealWorldEvent) -> List[Dict]:
        """生成默认游戏选项"""
        if event.category == RealEventCategory.MARKET:
            return [
                {"text": "加大投资", "impact": {"asset": 0.05, "risk": 0.1}},
                {"text": "保持观望", "impact": {}},
                {"text": "减少仓位", "impact": {"asset": -0.02, "risk": -0.05}}
            ]
        elif event.category == RealEventCategory.POLICY:
            return [
                {"text": "积极响应调整策略", "impact": {"asset": 0.03}},
                {"text": "等待更多信息", "impact": {}},
                {"text": "维持原有策略", "impact": {}}
            ]
        else:
            return [
                {"text": "关注并行动", "impact": {"happiness": 5}},
                {"text": "了解但暂不行动", "impact": {}},
                {"text": "忽略此事件", "impact": {"happiness": -2}}
            ]
    
    def _generate_game_event_with_ai(self, event: RealWorldEvent, 
                                     user_profile: Dict) -> Optional[GameEventFromPool]:
        """使用AI生成个性化游戏事件"""
        if not self.ai_engine:
            return self._convert_to_game_event(event, 0.7)
        
        prompt = f"""将以下真实事件转化为金融模拟游戏中的互动事件。

真实事件:
标题: {event.title}
摘要: {event.summary}
类别: {event.category.value}

用户信息:
MBTI: {user_profile.get('mbti', '')}
标签: {', '.join(user_profile.get('tags', []))}

请生成3个游戏选项，每个选项包含:
1. 选项文本（简洁有力，10字以内）
2. 影响类型和数值（asset/cash/happiness等）

返回JSON格式:
{{"options": [{{"text": "选项1", "impact": {{"asset": 0.05}}}}, ...]}}"""
        
        try:
            response = self.ai_engine._call_api(prompt)
            # 解析JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                options = data.get("options", [])
            else:
                options = self._generate_default_options(event)
            
            import uuid
            return GameEventFromPool(
                id=f"GAME_{uuid.uuid4().hex[:8]}",
                real_event_id=event.id,
                title=event.title,
                description=event.summary,
                category=event.category,
                options=options,
                relevance_score=0.8
            )
        except Exception as e:
            print(f"[WARN] AI game event generation failed: {e}")
            return self._convert_to_game_event(event, 0.6)


def create_sample_events() -> List[RealWorldEvent]:
    """创建示例事件（基于2025年12月6日真实新闻，当Wide-Research不可用时使用）"""
    import uuid
    
    # 使用最新的真实事件数据
    sample_events = [
        RealWorldEvent(
            id=f"EVT_{uuid.uuid4().hex[:8]}",
            title="Netflix以720亿美元收购华纳兄弟资产",
            summary="Netflix宣布以720亿美元收购华纳兄弟探索公司的影视和流媒体资产，这是流媒体行业史上最大规模的并购交易。",
            category=RealEventCategory.INDUSTRY,
            sentiment=EventSentiment.POSITIVE,
            sentiment_score=0.7,
            source="CNBC",
            tags=["并购", "流媒体", "科技"],
            relevance_keywords=["Netflix", "华纳", "收购", "流媒体"],
            impact_sectors=["科技", "传媒", "娱乐"]
        ),
        RealWorldEvent(
            id=f"EVT_{uuid.uuid4().hex[:8]}",
            title="美国核心PCE通胀率降至2.8%低于预期",
            summary="美联储关注的核心PCE通胀指标9月份降至2.8%，低于市场预期，增强了市场对美联储降息的预期。",
            category=RealEventCategory.ECONOMY,
            sentiment=EventSentiment.POSITIVE,
            sentiment_score=0.6,
            source="CNBC",
            tags=["通胀", "美联储", "PCE"],
            relevance_keywords=["PCE", "通胀", "美联储", "降息"],
            impact_sectors=["金融", "股市"]
        ),
        RealWorldEvent(
            id=f"EVT_{uuid.uuid4().hex[:8]}",
            title="SpaceX星舰第六次试飞取得重大突破",
            summary="SpaceX星舰完成第六次试飞，成功实现助推器回收和再入大气层，标志着可重复使用火箭技术的重大进步。",
            category=RealEventCategory.TECHNOLOGY,
            sentiment=EventSentiment.POSITIVE,
            sentiment_score=0.8,
            source="科技资讯",
            tags=["SpaceX", "航天", "科技"],
            relevance_keywords=["SpaceX", "星舰", "航天", "马斯克"],
            impact_sectors=["航天", "科技"]
        ),
        RealWorldEvent(
            id=f"EVT_{uuid.uuid4().hex[:8]}",
            title="Meta推出新一代AI助手功能",
            summary="Meta宣布其AI助手将获得重大升级，整合更多实时信息和个性化功能，与OpenAI、Google展开激烈竞争。",
            category=RealEventCategory.TECHNOLOGY,
            sentiment=EventSentiment.POSITIVE,
            sentiment_score=0.65,
            source="科技新闻",
            tags=["AI", "Meta", "科技"],
            relevance_keywords=["Meta", "AI", "人工智能"],
            impact_sectors=["科技", "互联网"]
        ),
        RealWorldEvent(
            id=f"EVT_{uuid.uuid4().hex[:8]}",
            title="OpenAI推出12天产品发布计划",
            summary="OpenAI宣布将在12月进行连续12天的产品发布，预计包括GPT-5等重磅产品，引发AI行业高度关注。",
            category=RealEventCategory.TECHNOLOGY,
            sentiment=EventSentiment.POSITIVE,
            sentiment_score=0.75,
            source="科技媒体",
            tags=["OpenAI", "AI", "GPT"],
            relevance_keywords=["OpenAI", "GPT", "AI", "ChatGPT"],
            impact_sectors=["科技", "软件"]
        ),
        RealWorldEvent(
            id=f"EVT_{uuid.uuid4().hex[:8]}",
            title="中国市场震荡，美股表现相对强势",
            summary="全球市场分化明显，A股市场震荡调整，而美股三大指数保持强势，投资者关注全球配置平衡。",
            category=RealEventCategory.MARKET,
            sentiment=EventSentiment.NEUTRAL,
            sentiment_score=0.1,
            source="市场分析",
            tags=["股市", "A股", "美股"],
            relevance_keywords=["A股", "美股", "市场", "投资"],
            impact_sectors=["股市", "金融"]
        ),
        RealWorldEvent(
            id=f"EVT_{uuid.uuid4().hex[:8]}",
            title="ADP就业数据低于预期",
            summary="美国ADP私人部门就业数据低于市场预期，显示劳动力市场有所降温，支持美联储放缓加息步伐的观点。",
            category=RealEventCategory.ECONOMY,
            sentiment=EventSentiment.NEUTRAL,
            sentiment_score=-0.1,
            source="经济数据",
            tags=["就业", "ADP", "美联储"],
            relevance_keywords=["ADP", "就业", "美联储"],
            impact_sectors=["金融", "服务业"]
        ),
        RealWorldEvent(
            id=f"EVT_{uuid.uuid4().hex[:8]}",
            title="Wells Fargo上调多家科技股目标价",
            summary="富国银行分析师上调包括英伟达、微软等科技巨头的目标价，看好AI驱动的科技股长期前景。",
            category=RealEventCategory.MARKET,
            sentiment=EventSentiment.POSITIVE,
            sentiment_score=0.5,
            source="投行研报",
            tags=["科技股", "投行", "目标价"],
            relevance_keywords=["科技股", "英伟达", "目标价"],
            impact_sectors=["科技", "投资"]
        )
    ]
    return sample_events


def fetch_latest_events() -> int:
    """从Wide-Research获取最新事件"""
    return event_pool_manager.fetch_from_wide_research()


def init_event_pool_with_samples():
    """初始化事件池 - 优先尝试从Wide-Research获取，失败则使用备用数据"""
    # 先尝试从Wide-Research获取真实数据
    added = event_pool_manager.fetch_from_wide_research()
    
    if added == 0:
        # 如果获取失败，使用备用的示例事件
        print("[EventPool] Wide-Research不可用，使用备用示例事件")
        samples = create_sample_events()
        added = event_pool_manager.add_events_batch(samples)
    
    print(f"[EventPool] 初始化完成，共 {added} 个事件")
    return added


# 全局实例
event_pool_manager = EventPoolManager()
