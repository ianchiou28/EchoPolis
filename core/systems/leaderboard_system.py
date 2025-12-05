"""
排行榜系统 - EchoPolis
资产排行、成就排行、投资收益率排行
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class LeaderboardType(Enum):
    """排行榜类型"""
    TOTAL_ASSETS = "总资产榜"
    NET_WORTH_GROWTH = "资产增速榜"
    INVESTMENT_RETURN = "投资收益榜"
    ACHIEVEMENT_COUNT = "成就数量榜"
    RARE_ACHIEVEMENT = "稀有成就榜"


@dataclass
class LeaderboardEntry:
    """排行榜条目"""
    rank: int
    session_id: str
    player_name: str
    value: float
    extra_info: Dict


class LeaderboardSystem:
    """排行榜系统"""
    
    def __init__(self, db=None):
        self.db = db
    
    def set_db(self, db):
        """设置数据库连接"""
        self.db = db
    
    def get_total_assets_leaderboard(self, limit: int = 20) -> List[Dict]:
        """获取总资产排行榜"""
        if not self.db:
            return []
        
        import sqlite3
        from core.systems.avatar_system import avatar_system
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.session_id, u.name, u.credits,
                       COALESCE(SUM(i.amount), 0) as invested,
                       u.current_avatar
                FROM users u
                LEFT JOIN investments i ON u.session_id = i.session_id 
                    AND i.remaining_months > 0
                GROUP BY u.session_id
                ORDER BY (u.credits + COALESCE(SUM(i.amount), 0)) DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for rank, row in enumerate(cursor.fetchall(), 1):
                total = row[2] + row[3]
                avatar_id = row[4] or 'default_orange'
                avatar_info = avatar_system.get_avatar(avatar_id)
                results.append({
                    "rank": rank,
                    "session_id": row[0],
                    "name": row[1],
                    "total_assets": total,
                    "cash": row[2],
                    "invested": row[3],
                    "avatar_id": avatar_id,
                    "avatar_emoji": avatar_info.get('emoji', '🎭') if avatar_info else '🎭',
                    "avatar_color": avatar_info.get('color', '#ff8c00') if avatar_info else '#ff8c00'
                })
            return results
    
    def get_growth_leaderboard(self, limit: int = 20) -> List[Dict]:
        """获取资产增速排行榜"""
        if not self.db:
            return []
        
        import sqlite3
        from core.systems.avatar_system import avatar_system
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            # 计算最近3个月的增长率
            cursor.execute('''
                SELECT 
                    s.session_id,
                    u.name,
                    s1.total_assets as recent,
                    s2.total_assets as older,
                    CASE WHEN s2.total_assets > 0 
                        THEN (s1.total_assets - s2.total_assets) * 100.0 / s2.total_assets
                        ELSE 0 
                    END as growth_rate,
                    u.current_avatar
                FROM sessions s
                JOIN users u ON s.session_id = u.session_id
                LEFT JOIN (
                    SELECT session_id, total_assets, month
                    FROM monthly_snapshots m1
                    WHERE month = (SELECT MAX(month) FROM monthly_snapshots m2 
                                   WHERE m2.session_id = m1.session_id)
                ) s1 ON s.session_id = s1.session_id
                LEFT JOIN (
                    SELECT session_id, total_assets, month
                    FROM monthly_snapshots m1
                    WHERE month = (SELECT MAX(month) - 3 FROM monthly_snapshots m2 
                                   WHERE m2.session_id = m1.session_id)
                ) s2 ON s.session_id = s2.session_id
                WHERE s1.total_assets IS NOT NULL AND s2.total_assets IS NOT NULL
                ORDER BY growth_rate DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for rank, row in enumerate(cursor.fetchall(), 1):
                avatar_id = row[5] or 'default_orange'
                avatar_info = avatar_system.get_avatar(avatar_id)
                results.append({
                    "rank": rank,
                    "session_id": row[0],
                    "name": row[1],
                    "current_assets": row[2],
                    "growth_rate": round(row[4], 2),
                    "avatar_id": avatar_id,
                    "avatar_emoji": avatar_info.get('emoji', '🎭') if avatar_info else '🎭',
                    "avatar_color": avatar_info.get('color', '#ff8c00') if avatar_info else '#ff8c00'
                })
            return results
    
    def get_investment_return_leaderboard(self, limit: int = 20) -> List[Dict]:
        """获取投资收益率排行榜"""
        if not self.db:
            return []
        
        import sqlite3
        from core.systems.avatar_system import avatar_system
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    st.session_id,
                    u.name,
                    SUM(st.profit) as total_profit,
                    COUNT(*) as trade_count,
                    SUM(CASE WHEN st.profit > 0 THEN 1 ELSE 0 END) as win_count,
                    u.current_avatar
                FROM stock_transactions st
                JOIN users u ON st.session_id = u.session_id
                WHERE st.action = 'sell'
                GROUP BY st.session_id
                ORDER BY total_profit DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for rank, row in enumerate(cursor.fetchall(), 1):
                win_rate = row[4] / row[3] * 100 if row[3] > 0 else 0
                avatar_id = row[5] or 'default_orange'
                avatar_info = avatar_system.get_avatar(avatar_id)
                results.append({
                    "rank": rank,
                    "session_id": row[0],
                    "name": row[1],
                    "total_profit": row[2],
                    "trade_count": row[3],
                    "win_rate": round(win_rate, 1),
                    "avatar_id": avatar_id,
                    "avatar_emoji": avatar_info.get('emoji', '🎭') if avatar_info else '🎭',
                    "avatar_color": avatar_info.get('color', '#ff8c00') if avatar_info else '#ff8c00'
                })
            return results
    
    def get_achievement_leaderboard(self, limit: int = 20) -> List[Dict]:
        """获取成就数量排行榜"""
        if not self.db:
            return []
        
        import sqlite3
        from core.systems.avatar_system import avatar_system
        
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    a.session_id,
                    u.name,
                    COUNT(*) as achievement_count,
                    SUM(a.reward_coins) as total_coins,
                    SUM(a.reward_exp) as total_exp,
                    u.current_avatar
                FROM achievements_unlocked a
                JOIN users u ON a.session_id = u.session_id
                GROUP BY a.session_id
                ORDER BY achievement_count DESC, total_exp DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for rank, row in enumerate(cursor.fetchall(), 1):
                avatar_id = row[5] or 'default_orange'
                avatar_info = avatar_system.get_avatar(avatar_id)
                results.append({
                    "rank": rank,
                    "session_id": row[0],
                    "name": row[1],
                    "achievement_count": row[2],
                    "total_coins": row[3] or 0,
                    "total_exp": row[4] or 0,
                    "avatar_id": avatar_id,
                    "avatar_emoji": avatar_info.get('emoji', '🎭') if avatar_info else '🎭',
                    "avatar_color": avatar_info.get('color', '#ff8c00') if avatar_info else '#ff8c00'
                })
            return results
    
    def get_rare_achievement_leaderboard(self, limit: int = 20) -> List[Dict]:
        """获取稀有成就排行榜"""
        if not self.db:
            return []
        
        rarity_scores = {
            "legendary": 100,
            "epic": 50,
            "rare": 20,
            "uncommon": 5,
            "common": 1
        }
        
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    a.session_id,
                    u.name,
                    a.rarity,
                    COUNT(*) as count
                FROM achievements_unlocked a
                JOIN users u ON a.session_id = u.session_id
                GROUP BY a.session_id, a.rarity
            ''')
            
            scores = {}
            names = {}
            for row in cursor.fetchall():
                session_id = row[0]
                name = row[1]
                rarity = row[2].lower()
                count = row[3]
                
                if session_id not in scores:
                    scores[session_id] = 0
                    names[session_id] = name
                
                scores[session_id] += rarity_scores.get(rarity, 1) * count
            
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            results = []
            for rank, (session_id, score) in enumerate(sorted_scores, 1):
                results.append({
                    "rank": rank,
                    "session_id": session_id,
                    "name": names[session_id],
                    "rarity_score": score
                })
            return results
    
    def get_player_rank(self, session_id: str, 
                       leaderboard_type: LeaderboardType) -> Optional[Dict]:
        """获取玩家在指定排行榜的排名"""
        if leaderboard_type == LeaderboardType.TOTAL_ASSETS:
            lb = self.get_total_assets_leaderboard(100)
        elif leaderboard_type == LeaderboardType.NET_WORTH_GROWTH:
            lb = self.get_growth_leaderboard(100)
        elif leaderboard_type == LeaderboardType.INVESTMENT_RETURN:
            lb = self.get_investment_return_leaderboard(100)
        elif leaderboard_type == LeaderboardType.ACHIEVEMENT_COUNT:
            lb = self.get_achievement_leaderboard(100)
        else:
            lb = self.get_rare_achievement_leaderboard(100)
        
        for entry in lb:
            if entry["session_id"] == session_id:
                return entry
        
        return None
    
    def get_all_leaderboards_summary(self, limit: int = 5) -> Dict:
        """获取所有排行榜摘要"""
        return {
            "total_assets": self.get_total_assets_leaderboard(limit),
            "growth": self.get_growth_leaderboard(limit),
            "investment": self.get_investment_return_leaderboard(limit),
            "achievements": self.get_achievement_leaderboard(limit)
        }


# 全局实例
leaderboard_system = LeaderboardSystem()
