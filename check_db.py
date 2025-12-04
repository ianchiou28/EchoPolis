import sqlite3

conn = sqlite3.connect('echopolis.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("所有表:", tables)

# 查看行为相关的表
behavior_tables = [t for t in tables if 'behavior' in t or 'cohort' in t]
print("\n行为洞察相关表:", behavior_tables)

# 查看表结构
for table in behavior_tables:
    print(f"\n{table} 表结构:")
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

conn.close()
