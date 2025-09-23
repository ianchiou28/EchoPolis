import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(-7, 7)
ax.set_ylim(-5, 5)
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
center = Circle((0, 0), 1.2, facecolor=primary_color, edgecolor=arrow_color, linewidth=3)
ax.add_patch(center)

# 中心文字
ax.text(0, 0.2, 'AI化身', fontsize=16, ha='center', va='center', color=text_color, weight='bold')
ax.text(0, -0.2, 'Digital Twin', fontsize=10, ha='center', va='center', color=arrow_color)
ax.text(0, -0.5, '🤖', fontsize=24, ha='center', va='center')

# 四个主要节点的位置
positions = {
    'create': (-4, 3),      # 左上 - 创建化身
    'interact': (4, 3),     # 右上 - 互动决策  
    'evolve': (4, -3),      # 右下 - 演化成长
    'observe': (-4, -3)     # 左下 - 观察分析
}

# 节点内容
nodes = {
    'create': {
        'title': '1. 创建化身\nCreate Avatar',
        'items': ['> 选择MBTI人格', '> 命运轮盘分配', '> 初始资产设定', '> AI个性生成'],
        'icon': '🎭',
        'color': accent_color
    },
    'interact': {
        'title': '2. 互动决策\nInteract & Decide', 
        'items': ['> 生成决策情况', '> 发送意识回响', '> AI智能决策', '> 影响权重计算'],
        'icon': '💭',
        'color': highlight_color
    },
    'evolve': {
        'title': '3. 演化成长\nEvolve & Grow',
        'items': ['> 资产状态更新', '> 信任度调整', '> 人格特质强化', '> 经验积累'],
        'icon': '📈',
        'color': accent_color
    },
    'observe': {
        'title': '4. 观察分析\nObserve & Analyze',
        'items': ['> 查看财务状况', '> 分析决策效果', '> 评估AI状态', '> 准备下轮干预'],
        'icon': '👁️',
        'color': accent_color
    }
}

# 绘制节点
for key, pos in positions.items():
    node = nodes[key]
    
    # 节点框
    if key == 'interact':  # 突出显示互动节点
        box = FancyBboxPatch((pos[0]-1.5, pos[1]-1), 3, 2, 
                           boxstyle="round,pad=0.1", 
                           facecolor=node['color'], 
                           edgecolor=arrow_color, 
                           linewidth=2)
    else:
        box = FancyBboxPatch((pos[0]-1.5, pos[1]-1), 3, 2, 
                           boxstyle="round,pad=0.1", 
                           facecolor=node['color'], 
                           edgecolor=text_color, 
                           linewidth=1)
    ax.add_patch(box)
    
    # 图标
    ax.text(pos[0], pos[1]+0.6, node['icon'], fontsize=20, ha='center', va='center')
    
    # 标题
    ax.text(pos[0], pos[1]+0.2, node['title'], fontsize=11, ha='center', va='center', 
            color=text_color, weight='bold')
    
    # 描述项目
    for i, item in enumerate(node['items']):
        ax.text(pos[0], pos[1]-0.2-i*0.2, item, fontsize=8, ha='center', va='center', 
                color=text_color)

# 绘制循环箭头
arrow_style = "Simple, tail_width=0.5, head_width=4, head_length=8"
kw = dict(arrowstyle=arrow_style, color=arrow_color, linewidth=2)

# 创建 -> 互动
arrow1 = FancyArrowPatch((-2.5, 3.5), (2.5, 3.5), 
                        connectionstyle="arc3,rad=0.3", **kw)
ax.add_patch(arrow1)

# 互动 -> 演化  
arrow2 = FancyArrowPatch((4.5, 2), (4.5, -2), 
                        connectionstyle="arc3,rad=0.3", **kw)
ax.add_patch(arrow2)

# 演化 -> 观察
arrow3 = FancyArrowPatch((2.5, -3.5), (-2.5, -3.5), 
                        connectionstyle="arc3,rad=0.3", **kw)
ax.add_patch(arrow3)

# 观察 -> 创建
arrow4 = FancyArrowPatch((-4.5, -2), (-4.5, 2), 
                        connectionstyle="arc3,rad=0.3", **kw)
ax.add_patch(arrow4)

# 添加箭头标签
ax.text(0, 4, '开始游戏', fontsize=9, ha='center', va='center', color=arrow_color)
ax.text(5.2, 0, '执行决策', fontsize=9, ha='center', va='center', color=arrow_color, rotation=-90)
ax.text(0, -4, '状态更新', fontsize=9, ha='center', va='center', color=arrow_color)
ax.text(-5.2, 0, '新回合', fontsize=9, ha='center', va='center', color=arrow_color, rotation=90)

# 标题
ax.text(0, 4.5, 'Echopolis 核心游戏循环', fontsize=18, ha='center', va='center', 
        color=text_color, weight='bold')
ax.text(0, -4.5, '🌆 回声都市 - AI驱动的金融模拟器', fontsize=12, ha='center', va='center', 
        color=arrow_color)

# 添加关键机制说明
mechanism_text = [
    "MBTI人格系统 - 16种独特决策模式",
    "命运轮盘 - 8种出身背景影响起点", 
    "意识回响 - 自然语言影响AI决策",
    "DeepSeek AI - 智能化身自主思考"
]

for i, text in enumerate(mechanism_text):
    ax.text(-6.5, 2-i*0.4, text, fontsize=9, ha='left', va='center', color=text_color)

plt.tight_layout()
plt.savefig('echopolis_flowchart.png', dpi=300, bbox_inches='tight', 
            facecolor=bg_color, edgecolor='none')
plt.show()

print("✅ Echopolis循环流程图已生成: echopolis_flowchart.png")