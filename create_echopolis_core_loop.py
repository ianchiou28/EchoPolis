import graphviz
import os
import codecs

# 设置中文字体，确保Graphviz能找到
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

# --- 设计参数 ---
# 颜色
BG_COLOR = "#1a2a3b"  # 深蓝灰色背景
NODE_COLOR = "#2a394d"
NODE_BORDER_COLOR = "#00aaff" # 亮蓝色
FONT_COLOR = "#ffffff" # 白色
ACCENT_COLOR_ORANGE = "#ff8c00" # 橙色

# 字体
FONT_NAME = "Microsoft YaHei"

# --- 创建有向图 ---
dot = graphviz.Digraph('Echopolis_Core_Loop', comment='The Core Loop of Echopolis Gameplay', encoding='utf-8')
dot.attr(
    'graph',
    bgcolor=BG_COLOR,
    label='The Core Loop: Echopolis Gameplay Cycle (核心循环：Echopolis玩法周期)',
    fontname=FONT_NAME,
    fontsize='24',
    fontcolor=FONT_COLOR,
    rankdir='TB', 
    splines='curved'
)

dot.attr('node', shape='box', style='rounded,filled', color=NODE_BORDER_COLOR, fillcolor=NODE_COLOR, fontname=FONT_NAME, fontcolor=FONT_COLOR, fontsize='16', labelloc='c')
dot.attr('edge', color=NODE_BORDER_COLOR, fontname=FONT_NAME, fontcolor=FONT_COLOR, fontsize='12')


# --- 节点定义 ---

# 1. 中心区域 (The Core Concept)
with dot.subgraph(name='cluster_core') as c:
    c.attr(style='filled', color=BG_COLOR) # 无边框
    c.node_attr.update(shape='doublecircle', style='filled', fillcolor=NODE_COLOR, fontcolor=FONT_COLOR, fontsize='20')
    c.node('agent', 'AI Agent\nYour Digital Twin\n(你的数字孪生)')

# 2. 四个关键节点
with dot.subgraph(name='cluster_loop') as c:
    c.attr(color=BG_COLOR) # 无边框
    
    # 创建节点 (使用简化标签)
    c.node('observe', label='1. 观察 (Observe)\n\n- 审阅财务报表 (Review Financials)\n- 查看AI心理状态 (Check AI\'s Psychology)\n- 接收宏观新闻 (Receive Market News)\n- 发现决策事件 (Identify Decision Points)')
    c.node('reflect', label='2. 思考 (Reflect)\n\n- 分析AI行为动机 (Analyze AI\'s Motivation)\n- 评估风险与机遇 (Assess Risks & Opportunities)\n- 制定干预策略 (Formulate Intervention Strategy)\n- "我该对‘他’说些什么？" ("What should I say to \'him\'?")')
    c.node('intervene', label='3. 干预 (Intervene)\n\n- 发出“意识回响” (Send "Echoes of Consciousness")\n- 消耗干预点数(IP) (Consume Intervention Points)\n- 选择干预类型 (Choose Intervention Type)\n- (启发/建议/指令/鼓励)', color=ACCENT_COLOR_ORANGE, fontcolor=ACCENT_COLOR_ORANGE)
    c.node('witness', label='4. 见证 (Witness)\n\n- 观察AI的即时反馈 (Observe AI\'s Immediate Feedback)\n- 追踪长期连锁后果 (Track Long-term Consequences)\n- AI化身学习与演化 (AI Agent Learns & Evolves)\n- 世界状态发生改变 (World State is Altered)')

# --- 布局与连接 ---
dot.edge('observe', 'reflect', style='invis')
dot.edge('intervene', 'witness', style='invis')

# 逆时针连接
dot.edge('observe', 'reflect', label='  ', constraint='false')
dot.edge('reflect', 'intervene', label='  ', constraint='false')
dot.edge('intervene', 'witness', label='Action & Consequence', constraint='false')
dot.edge('witness', 'observe', label='New State, New Loop', constraint='false')

# 将中心节点连接到环上，以保持居中
dot.edge('agent', 'observe', style='invis')
dot.edge('agent', 'intervene', style='invis')


# --- 渲染并保存 ---
try:
    # Manually save with utf-8-sig encoding to include BOM for Windows
    with codecs.open('echopolis_core_loop.dot', 'w', 'utf-8-sig') as f:
        f.write(dot.source)
    print("Success: DOT file generated: echopolis_core_loop.dot")
except Exception as e:
    print(f"Error: Could not generate DOT file.")
    print(f"Error details: {e}")