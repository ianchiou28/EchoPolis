"""
新闻事件数据库 - 存储从 finai.org.cn 爬取的新闻和生成的事件
"""
import sqlite3
import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os

class NewsEventDatabase:
    """新闻事件数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 默认使用项目根目录下的数据库
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, 'echopolis.db')
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 新闻表 - 存储爬取的原始新闻
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    news_id TEXT UNIQUE,
                    title TEXT NOT NULL,
                    title_cn TEXT,
                    summary TEXT,
                    source TEXT,
                    category TEXT,
                    sentiment TEXT,
                    raw_data TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # AI生成的事件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generated_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE,
                    news_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    tags TEXT,
                    options TEXT,
                    ai_analysis TEXT,
                    source_news TEXT,
                    match_score REAL DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    times_shown INTEGER DEFAULT 0,
                    times_selected INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (news_id) REFERENCES news_items(news_id)
                )
            ''')
            
            # 市场状态表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sentiment TEXT,
                    global_score REAL,
                    china_score REAL,
                    us_score REAL,
                    hot_topics TEXT,
                    outlook TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 用户事件交互记录
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS event_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    event_id TEXT,
                    action TEXT,
                    choice_index INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_category ON news_items(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_active ON news_items(is_active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_category ON generated_events(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_active ON generated_events(is_active)')
            
            conn.commit()
            print("[NewsEventDB] 数据库表初始化完成")
    
    def save_news(self, news_item: Dict) -> bool:
        """保存新闻到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                news_id = news_item.get('news_id') or f"news_{int(time.time()*1000)}_{hash(news_item.get('title', ''))}"
                expires_at = datetime.now() + timedelta(hours=24)  # 新闻24小时后过期
                
                cursor.execute('''
                    INSERT OR REPLACE INTO news_items 
                    (news_id, title, title_cn, summary, source, category, sentiment, raw_data, expires_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    news_id,
                    news_item.get('title', ''),
                    news_item.get('title_cn', news_item.get('title', '')),
                    news_item.get('summary', ''),
                    news_item.get('source', 'finai.org.cn'),
                    news_item.get('category', 'macro'),
                    news_item.get('sentiment', 'neutral'),
                    json.dumps(news_item, ensure_ascii=False),
                    expires_at
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"[NewsEventDB] 保存新闻失败: {e}")
            return False
    
    def save_news_batch(self, news_items: List[Dict]) -> int:
        """批量保存新闻"""
        saved_count = 0
        for item in news_items:
            if self.save_news(item):
                saved_count += 1
        print(f"[NewsEventDB] 批量保存 {saved_count}/{len(news_items)} 条新闻")
        return saved_count
    
    def save_generated_event(self, event: Dict) -> bool:
        """保存AI生成的事件"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                event_id = event.get('id') or f"evt_{int(time.time()*1000)}"
                expires_at = datetime.now() + timedelta(hours=12)  # 事件12小时后过期
                
                cursor.execute('''
                    INSERT OR REPLACE INTO generated_events 
                    (event_id, news_id, title, description, category, tags, options, 
                     ai_analysis, source_news, match_score, expires_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    event_id,
                    event.get('news_id'),
                    event.get('title', ''),
                    event.get('description', ''),
                    event.get('category', 'macro'),
                    json.dumps(event.get('tags', []), ensure_ascii=False),
                    json.dumps(event.get('options', []), ensure_ascii=False),
                    event.get('ai_analysis', ''),
                    event.get('source_news', ''),
                    event.get('match_score', 0.5),
                    expires_at
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"[NewsEventDB] 保存事件失败: {e}")
            return False
    
    def save_events_batch(self, events: List[Dict]) -> int:
        """批量保存事件"""
        saved_count = 0
        for event in events:
            if self.save_generated_event(event):
                saved_count += 1
        print(f"[NewsEventDB] 批量保存 {saved_count}/{len(events)} 条事件")
        return saved_count
    
    def get_active_events(self, category: str = None, limit: int = 20) -> List[Dict]:
        """获取活跃的事件"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = '''
                    SELECT * FROM generated_events 
                    WHERE is_active = 1 AND (expires_at IS NULL OR expires_at > datetime('now'))
                '''
                params = []
                
                if category:
                    query += ' AND category = ?'
                    params.append(category)
                
                query += ' ORDER BY created_at DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event = dict(row)
                    event['tags'] = json.loads(event['tags']) if event['tags'] else []
                    event['options'] = json.loads(event['options']) if event['options'] else []
                    event['is_real_news'] = True
                    events.append(event)
                
                return events
        except Exception as e:
            print(f"[NewsEventDB] 获取事件失败: {e}")
            return []
    
    def get_active_news(self, limit: int = 50) -> List[Dict]:
        """获取活跃的新闻"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM news_items 
                    WHERE is_active = 1 AND (expires_at IS NULL OR expires_at > datetime('now'))
                    ORDER BY fetched_at DESC LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[NewsEventDB] 获取新闻失败: {e}")
            return []
    
    def save_market_status(self, status: Dict) -> bool:
        """保存市场状态"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO market_status 
                    (sentiment, global_score, china_score, us_score, hot_topics, outlook)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    status.get('sentiment', 'neutral'),
                    status.get('global_score', 0),
                    status.get('china_score', 0),
                    status.get('us_score', 0),
                    json.dumps(status.get('hot_topics', []), ensure_ascii=False),
                    status.get('outlook', '震荡')
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"[NewsEventDB] 保存市场状态失败: {e}")
            return False
    
    def get_latest_market_status(self) -> Optional[Dict]:
        """获取最新市场状态"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM market_status 
                    ORDER BY recorded_at DESC LIMIT 1
                ''')
                row = cursor.fetchone()
                if row:
                    status = dict(row)
                    status['hot_topics'] = json.loads(status['hot_topics']) if status['hot_topics'] else []
                    return status
                return None
        except Exception as e:
            print(f"[NewsEventDB] 获取市场状态失败: {e}")
            return None
    
    def record_interaction(self, session_id: str, event_id: str, action: str, choice_index: int = None):
        """记录用户交互"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO event_interactions (session_id, event_id, action, choice_index)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, event_id, action, choice_index))
                
                # 更新事件统计
                if action == 'shown':
                    cursor.execute('''
                        UPDATE generated_events SET times_shown = times_shown + 1 
                        WHERE event_id = ?
                    ''', (event_id,))
                elif action == 'selected':
                    cursor.execute('''
                        UPDATE generated_events SET times_selected = times_selected + 1 
                        WHERE event_id = ?
                    ''', (event_id,))
                
                conn.commit()
        except Exception as e:
            print(f"[NewsEventDB] 记录交互失败: {e}")
    
    def cleanup_expired(self) -> int:
        """清理过期数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 将过期的标记为不活跃
                cursor.execute('''
                    UPDATE news_items SET is_active = 0 
                    WHERE expires_at < datetime('now') AND is_active = 1
                ''')
                news_count = cursor.rowcount
                
                cursor.execute('''
                    UPDATE generated_events SET is_active = 0 
                    WHERE expires_at < datetime('now') AND is_active = 1
                ''')
                events_count = cursor.rowcount
                
                conn.commit()
                
                total = news_count + events_count
                if total > 0:
                    print(f"[NewsEventDB] 清理了 {news_count} 条新闻, {events_count} 条事件")
                return total
        except Exception as e:
            print(f"[NewsEventDB] 清理失败: {e}")
            return 0
    
    def get_event_stats(self) -> Dict:
        """获取事件统计"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM news_items WHERE is_active = 1')
                active_news = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM generated_events WHERE is_active = 1')
                active_events = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM news_items')
                total_news = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM generated_events')
                total_events = cursor.fetchone()[0]
                
                return {
                    'active_news': active_news,
                    'active_events': active_events,
                    'total_news': total_news,
                    'total_events': total_events
                }
        except Exception as e:
            print(f"[NewsEventDB] 获取统计失败: {e}")
            return {}


# 全局实例
news_event_db = NewsEventDatabase()
