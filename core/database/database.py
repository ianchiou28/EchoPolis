"""
数据库管理系统 - SQLite数据库
"""
import sqlite3
import os
from typing import List, Dict, Optional

class EchopolisDatabase:
    """Echopolis数据库管理器"""
    
    def __init__(self, db_path: str = "echopolis.db"):
        # 确保数据库文件在项目根目录
        if not os.path.isabs(db_path):
            # 找到项目根目录（包含 README.md 的目录）
            current_dir = os.path.dirname(__file__)
            while current_dir != os.path.dirname(current_dir):
                if os.path.exists(os.path.join(current_dir, 'README.md')):
                    project_root = current_dir
                    break
                current_dir = os.path.dirname(current_dir)
            else:
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            db_path = os.path.join(project_root, db_path)
        self.db_path = db_path
        print(f"Database path: {self.db_path}")
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查并更新表结构
            try:
                cursor.execute("PRAGMA table_info(transactions)")
                columns = [column[1] for column in cursor.fetchall()]
                if 'ai_thoughts' not in columns:
                    cursor.execute('ALTER TABLE transactions ADD COLUMN ai_thoughts TEXT')
                    print("[INFO] 添加 ai_thoughts 列到 transactions 表")
            except:
                pass
            
            try:
                cursor.execute("PRAGMA table_info(investments)")
                columns = [column[1] for column in cursor.fetchall()]
                if 'ai_thoughts' not in columns:
                    cursor.execute('ALTER TABLE investments ADD COLUMN ai_thoughts TEXT')
                    print("[INFO] 添加 ai_thoughts 列到 investments 表")
            except:
                pass
            
            # 检查 users 表是否有新属性
            try:
                cursor.execute("PRAGMA table_info(users)")
                columns = [column[1] for column in cursor.fetchall()]
                if 'happiness' not in columns:
                    cursor.execute('ALTER TABLE users ADD COLUMN happiness INTEGER DEFAULT 70')
                if 'energy' not in columns:
                    cursor.execute('ALTER TABLE users ADD COLUMN energy INTEGER DEFAULT 75')
                if 'health' not in columns:
                    cursor.execute('ALTER TABLE users ADD COLUMN health INTEGER DEFAULT 80')
            except:
                pass
            
            # 账户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    session_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    mbti TEXT NOT NULL,
                    fate TEXT NOT NULL,
                    credits INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES accounts (username)
                )
            ''')
            
            # 投资表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS investments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    investment_type TEXT NOT NULL,
                    remaining_months INTEGER NOT NULL,
                    monthly_return INTEGER DEFAULT 0,
                    return_rate REAL DEFAULT 0,
                    created_round INTEGER NOT NULL,
                    ai_thoughts TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES accounts (username)
                )
            ''')
            
            # 交易记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    round_num INTEGER NOT NULL,
                    transaction_name TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    ai_thoughts TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES accounts (username)
                )
            ''')
            
            # 会话表：记录每个角色游戏进度（按月份）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    current_month INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 月度快照表：用于资产/情绪曲线与结局分析
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monthly_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    total_assets INTEGER NOT NULL,
                    cash INTEGER NOT NULL,
                    invested_assets INTEGER NOT NULL,
                    trust_level INTEGER,
                    happiness INTEGER,
                    stress INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 城市区块状态表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS district_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    district_id TEXT NOT NULL,
                    influence REAL DEFAULT 0,
                    heat REAL DEFAULT 0,
                    prosperity REAL DEFAULT 0,
                    unlock_level INTEGER DEFAULT 1,
                    events_completed INTEGER DEFAULT 0,
                    last_event TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, district_id)
                )
            ''')

            # 成就进度表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievement_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    achievement_id TEXT NOT NULL,
                    progress REAL DEFAULT 0,
                    completed INTEGER DEFAULT 0,
                    unlocked_at TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, achievement_id)
                )
            ''')

            # 城市事件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS city_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    district_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    type TEXT DEFAULT 'story',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                    FOREIGN KEY (district_id) REFERENCES district_states (district_id)
                )
            ''')

            conn.commit()
    
    def create_account(self, username: str, password: str) -> bool:
        """创建账户"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO accounts (username, password)
                    VALUES (?, ?)
                ''', (username, password))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def verify_account(self, username: str, password: str) -> bool:
        """验证账户"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT password FROM accounts WHERE username = ?
            ''', (username,))
            result = cursor.fetchone()
            return result and result[0] == password
    
    def save_user(self, username: str, session_id: str, name: str, mbti: str, fate: str, credits: int):
        """保存用户信息（一个账户可以有多个角色）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 检查session_id是否已存在
            cursor.execute('SELECT id FROM users WHERE session_id = ?', (session_id,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute('''
                    UPDATE users SET credits = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                ''', (credits, session_id))
            else:
                # 创建新记录
                cursor.execute('''
                    INSERT INTO users (username, session_id, name, mbti, fate, credits, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (username, session_id, name, mbti, fate, credits))
            conn.commit()
    
    def save_investment(self, username: str, session_id: str, name: str, amount: int, 
                       investment_type: str, remaining_months: int, 
                       monthly_return: int, return_rate: float, created_round: int, ai_thoughts: str = None):
        """保存投资记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO investments 
                (username, session_id, name, amount, investment_type, remaining_months, 
                 monthly_return, return_rate, created_round, ai_thoughts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, session_id, name, amount, investment_type, remaining_months, 
                  monthly_return, return_rate, created_round, ai_thoughts))
            conn.commit()
    
    def save_transaction(self, username: str, session_id: str, round_num: int, 
                        transaction_name: str, amount: int, ai_thoughts: str = None):
        """保存交易记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (username, session_id, round_num, transaction_name, amount, ai_thoughts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, session_id, round_num, transaction_name, amount, ai_thoughts))
            conn.commit()
    
    def get_user_info(self, username: str):
        """获取用户信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, mbti, fate, credits FROM users WHERE username = ?
                ''', (username,))
                result = cursor.fetchone()
                if result:
                    return {
                        'name': result[0],
                        'mbti': result[1], 
                        'fate': result[2],
                        'credits': result[3]
                    }
                return None
        except Exception as e:
            print(f"Database error in get_user_info: {e}")
            return None
    
    def get_user_investments(self, username: str) -> List[Dict]:
        """获取用户投资"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, amount, investment_type, remaining_months, monthly_return
                FROM investments 
                WHERE username = ? AND remaining_months > 0
                ORDER BY created_at DESC
            ''', (username,))
            
            investments = []
            for row in cursor.fetchall():
                investments.append({
                    'name': row[0],
                    'amount': row[1],
                    'type': row[2],
                    'remaining_months': row[3],
                    'monthly_return': row[4]
                })
            return investments
    
    def get_user_transactions(self, username: str, limit: int = 10) -> List[Dict]:
        """获取用户交易记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT round_num, transaction_name, amount
                FROM transactions 
                WHERE username = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (username, limit))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    'round': row[0],
                    'type': '交易',
                    'amount': row[2],
                    'description': row[1]
                })
            return transactions
    
    def upsert_session(self, session_id: str, username: str) -> None:
        """创建或确保存在一个会话记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM sessions WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute('''
                    UPDATE sessions SET updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                ''', (session_id,))
            else:
                cursor.execute('''
                    INSERT INTO sessions (session_id, username, current_month)
                    VALUES (?, ?, 1)
                ''', (session_id, username))
            conn.commit()
    
    def advance_session_month(self, session_id: str) -> int:
        """会话月份+1，返回新的月份"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT current_month FROM sessions WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            current = row[0] if row else 0
            new_month = current + 1
            if row:
                cursor.execute('''
                    UPDATE sessions
                    SET current_month = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = ?
                ''', (new_month, session_id))
            else:
                # fallback: 创建
                cursor.execute('''
                    INSERT INTO sessions (session_id, username, current_month)
                    VALUES (?, (SELECT username FROM users WHERE session_id = ? LIMIT 1), ?)
                ''', (session_id, session_id, new_month))
            conn.commit()
            return new_month
    
    def get_session_month(self, session_id: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT current_month FROM sessions WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            return row[0] if row else 1
    
    def save_monthly_snapshot(
        self,
        session_id: str,
        month: int,
        total_assets: int,
        cash: int,
        invested_assets: int,
        trust_level: Optional[int] = None,
        happiness: Optional[int] = None,
        stress: Optional[int] = None,
    ) -> None:
        """保存某个月的资产与情绪快照"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO monthly_snapshots (
                    session_id, month, total_assets, cash, invested_assets,
                    trust_level, happiness, stress
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                month,
                total_assets,
                cash,
                invested_assets,
                trust_level,
                happiness,
                stress,
            ))
            conn.commit()
    
    def get_session_timeline(self, session_id: str, limit: int = 36) -> List[Dict]:
        """获取最近若干个月的快照（按月份升序）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT month, total_assets, cash, invested_assets,
                       COALESCE(trust_level, 0), COALESCE(happiness, 0), COALESCE(stress, 0)
                FROM monthly_snapshots
                WHERE session_id = ?
                ORDER BY month DESC
                LIMIT ?
            ''', (session_id, limit))
            rows = cursor.fetchall()
            # 反转为升序
            rows = list(reversed(rows))
            return [
                {
                    "month": r[0],
                    "total_assets": r[1],
                    "cash": r[2],
                    "invested_assets": r[3],
                    "trust_level": r[4],
                    "happiness": r[5],
                    "stress": r[6],
                }
                for r in rows
            ]

    # 城市区块 & 成就相关工具
    def ensure_district_states(self, session_id: str) -> None:
        defaults = [
            ('finance', 0.62, 0.58, 0.74),
            ('tech', 0.55, 0.66, 0.68),
            ('housing', 0.48, 0.42, 0.6),
            ('learning', 0.35, 0.32, 0.52),
            ('leisure', 0.4, 0.5, 0.57),
            ('green', 0.44, 0.46, 0.63)
        ]
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(1) FROM district_states WHERE session_id = ?', (session_id,))
            count = cursor.fetchone()[0]
            if count:
                return
            for district_id, influence, heat, prosperity in defaults:
                cursor.execute('''
                    INSERT OR IGNORE INTO district_states (
                        session_id, district_id, influence, heat, prosperity, unlock_level, events_completed
                    ) VALUES (?, ?, ?, ?, ?, 1, 0)
                ''', (session_id, district_id, influence, heat, prosperity))
            conn.commit()

    def get_district_states(self, session_id: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT district_id, influence, heat, prosperity, unlock_level, events_completed, last_event
                FROM district_states
                WHERE session_id = ?
                ORDER BY district_id
            ''', (session_id,))
            rows = cursor.fetchall()
            return [
                {
                    'district_id': r[0],
                    'influence': r[1],
                    'heat': r[2],
                    'prosperity': r[3],
                    'unlock_level': r[4],
                    'events_completed': r[5],
                    'last_event': r[6]
                }
                for r in rows
            ]

    def upsert_district_state(
        self,
        session_id: str,
        district_id: str,
        *,
        influence: Optional[float] = None,
        heat: Optional[float] = None,
        prosperity: Optional[float] = None,
        unlock_level: Optional[int] = None,
        events_completed: Optional[int] = None,
        last_event: Optional[str] = None
    ) -> None:
        fields = []
        params = []
        if influence is not None:
            fields.append('influence = ?')
            params.append(influence)
        if heat is not None:
            fields.append('heat = ?')
            params.append(heat)
        if prosperity is not None:
            fields.append('prosperity = ?')
            params.append(prosperity)
        if unlock_level is not None:
            fields.append('unlock_level = ?')
            params.append(unlock_level)
        if events_completed is not None:
            fields.append('events_completed = ?')
            params.append(events_completed)
        if last_event is not None:
            fields.append('last_event = ?')
            params.append(last_event)
        fields.append('updated_at = CURRENT_TIMESTAMP')
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO district_states (session_id, district_id)
                VALUES (?, ?)
                ON CONFLICT(session_id, district_id) DO NOTHING
            ''', (session_id, district_id))
            if params:
                sql = f"UPDATE district_states SET {' ,'.join(fields)} WHERE session_id = ? AND district_id = ?"
                cursor.execute(sql, (*params, session_id, district_id))
            conn.commit()

    def get_achievement_progress(self, session_id: str) -> Dict[str, Dict[str, float]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT achievement_id, progress, completed, unlocked_at
                FROM achievement_progress
                WHERE session_id = ?
            ''', (session_id,))
            rows = cursor.fetchall()
            return {
                row[0]: {
                    'progress': row[1],
                    'completed': bool(row[2]),
                    'unlocked_at': row[3]
                }
                for row in rows
            }

    def set_achievement_progress(
        self,
        session_id: str,
        achievement_id: str,
        progress: float,
        completed: bool
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO achievement_progress (session_id, achievement_id, progress, completed, unlocked_at)
                VALUES (?, ?, ?, ?, CASE WHEN ? = 1 THEN CURRENT_TIMESTAMP ELSE NULL END)
                ON CONFLICT(session_id, achievement_id) DO UPDATE SET
                    progress = excluded.progress,
                    completed = excluded.completed,
                    updated_at = CURRENT_TIMESTAMP,
                    unlocked_at = CASE
                        WHEN excluded.completed = 1 AND achievement_progress.unlocked_at IS NULL THEN CURRENT_TIMESTAMP
                        ELSE achievement_progress.unlocked_at
                    END
            ''', (session_id, achievement_id, progress, int(completed), int(completed)))
            conn.commit()

    def get_city_events(self, session_id: str, limit: int = 15) -> List[Dict]:
        """获取城市事件"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, session_id, district_id, title, description, type, created_at
                FROM city_events
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "session_id": row[1],
                    "district_id": row[2],
                    "title": row[3],
                    "description": row[4],
                    "type": row[5],
                    "created_at": row[6]
                }
                for row in rows
            ]

    def save_city_event(self, session_id: str, district_id: str, title: str, description: str, event_type: str = "story") -> None:
        """保存城市事件"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO city_events (session_id, district_id, title, description, type)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, district_id, title, description, event_type))
            conn.commit()

    def get_or_create_district_state(self, session_id: str, district_id: str) -> Dict:
        """获取或创建区块状态"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT influence, heat, prosperity, unlock_level, events_completed, last_event
                FROM district_states
                WHERE session_id = ? AND district_id = ?
            ''', (session_id, district_id))
            row = cursor.fetchone()
            if row:
                influence, heat, prosperity, unlock_level, events_completed, last_event = row
            else:
                cursor.execute('''
                    INSERT INTO district_states (session_id, district_id, influence, heat, prosperity)
                    VALUES (?, ?, 0, 0, 0)
                ''', (session_id, district_id))
                conn.commit()
                influence = heat = prosperity = 0
                unlock_level = 1
                events_completed = 0
                last_event = None
            return {
                "session_id": session_id,
                "district_id": district_id,
                "influence": influence,
                "heat": heat,
                "prosperity": prosperity,
                "unlock_level": unlock_level,
                "events_completed": events_completed,
                "last_event": last_event,
            }

    def update_district_state(self, session_id: str, district_id: str, **kwargs) -> None:
        """更新区块状态"""
        if not kwargs:
            return
        columns = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.extend([session_id, district_id])
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE district_states
                SET {columns}, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ? AND district_id = ?
            ''', values)
            conn.commit()

# 全局数据库实例
db = EchopolisDatabase()