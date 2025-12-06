import sqlite3

conn = sqlite3.connect('echopolis.db')
cursor = conn.cursor()

# 检查 users 表是否已有 tags 列
cursor.execute('PRAGMA table_info(users)')
users_cols = [r[1] for r in cursor.fetchall()]
print(f"Users columns: {users_cols}")

if 'tags' not in users_cols:
    cursor.execute('ALTER TABLE users ADD COLUMN tags TEXT DEFAULT ""')
    print("Added tags column to users")
else:
    print("tags column already exists in users")

# 检查 behavior_profiles 表是否已有 auto_tags 列
cursor.execute('PRAGMA table_info(behavior_profiles)')
profiles_cols = [r[1] for r in cursor.fetchall()]
print(f"Behavior profiles columns: {profiles_cols}")

if 'auto_tags' not in profiles_cols:
    cursor.execute('ALTER TABLE behavior_profiles ADD COLUMN auto_tags TEXT DEFAULT ""')
    print("Added auto_tags column to behavior_profiles")
else:
    print("auto_tags column already exists in behavior_profiles")

conn.commit()
conn.close()
print("Done!")
