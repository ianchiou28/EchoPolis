import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
ax.set_xlim(-6, 6)
ax.set_ylim(-4, 4)
ax.set_aspect('equal')
ax.axis('off')

# 颜色配置
bg_color = '#1a1a2e'
primary_color = '#16213e'
accent_color = '#0f3460'
text_color = '#eee'
highlight_color = '#e94560'
arrow_color = '#00d4ff'

fig.patch.set_facecolor(bg_color)

# 中心圆形 - AI化身
center = Circle((0, 0), 1, facecolor=primary_color, edgecolor=arrow_color, linewidth=3)
ax.add_patch(center)

# 中心文字
ax.text(0, 0.2, 'AI化身', fontsize=14, ha='center', va='center', color=text_color, weight='bold')
ax.text(0, -0.3, 'Digital Twin', fontsize=10, ha='center', va='center', color=arrow_color)

# 四个主要节点的位置
positions = {
    'create': (-3.5, 2.5),      # 左上 - 创建化身
    'interact': (3.5, 2.5),     # 右上 - 互动决策  
    'evolve': (3.5, -2.5),      # 右下 - 演化成长
    'observe': (-3.5, -2.5)     # 左下 - 观察分析
}

# 节点内容
nodes = {
    'create': {
        'title': '1. 创建化身',
        'subtitle': 'Create Avatar',
        'items': ['选择MBTI人格', '命运轮盘分配', '初始资产设定'],
        'color': accent_color
    },
    'interact': {
        'title': '2. 互动决策', 
        'subtitle': 'Interact & Decide',
        'items': ['生成决策情况', '发送意识回响', 'AI智能决策'],
        'color': highlight_color
    },
    'evolve': {
        'title': '3. 演化成长',
        'subtitle': 'Evolve & Grow',
        'items': ['资产状态更新', '信任度调整', '经验积累'],
        'color': accent_color
    },
    'observe': {
        'title': '4. 观察分析',
        'subtitle': 'Observe & Analyze',
        'items': ['查看财务状况', '分析决策效果', '评估AI状态'],
        'color': accent_color
    }
}

# 绘制节点
for key, pos in positions.items():
    node = nodes[key]
    
    # 节点框
    if key == 'interact':  # 突出显示互动节点
        box = FancyBboxPatch((pos[0]-1.2, pos[1]-0.8), 2.4, 1.6, 
                           boxstyle="round,pad=0.1", 
                           facecolor=node['color'], 
                           edgecolor=arrow_color, 
                           linewidth=2)
    else:
        box = FancyBboxPatch((pos[0]-1.2, pos[1]-0.8), 2.4, 1.6, 
                           boxstyle="round,pad=0.1", 
                           facecolor=node['color'], 
                           edgecolor=text_color, 
                           linewidth=1)
    ax.add_patch(box)
    
    # 标题
    ax.text(pos[0], pos[1]+0.4, node['title'], fontsize=11, ha='center', va='center', 
            color=text_color, weight='bold')
    ax.text(pos[0], pos[1]+0.1, node['subtitle'], fontsize=8, ha='center', va='center', 
            color=arrow_color)
    
    # 描述项目
    for i, item in enumerate(node['items']):
        ax.text(pos[0], pos[1]-0.2-i*0.15, f"- {item}", fontsize=7, ha='center', va='center', 
                color=text_color)

# 绘制循环箭头
arrow_style = "Simple, tail_width=0.5, head_width=4, head_length=8"
kw = dict(arrowstyle=arrow_style, color=arrow_color, linewidth=2)

# 创建 -> 互动
arrow1 = FancyArrowPatch((-2.3, 2.8), (2.3, 2.8), 
                        connectionstyle="arc3,rad=0.2", **kw)
ax.add_patch(arrow1)

# 互动 -> 演化  
arrow2 = FancyArrowPatch((3.8, 1.7), (3.8, -1.7), 
                        connectionstyle="arc3,rad=0.2", **kw)
ax.add_patch(arrow2)

# 演化 -> 观察
arrow3 = FancyArrowPatch((2.3, -2.8), (-2.3, -2.8), 
                        connectionstyle="arc3,rad=0.2", **kw)
ax.add_patch(arrow3)

# 观察 -> 创建
arrow4 = FancyArrowPatch((-3.8, -1.7), (-3.8, 1.7), 
                        connectionstyle="arc3,rad=0.2", **kw)
ax.add_patch(arrow4)

# 标题
ax.text(0, 3.5, 'Echopolis 核心游戏循环', fontsize=16, ha='center', va='center', 
        color=text_color, weight='bold')
ax.text(0, -3.5, '回声都市 - AI驱动的金融模拟器', fontsize=11, ha='center', va='center', 
        color=arrow_color)

plt.tight_layout()
plt.savefig('echopolis_flowchart.png', dpi=300, bbox_inches='tight', 
            facecolor=bg_color, edgecolor='none')
plt.show()

print("流程图已生成: echopolis_flowchart.png")