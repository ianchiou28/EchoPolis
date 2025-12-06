"""
初始化股票数据库脚本
从 Longbridge API 获取所有股票的历史K线数据并存入 stock.db
"""
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.systems.longbridge_client import (
    longbridge_client, 
    STOCK_MAPPING, 
    fetch_all_klines,
    init_stock_database
)


def main():
    print("=" * 60)
    print("EchoPolis 股票数据库初始化工具")
    print("=" * 60)
    print()
    
    print(f"数据库路径: {longbridge_client.db_path}")
    print(f"股票数量: {len(STOCK_MAPPING)}")
    print()
    
    # 显示股票映射关系
    print("股票映射关系:")
    print("-" * 60)
    for game_code, mapping in STOCK_MAPPING.items():
        real_symbol = mapping[0]
        real_name = mapping[3] if len(mapping) > 3 else real_symbol
        print(f"  {game_code} -> {real_name} ({real_symbol})")
    print()
    
    # 检查现有数据
    counts = longbridge_client.get_all_kline_counts()
    print("现有K线数据:")
    print("-" * 60)
    for game_code in STOCK_MAPPING.keys():
        count = counts.get(game_code, 0)
        status = "✓" if count >= 200 else "✗"
        print(f"  {game_code}: {count:>4} 条 {status}")
    print()
    
    total = sum(counts.values())
    print(f"总计: {total} 条K线数据")
    print()
    
    # 询问是否获取数据
    if total < len(STOCK_MAPPING) * 200:
        response = input("数据不足，是否从 Longbridge 获取历史数据? (y/n): ")
        if response.lower() == 'y':
            print()
            print("开始获取数据...")
            print("-" * 60)
            results = fetch_all_klines(365)
            
            print()
            print("获取结果:")
            print("-" * 60)
            for game_code, count in results.items():
                status = "✓" if count > 0 else "✗"
                print(f"  {game_code}: {count:>4} 条 {status}")
            
            print()
            print(f"总计获取: {sum(results.values())} 条K线数据")
    else:
        print("数据库已有足够数据，无需更新。")
    
    print()
    print("完成!")


if __name__ == "__main__":
    main()
