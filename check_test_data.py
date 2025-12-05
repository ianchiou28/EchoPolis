"""检查测试数据状态"""
import sqlite3

conn = sqlite3.connect('echopolis.db')
c = conn.cursor()

print("=" * 60)
print("测试账号用户表:")
print("=" * 60)
c.execute('SELECT session_id, username, name FROM users WHERE username LIKE "test_%"')
for r in c.fetchall():
    print(f"  session: {r[0]}, user: {r[1]}, name: {r[2]}")

print("\n" + "=" * 60)
print("行为日志统计 (按 session_id):")
print("=" * 60)
c.execute('SELECT session_id, COUNT(*) FROM behavior_logs GROUP BY session_id')
for r in c.fetchall():
    print(f"  session: {r[0]}, logs: {r[1]}")

print("\n" + "=" * 60)
print("行为画像表:")
print("=" * 60)
c.execute('SELECT session_id, risk_preference, decision_style, action_count FROM behavior_profiles')
for r in c.fetchall():
    print(f"  session: {r[0]}, risk: {r[1]}, style: {r[2]}, actions: {r[3]}")

print("\n" + "=" * 60)
print("群体洞察表:")
print("=" * 60)
c.execute('SELECT COUNT(*) FROM cohort_insights')
count = c.fetchone()[0]
print(f"  共 {count} 条群体洞察")

conn.close()
