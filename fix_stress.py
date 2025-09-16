import re

# 读取文件
with open('web_minimal.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有stress引用为energy
content = content.replace('"stress": avatar_data["stress"]', '"energy": avatar_data.get("energy", 100)')

# 写回文件
with open('web_minimal.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all stress references to energy")