# 行为洞察引擎 (Behavior Insight System) 技术文档

## 概述

行为洞察引擎是 EchoPolis 金融模拟沙盘的核心分析系统，负责追踪、分析用户的金融决策行为，生成个性化的行为画像和投资建议。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    行为洞察引擎 (BehaviorInsightSystem)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  行为记录模块  │───▶│  分析计算模块  │───▶│  输出生成模块  │      │
│  │  log_action  │    │ analyze_profile│   │ get_insights │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────────────────────────────────────────────┐      │
│  │                    数据库 (SQLite)                     │      │
│  │  behavior_logs | behavior_profiles | cohort_insights  │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐                          │
│  │  AI 引擎集成  │    │  预警检测模块  │                          │
│  │  DeepSeek    │    │  detect_risks │                          │
│  └──────────────┘    └──────────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 核心数据流

```
用户操作 ──▶ log_action() ──▶ behavior_logs 表
                                    │
                                    ▼
                          analyze_profile() 
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              风险偏好计算     决策风格判断     行为特征计算
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                          behavior_profiles 表
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              个人洞察输出     预警检测      AI 洞察生成
```

---

## 一、数据采集层

### 1.1 行为日志记录

每当用户执行金融操作时，系统调用 `log_action()` 记录行为：

```python
def log_action(self, session_id: str, month: int, action_type: str, 
               action_data: Dict, market_state: Dict) -> None:
    """
    记录用户行为
    
    参数:
        session_id: 用户会话ID
        month: 游戏内月份
        action_type: 行为类型 (如 'stock_buy', 'loan_apply')
        action_data: 行为详情 (金额、标的等)
        market_state: 市场状态 (经济周期、利率等)
    """
```

### 1.2 行为类型分类

| 类别 (category) | 行为类型 (action_type) | 说明 |
|----------------|----------------------|------|
| investment | stock_buy, stock_sell, fund_buy, fund_sell | 投资行为 |
| financing | loan_apply, loan_repay, debt_* | 融资/债务 |
| housing | house_buy, house_sell, house_rent | 住房相关 |
| protection | insurance_buy | 保障类 |
| consumption | lifestyle_luxury, lifestyle_basic | 消费行为 |
| other | side_business, 其他 | 其他行为 |

### 1.3 风险评分计算

每条行为记录包含系统自动计算的风险分 (`risk_score`) 和理性分 (`rationality_score`)：

```python
def _calculate_risk_score(self, action_type: str, action_data: Dict, market_state: Dict) -> float:
    """
    计算风险评分 (0-1)
    
    计算因素:
    1. 行为固有风险 (如 stock_buy=0.7, insurance_buy=0.15)
    2. 市场环境调整 (衰退期买入 +0.2, 繁荣期卖出 -0.1)
    3. 金额占比调整 (大额投入 +0.15)
    4. 杠杆使用调整 (使用杠杆 +0.2)
    """
```

**固有风险等级表：**

| 行为类型 | 风险分 | 说明 |
|---------|-------|------|
| stock_buy | 0.70 | 股票投资风险较高 |
| side_business | 0.75 | 创业风险高 |
| loan_apply | 0.80 | 举债增加杠杆 |
| fund_buy | 0.50 | 基金相对分散 |
| lifestyle_basic | 0.20 | 基本消费低风险 |
| insurance_buy | 0.15 | 保险是风险对冲 |

---

## 二、分析计算层

### 2.1 行为画像分析

`analyze_profile()` 是核心分析函数，聚合用户所有行为数据生成画像：

```python
def analyze_profile(self, session_id: str, current_month: int) -> Dict:
    """
    分析用户行为画像
    
    返回:
        {
            'risk_preference': 风险偏好 (conservative/moderate/aggressive),
            'decision_style': 决策风格 (rational/impulsive/passive/adaptive),
            'loss_aversion': 损失厌恶度 (0-1),
            'overconfidence': 过度自信度 (0-1),
            'herding_tendency': 羊群倾向 (0-1),
            'planning_ability': 规划能力 (0-1),
            'action_count': 行为总数,
            'avg_risk_score': 平均风险分,
            'avg_rationality': 平均理性分
        }
    """
```

### 2.2 风险偏好判断

基于用户所有行为的**平均风险分**判断：

```python
RISK_THRESHOLDS = {
    'conservative': (0, 0.4),    # 保守型：平均风险分 < 0.4
    'moderate': (0.4, 0.65),     # 稳健型：0.4 <= 平均风险分 < 0.65
    'aggressive': (0.65, 1.0)    # 激进型：平均风险分 >= 0.65
}
```

### 2.3 决策风格判断

综合考虑**理性度**和**行为频率**：

```python
def _determine_decision_style(self, logs: List[Dict], avg_rationality: float) -> str:
    """
    判断决策风格
    
    规则:
    - 理性规划型 (rational): 理性度 > 0.65 且 月均行为 >= 2
    - 冲动跟风型 (impulsive): 理性度 < 0.45 且 月均行为 >= 2.5
    - 被动随缘型 (passive): 月均行为 < 1.5
    - 灵活应变型 (adaptive): 其他情况
    """
```

### 2.4 行为特征指标计算

#### 2.4.1 损失厌恶 (Loss Aversion)

```python
def _calculate_loss_aversion(self, logs: List[Dict]) -> float:
    """
    计算损失厌恶程度
    
    算法: 止损行为次数 / 总卖出次数
    
    解释:
    - 高损失厌恶者倾向于设置止损，及时止损
    - 低损失厌恶者倾向于死扛亏损，不愿意认亏
    """
```

#### 2.4.2 过度自信 (Overconfidence)

```python
def _calculate_overconfidence(self, logs: List[Dict], avg_risk: float) -> float:
    """
    计算过度自信程度
    
    算法: 在高风险行为中，低理性度操作的占比
    
    解释:
    - 高风险 + 低理性 = 过度自信（盲目自信能赚钱）
    """
```

#### 2.4.3 羊群倾向 (Herding Tendency)

```python
def _calculate_herding_tendency(self, logs: List[Dict]) -> float:
    """
    计算羊群效应倾向
    
    算法: (繁荣期买入次数 + 衰退期卖出次数) / 总市场操作次数
    
    解释:
    - 繁荣期追涨 = 跟风买入
    - 衰退期恐慌抛售 = 跟风卖出
    """
```

#### 2.4.4 规划能力 (Planning Ability)

```python
def _calculate_planning_ability(self, logs: List[Dict], avg_rationality: float) -> float:
    """
    计算规划能力
    
    算法: (avg_rationality * 0.6) + (insurance_ratio * 0.4)
    
    解释:
    - 高理性度 + 购买保险 = 有规划意识
    """
```

---

## 三、输出生成层

### 3.1 个人洞察 API

```python
def get_personal_insights(self, session_id: str) -> Dict:
    """
    获取个人行为洞察
    
    返回:
        {
            'profile': 行为画像,
            'recent_actions': 近期行为统计 (3个月),
            'recommendations': 个性化建议列表
        }
    """
```

### 3.2 行为统计 API

```python
def get_statistics(self, session_id: str) -> Dict:
    """
    获取行为统计数据
    
    返回:
        {
            'monthly_activity': 月度活跃度 [{month, count}],
            'category_distribution': 类别分布 [{category, count}],
            'risk_trend': 风险趋势 [{month, value}],
            'rationality_trend': 理性趋势 [{month, value}],
            'behavior_radar': 行为雷达图数据 [{axis, value}]
        }
    """
```

### 3.3 同龄人对比

```python
def get_peer_comparison(self, session_id: str) -> Dict:
    """
    与Z世代同龄人对比
    
    对比维度:
    - 风险承受 (avg_risk_score)
    - 决策理性 (avg_rationality)
    - 规划能力 (planning_ability)
    - 羊群倾向 (herding_tendency)
    - 损失厌恶 (loss_aversion)
    - 过度自信 (overconfidence)
    
    返回百分位排名和优劣判断
    """
```

### 3.4 行为演变趋势

```python
def get_evolution_data(self, session_id: str) -> Dict:
    """
    获取行为演变数据
    
    返回:
        {
            'timeline': 月度风险/理性趋势,
            'trend_summary': {
                'risk_trend': 上升/下降/稳定,
                'rationality_trend': 上升/下降/稳定,
                'overall': 总体评价
            },
            'milestones': 行为里程碑事件
        }
    """
```

---

## 四、预警检测模块

### 4.1 风险预警检测

```python
def detect_warnings(self, session_id: str, game_state: Dict) -> List[Dict]:
    """
    检测行为风险预警
    
    检测项:
    1. 高风险行为占比过高 (>70%)
    2. 过度借贷 (负债率>80%)
    3. 低现金储备投资 (现金<总资产20%时仍投资)
    4. 频繁交易 (月均>6次)
    5. 逆势操作过多
    """
```

### 4.2 预警等级

| 等级 | 说明 | 触发条件示例 |
|------|------|-------------|
| critical | 紧急 | 负债率 > 100% |
| high | 高风险 | 高风险行为占比 > 80% |
| medium | 中风险 | 频繁交易 > 6次/月 |
| low | 低风险 | 轻微逆势操作 |

---

## 五、AI 洞察生成

### 5.1 AI 分析流程

```
用户画像数据 + 近期行为日志
        │
        ▼
   构建分析上下文
        │
        ▼
   调用 DeepSeek API
        │
        ▼
   解析 JSON 响应
        │
        ▼
   返回结构化洞察
```

### 5.2 AI 洞察输出格式

```python
{
    'title': '一句话概括用户金融行为特征',
    'summary': '50字以内简短总结',
    'analysis': '100-150字详细分析（优点和问题）',
    'suggestions': ['建议1', '建议2', '建议3'],
    'risk_alert': '高风险警告（如有）',
    'generated_by': 'ai',
    'generated_month': 24
}
```

### 5.3 示例输出

```json
{
  "title": "该用户是极度激进且非理性的冲动型投资者",
  "summary": "用户投资行为极度激进，风险容忍度极高，但决策高度冲动且非理性",
  "analysis": "优点在于用户具备高行动力与风险承担意愿。但问题突出：损失厌恶指数为0，表明对亏损毫无心理防备；过度自信指数高达0.85，决策严重依赖情绪而非分析。",
  "suggestions": [
    "强制设定单笔投资上限与止损线",
    "交易前完成风险评估清单",
    "将大部分资金转入低风险配置"
  ],
  "risk_alert": "警告：检测到极高风险行为模式，存在重大本金损失可能"
}
```

---

## 六、群体洞察

### 6.1 群体洞察生成

```python
def generate_cohort_insights(self, current_month: int) -> List[Dict]:
    """
    生成Z世代群体行为洞察
    
    洞察类型:
    - risk_profile: 风险画像类 (投资偏好两极分化等)
    - decision_pattern: 决策模式类 (追涨杀跌行为等)
    - behavioral_bias: 行为偏差类 (过度自信普遍等)
    """
```

### 6.2 群体洞察示例

```python
{
    'insight_type': 'risk_profile',
    'insight_category': 'investment',
    'title': 'Z世代投资者风险偏好呈两极分化',
    'description': '数据显示，45%的Z世代玩家表现出激进型投资风格，倾向高风险高回报；35%为保守型，优先资金安全；仅20%为稳健型。',
    'confidence_level': 0.85,
    'sample_size': 500,
    'generated_month': 24
}
```

---

## 七、数据库表结构

### 7.1 behavior_logs 表

```sql
CREATE TABLE behavior_logs (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    month INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    action_category TEXT,
    amount REAL,
    risk_score REAL,
    rationality_score REAL,
    market_condition TEXT,
    decision_context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7.2 behavior_profiles 表

```sql
CREATE TABLE behavior_profiles (
    session_id TEXT PRIMARY KEY,
    risk_preference TEXT,
    decision_style TEXT,
    loss_aversion REAL,
    overconfidence REAL,
    herding_tendency REAL,
    planning_ability REAL,
    action_count INTEGER,
    avg_risk_score REAL,
    avg_rationality REAL,
    last_updated_month INTEGER,
    updated_at TIMESTAMP
);
```

### 7.3 cohort_insights 表

```sql
CREATE TABLE cohort_insights (
    id INTEGER PRIMARY KEY,
    insight_type TEXT,
    insight_category TEXT,
    title TEXT,
    description TEXT,
    confidence_level REAL,
    sample_size INTEGER,
    generated_month INTEGER,
    created_at TIMESTAMP
);
```

---

## 八、API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/insights/personal/{session_id}` | GET | 获取个人洞察 |
| `/api/insights/statistics/{session_id}` | GET | 获取行为统计 |
| `/api/insights/cohort` | GET | 获取群体洞察 |
| `/api/insights/warnings/{session_id}` | GET | 获取行为预警 |
| `/api/insights/peer-comparison/{session_id}` | GET | 获取同龄人对比 |
| `/api/insights/evolution/{session_id}` | GET | 获取行为演变 |
| `/api/insights/ai/{session_id}` | GET | 生成AI洞察 |

---

## 九、配置常量

```python
# 风险偏好阈值
RISK_THRESHOLDS = {
    'conservative': (0, 0.4),
    'moderate': (0.4, 0.65),
    'aggressive': (0.65, 1.0)
}

# 决策风格中文映射
DECISION_STYLES = {
    'rational': '理性规划型',
    'impulsive': '冲动跟风型',
    'passive': '被动随缘型',
    'adaptive': '灵活应变型'
}

# 风险偏好中文映射
RISK_PREFERENCES = {
    'conservative': '保守型',
    'moderate': '稳健型',
    'aggressive': '激进型'
}
```

---

## 十、使用示例

### 10.1 记录用户行为

```python
from core.systems.behavior_insight_system import BehaviorInsightSystem

# 初始化
insight_system = BehaviorInsightSystem(db)

# 记录一次股票购买
insight_system.log_action(
    session_id='user_123',
    month=12,
    action_type='stock_buy',
    action_data={'amount': 50000, 'cash': 100000},
    market_state={'economic_phase': 'boom'}
)
```

### 10.2 获取用户画像

```python
# 分析画像
profile = insight_system.analyze_profile('user_123', current_month=12)

print(f"风险偏好: {profile['risk_preference']}")  # aggressive
print(f"决策风格: {profile['decision_style']}")  # impulsive
print(f"平均风险分: {profile['avg_risk_score']:.2f}")  # 0.82
```

### 10.3 生成 AI 洞察

```python
# 设置 AI 引擎
from core.ai.deepseek_engine import DeepSeekEngine
ai_engine = DeepSeekEngine()
insight_system.set_ai_engine(ai_engine)

# 生成洞察
import asyncio
insight = asyncio.run(insight_system.generate_ai_insight('user_123', 12))
print(insight['analysis'])
```

---

## 十一、扩展与优化

### 11.1 可扩展点

1. **更多行为特征指标**：如锚定效应、确认偏误等
2. **机器学习模型**：使用历史数据训练预测模型
3. **实时预警推送**：WebSocket 推送风险提醒
4. **社交比较功能**：与好友/排行榜用户对比

### 11.2 性能优化建议

1. 缓存热点用户画像（Redis）
2. 批量计算群体洞察（定时任务）
3. 索引优化（session_id + month 复合索引）

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2024-12 | 初始版本，基础画像分析 |
| 1.1 | 2025-01 | 添加 AI 洞察生成 |
| 1.2 | 2025-12 | 添加同龄人对比、行为演变分析 |
