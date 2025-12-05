"""
EchoPolis 实时同步系统
- 游戏时间与现实时间同步 (1小时=1月)
- 每小时自动抓取 Longbridge 股票数据
- 自动触发月度事件
"""
import os
import sys
import time
import threading
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def get_project_root() -> str:
    """获取项目根目录"""
    return project_root


class RealtimeSyncSystem:
    """
    实时同步系统
    
    时间流速：1现实小时 = 1游戏月
    每小时整点：
      1. 抓取 Longbridge 股票数据
      2. 更新所有活跃会话的游戏时间
      3. 触发月度事件和收益结算
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(get_project_root(), "game.db")
        self.stock_db_path = os.path.join(get_project_root(), "stock.db")
        
        self._running = False
        self._sync_thread: Optional[threading.Thread] = None
        self._last_hour = -1
        self._last_sync_time: Optional[datetime] = None
        
        # 回调函数
        self._on_hour_change_callbacks: List[Callable[[int], None]] = []
        self._on_data_sync_callbacks: List[Callable[[Dict], None]] = []
        
        # 配置
        self.sync_interval = 60  # 检查间隔（秒）
        self.hours_per_month = 1  # 1小时 = 1游戏月
        
        # 初始化数据库
        self._init_db()
        
        print(f"[RealtimeSync] Initialized with db: {self.db_path}")
    
    def _init_db(self):
        """初始化同步状态表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 同步状态表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_status (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_sync_time TIMESTAMP,
                    last_sync_hour INTEGER,
                    total_syncs INTEGER DEFAULT 0,
                    last_stock_sync TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 确保有一条记录
            cursor.execute('SELECT id FROM sync_status WHERE id = 1')
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO sync_status (id, last_sync_time, last_sync_hour, total_syncs)
                    VALUES (1, NULL, -1, 0)
                ''')
            
            # 会话实时状态表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_realtime_state (
                    session_id TEXT PRIMARY KEY,
                    start_real_time TIMESTAMP NOT NULL,
                    current_game_month INTEGER DEFAULT 1,
                    last_update_hour INTEGER DEFAULT -1,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def register_hour_change_callback(self, callback: Callable[[int], None]):
        """注册小时变化回调"""
        self._on_hour_change_callbacks.append(callback)
    
    def register_data_sync_callback(self, callback: Callable[[Dict], None]):
        """注册数据同步回调"""
        self._on_data_sync_callbacks.append(callback)
    
    def get_current_game_time(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话的当前游戏时间
        
        Returns:
            {
                "real_time": "2025-12-05 14:30:00",
                "game_month": 14,
                "game_year": 2,
                "next_month_in": 1800,  # 秒
                "progress": 0.5  # 当前小时进度
            }
        """
        now = datetime.now()
        current_hour = now.hour
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT start_real_time, current_game_month, is_active
                FROM session_realtime_state
                WHERE session_id = ?
            ''', (session_id,))
            row = cursor.fetchone()
            
            if row:
                start_time = datetime.fromisoformat(row[0]) if row[0] else now
                game_month = row[1] or 1
                is_active = row[2]
            else:
                # 新会话，初始化状态
                start_time = now
                game_month = 1
                is_active = 1
                cursor.execute('''
                    INSERT INTO session_realtime_state 
                    (session_id, start_real_time, current_game_month, last_update_hour, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, now.isoformat(), game_month, current_hour, is_active))
                conn.commit()
        
        # 计算下一个整点的剩余时间
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        seconds_to_next = (next_hour - now).total_seconds()
        
        # 当前小时进度
        progress = now.minute / 60 + now.second / 3600
        
        return {
            "real_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "game_month": game_month,
            "game_year": (game_month - 1) // 12 + 1,
            "month_in_year": ((game_month - 1) % 12) + 1,
            "next_month_in": int(seconds_to_next),
            "progress": round(progress, 2),
            "is_active": is_active == 1
        }
    
    def _sync_stock_data(self) -> Dict[str, Any]:
        """同步股票数据"""
        result = {
            "success": False,
            "stocks_updated": 0,
            "error": None
        }
        
        try:
            from core.systems.longbridge_client import longbridge_client, sync_all_prices
            
            print("[RealtimeSync] Syncing stock data from Longbridge...")
            
            # 同步所有股票价格
            prices = sync_all_prices()
            result["stocks_updated"] = len(prices)
            result["success"] = True
            
            # 更新同步状态
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_status 
                    SET last_stock_sync = ?, updated_at = ?
                    WHERE id = 1
                ''', (datetime.now().isoformat(), datetime.now().isoformat()))
                conn.commit()
            
            print(f"[RealtimeSync] Stock sync complete: {len(prices)} stocks updated")
            
        except ImportError as e:
            result["error"] = f"Longbridge client not available: {e}"
            print(f"[RealtimeSync] {result['error']}")
        except Exception as e:
            result["error"] = str(e)
            print(f"[RealtimeSync] Stock sync error: {e}")
        
        return result
    
    def _advance_all_sessions(self, current_hour: int) -> Dict[str, Any]:
        """推进所有活跃会话的游戏时间"""
        result = {
            "sessions_updated": 0,
            "errors": []
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取所有活跃会话
                cursor.execute('''
                    SELECT session_id, current_game_month, last_update_hour
                    FROM session_realtime_state
                    WHERE is_active = 1
                ''')
                sessions = cursor.fetchall()
                
                for session_id, game_month, last_hour in sessions:
                    # 检查是否需要推进（避免重复推进）
                    if last_hour != current_hour:
                        new_month = game_month + 1
                        cursor.execute('''
                            UPDATE session_realtime_state
                            SET current_game_month = ?,
                                last_update_hour = ?,
                                updated_at = ?
                            WHERE session_id = ?
                        ''', (new_month, current_hour, datetime.now().isoformat(), session_id))
                        
                        # 同时更新 users 表中的 current_month (如果存在相关字段)
                        try:
                            cursor.execute('''
                                UPDATE sessions 
                                SET current_month = ?
                                WHERE session_id = ?
                            ''', (new_month, session_id))
                        except:
                            pass  # sessions 表可能没有 current_month 字段
                        
                        result["sessions_updated"] += 1
                        print(f"[RealtimeSync] Session {session_id[:8]}... advanced to month {new_month}")
                
                conn.commit()
                
        except Exception as e:
            result["errors"].append(str(e))
            print(f"[RealtimeSync] Error advancing sessions: {e}")
        
        return result
    
    def _check_and_sync(self):
        """检查并执行同步"""
        now = datetime.now()
        current_hour = now.hour
        
        # 检查是否到了新的整点
        if current_hour != self._last_hour:
            print(f"\n[RealtimeSync] === Hour changed: {self._last_hour} -> {current_hour} ===")
            
            # 1. 同步股票数据
            stock_result = self._sync_stock_data()
            
            # 2. 推进所有会话
            session_result = self._advance_all_sessions(current_hour)
            
            # 3. 更新同步状态
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sync_status
                    SET last_sync_time = ?,
                        last_sync_hour = ?,
                        total_syncs = total_syncs + 1,
                        updated_at = ?
                    WHERE id = 1
                ''', (now.isoformat(), current_hour, now.isoformat()))
                conn.commit()
            
            self._last_hour = current_hour
            self._last_sync_time = now
            
            # 4. 触发回调
            sync_data = {
                "hour": current_hour,
                "stock_sync": stock_result,
                "session_sync": session_result,
                "timestamp": now.isoformat()
            }
            
            for callback in self._on_hour_change_callbacks:
                try:
                    callback(current_hour)
                except Exception as e:
                    print(f"[RealtimeSync] Hour callback error: {e}")
            
            for callback in self._on_data_sync_callbacks:
                try:
                    callback(sync_data)
                except Exception as e:
                    print(f"[RealtimeSync] Data sync callback error: {e}")
            
            print(f"[RealtimeSync] Sync complete: {stock_result['stocks_updated']} stocks, "
                  f"{session_result['sessions_updated']} sessions updated")
    
    def _sync_loop(self):
        """同步主循环"""
        print("[RealtimeSync] Sync loop started")
        
        while self._running:
            try:
                self._check_and_sync()
            except Exception as e:
                print(f"[RealtimeSync] Sync loop error: {e}")
            
            # 等待下一次检查
            time.sleep(self.sync_interval)
        
        print("[RealtimeSync] Sync loop stopped")
    
    def start(self):
        """启动同步系统"""
        if self._running:
            print("[RealtimeSync] Already running")
            return
        
        self._running = True
        self._last_hour = datetime.now().hour
        
        # 启动时立即同步一次
        print("[RealtimeSync] Starting realtime sync system...")
        self._sync_stock_data()
        
        # 启动后台线程
        self._sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._sync_thread.start()
        
        print("[RealtimeSync] Realtime sync system started")
        print(f"[RealtimeSync] Time flow: 1 hour = 1 game month")
        print(f"[RealtimeSync] Stock data sync: Every hour")
    
    def stop(self):
        """停止同步系统"""
        if not self._running:
            return
        
        self._running = False
        if self._sync_thread:
            self._sync_thread.join(timeout=5)
        
        print("[RealtimeSync] Realtime sync system stopped")
    
    def force_sync(self) -> Dict[str, Any]:
        """强制立即同步"""
        print("[RealtimeSync] Force sync triggered")
        
        stock_result = self._sync_stock_data()
        session_result = self._advance_all_sessions(datetime.now().hour)
        
        return {
            "stock_sync": stock_result,
            "session_sync": session_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sync_status WHERE id = 1')
            row = cursor.fetchone()
            
            if row:
                return {
                    "last_sync_time": row["last_sync_time"],
                    "last_sync_hour": row["last_sync_hour"],
                    "total_syncs": row["total_syncs"],
                    "last_stock_sync": row["last_stock_sync"],
                    "is_running": self._running,
                    "next_sync_in": self._get_seconds_to_next_hour()
                }
            
            return {"is_running": self._running}
    
    def _get_seconds_to_next_hour(self) -> int:
        """获取到下一个整点的秒数"""
        now = datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        return int((next_hour - now).total_seconds())
    
    def init_session_realtime(self, session_id: str) -> Dict[str, Any]:
        """初始化会话的实时状态"""
        now = datetime.now()
        current_hour = now.hour
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO session_realtime_state
                (session_id, start_real_time, current_game_month, last_update_hour, is_active)
                VALUES (?, ?, 1, ?, 1)
            ''', (session_id, now.isoformat(), current_hour))
            conn.commit()
        
        return self.get_current_game_time(session_id)
    
    def set_session_active(self, session_id: str, is_active: bool):
        """设置会话是否活跃"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE session_realtime_state
                SET is_active = ?, updated_at = ?
                WHERE session_id = ?
            ''', (1 if is_active else 0, datetime.now().isoformat(), session_id))
            conn.commit()


# 全局实例
realtime_sync = RealtimeSyncSystem()


def start_realtime_sync():
    """启动实时同步"""
    realtime_sync.start()


def stop_realtime_sync():
    """停止实时同步"""
    realtime_sync.stop()


def get_game_time(session_id: str) -> Dict[str, Any]:
    """获取游戏时间"""
    return realtime_sync.get_current_game_time(session_id)


def force_sync() -> Dict[str, Any]:
    """强制同步"""
    return realtime_sync.force_sync()


if __name__ == "__main__":
    # 测试
    print("Testing RealtimeSync System...")
    
    sync = RealtimeSyncSystem()
    
    # 测试获取游戏时间
    test_session = "test-session-001"
    game_time = sync.get_current_game_time(test_session)
    print(f"Game time: {json.dumps(game_time, indent=2)}")
    
    # 测试同步状态
    status = sync.get_sync_status()
    print(f"Sync status: {json.dumps(status, indent=2)}")
    
    # 启动同步（测试模式）
    sync.start()
    
    print("\nSync system running. Press Ctrl+C to stop...")
    try:
        while True:
            time.sleep(10)
            print(f"Status: {sync.get_sync_status()}")
    except KeyboardInterrupt:
        sync.stop()
        print("\nStopped.")
