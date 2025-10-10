#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为游戏中的avatar添加测试数据
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from core.database.database import db

def add_game_data():
    """为游戏avatar添加测试数据"""
    print("[GAME] 为游戏avatar添加测试数据...")
    
    # 常见的游戏avatar名称
    avatars = [
        ("Alex", "INTP"),
        ("Emma", "ENTJ"), 
        ("John", "ISFJ"),
        ("Sarah", "ESFP"),
        ("testuser", "INTP")  # 保留原测试用户
    ]
    
    for name, mbti in avatars:
        print(f"\n处理avatar: {name} ({mbti})")
        
        # 1. 创建账户（如果不存在）
        success = db.create_account(name, "password123")
        if success:
            print(f"[OK] 账户创建成功: {name}")
        else:
            print(f"[INFO] 账户已存在: {name}")
        
        # 2. 保存用户信息
        db.save_user(name, f"session_{name}", name, mbti, "书香门第", 1000000)
        print(f"[OK] 用户信息保存成功: {name}")
        
        # 3. 添加投资记录
        investments = [
            ("投资基金", 600000, "MONTHLY", 30, 3616, 0.08, 1),
            ("股票投资", 200000, "LONG_TERM", 18, 0, 0.12, 1),
            ("债券投资", 100000, "SHORT_TERM", 6, 800, 0.05, 2)
        ]
        
        for inv_name, amount, inv_type, months, monthly_return, rate, round_num in investments:
            db.save_investment(name, f"session_{name}", inv_name, amount, inv_type, months, monthly_return, rate, round_num)
            print(f"[OK] 投资记录添加: {inv_name}")
        
        # 4. 添加交易记录
        transactions = [
            (1, "投资投资基金", -600000),
            (1, "投资股票投资", -200000),
            (2, "投资债券投资", -100000),
            (3, "投资基金月收益", 3616),
            (4, "投资基金月收益", 3616),
            (4, "债券投资收益", 800),
            (5, "投资基金月收益", 3616),
            (5, "工作收入", 8000),
            (5, "生活支出", -3000)
        ]
        
        for round_num, desc, amount in transactions:
            db.save_transaction(name, f"session_{name}", round_num, desc, amount)
        
        print(f"[OK] 交易记录添加完成: {len(transactions)}条")
    
    print("\n[DONE] 游戏数据添加完成!")

if __name__ == "__main__":
    add_game_data()