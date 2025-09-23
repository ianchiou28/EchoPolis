---
title: The Core Loop - Echopolis Gameplay Cycle
---

# 🌆 Echopolis 核心玩法循环

```mermaid
flowchart TD
    %% 中心AI化身
    Core(("🤖 AI Agent<br/>Digital Twin"))
    
    %% 四个核心节点
    A["👁️ 观察 OBSERVE<br/>━━━━━━━━━━━━━━━━<br/>审阅财务报表<br/>查看AI心理状态<br/>接收宏观新闻<br/>发现决策事件"]
    
    B["💭 思考 REFLECT<br/>━━━━━━━━━━━━━━━━<br/>分析AI行为动机<br/>评估风险与机遇<br/>制定干预策略<br/>我该对他说什么？"]
    
    C["🎯 干预 INTERVENE<br/>━━━━━━━━━━━━━━━━<br/>发出意识回响<br/>消耗干预点数IP<br/>选择干预类型<br/>启发建议指令鼓励"]
    
    D["⏳ 见证 WITNESS<br/>━━━━━━━━━━━━━━━━<br/>观察AI即时反馈<br/>追踪长期连锁后果<br/>AI化身学习演化<br/>世界状态发生改变"]
    
    %% 循环连接
    A --> B
    B --> C
    C -->|行动与后果| D
    D -->|新状态新循环| A
    
    %% 样式定义
    classDef coreStyle fill:#1a1a2e,stroke:#4fc3f7,stroke-width:4px,color:#ffffff,font-size:16px
    classDef nodeStyle fill:#2c2c54,stroke:#4fc3f7,stroke-width:2px,color:#ffffff,font-size:14px
    classDef interveneStyle fill:#2c2c54,stroke:#ff9800,stroke-width:3px,color:#ffffff,font-size:14px
    
    %% 应用样式
    class Core coreStyle
    class A,B,D nodeStyle
    class C interveneStyle
```

## 🔄 核心循环说明

这个循环图展示了Echopolis的核心玩法机制：

1. **观察阶段** - 玩家收集信息，了解AI化身的当前状态
2. **思考阶段** - 玩家分析情况，制定干预策略
3. **干预阶段** - 玩家通过"意识回响"影响AI决策（关键互动点）
4. **见证阶段** - 玩家观察干预结果，AI学习演化，世界状态改变

整个循环强调了玩家与AI化身之间的深度互动关系，每次循环都会产生新的状态和可能性。