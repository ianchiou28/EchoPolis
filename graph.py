# -*- coding: utf-8 -*-
from graphviz import Digraph

def create_echopolis_core_loop_diagram():
    dot = Digraph(comment='The Core Loop: Echopolis Gameplay Cycle', format='png')
    dot.attr(rankdir='LR',
             bgcolor='#1A1A2E',
             fontname='Arial')

    # Set up global node styles
    dot.attr('node', shape='box', style='filled', color='#303F9F', penwidth='2',
             fontname='Arial', fontsize='12', fontcolor='white',
             margin='0.4,0.3', # Padding inside nodes
             fillcolor='#2C2C4E', # Darker node background
             labelloc='t') # Label at top if multi-line

    # Set up global edge styles
    dot.attr('edge', color='white', fontname='Arial', fontsize='10', fontcolor='white',
             arrowhead='vee', arrowsize='1.2', penwidth='1.5')

    # 1. 中心区域 (The Core Concept) - A special node
    dot.node('center_ai', 'AI Agent\n🤖\nYour Digital Twin',
        shape='circle', width='2.5', height='2.5', fixedsize='true',
        fillcolor='#101018', style='filled', penwidth='3',
        fontcolor='white', fontsize='16', color='#4FC3F7')

    # 2. 左上角节点 (Quadrant 1 - Observe)
    dot.node('observe', '''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2">
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="18" COLOR="#4FC3F7">1. 观察 (Observe)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 审阅财务报表</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 查看AI心理状态</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 接收宏观新闻</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 发现决策事件</FONT></TD></TR>
        </TABLE>
        >''',
        shape='box', style='rounded,filled', fillcolor='#2C2C4E',
        color='#4FC3F7', penwidth='2')

    # 3. 左下角节点 (Quadrant 2 - Reflect)
    dot.node('reflect', '''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2">
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="18" COLOR="#4FC3F7">2. 思考 (Reflect)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 分析AI行为动机</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 评估风险与机遇</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 制定干预策略</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; “我该对‘他’说些什么？”</FONT></TD></TR>
        </TABLE>
        >''',
        shape='box', style='rounded,filled', fillcolor='#2C2C4E',
        color='#4FC3F7', penwidth='2')

    # 4. 右下角节点 (Quadrant 3 - Intervene)
    dot.node('intervene', '''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2">
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="18" COLOR="#FF9800">3. 干预 (Intervene)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 发出“意识回响”</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 消耗干预点数(IP)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 选择干预类型</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&nbsp;&nbsp;(启发/建议/指令/鼓励)</FONT></TD></TR>
        </TABLE>
        >''',
        shape='box', style='rounded,filled', fillcolor='#2C2C4E',
        color='#FF9800', penwidth='2') # Orange border for emphasis

    # 5. 右上角节点 (Quadrant 4 - Witness)
    dot.node('witness', '''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2">
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="18" COLOR="#4FC3F7">4. 见证 (Witness)</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 观察AI的即时反馈</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 追踪长期连锁后果</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; AI化身学习与演化</FONT></TD></TR>
            <TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#FFFFFF">&#8226; 世界状态发生改变</FONT></TD></TR>
        </TABLE>
        >''',
        shape='box', style='rounded,filled', fillcolor='#2C2C4E',
        color='#4FC3F7', penwidth='2')

    # Connections for the loop (counter-clockwise)
    dot.edge('observe', 'reflect')
    dot.edge('reflect', 'intervene')
    dot.edge('intervene', 'witness')
    dot.edge('witness', 'observe')

    # To position the nodes somewhat circularly around the center
    # This is a bit manual and might need tweaking for perfect symmetry
    # Use subgraph with rank to enforce relative positioning
    dot.subgraph(name='cluster_nodes') # Using a cluster for layout
    dot.attr(compound='true')

    # Render the graph
    dot.render('echopolis_core_loop', view=False, cleanup=True)
    print("Core loop diagram generated: echopolis_core_loop.png")

# Run the function to create the diagram
if __name__ == "__main__":
    create_echopolis_core_loop_diagram()