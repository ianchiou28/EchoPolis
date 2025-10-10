#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查用户数据
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from core.database.database import db

def check_user():
    """检查用户数据"""
    print("[CHECK] 检查用户数据...")
    
    # 检查所有账户
    import sqlite3
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        print("\n=== 账户表 ===")
        cursor.execute("SELECT username FROM accounts")
        accounts = cursor.fetchall()
        print(f"账户数量: {len(accounts)}")
        for account in accounts:
            print(f"  - {account[0]}")
        
        print("\n=== 用户表 ===")
        cursor.execute("SELECT username, name, mbti, fate, credits FROM users")
        users = cursor.fetchall()
        print(f"用户数量: {len(users)}")
        for user in users:
            print(f"  - {user[0]}: {user[1]} ({user[2]}) - {user[3]} - {user[4]:,} CP")
        
        # 检查特定用户
        print("\n=== 检查用户 'ian' ===")
        cursor.execute("SELECT * FROM accounts WHERE username = ?", ("ian",))
        account = cursor.fetchone()
        if account:
            print(f"账户存在: {account}")
        else:
            print("账户不存在")
        
        cursor.execute("SELECT * FROM users WHERE username = ?", ("ian",))
        user = cursor.fetchone()
        if user:
            print(f"用户记录存在: {user}")
        else:
            print("用户记录不存在")

if __name__ == "__main__":
    check_user()