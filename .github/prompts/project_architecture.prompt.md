---
agent: agent
description: EchoPolis 项目架构文档 - 帮助理解项目设计理念、技术架构和实现细节
---

# 📊 EchoPolis 项目架构文档

> 本文档旨在帮助新开发者快速理解 EchoPolis 项目的设计理念、技术架构和实现细节。

---

## 一、项目概述

### 1.1 项目简介
**EchoPolis (回声都市)** 是一个由 AI 驱动的社会金融模拟器，旨在为 Z 世代提供安全可控的"第二人生"财富体验。通过"意识回响"机制与 DeepSeek AI 化身深度互动，用户可以在零风险环境中探索金融决策、理解风险与成长。

### 1.2 核心设计哲学
| 概念 | 描述 |
|------|------|
| **一面镜子** | AI化身精准映射用户的决策模式、风险偏好与思维惯性 |
| **一个回响** | 语言干预如投石入湖，激起层层涟漪，模拟现实选择的复杂性 |
| **一个沙盘** | 绝对安全的实验场，无惧风险地体验贷款、创业、投资的全过程 |

### 1.3 核心特色
- **DeepSeek AI驱动**: 真正的AI思考与决策
- **MBTI人格系统**: 16种人格类型的"意识复刻"
- **意识回响机制**: 非线性语言干预，动态影响权重
- **完整金融生态**: 宏观经济周期、个人财务管理、社交化投资
- **命运轮盘**: 8种社会阶层起点，差异化人生轨迹
- **行为洞察**: 个性化用户画像与群体洞察

对前端的改动，重新修改前端，不改变风格，分为三大模块
1.	世界沙盘：
把建筑地图都放上去，将原本的主页、金融服务、生活规划都整合进去
将每个金融服务、生活规划变成点击建筑就进入的分页，让这个页面作为首页只有地图和主体状态
2.	事件回响
我先来说明我们的设计，对基于wide-research生成的事件作为事件池（1000+），然后基于用户标签来筛选用户可能想要的选项，在这个页面，我们显示对用户个人化定制的选项，来让用户选择，并且不断根据用户选择来增加或减少标签
3.	个人中心
显示个人中心、系统档案、排行榜、成就，用户标签（不断更新）

也请基于更新的设计理念来相应修改后端

---

## 二、技术栈

### 2.1 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 主要编程语言 |
| FastAPI | ≥0.104.0 | Web框架 |
| Uvicorn | ≥0.24.0 | ASGI服务器 |
| Pydantic | ≥2.0.0 | 数据验证 |
| SQLite | 内置 | 数据库 |
| NumPy | ≥1.24.0 | 数值计算 |

### 2.2 前端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | ^3.4.0 | 前端框架 |
| Vite | ^5.0.0 | 构建工具 |
| Pinia | ^2.1.0 | 状态管理 |
| Vue Router | ^4.2.0 | 路由管理 |
| Axios | ^1.6.0 | HTTP客户端 |
| ECharts | ^5.6.0 | 数据可视化 |

### 2.3 AI集成
| 服务 | 用途 |
|------|------|
| DeepSeek API | AI决策引擎、情况生成、对话系统 |

---

## 三、目录结构

```
EchoPolis/
├── 📄 config.json              # DeepSeek API 配置
├── 📄 requirements.txt         # Python 依赖
├── 📄 package.json             # Node.js 依赖
├── 📄 start.py                 # 一键启动脚本
├── 📄 echopolis.db             # SQLite 数据库文件
│
├── 📁 backend/                 # 后端服务
│   ├── 📄 start_backend_only.py
│   └── 📁 app/
│       ├── 📄 main.py          # FastAPI 应用入口
│       ├── 📁 api/
│       │   └── 📄 routes.py    # API 路由定义 (~2900行)
│       ├── 📁 models/
│       │   ├── 📄 auth.py      # 认证模型
│       │   └── 📄 requests.py  # 请求模型
│       └── 📁 services/
│           └── 📄 game_service.py  # 游戏核心服务 (~1400行)
│
├── 📁 core/                    # 核心游戏逻辑
│   ├── 📁 ai/
│   │   └── 📄 deepseek_engine.py   # DeepSeek AI 引擎
│   ├── 📁 avatar/
│   │   └── 📄 ai_avatar.py         # AI 化身系统
│   ├── 📁 database/
│   │   └── 📄 database.py          # 数据库管理
│   ├── 📁 entities/
│   │   ├── 📄 person.py            # 人物实体
│   │   ├── 📄 brain.py             # AI大脑
│   │   └── 📄 action.py            # 行为定义
│   └── 📁 systems/             # 游戏子系统
│       ├── 📄 career_system.py         # 职业系统
│       ├── 📄 investment_system.py     # 投资系统
│       ├── 📄 market_engine.py         # 市场引擎
│       ├── 📄 behavior_insight_system.py # 行为洞察
│       ├── 📄 achievement_system.py    # 成就系统
│       ├── 📄 event_system.py          # 事件系统
│       ├── 📄 macro_economy.py         # 宏观经济
│       ├── 📄 mbti_traits.py           # MBTI人格
│       ├── 📄 fate_wheel.py            # 命运轮盘
│       ├── 📄 echo_system.py           # 回响系统
│       ├── 📄 debt_system.py           # 债务系统
│       ├── 📄 insurance_system.py      # 保险系统
│       ├── 📄 cashflow_system.py       # 现金流系统
│       └── 📄 leaderboard_system.py    # 排行榜
│
└── 📁 frontend/                # 前端应用
    ├── 📄 package.json
    ├── 📄 vite.config.js
    └── 📁 src/
        ├── 📄 App.vue
        ├── 📄 main.js
        ├── 📁 views/           # 页面视图
        │   ├── 📄 HomeNew.vue      # 主页
        │   ├── 📄 Insights.vue     # 行为洞察
        │   ├── 📄 Login.vue        # 登录
        │   └── 📄 CharacterSelect.vue # 角色选择
        ├── 📁 components/      # 组件
        │   └── 📁 views/       # 子视图组件
        │       ├── 📄 TradingView.vue
        │       ├── 📄 BankingView.vue
        │       ├── 📄 CareerView.vue
        │       └── 📄 TimelineView.vue
        ├── 📁 stores/
        │   ├── 📄 game.js      # 游戏状态管理
        │   └── 📄 theme.js     # 主题管理
        └── 📁 styles/
            ├── 📄 design-system.css
            └── 📄 terminal-theme.css
```

---

## 四、数据库表结构

### 4.1 账户与用户表
```sql
-- 账户表
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP
);

-- 用户/角色表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,           -- 关联账户
    session_id TEXT UNIQUE NOT NULL,  -- 会话ID (格式: {user_id}_{random})
    name TEXT NOT NULL,               -- 角色名
    mbti TEXT NOT NULL,               -- MBTI类型
    fate TEXT NOT NULL,               -- 命运类型
    credits INTEGER NOT NULL,         -- 现金
    happiness INTEGER DEFAULT 70,     -- 幸福度 (0-100)
    energy INTEGER DEFAULT 75,        -- 精力 (0-100)
    health INTEGER DEFAULT 80,        -- 健康 (0-100)
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 会话表
CREATE TABLE sessions (
    session_id TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    current_month INTEGER DEFAULT 1   -- 当前游戏月份
);
```

### 4.2 投资系统表
```sql
-- 投资表
CREATE TABLE investments (
    id INTEGER PRIMARY KEY,
    session_id TEXT, 
    name TEXT,
    amount INTEGER,
    investment_type TEXT,         -- 短期/中期/长期
    remaining_months INTEGER,
    monthly_return INTEGER,
    return_rate REAL,
    ai_thoughts TEXT
);

-- 股票持仓表
CREATE TABLE stock_holdings (
    session_id TEXT,
    stock_id TEXT,
    stock_name TEXT,
    shares INTEGER,
    avg_cost REAL,
    buy_month INTEGER,
    UNIQUE(session_id, stock_id)
);

-- 股票交易历史
CREATE TABLE stock_transactions (
    session_id TEXT,
    stock_id TEXT,
    action TEXT,          -- buy/sell
    shares INTEGER,
    price REAL,
    total_amount REAL,
    month INTEGER,
    profit REAL
);

-- 金融产品持仓
CREATE TABLE financial_holdings (
    session_id TEXT,
    product_id TEXT,
    product_name TEXT,
    product_type TEXT,    -- fund/bond/deposit
    amount INTEGER,
    buy_price REAL,
    current_value REAL,
    maturity_month INTEGER
);
```

### 4.3 贷款与保险表
```sql
-- 贷款表
CREATE TABLE loans (
    session_id TEXT,
    loan_id TEXT UNIQUE,
    loan_type TEXT,
    product_name TEXT,
    principal INTEGER,
    remaining_principal INTEGER,
    annual_rate REAL,
    term_months INTEGER,
    remaining_months INTEGER,
    monthly_payment INTEGER,
    is_overdue INTEGER,
    overdue_days INTEGER
);

-- 保险保单表
CREATE TABLE insurance_policies (
    session_id TEXT,
    policy_id TEXT UNIQUE,
    product_id TEXT,
    product_name TEXT,
    insurance_type TEXT,
    monthly_premium INTEGER,
    coverage_amount INTEGER,
    remaining_months INTEGER,
    claim_count INTEGER
);
```

### 4.4 行为洞察表
```sql
-- 行为日志表
CREATE TABLE behavior_logs (
    session_id TEXT,
    month INTEGER,
    action_type TEXT,         -- stock_buy, loan_apply 等
    action_category TEXT,     -- investment, financing 等
    amount REAL,
    risk_score REAL,          -- 0-1
    rationality_score REAL,   -- 0-1
    market_condition TEXT,
    decision_context TEXT
);

-- 行为画像表
CREATE TABLE behavior_profiles (
    session_id TEXT UNIQUE,
    risk_preference TEXT,     -- conservative/moderate/aggressive
    decision_style TEXT,      -- rational/impulsive/passive/adaptive
    avg_risk_score REAL,
    avg_rationality REAL,
    action_count INTEGER
);
```

---

## 五、核心 API 端点

### 5.1 认证 API
```
POST /api/login          # 用户登录
POST /api/register       # 用户注册
```

### 5.2 角色管理
```
GET  /api/mbti-types              # 获取MBTI类型列表
GET  /api/fate-options            # 获取命运轮盘选项
POST /api/characters              # 创建新角色
GET  /api/characters/{username}   # 获取用户角色列表
DELETE /api/characters/{session_id} # 删除角色
```

### 5.3 游戏核心
```
POST /api/generate-situation      # 生成决策情况
POST /api/echo                    # 发送意识回响
POST /api/decide                  # AI自主决策
POST /api/session/advance         # 推进时间(月)
GET  /api/session/state           # 获取会话状态
```

### 5.4 投资与交易
```
GET  /api/investments             # 获取投资列表
GET  /api/market/stocks           # 获取股票行情
POST /api/market/buy              # 购买股票
POST /api/market/sell             # 卖出股票
GET  /api/stock/holdings          # 获取股票持仓
```

### 5.5 银行与贷款
```
GET  /api/loans/{session_id}      # 获取贷款列表
POST /api/loans/apply             # 申请贷款
POST /api/loans/repay             # 还款
GET  /api/bank/balance            # 获取银行余额
POST /api/bank/deposit            # 存款
```

### 5.6 行为洞察
```
GET  /api/insights/personal/{session_id}   # 个人行为洞察
GET  /api/insights/cohort                  # 群体洞察
GET  /api/insights/statistics/{session_id} # 行为统计
GET  /api/insights/warnings/{session_id}   # 风险预警
```

---

## 六、游戏玩法设计

### 6.1 核心游戏循环

```
┌─────────────────────────────────────────────────────────┐
│                    游戏主循环                            │
├─────────────────────────────────────────────────────────┤
│  1. 生成情况 (AI生成/预设情况)                           │
│         ↓                                               │
│  2. 玩家发送"意识回响" (可选)                            │
│         ↓                                               │
│  3. AI化身做出决策                                       │
│         ↓                                               │
│  4. 执行决策结果 (资金变动/属性变化)                     │
│         ↓                                               │
│  5. 推进月份 (处理收入支出/投资收益/事件触发)            │
│         ↓                                               │
│  6. 更新行为画像 & 检查成就                              │
│         ↓                                               │
│  [循环回到步骤1]                                         │
└─────────────────────────────────────────────────────────┘
```

### 6.2 意识回响机制 (核心玩法)

**玩法概念:** 玩家不直接控制AI化身，而是通过"意识回响"来影响AI的决策。

**四种回响类型:**
| 类型 | 描述 | 示例 | AI反应 |
|------|------|------|--------|
| **启发式** | 引导AI思考 | "想想长期收益" | 高接受度 |
| **建议式** | 提供具体建议 | "建议选择稳健投资" | 中等接受度 |
| **指令式** | 直接命令 | "必须买入股票" | 可能被拒绝 |
| **情感式** | 情绪调节 | "别太担心风险" | 影响情绪状态 |

**信任度系统:**
```
信任度 (0-100)
├── 初始: 50
├── 建议成功 → +5~15
├── 建议失败 → -10~20
├── 频繁干预 → -5
└── 影响:
    ├── 高信任 (>70): AI更易采纳建议
    ├── 中等 (30-70): 正常权衡
    └── 低信任 (<30): AI可能无视/反驳建议
```

### 6.3 决策情况系统

**情况生成来源:**
1. **AI动态生成** - DeepSeek根据角色状态实时生成
2. **预设情况池** - 备用的固定情况

**情况结构:**
```python
{
    "situation": "描述当前面临的情况...",
    "options": [
        "选项1: 保守策略",
        "选项2: 激进策略", 
        "选项3: 观望等待"
    ],
    "context_type": "ai_generated" | "preset"
}
```

**情况类型:**
- 💼 职场决策 (升职/跳槽/创业)
- 💰 投资机会 (股票/基金/房产)
- 🏠 生活选择 (租房/买房/消费)
- ⚠️ 风险事件 (意外/疾病/经济危机)
- 🎯 人生抉择 (婚姻/教育/养老)

### 6.4 金融操作系统

**股票交易:**
```
买入股票 → 扣除现金 → 记录持仓 → 记录行为日志
卖出股票 → 计算盈亏 → 增加现金 → 更新画像
```

**银行业务:**
- 活期存款: 随存随取，利率低
- 定期存款: 锁定期限，利率高
- 贷款申请: 信用评估 → 额度审批 → 月供扣款

**保险产品:**
- 医疗险: 覆盖医疗支出
- 意外险: 覆盖意外事件
- 理财险: 储蓄+保障

### 6.5 经济模拟系统

**宏观经济周期影响:**
```
扩张期 → 股市上涨，就业好，消费旺
顶峰期 → 泡沫风险，需要警惕
收缩期 → 股市下跌，失业增加
谷底期 → 抄底机会，现金为王
```

**个人财务公式:**
```
月末现金 = 月初现金 + 工资收入 + 投资收益 - 生活开销 - 贷款月供 - 保险费用
总资产 = 现金 + 股票市值 + 基金市值 + 房产价值 - 负债
```

---

## 七、核心游戏逻辑

### 7.1 AI 化身系统 (ai_avatar.py)

**化身属性结构:**
```python
AIAvatarAttributes:
    name: str              # 名字
    age: int               # 年龄
    mbti_type: MBTIType    # MBTI类型
    life_stage: LifeStage  # 人生阶段
    credits: int           # 现金
    health: int            # 健康 (0-100)
    energy: int            # 精力 (0-100)
    happiness: int         # 幸福 (0-100)
    stress: int            # 压力 (0-100)
    trust_level: int       # 对玩家信任度 (0-100)
    decision_count: int    # 决策次数
```

**人生阶段:**
- STARTUP (18-22岁) - 启航期
- EXPLORATION (23-30岁) - 探索期
- STRUGGLE (31-45岁) - 奋斗期
- ACCUMULATION (46-60岁) - 沉淀期
- RETIREMENT (60+岁) - 黄昏期

### 7.2 DeepSeek AI 引擎 (deepseek_engine.py)

**决策流程:**
```
1. 构建 Prompt (角色信息 + 当前状态 + 情况选项 + 玩家建议)
2. 调用 DeepSeek API (model: deepseek-chat)
3. 解析响应:
   - chosen_option: 选择的选项索引
   - ai_thoughts: AI思考过程
   - decision_impact: {cash_change, health_change, happiness_change}
```

**MBTI 人格描述示例:**
```python
MBTI_PROFILES = {
    "INTJ": "战略家 - 棋盘延伸到十年之后，卒子过河即成女王",
    "INTP": "逻辑学家 - 在脑内搭建巴别图书馆，用公式翻译上帝呓语",
    "ENFP": "倡导者 - 思维是永不停歇的烟花厂",
    "ENTP": "辩论家 - 用悖论编织投石器，击碎所有庄严的玻璃窗",
    # ... 共16种
}
```

### 7.3 市场引擎 (market_engine.py)

**虚拟股票池 (20只):**
```
科技股(高波动): ECHO01-回声科技, ECHO02-量子计算
金融股(与利率强相关): ECHO04-汇通银行, ECHO05-诚信保险
消费股(稳定增长): ECHO07-国民饮品, ECHO08-潮流服饰
医疗股(防御性): ECHO10-康健医药
能源股(周期性): ECHO13-绿能科技, ECHO14-锂电未来
```

**K线生成:**
```python
日收益率 = 高斯随机(0, 波动率) + 趋势 × Beta × 0.01
收盘价 = 前收盘 × (1 + 日收益率)
成交量 = 基础量 × (1 + |日收益率| × 10) × 随机(0.5, 1.5)
```

### 7.4 宏观经济 (macro_economy.py)

**经济周期:**
```
EXPANSION (扩张期) → PEAK (顶峰期) → CONTRACTION (收缩期) → TROUGH (谷底期)
```

**经济指标:**
- GDP增长率、通胀率、基准利率
- 失业率、CPI指数、房价指数、股票指数
- 市场情绪 (0-100)

### 7.5 行为洞察系统 (behavior_insight_system.py)

**风险评分 (0-1):**
```python
risk_score = 0.5 + 行为固有风险 + 市场环境调整 + 金额占比调整
```

**理性度评分 (0-1):**
```python
rationality = 0.5 + 时机选择 + 分散投资 + 现金储备 + 止损策略
```

**行为画像输出:**
- risk_preference: conservative / moderate / aggressive
- decision_style: rational / impulsive / passive / adaptive

### 7.6 职业系统 (career_system.py)

**职业等级:**
```
INTERN → JUNIOR → MID → SENIOR → LEAD → MANAGER → DIRECTOR → VP → CXO
```

**行业:**
- 科技互联网 (tech)
- 金融 (finance)
- 咨询 (consulting)
- 制造业 (manufacturing)
- 教育 (education)
- 医疗 (healthcare)

### 7.7 命运轮盘 (fate_wheel.py)

**8种出身:**
| 命运 | 初始资金 | 描述 |
|------|----------|------|
| 亿万富豪 | 100,000,000 | 含金钥匙出生 |
| 书香门第 | 1,000,000 | 知识分子家庭 |
| 小康之家 | 300,000 | 中产阶级 |
| 普通家庭 | 50,000 | 工薪阶层 |
| 低收入户 | 25,000 | 家庭收入微薄 |
| 家道中落 | 10,000 | 曾经辉煌的家族 |
| 白手起家 | 5,000 | 一无所有 |
| 负债累累 | -50,000 | 背负家庭债务 |

---

## 八、月度推进流程

```python
def advance_session(session_id):
    # 1. 推进宏观经济
    macro_economy.advance_month()
    
    # 2. 处理投资收益
    investment_system.process_monthly_returns(session_id)
    
    # 3. 处理贷款还款
    debt_system.process_repayments(session_id)
    
    # 4. 处理保险费用
    insurance_system.process_premiums(session_id)
    
    # 5. 计算工资收入
    salary = career_system.get_monthly_salary(session_id)
    
    # 6. 扣除生活开销
    living_cost = calculate_living_cost(session_id)
    
    # 7. 触发随机事件
    event_system.check_events(session_id)
    
    # 8. 检查成就解锁
    achievement_system.check_achievements(session_id)
    
    # 9. 更新行为画像 (每3个月)
    if month % 3 == 0:
        behavior_system.analyze_profile(session_id)
    
    # 10. 保存月度快照
    db.save_monthly_snapshot(session_id)
```

---

## 九、前端状态管理 (game.js)

**核心状态:**
```javascript
state: {
  avatar: null,                    // 当前角色
  assets: { 
    total: 0,                      // 总资产
    cash: 0,                       // 现金
    investments: 0                 // 投资
  },
  trustLevel: 50,                  // 信任度
  wealthLevel: '贫困',             // 财富等级
  lifeStage: '起步期',             // 人生阶段
  isBankrupt: false,               // 是否破产
  assetHistory: [],                // 资产曲线
  macroIndicators: {               // 宏观指标
    gdp_growth: 0,
    inflation: 0,
    interest_rate: 0
  }
}
```

**关键方法:**
```javascript
// 加载角色状态
async loadAvatar(sessionId)

// 推进月份
async advanceMonth()

// 发送意识回响
async sendEcho(echoText)

// 做出决策
async makeDecision(optionIndex, optionText)

// 购买股票
async buyStock(stockId, shares)

// 申请贷款
async applyLoan(productId, amount)
```

---

## 十、前端设计风格

### 10.1 设计理念

**风格定位:** 工业复古终端风 (Industrial Retro Terminal)

**设计关键词:**
- 🖥️ 终端/控制台美学
- 📊 数据可视化仪表盘
- 🏭 工业风格/Brutalist
- 📋 档案卡片/文档风格
- 🎮 科幻游戏界面

### 10.2 色彩系统

**深色主题 (默认):**
```css
--term-bg: #050505;           /* 纯黑背景 */
--term-text: #ffffff;         /* 纯白文字 */
--term-accent: #FF5500;       /* 橙色强调 (Project Echo Orange) */
--term-border: #333333;       /* 灰色边框 */
--term-success: #22c55e;      /* 绿色成功 */
--term-accent-secondary: #eab308; /* 黄色警告 */
```

**浅色主题 (档案风):**
```css
--term-bg: #F2F0E6;           /* 米色纸张背景 */
--term-text: #111111;         /* 深色文字 */
--term-accent: #E04F00;       /* 深橙色 */
--term-border: #000000;       /* 纯黑边框 */
```

### 10.3 字体系统

```css
/* 主要字体: 等宽编程字体 */
font-family: 'JetBrains Mono', 'Courier New', monospace;

/* 标题字体: 粗体无衬线 */
font-family: 'Arial Black', 'Impact', sans-serif;
```

**字体层级:**
| 用途 | 大小 | 字重 | 样式 |
|------|------|------|------|
| 品牌Logo | 48-56px | 900 | 斜体/大写 |
| 页面标题 | 24-32px | 800 | 大写 |
| 卡片标题 | 14-16px | 700 | 大写+字间距 |
| 正文 | 13-14px | 400 | 正常 |
| 标签/小字 | 11-12px | 600 | 大写 |

### 10.4 组件设计

**档案卡片 (Archive Card):**
```
┌─────────────────────────────┐
│ CARD HEADER // 卡片标题      │  ← 2px实线边框，无圆角
├─────────────────────────────┤
│                             │
│   卡片内容区域               │  ← 6px黑色阴影偏移
│                             │
└─────────────────────────────┘
    ↘ 阴影
```

**按钮风格:**
```css
.term-btn {
  border: 2px solid;
  border-radius: 0;        /* 无圆角 */
  text-transform: uppercase;
  box-shadow: 2px 2px 0px; /* 实心阴影 */
}
/* Hover: 阴影加深，轻微位移 */
/* Active: 阴影消失，按下效果 */
```

**输入框:**
```css
.term-input {
  background: var(--term-bg);
  border: 2px solid var(--term-border);
  border-radius: 0;
  font-family: monospace;
}
/* Focus: 橙色边框 + 发光效果 */
```

### 10.5 视觉效果

**网格背景 (Graph Paper):**
```css
.grid-bg {
  background-image: 
    linear-gradient(var(--term-grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--term-grid) 1px, transparent 1px);
  background-size: 20px 20px;
}
```

**CRT扫描线效果:**
```css
.crt-overlay {
  background: linear-gradient(
    rgba(18, 16, 16, 0) 50%, 
    rgba(0, 0, 0, 0.15) 50%
  );
  background-size: 100% 3px;
  opacity: 0.4;
}
```

**发光效果:**
```css
/* 文字发光 */
text-shadow: 0 0 8px var(--term-accent-glow);

/* 边框发光 */
box-shadow: 0 0 10px var(--term-accent-glow);
```

### 10.6 页面布局

**主页面结构:**
```
┌──────────────────────────────────────────────────┐
│ [侧边栏]  │  [顶部导航栏: ECHOPOLIS // 系统]     │
│           │─────────────────────────────────────│
│ ⚡ 城市概览│  ┌─────────┐  ┌─────────┐          │
│ 👤 主体数据│  │ 状态面板 │  │ 城市地图 │          │
│ 🏦 银行系统│  │ (角色信息)│  │ (互动区块)│          │
│ 📈 股票交易│  └─────────┘  └─────────┘          │
│ 💼 职业发展│                                     │
│ 🧠 行为洞察│  ┌─────────────────────────────┐   │
│ 📁 档案库  │  │      当前指令 (决策面板)      │   │
│ 🕐 时间线  │  │  情况描述 + 选项 + 回响输入   │   │
│ 🏆 排行榜  │  └─────────────────────────────┘   │
├───────────┤                                     │
│ [音乐播放器]│  [底部命令行: 用户@ECHO:~$]        │
│ [设置/断开] │                                    │
└──────────────────────────────────────────────────┘
```

**响应式设计:**
- **桌面 (>1024px):** 完整侧边栏 + 多列布局
- **平板 (768-1024px):** 可折叠侧边栏
- **手机 (<768px):** 底部标签导航 + 单列布局

### 10.7 交互动效

**状态转换:**
```css
transition: all 0.2s ease;
```

**悬停效果:**
- 卡片: 边框变亮，阴影加深
- 按钮: 位移 + 阴影扩展
- 链接: 下划线 + 发光

**加载状态:**
- 骨架屏 (Skeleton)
- 脉冲动画
- 终端风格"加载中..."

### 10.8 图标与装饰

**图标风格:** Emoji + 文字标签
```
⚡ 城市概览    👤 主体数据    🏦 银行系统
📈 股票交易    💼 职业发展    🧠 行为洞察
```

**装饰元素:**
- 双斜杠分隔符: `// TITLE`
- 下划线命名: `SUBJECT_DATA`
- 方括号标注: `[STATUS: ACTIVE]`

---

## 十一、启动方式

### 一键启动 (推荐)
```bash
python start.py
```

### 分别启动
```bash
# 后端
python backend/start_backend_only.py

# 前端
cd frontend
npm install
npm run dev
```

### 访问地址
- 游戏界面: http://localhost:3001
- API 文档: http://localhost:8000/docs

### 配置文件 (config.json)
```json
{
  "deepseek_api_key": "your-api-key-here"
}
```

---

## 十二、开发指南

### 12.1 添加新的游戏系统
1. 在 `core/systems/` 创建新的 Python 文件
2. 实现系统类，提供必要的方法
3. 在 `game_service.py` 中导入并初始化
4. 在 `routes.py` 中添加 API 端点

### 12.2 添加新的前端视图
1. 在 `frontend/src/views/` 或 `components/views/` 创建 Vue 组件
2. 在 `router/index.js` 添加路由 (如需要)
3. 在 `stores/game.js` 添加相关状态和方法

### 12.3 添加新的数据库表
1. 在 `database.py` 的 `init_database()` 添加建表语句
2. 添加相应的 CRUD 方法
3. 在相关系统中调用

---

## 十三、代码规模统计

| 模块 | 文件 | 代码行数 |
|------|------|----------|
| 后端 API | routes.py | ~2,900 |
| 游戏服务 | game_service.py | ~1,400 |
| 数据库 | database.py | ~1,600 |
| 行为洞察 | behavior_insight_system.py | ~1,300 |
| 成就系统 | achievement_system.py | ~1,000 |
| AI 化身 | ai_avatar.py | ~970 |
| 职业系统 | career_system.py | ~920 |
| 事件系统 | event_system.py | ~730 |
| 前端状态 | game.js | ~750 |
| DeepSeek | deepseek_engine.py | ~620 |
| **总计** | | **~15,000+** |

---

*文档更新时间: 2025年12月*