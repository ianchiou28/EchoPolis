"""
数据库管理系统 - SQLite数据库
"""
import sqlite3
import os
from typing import List, Dict, Optional

class FinAIDatabase:
    """FinAI数据库管理器"""
    
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
            
            # ============ 新增金融系统表 ============
            
            # 股票持仓表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    stock_id TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    shares INTEGER NOT NULL,
                    avg_cost REAL NOT NULL,
                    buy_month INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, stock_id)
                )
            ''')
            
            # 股票交易历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    stock_id TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    shares INTEGER NOT NULL,
                    price REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    month INTEGER NOT NULL,
                    profit REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 股票价格历史表（K线数据）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_id TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    day INTEGER NOT NULL,
                    open_price REAL NOT NULL,
                    high_price REAL NOT NULL,
                    low_price REAL NOT NULL,
                    close_price REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    UNIQUE(stock_id, month, day)
                )
            ''')
            
            # 贷款表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    loan_id TEXT UNIQUE NOT NULL,
                    loan_type TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    principal INTEGER NOT NULL,
                    remaining_principal INTEGER NOT NULL,
                    annual_rate REAL NOT NULL,
                    term_months INTEGER NOT NULL,
                    remaining_months INTEGER NOT NULL,
                    monthly_payment INTEGER NOT NULL,
                    repayment_method TEXT NOT NULL,
                    start_month INTEGER NOT NULL,
                    is_overdue INTEGER DEFAULT 0,
                    overdue_days INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 还款记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS loan_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    loan_id TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    payment_amount INTEGER NOT NULL,
                    principal_part INTEGER NOT NULL,
                    interest_part INTEGER NOT NULL,
                    remaining_principal INTEGER NOT NULL,
                    is_early_repayment INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 保险保单表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS insurance_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    policy_id TEXT UNIQUE NOT NULL,
                    product_id TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    insurance_type TEXT NOT NULL,
                    monthly_premium INTEGER NOT NULL,
                    coverage_amount INTEGER NOT NULL,
                    deductible INTEGER NOT NULL,
                    coverage_ratio REAL NOT NULL,
                    start_month INTEGER NOT NULL,
                    remaining_months INTEGER NOT NULL,
                    claim_count INTEGER DEFAULT 0,
                    max_claims INTEGER NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 保险理赔记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS insurance_claims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    policy_id TEXT NOT NULL,
                    claim_id TEXT UNIQUE NOT NULL,
                    event_type TEXT NOT NULL,
                    event_description TEXT,
                    claim_amount INTEGER NOT NULL,
                    approved_amount INTEGER DEFAULT 0,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 金融产品持仓表（基金、债券、定期等）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financial_holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    product_type TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    buy_price REAL NOT NULL,
                    current_value REAL NOT NULL,
                    buy_month INTEGER NOT NULL,
                    maturity_month INTEGER,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, product_id)
                )
            ''')
            
            # 现金流记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cashflow_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    item_name TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    is_income INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 月度现金流汇总表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monthly_cashflow (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    total_income INTEGER NOT NULL,
                    total_expense INTEGER NOT NULL,
                    net_cashflow INTEGER NOT NULL,
                    saving_rate REAL NOT NULL,
                    cash_balance INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, month)
                )
            ''')
            
            # 信用分历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credit_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    credit_score INTEGER NOT NULL,
                    change_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 宏观经济状态表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS economic_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month INTEGER UNIQUE NOT NULL,
                    gdp_growth REAL NOT NULL,
                    inflation REAL NOT NULL,
                    interest_rate REAL NOT NULL,
                    unemployment REAL NOT NULL,
                    cpi_index REAL NOT NULL,
                    house_price_index REAL NOT NULL,
                    stock_index REAL NOT NULL,
                    economic_phase TEXT NOT NULL,
                    active_event TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 成就解锁记录表（更详细的版本）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements_unlocked (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    achievement_id TEXT NOT NULL,
                    achievement_name TEXT NOT NULL,
                    rarity TEXT NOT NULL,
                    reward_coins INTEGER DEFAULT 0,
                    reward_exp INTEGER DEFAULT 0,
                    reward_title TEXT,
                    unlocked_month INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, achievement_id)
                )
            ''')
            
            # 行为日志表（记录用户每次操作）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS behavior_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    action_category TEXT NOT NULL,
                    amount REAL,
                    risk_score REAL,
                    rationality_score REAL,
                    market_condition TEXT,
                    decision_context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 行为画像表（每个用户的行为特征）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS behavior_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL UNIQUE,
                    risk_preference TEXT,
                    decision_style TEXT,
                    loss_aversion REAL,
                    overconfidence REAL,
                    herding_tendency REAL,
                    planning_ability REAL,
                    action_count INTEGER DEFAULT 0,
                    avg_risk_score REAL DEFAULT 0,
                    avg_rationality REAL DEFAULT 0,
                    last_updated_month INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 群体洞察表（Z世代群体的行为模式）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cohort_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_type TEXT NOT NULL,
                    insight_category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    data_source TEXT,
                    sample_size INTEGER,
                    confidence_level REAL,
                    tags TEXT,
                    generated_month INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT password FROM accounts WHERE username = ?
                ''', (username,))
                result = cursor.fetchone()
                
                if result:
                    if result[0] == password:
                        print(f"[Login] User '{username}' logged in successfully.")
                        return True
                    else:
                        print(f"[Login] User '{username}' password mismatch.")
                        return False
                else:
                    print(f"[Login] User '{username}' not found.")
                    # Debug: print all users
                    cursor.execute('SELECT username FROM accounts')
                    users = cursor.fetchall()
                    print(f"[Login] Existing users: {[u[0] for u in users]}")
                    return False
        except Exception as e:
            print(f"[Login] Error verifying account: {e}")
            return False
    
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

    def delete_user(self, session_id: str) -> bool:
        """删除用户及其所有相关数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 删除相关表中的数据
                tables = [
                    'investments', 'transactions', 'sessions', 
                    'monthly_snapshots', 'district_states', 
                    'achievement_progress', 'city_events',
                    'stock_holdings', 'stock_transactions',
                    'loans', 'loan_payments', 'insurance_policies',
                    'insurance_claims', 'financial_holdings',
                    'cashflow_records', 'monthly_cashflow',
                    'credit_history', 'achievements_unlocked'
                ]
                
                for table in tables:
                    try:
                        cursor.execute(f'DELETE FROM {table} WHERE session_id = ?', (session_id,))
                    except:
                        pass
                
                # 最后删除用户表中的记录
                cursor.execute('DELETE FROM users WHERE session_id = ?', (session_id,))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"[Delete] Error deleting user {session_id}: {e}")
            return False
    
    # ============ 股票系统方法 ============
    
    def save_stock_holding(self, session_id: str, stock_id: str, stock_name: str,
                          shares: int, avg_cost: float, buy_month: int) -> None:
        """保存或更新股票持仓"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO stock_holdings (session_id, stock_id, stock_name, shares, avg_cost, buy_month)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id, stock_id) DO UPDATE SET
                    shares = excluded.shares,
                    avg_cost = excluded.avg_cost
            ''', (session_id, stock_id, stock_name, shares, avg_cost, buy_month))
            conn.commit()
    
    def get_stock_holdings(self, session_id: str) -> List[Dict]:
        """获取股票持仓"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT stock_id, stock_name, shares, avg_cost, buy_month
                FROM stock_holdings
                WHERE session_id = ? AND shares > 0
            ''', (session_id,))
            return [
                {
                    'stock_id': r[0],
                    'stock_name': r[1],
                    'shares': r[2],
                    'avg_cost': r[3],
                    'buy_month': r[4]
                }
                for r in cursor.fetchall()
            ]
    
    def delete_stock_holding(self, session_id: str, stock_id: str) -> None:
        """删除股票持仓（清仓时）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM stock_holdings WHERE session_id = ? AND stock_id = ?
            ''', (session_id, stock_id))
            conn.commit()
    
    def save_stock_transaction(self, session_id: str, stock_id: str, stock_name: str,
                               action: str, shares: int, price: float, 
                               total_amount: float, month: int, profit: float = 0) -> None:
        """保存股票交易记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO stock_transactions 
                (session_id, stock_id, stock_name, action, shares, price, total_amount, month, profit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, stock_id, stock_name, action, shares, price, total_amount, month, profit))
            conn.commit()
    
    def get_stock_transactions(self, session_id: str, limit: int = 50) -> List[Dict]:
        """获取股票交易历史"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT stock_id, stock_name, action, shares, price, total_amount, month, profit, created_at
                FROM stock_transactions
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            return [
                {
                    'stock_id': r[0],
                    'stock_name': r[1],
                    'action': r[2],
                    'shares': r[3],
                    'price': r[4],
                    'total_amount': r[5],
                    'month': r[6],
                    'profit': r[7],
                    'created_at': r[8]
                }
                for r in cursor.fetchall()
            ]
    
    def get_stock_profit_stats(self, session_id: str) -> Dict:
        """获取股票盈亏统计"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT SUM(profit), COUNT(*), SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END)
                FROM stock_transactions
                WHERE session_id = ? AND action = 'sell'
            ''', (session_id,))
            row = cursor.fetchone()
            total_profit = row[0] or 0
            total_trades = row[1] or 0
            winning_trades = row[2] or 0
            return {
                'total_profit': total_profit,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': winning_trades / total_trades if total_trades > 0 else 0
            }
    
    # ============ 贷款系统方法 ============
    
    def save_loan(self, session_id: str, loan_data: Dict) -> None:
        """保存贷款"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO loans (
                    session_id, loan_id, loan_type, product_name, principal,
                    remaining_principal, annual_rate, term_months, remaining_months,
                    monthly_payment, repayment_method, start_month
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, loan_data['loan_id'], loan_data['loan_type'],
                loan_data['product_name'], loan_data['principal'],
                loan_data['remaining_principal'], loan_data['annual_rate'],
                loan_data['term_months'], loan_data['remaining_months'],
                loan_data['monthly_payment'], loan_data['repayment_method'],
                loan_data['start_month']
            ))
            conn.commit()
    
    def get_loans(self, session_id: str, active_only: bool = True) -> List[Dict]:
        """获取贷款列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''
                SELECT loan_id, loan_type, product_name, principal, remaining_principal,
                       annual_rate, term_months, remaining_months, monthly_payment,
                       repayment_method, start_month, is_overdue, overdue_days
                FROM loans
                WHERE session_id = ?
            '''
            if active_only:
                query += ' AND remaining_months > 0'
            cursor.execute(query, (session_id,))
            return [
                {
                    'loan_id': r[0], 'loan_type': r[1], 'product_name': r[2],
                    'principal': r[3], 'remaining_principal': r[4],
                    'annual_rate': r[5], 'term_months': r[6], 'remaining_months': r[7],
                    'monthly_payment': r[8], 'repayment_method': r[9],
                    'start_month': r[10], 'is_overdue': bool(r[11]), 'overdue_days': r[12]
                }
                for r in cursor.fetchall()
            ]
    
    def update_loan(self, session_id: str, loan_id: str, **kwargs) -> None:
        """更新贷款信息"""
        if not kwargs:
            return
        columns = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE loans SET {columns}
                WHERE session_id = ? AND loan_id = ?
            ''', (*values, session_id, loan_id))
            conn.commit()
    
    def save_loan_payment(self, session_id: str, payment_data: Dict) -> None:
        """保存还款记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO loan_payments (
                    session_id, loan_id, month, payment_amount, principal_part,
                    interest_part, remaining_principal, is_early_repayment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, payment_data['loan_id'], payment_data['month'],
                payment_data['payment_amount'], payment_data['principal_part'],
                payment_data['interest_part'], payment_data['remaining_principal'],
                int(payment_data.get('is_early_repayment', False))
            ))
            conn.commit()
    
    # ============ 保险系统方法 ============
    
    def save_insurance_policy(self, session_id: str, policy_data: Dict) -> None:
        """保存保险保单"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO insurance_policies (
                    session_id, policy_id, product_id, product_name, insurance_type,
                    monthly_premium, coverage_amount, deductible, coverage_ratio,
                    start_month, remaining_months, max_claims
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, policy_data['policy_id'], policy_data['product_id'],
                policy_data['product_name'], policy_data['insurance_type'],
                policy_data['monthly_premium'], policy_data['coverage_amount'],
                policy_data['deductible'], policy_data['coverage_ratio'],
                policy_data['start_month'], policy_data['remaining_months'],
                policy_data['max_claims']
            ))
            conn.commit()
    
    def get_insurance_policies(self, session_id: str, active_only: bool = True) -> List[Dict]:
        """获取保险保单列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''
                SELECT policy_id, product_id, product_name, insurance_type,
                       monthly_premium, coverage_amount, deductible, coverage_ratio,
                       start_month, remaining_months, claim_count, max_claims, is_active
                FROM insurance_policies
                WHERE session_id = ?
            '''
            if active_only:
                query += ' AND is_active = 1'
            cursor.execute(query, (session_id,))
            return [
                {
                    'policy_id': r[0], 'product_id': r[1], 'product_name': r[2],
                    'insurance_type': r[3], 'monthly_premium': r[4],
                    'coverage_amount': r[5], 'deductible': r[6], 'coverage_ratio': r[7],
                    'start_month': r[8], 'remaining_months': r[9],
                    'claim_count': r[10], 'max_claims': r[11], 'is_active': bool(r[12])
                }
                for r in cursor.fetchall()
            ]
    
    def update_insurance_policy(self, session_id: str, policy_id: str, **kwargs) -> None:
        """更新保险保单"""
        if not kwargs:
            return
        columns = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE insurance_policies SET {columns}
                WHERE session_id = ? AND policy_id = ?
            ''', (*values, session_id, policy_id))
            conn.commit()
    
    def save_insurance_claim(self, session_id: str, claim_data: Dict) -> None:
        """保存理赔记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO insurance_claims (
                    session_id, policy_id, claim_id, event_type, event_description,
                    claim_amount, approved_amount, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, claim_data['policy_id'], claim_data['claim_id'],
                claim_data['event_type'], claim_data.get('event_description', ''),
                claim_data['claim_amount'], claim_data.get('approved_amount', 0),
                claim_data['status']
            ))
            conn.commit()
    
    # ============ 现金流系统方法 ============
    
    def save_cashflow_record(self, session_id: str, month: int, category: str,
                            item_type: str, item_name: str, amount: int, is_income: bool) -> None:
        """保存现金流记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cashflow_records (session_id, month, category, item_type, item_name, amount, is_income)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, month, category, item_type, item_name, amount, int(is_income)))
            conn.commit()
    
    def save_monthly_cashflow(self, session_id: str, month: int, total_income: int,
                             total_expense: int, net_cashflow: int, 
                             saving_rate: float, cash_balance: int) -> None:
        """保存月度现金流汇总"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO monthly_cashflow (session_id, month, total_income, total_expense, net_cashflow, saving_rate, cash_balance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id, month) DO UPDATE SET
                    total_income = excluded.total_income,
                    total_expense = excluded.total_expense,
                    net_cashflow = excluded.net_cashflow,
                    saving_rate = excluded.saving_rate,
                    cash_balance = excluded.cash_balance
            ''', (session_id, month, total_income, total_expense, net_cashflow, saving_rate, cash_balance))
            conn.commit()
    
    def get_cashflow_history(self, session_id: str, months: int = 12) -> List[Dict]:
        """获取现金流历史"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT month, total_income, total_expense, net_cashflow, saving_rate, cash_balance
                FROM monthly_cashflow
                WHERE session_id = ?
                ORDER BY month DESC
                LIMIT ?
            ''', (session_id, months))
            return [
                {
                    'month': r[0], 'total_income': r[1], 'total_expense': r[2],
                    'net_cashflow': r[3], 'saving_rate': r[4], 'cash_balance': r[5]
                }
                for r in cursor.fetchall()
            ]
    
    # ============ 信用分系统方法 ============
    
    def save_credit_score(self, session_id: str, month: int, 
                         credit_score: int, change_reason: str = None) -> None:
        """保存信用分记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO credit_history (session_id, month, credit_score, change_reason)
                VALUES (?, ?, ?, ?)
            ''', (session_id, month, credit_score, change_reason))
            conn.commit()
    
    def get_credit_history(self, session_id: str, months: int = 24) -> List[Dict]:
        """获取信用分历史"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT month, credit_score, change_reason, created_at
                FROM credit_history
                WHERE session_id = ?
                ORDER BY month DESC
                LIMIT ?
            ''', (session_id, months))
            return [
                {'month': r[0], 'credit_score': r[1], 'change_reason': r[2], 'created_at': r[3]}
                for r in cursor.fetchall()
            ]
    
    def get_latest_credit_score(self, session_id: str) -> int:
        """获取最新信用分"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT credit_score FROM credit_history
                WHERE session_id = ?
                ORDER BY month DESC LIMIT 1
            ''', (session_id,))
            row = cursor.fetchone()
            return row[0] if row else 650  # 默认信用分
    
    # ============ 成就系统方法 ============
    
    def save_achievement_unlock(self, session_id: str, achievement_data: Dict) -> None:
        """保存解锁的成就"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO achievements_unlocked (
                    session_id, achievement_id, achievement_name, rarity,
                    reward_coins, reward_exp, reward_title, unlocked_month
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id, achievement_id) DO NOTHING
            ''', (
                session_id, achievement_data['achievement_id'],
                achievement_data['achievement_name'], achievement_data['rarity'],
                achievement_data.get('reward_coins', 0), achievement_data.get('reward_exp', 0),
                achievement_data.get('reward_title'), achievement_data['unlocked_month']
            ))
            conn.commit()
    
    def get_unlocked_achievements(self, session_id: str) -> List[Dict]:
        """获取已解锁成就列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT achievement_id, achievement_name, rarity, reward_coins,
                       reward_exp, reward_title, unlocked_month, created_at
                FROM achievements_unlocked
                WHERE session_id = ?
                ORDER BY created_at DESC
            ''', (session_id,))
            return [
                {
                    'achievement_id': r[0], 'achievement_name': r[1], 'rarity': r[2],
                    'reward_coins': r[3], 'reward_exp': r[4], 'reward_title': r[5],
                    'unlocked_month': r[6], 'created_at': r[7]
                }
                for r in cursor.fetchall()
            ]
    
    def get_achievement_stats(self, session_id: str) -> Dict:
        """获取成就统计"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*), SUM(reward_coins), SUM(reward_exp)
                FROM achievements_unlocked
                WHERE session_id = ?
            ''', (session_id,))
            row = cursor.fetchone()
            return {
                'unlocked_count': row[0] or 0,
                'total_coins': row[1] or 0,
                'total_exp': row[2] or 0
            }
    
    # ============ 经济状态方法 ============
    
    def save_economic_state(self, month: int, state_data: Dict) -> None:
        """保存宏观经济状态"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO economic_state (
                    month, gdp_growth, inflation, interest_rate, unemployment,
                    cpi_index, house_price_index, stock_index, economic_phase, active_event
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(month) DO UPDATE SET
                    gdp_growth = excluded.gdp_growth,
                    inflation = excluded.inflation,
                    interest_rate = excluded.interest_rate,
                    unemployment = excluded.unemployment,
                    cpi_index = excluded.cpi_index,
                    house_price_index = excluded.house_price_index,
                    stock_index = excluded.stock_index,
                    economic_phase = excluded.economic_phase,
                    active_event = excluded.active_event
            ''', (
                month, state_data['gdp_growth'], state_data['inflation'],
                state_data['interest_rate'], state_data['unemployment'],
                state_data['cpi_index'], state_data['house_price_index'],
                state_data['stock_index'], state_data['economic_phase'],
                state_data.get('active_event')
            ))
            conn.commit()
    
    def get_economic_history(self, months: int = 36) -> List[Dict]:
        """获取经济历史"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT month, gdp_growth, inflation, interest_rate, unemployment,
                       cpi_index, house_price_index, stock_index, economic_phase, active_event
                FROM economic_state
                ORDER BY month DESC
                LIMIT ?
            ''', (months,))
            return [
                {
                    'month': r[0], 'gdp_growth': r[1], 'inflation': r[2],
                    'interest_rate': r[3], 'unemployment': r[4], 'cpi_index': r[5],
                    'house_price_index': r[6], 'stock_index': r[7],
                    'economic_phase': r[8], 'active_event': r[9]
                }
                for r in cursor.fetchall()
            ]
    
    # ============ 行为洞察系统方法 ============
    
    def log_behavior(self, session_id: str, month: int, action_type: str,
                    action_category: str, amount: float = None, risk_score: float = None,
                    rationality_score: float = None, market_condition: str = None,
                    decision_context: str = None) -> None:
        """记录用户行为日志"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO behavior_logs (
                    session_id, month, action_type, action_category, amount,
                    risk_score, rationality_score, market_condition, decision_context
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, month, action_type, action_category, amount,
                  risk_score, rationality_score, market_condition, decision_context))
            conn.commit()
    
    def get_behavior_logs(self, session_id: str, months: int = None) -> List[Dict]:
        """获取行为日志"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if months:
                cursor.execute('''
                    SELECT month, action_type, action_category, amount, risk_score,
                           rationality_score, market_condition, decision_context, created_at
                    FROM behavior_logs
                    WHERE session_id = ?
                    ORDER BY month DESC
                    LIMIT ?
                ''', (session_id, months * 10))  # 假设每月约10条记录
            else:
                cursor.execute('''
                    SELECT month, action_type, action_category, amount, risk_score,
                           rationality_score, market_condition, decision_context, created_at
                    FROM behavior_logs
                    WHERE session_id = ?
                    ORDER BY month DESC
                ''', (session_id,))
            return [
                {
                    'month': r[0], 'action_type': r[1], 'action_category': r[2],
                    'amount': r[3], 'risk_score': r[4], 'rationality_score': r[5],
                    'market_condition': r[6], 'decision_context': r[7], 'created_at': r[8]
                }
                for r in cursor.fetchall()
            ]
    
    def update_behavior_profile(self, session_id: str, profile_data: Dict) -> None:
        """更新行为画像"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO behavior_profiles (
                    session_id, risk_preference, decision_style, loss_aversion,
                    overconfidence, herding_tendency, planning_ability,
                    action_count, avg_risk_score, avg_rationality, last_updated_month
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    risk_preference = excluded.risk_preference,
                    decision_style = excluded.decision_style,
                    loss_aversion = excluded.loss_aversion,
                    overconfidence = excluded.overconfidence,
                    herding_tendency = excluded.herding_tendency,
                    planning_ability = excluded.planning_ability,
                    action_count = excluded.action_count,
                    avg_risk_score = excluded.avg_risk_score,
                    avg_rationality = excluded.avg_rationality,
                    last_updated_month = excluded.last_updated_month,
                    updated_at = CURRENT_TIMESTAMP
            ''', (
                session_id, profile_data['risk_preference'], profile_data['decision_style'],
                profile_data['loss_aversion'], profile_data['overconfidence'],
                profile_data['herding_tendency'], profile_data['planning_ability'],
                profile_data['action_count'], profile_data['avg_risk_score'],
                profile_data['avg_rationality'], profile_data['last_updated_month']
            ))
            conn.commit()
    
    def get_behavior_profile(self, session_id: str) -> Dict:
        """获取行为画像"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT risk_preference, decision_style, loss_aversion, overconfidence,
                       herding_tendency, planning_ability, action_count, avg_risk_score,
                       avg_rationality, last_updated_month, updated_at
                FROM behavior_profiles
                WHERE session_id = ?
            ''', (session_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'risk_preference': row[0], 'decision_style': row[1],
                    'loss_aversion': row[2], 'overconfidence': row[3],
                    'herding_tendency': row[4], 'planning_ability': row[5],
                    'action_count': row[6], 'avg_risk_score': row[7],
                    'avg_rationality': row[8], 'last_updated_month': row[9],
                    'updated_at': row[10]
                }
            return None
    
    def save_cohort_insight(self, insight_data: Dict) -> None:
        """保存群体洞察"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cohort_insights (
                    insight_type, insight_category, title, description,
                    data_source, sample_size, confidence_level, tags, generated_month
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight_data['insight_type'], insight_data['insight_category'],
                insight_data['title'], insight_data['description'],
                insight_data.get('data_source'), insight_data.get('sample_size'),
                insight_data.get('confidence_level'), insight_data.get('tags'),
                insight_data['generated_month']
            ))
            conn.commit()
    
    def get_cohort_insights(self, insight_type: str = None, limit: int = 20) -> List[Dict]:
        """获取群体洞察列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if insight_type:
                cursor.execute('''
                    SELECT id, insight_type, insight_category, title, description,
                           data_source, sample_size, confidence_level, tags, generated_month, created_at
                    FROM cohort_insights
                    WHERE insight_type = ?
                    ORDER BY generated_month DESC
                    LIMIT ?
                ''', (insight_type, limit))
            else:
                cursor.execute('''
                    SELECT id, insight_type, insight_category, title, description,
                           data_source, sample_size, confidence_level, tags, generated_month, created_at
                    FROM cohort_insights
                    ORDER BY generated_month DESC
                    LIMIT ?
                ''', (limit,))
            return [
                {
                    'id': r[0], 'insight_type': r[1], 'insight_category': r[2],
                    'title': r[3], 'description': r[4], 'data_source': r[5],
                    'sample_size': r[6], 'confidence_level': r[7], 'tags': r[8],
                    'generated_month': r[9], 'created_at': r[10]
                }
                for r in cursor.fetchall()
            ]


# 全局数据库实例
db = FinAIDatabase()