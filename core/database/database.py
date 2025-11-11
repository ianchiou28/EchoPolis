"""
数据库管理系统 - SQLite数据库
"""
import sqlite3
import json
import os
from typing import List, Dict, Optional
from datetime import datetime

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
    
    def _ensure_column(self, cursor, table: str, column: str, definition_sql: str):
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in cursor.fetchall()]
        if column not in cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition_sql}")
            print(f"[INFO] 添加列 {table}.{column}")

    def init_database(self):
        """初始化数据库表并迁移旧结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 先创建表(若不存在)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    mbti TEXT NOT NULL,
                    fate TEXT NOT NULL,
                    credits INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES accounts (username)
                )
            ''')
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
            # 迁移: 新增 avatar_id 及详细属性列
            try:
                self._ensure_column(cursor, 'users', 'avatar_id', 'TEXT')
                self._ensure_column(cursor, 'users', 'health', 'INTEGER DEFAULT 100')
                self._ensure_column(cursor, 'users', 'energy', 'INTEGER DEFAULT 100')
                self._ensure_column(cursor, 'users', 'happiness', 'INTEGER DEFAULT 50')
                self._ensure_column(cursor, 'users', 'stress', 'INTEGER DEFAULT 0')
                self._ensure_column(cursor, 'users', 'trust_level', 'INTEGER DEFAULT 50')
                self._ensure_column(cursor, 'users', 'current_round', 'INTEGER DEFAULT 1')
                self._ensure_column(cursor, 'users', 'long_term_investments', 'INTEGER DEFAULT 0')
                self._ensure_column(cursor, 'users', 'locked_investments', "TEXT DEFAULT '[]'")
            except Exception as e:
                print(f"[WARN] 用户表迁移失败: {e}")
            try:
                self._ensure_column(cursor, 'investments', 'avatar_id', 'TEXT')
            except Exception as e:
                print(f"[WARN] 投资表迁移失败: {e}")
            try:
                self._ensure_column(cursor, 'transactions', 'avatar_id', 'TEXT')
            except Exception as e:
                print(f"[WARN] 交易表迁移失败: {e}")
            # 为旧表补充 ai_thoughts
            try:
                self._ensure_column(cursor, 'transactions', 'ai_thoughts', 'TEXT')
            except Exception:
                pass
            try:
                self._ensure_column(cursor, 'investments', 'ai_thoughts', 'TEXT')
            except Exception:
                pass
            conn.commit()
    
    def create_account(self, username: str, password: str) -> bool:
        """创建账户"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO accounts (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def verify_account(self, username: str, password: str) -> bool:
        """验证账户"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM accounts WHERE username = ?', (username,))
            result = cursor.fetchone()
            return result and result[0] == password
    
    def save_user(self, username: str, avatar_id: str, session_id: str, name: str, mbti: str, fate: str, credits: int):
        """保存化身信息(新增一条记录)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, avatar_id, session_id, name, mbti, fate, credits, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (username, avatar_id, session_id, name, mbti, fate, credits))
            conn.commit()

    def update_avatar_state(self, avatar_id: str, **kwargs):
        """更新单个化身部分字段"""
        if not kwargs:
            return
        allowed = {"credits","health","energy","happiness","stress","trust_level","current_round","long_term_investments","locked_investments"}
        set_parts = []
        values = []
        for k,v in kwargs.items():
            if k in allowed:
                set_parts.append(f"{k} = ?")
                values.append(json.dumps(v) if k == 'locked_investments' else v)
        if not set_parts:
            return
        values.append(avatar_id)
        sql = f"UPDATE users SET {', '.join(set_parts)}, updated_at = CURRENT_TIMESTAMP WHERE avatar_id = ?"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()

    def list_avatars(self, username: str) -> List[Dict]:
        """列出账户下所有化身"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT avatar_id, name, mbti, fate, credits, health, energy, happiness, stress, trust_level, current_round, long_term_investments, locked_investments
                FROM users WHERE username = ? ORDER BY updated_at DESC
            ''', (username,))
            rows = cursor.fetchall()
            avatars = []
            for r in rows:
                avatars.append({
                    'avatar_id': r[0], 'name': r[1], 'mbti': r[2], 'fate': r[3], 'credits': r[4], 'health': r[5], 'energy': r[6], 'happiness': r[7], 'stress': r[8], 'trust_level': r[9], 'current_round': r[10], 'long_term_investments': r[11], 'locked_investments': json.loads(r[12] or '[]')
                })
            return avatars

    def get_avatar(self, avatar_id: str) -> Optional[Dict]:
        """获取单个化身"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, avatar_id, name, mbti, fate, credits, health, energy, happiness, stress, trust_level, current_round, long_term_investments, locked_investments
                FROM users WHERE avatar_id = ?
            ''', (avatar_id,))
            r = cursor.fetchone()
            if r:
                return {
                    'username': r[0], 'avatar_id': r[1], 'name': r[2], 'mbti': r[3], 'fate': r[4], 'credits': r[5], 'health': r[6], 'energy': r[7], 'happiness': r[8], 'stress': r[9], 'trust_level': r[10], 'current_round': r[11], 'long_term_investments': r[12], 'locked_investments': json.loads(r[13] or '[]')
                }
            return None

    def get_avatar_investments(self, avatar_id: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, amount, investment_type, remaining_months, monthly_return
                FROM investments WHERE avatar_id = ? AND remaining_months > 0 ORDER BY created_at DESC
            ''', (avatar_id,))
            res = []
            for row in cursor.fetchall():
                res.append({'name': row[0], 'amount': row[1], 'type': row[2], 'remaining_months': row[3], 'monthly_return': row[4]})
            return res

    def get_avatar_transactions(self, avatar_id: str, limit: int = 10) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT round_num, transaction_name, amount
                FROM transactions WHERE avatar_id = ? ORDER BY created_at DESC LIMIT ?
            ''', (avatar_id, limit))
            res = []
            for row in cursor.fetchall():
                res.append({'round': row[0], 'type': '交易', 'amount': row[2], 'description': row[1]})
            return res

    def reset_avatar(self, avatar_id: str):
        """重置化身状态并清空其投资与交易"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT fate, mbti, name, username FROM users WHERE avatar_id = ?', (avatar_id,))
            base = cursor.fetchone()
            if not base:
                return False
            fate, mbti, name, username = base
            # 根据命运确定初始资金
            credits = 50000
            try:
                from ..systems.fate_wheel import FateType, FateWheel
                # 去除空格匹配
                fate_clean = (fate or '').strip()
                # 匹配到枚举
                ft = None
                for ft_candidate in FateWheel.FateType:
                    if getattr(ft_candidate, 'value', '').strip() == fate_clean:
                        ft = ft_candidate
                        break
                if ft:
                    info = FateWheel.get_fate_info(ft)
                    credits = info.get('initial_money', credits)
            except Exception as e:
                print(f"[WARN] 计算初始资金失败，使用默认值: {e}")
            # 重置主要字段
            cursor.execute('''
                UPDATE users SET credits = ?, health = 100, energy = 100, happiness = 50, stress = 0, trust_level = 50, current_round = 1, long_term_investments = 0, locked_investments = '[]', updated_at = CURRENT_TIMESTAMP WHERE avatar_id = ?
            ''', (credits, avatar_id))
            cursor.execute('DELETE FROM investments WHERE avatar_id = ?', (avatar_id,))
            cursor.execute('DELETE FROM transactions WHERE avatar_id = ?', (avatar_id,))
            conn.commit()
            return True

    def save_investment(self, username: str, avatar_id: str, session_id: str, name: str, amount: int,
                       investment_type: str, remaining_months: int,
                       monthly_return: int, return_rate: float, created_round: int, ai_thoughts: str = None):
        """保存投资记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO investments (username, avatar_id, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, avatar_id, session_id, name, amount, investment_type, remaining_months, monthly_return, return_rate, created_round, ai_thoughts))
            conn.commit()
    
    def save_transaction(self, username: str, avatar_id: str, session_id: str, round_num: int, transaction_name: str, amount: int, ai_thoughts: str = None):
        """保存交易记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (username, avatar_id, session_id, round_num, transaction_name, amount, ai_thoughts)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, avatar_id, session_id, round_num, transaction_name, amount, ai_thoughts))
            conn.commit()
    
    def get_user_info(self, username: str):
        """获取账号下第一个化身(兼容旧接口)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name, mbti, fate, credits FROM users WHERE username = ? ORDER BY created_at ASC LIMIT 1', (username,))
                result = cursor.fetchone()
                if result:
                    return {'name': result[0], 'mbti': result[1], 'fate': result[2], 'credits': result[3]}
                return None
        except Exception as e:
            print(f"Database error in get_user_info: {e}")
            return None
    
    def get_user_investments(self, username: str) -> List[Dict]:
        """获取用户投资"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, amount, investment_type, remaining_months, monthly_return FROM investments WHERE username = ? AND remaining_months > 0 ORDER BY created_at DESC
            ''', (username,))
            
            investments = []
            for row in cursor.fetchall():
                investments.append({'name': row[0], 'amount': row[1], 'type': row[2], 'remaining_months': row[3], 'monthly_return': row[4]})
            return investments
    
    def get_user_transactions(self, username: str, limit: int = 10) -> List[Dict]:
        """获取用户交易记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT round_num, transaction_name, amount FROM transactions WHERE username = ? ORDER BY created_at DESC LIMIT ?
            ''', (username, limit))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({'round': row[0], 'type': '交易', 'amount': row[2], 'description': row[1]})
            return transactions

# 全局数据库实例
db = EchopolisDatabase()