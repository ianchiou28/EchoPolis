# EchoPolis 行为洞察引擎

## 概述

行为洞察引擎是 EchoPolis 的核心模块之一，基于 AI 数字孪生技术，专门针对 Z 世代用户的金融行为进行分析和洞察。

## 功能架构

```
┌──────────────────────────────────────────────────────────────┐
│                   行为洞察引擎 (BehaviorInsightSystem)          │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  行为记录    │  │  画像分析    │  │  AI洞察     │          │
│  │  log_action │  │  analyze    │  │  generate   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  预警系统    │  │  群体洞察    │  │  同龄对比    │          │
│  │  warnings   │  │  cohort     │  │  peer       │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└──────────────────────────────────────────────────────────────┘
```

## 核心类

### 1. BehaviorInsightSystem

主要的行为分析系统，负责记录、分析用户行为。

```python
from core.systems.behavior_insight_system import BehaviorInsightSystem

behavior_system = BehaviorInsightSystem(db)

# 记录行为
behavior_system.log_action(
    session_id="xxx",
    action_type="investment",
    action_category="stock_buy",
    action_data={"symbol": "AAPL", "amount": 10000},
    game_month=6,
    market_context={"trend": "bull"}
)

# 分析画像
profile = behavior_system.analyze_profile(session_id, current_month)

# 生成AI洞察
ai_insight = behavior_system.generate_ai_insight(session_id)
```

### 2. 行为预警功能

预警功能集成在 `BehaviorInsightSystem` 类中，检测6种常见的金融行为风险：

| 预警类型 | 说明 | 严重程度 |
|---------|------|---------|
| high_risk_streak | 连续高风险操作 | high |
| overtrading | 过度交易 | medium |
| leverage_abuse | 杠杆过度使用 | high |
| herding_behavior | 羊群效应倾向 | medium |
| overconfidence | 过度自信风险 | medium |
| low_cash_reserve | 现金储备不足 | high |

```python
from core.systems.behavior_insight_system import BehaviorInsightSystem

behavior_system = BehaviorInsightSystem(db)

# 获取预警
warnings = behavior_system.get_warnings(session_id, game_state)

# 或直接调用内部方法
alerts = behavior_system.check_behavior_alerts(session_id, current_month)
```

## 数据库表结构

### behavior_logs
记录每一次用户行为

| 字段 | 类型 | 说明 |
|-----|------|-----|
| id | INTEGER | 主键 |
| session_id | TEXT | 会话ID |
| action_type | TEXT | 行为类型 |
| action_category | TEXT | 行为分类 |
| action_data | TEXT | 行为详情(JSON) |
| risk_score | REAL | 风险评分 (0-1) |
| rationality_score | REAL | 理性评分 (0-1) |
| game_month | INTEGER | 游戏月份 |
| market_context | TEXT | 市场背景(JSON) |
| created_at | TIMESTAMP | 创建时间 |

### behavior_profiles
用户行为画像

| 字段 | 类型 | 说明 |
|-----|------|-----|
| session_id | TEXT | 会话ID (主键) |
| risk_preference | TEXT | 风险偏好 (conservative/moderate/aggressive) |
| decision_style | TEXT | 决策风格 (rational/impulsive/passive/adaptive) |
| loss_aversion | REAL | 损失厌恶程度 |
| overconfidence | REAL | 过度自信程度 |
| herding_tendency | REAL | 羊群倾向 |
| planning_ability | REAL | 规划能力 |
| action_count | INTEGER | 总行为次数 |
| avg_risk_score | REAL | 平均风险评分 |
| avg_rationality | REAL | 平均理性评分 |
| last_updated | TIMESTAMP | 最后更新时间 |

### cohort_insights
群体洞察

| 字段 | 类型 | 说明 |
|-----|------|-----|
| id | INTEGER | 主键 |
| insight_type | TEXT | 洞察类型 |
| insight_category | TEXT | 洞察分类 |
| title | TEXT | 标题 |
| description | TEXT | 详细描述 |
| data_source | TEXT | 数据来源 |
| sample_size | INTEGER | 样本量 |
| confidence_level | REAL | 置信度 |
| tags | TEXT | 标签 |
| generated_month | INTEGER | 生成月份 |
| created_at | TIMESTAMP | 创建时间 |

## API 端点

### 个人洞察
```
GET /insights/personal/{session_id}
```

返回用户的行为画像、近期行为统计、个性化建议。

### 群体洞察
```
GET /insights/cohort?limit=20
```

返回Z世代群体的行为洞察。

### 行为统计
```
GET /insights/statistics/{session_id}
```

返回雷达图数据、分类分布、月度活跃度、风险趋势等。

### AI洞察
```
GET /insights/ai/{session_id}
```

调用DeepSeek AI生成个性化分析报告。

### 行为预警
```
GET /insights/warnings/{session_id}
```

返回当前检测到的行为风险预警。

### 同龄人对比
```
GET /insights/peer-comparison/{session_id}
```

返回与同龄人的多维度对比数据。

## 行为成就

系统会根据用户的行为模式解锁特定成就：

| 成就ID | 名称 | 解锁条件 |
|-------|------|---------|
| BEHAVIOR_RATIONAL | 理性投资者 | 平均理性评分 ≥ 80% |
| BEHAVIOR_DIVERSE | 多元配置师 | 持有3类以上不同资产 |
| BEHAVIOR_STABLE | 稳健派 | 风险偏好波动率 < 10% |
| BEHAVIOR_PLANNER | 财务规划师 | 规划能力评分 ≥ 70% |
| BEHAVIOR_NO_HERD | 独立思考者 | 羊群倾向 < 30% |
| BEHAVIOR_LOW_RISK | 风控达人 | 平均风险评分 < 30% |
| BEHAVIOR_CONSISTENT | 一致性大师 | 决策一致性 ≥ 90% |
| BEHAVIOR_IMPROVED | 自我提升者 | 3个月内理性评分提升20% |

## 风险评分算法

### 风险评分计算
```python
def calculate_risk_score(action_data, category, market_context):
    base_risk = RISK_WEIGHTS.get(category, 0.5)
    
    # 金额调整
    if amount > threshold:
        base_risk += 0.1 * (amount / threshold - 1)
    
    # 杠杆调整
    if leverage > 1:
        base_risk += 0.2 * (leverage - 1)
    
    # 市场情绪调整
    if market_euphoric and category == 'buy':
        base_risk += 0.1  # 追涨风险
    
    return min(1.0, base_risk)
```

### 理性评分计算
```python
def calculate_rationality_score(action_data, category, profile):
    base_rationality = 0.5
    
    # 分散投资加分
    if portfolio_diverse:
        base_rationality += 0.15
    
    # 风险匹配加分
    if risk_matches_profile:
        base_rationality += 0.1
    
    # 羊群行为减分
    if following_trend:
        base_rationality -= 0.1
    
    return max(0.0, min(1.0, base_rationality))
```

## 前端展示

行为洞察页面 (`/insights`) 包含5个Tab：

1. **个人画像** - 显示用户的行为特征画像
2. **行为统计** - 雷达图、分类分布、趋势图、行为演变曲线
3. **AI洞察** - AI生成的个性化分析报告
4. **群体洞察** - Z世代群体行为洞察 + 同龄人对比
5. **预警** - 实时风险预警

时间线页面 (`/timeline`) 也整合了行为日志：
- 🧠 行为日志与事件/交易并列展示
- 显示每次行为的风险评分和理性评分
- 颜色编码标识风险等级

## 更新日志

### Phase 4 (当前)
- ✅ 行为演变趋势图表
- ✅ 行为里程碑检测
- ✅ 趋势总结自动生成
- ✅ 时间线集成行为日志
- ✅ 新增 `/insights/evolution/{session_id}` API
- ✅ 新增 `/behavior-logs/{session_id}` API

### Phase 3
- ✅ 行为预警系统 (集成到 BehaviorInsightSystem)
- ✅ 行为与成就关联
- ✅ 同龄人对比功能

### Phase 2
- ✅ 扩展行为记录到6个API
- ✅ AI洞察生成
- ✅ 行为统计端点
- ✅ 前端增强

### Phase 1
- ✅ 数据库表结构
- ✅ BehaviorInsightSystem核心类
- ✅ 基础API端点

## 作者

FinAI Team - Z世代金融教育平台
