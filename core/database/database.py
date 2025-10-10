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
        """保存用户信息（一个账户只能有一套人格）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 检查是否已存在用户记录
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute('''
                    UPDATE users SET credits = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE username = ?
                ''', (credits, username))
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

# 全局数据库实例
db = EchopolisDatabase()