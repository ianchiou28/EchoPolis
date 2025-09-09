# Echopolis 开发文档

## 项目概述

Echopolis (回声都市) 是一个超个人化AI驱动的社会金融模拟器，旨在为年轻用户提供一个安全的虚拟环境来学习和体验金融决策。

## 技术架构

### 后端架构
```
backend/
├── ai_agent/           # AI化身系统
│   ├── agent_brain.py  # 决策引擎
│   └── behavior.py     # 行为模式
├── economic_system/    # 经济系统
│   ├── currency_system.py  # 货币系统
│   └── market.py       # 市场模拟
├── event_system/       # 事件系统
│   └── event_engine.py # 事件引擎
├── api/               # API接口
│   ├── main.py        # FastAPI主应用
│   └── models.py      # 数据模型
└── core/              # 核心模块
    └── game_manager.py # 游戏管理器
```

### 前端架构
```
frontend/
├── app/               # Next.js App Router
├── components/        # React组件
│   ├── ui/           # 基础UI组件
│   ├── dashboard/    # 仪表盘组件
│   └── echo/         # 回响交互组件
├── lib/              # 工具库
│   ├── store/        # 状态管理
│   ├── api/          # API客户端
│   └── utils/        # 工具函数
└── styles/           # 样式文件
```

### AI模型架构
```
ai_models/
├── personality/       # 人格模型
│   └── big_five_model.py  # 大五人格模型
├── decision_engine/   # 决策引擎
│   └── agent_brain.py # AI大脑
├── nlp/              # 自然语言处理
└── behavioral_layer/ # 行为层
```

## 核心系统设计

### 1. AI化身系统

#### 人格建模
- 基于大五人格模型 (Big Five)
- 通过初始评估生成个性化AI化身
- 支持动态人格特质演化

#### 决策引擎
- 多因子加权决策矩阵
- 人格特质影响决策偏好
- 状态和环境因素调节

#### 信任机制
- 动态信任度系统
- 基于历史表现调整信任权重
- 影响AI对玩家建议的采纳程度

### 2. 经济系统

#### 双轨制货币
- **信用点 (CP)**: 主要流通货币
- **启示结晶 (IC)**: 元成长货币

#### 宏观经济模拟
- 动态利率调节
- 通胀/通缩周期
- 经济周期模拟

#### 市场系统
- 股票市场模拟
- 房地产市场
- 商品期货市场

### 3. 事件系统

#### 事件分类
- **宏观事件**: 经济政策、金融危机
- **行业事件**: 技术突破、监管变化
- **个人事件**: 职业发展、健康变化
- **黑/白天鹅**: 极端概率事件

#### 触发机制
- 概率触发
- 条件触发
- 玩家行为触发

### 4. 回响系统

#### 干预类型
- **启发式**: 引导思考
- **建议式**: 直接建议
- **指令式**: 明确指令
- **情感式**: 鼓励/警告

#### NLP处理
- 意图识别
- 情感分析
- 关键词提取

## 开发环境设置

### 后端环境

1. **Python环境**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **数据库设置**
```bash
# PostgreSQL
createdb echopolis

# Redis
redis-server
```

3. **启动后端**
```bash
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端环境

1. **Node.js环境**
```bash
cd frontend
npm install
```

2. **启动前端**
```bash
npm run dev
```

### 环境变量

创建 `.env` 文件：
```env
# 数据库
DATABASE_URL=postgresql://user:password@localhost/echopolis
REDIS_URL=redis://localhost:6379

# AI模型
OPENAI_API_KEY=your_openai_api_key

# 安全
SECRET_KEY=your_secret_key

# 前端
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## API文档

### 认证接口

#### 用户注册
```http
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

#### 用户登录
```http
POST /auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

### 游戏接口

#### 获取AI化身状态
```http
GET /agent/status
Authorization: Bearer <token>
```

#### 发送回响干预
```http
POST /agent/intervention
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "string",
  "intervention_type": "advisory"
}
```

#### 获取经济指标
```http
GET /economy/indicators
```

## 数据库设计

### 核心表结构

#### 用户表 (users)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
```

#### AI化身表 (agents)
```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    personality_profile JSONB NOT NULL,
    traits TEXT[] NOT NULL,
    current_state JSONB NOT NULL,
    trust_level FLOAT DEFAULT 50.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 交易记录表 (transactions)
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    transaction_type VARCHAR(50) NOT NULL,
    currency_type VARCHAR(10) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    description TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    balance_after DECIMAL(15,2)
);
```

## 部署指南

### Docker部署

1. **构建镜像**
```bash
# 后端
docker build -t echopolis-backend ./backend

# 前端
docker build -t echopolis-frontend ./frontend
```

2. **使用Docker Compose**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/echopolis
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=echopolis
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

### 云部署

#### AWS部署
- **ECS**: 容器化部署
- **RDS**: PostgreSQL数据库
- **ElastiCache**: Redis缓存
- **CloudFront**: CDN加速

#### 阿里云部署
- **容器服务**: Kubernetes部署
- **RDS**: 云数据库
- **Redis**: 云缓存
- **CDN**: 内容分发

## 测试

### 后端测试
```bash
cd backend
pytest tests/ -v --cov=.
```

### 前端测试
```bash
cd frontend
npm run test
npm run test:e2e
```

## 性能优化

### 后端优化
- 数据库索引优化
- Redis缓存策略
- 异步任务处理
- API响应压缩

### 前端优化
- 代码分割
- 图片优化
- 缓存策略
- 懒加载

## 监控和日志

### 应用监控
- **Prometheus**: 指标收集
- **Grafana**: 可视化监控
- **Sentry**: 错误追踪

### 日志管理
- **ELK Stack**: 日志收集和分析
- **结构化日志**: JSON格式
- **日志轮转**: 防止磁盘占满

## 安全考虑

### 数据安全
- 密码哈希存储
- JWT令牌认证
- API限流
- 输入验证

### 隐私保护
- 数据脱敏
- 用户同意机制
- 数据删除权
- 透明度报告

## 贡献指南

### 代码规范
- **Python**: PEP 8
- **TypeScript**: ESLint + Prettier
- **Git**: Conventional Commits

### 提交流程
1. Fork项目
2. 创建功能分支
3. 编写测试
4. 提交代码
5. 创建Pull Request

## 常见问题

### Q: 如何重置AI化身？
A: 目前需要通过API调用或数据库操作，未来版本将提供UI界面。

### Q: 游戏数据如何备份？
A: 使用PostgreSQL的pg_dump工具进行定期备份。

### Q: 如何扩展新的事件类型？
A: 在event_engine.py中添加新的事件定义，并更新相应的触发逻辑。

## 路线图

### v1.1 (Q2 2024)
- [ ] 完整的社交系统
- [ ] 高级AI决策模型
- [ ] 移动端适配

### v1.2 (Q3 2024)
- [ ] 多人协作模式
- [ ] 高级数据分析
- [ ] 第三方集成

### v2.0 (Q4 2024)
- [ ] VR/AR支持
- [ ] 机器学习优化
- [ ] 国际化支持

## 联系方式

- **项目负责人**: [联系邮箱]
- **技术支持**: [技术邮箱]
- **问题反馈**: [GitHub Issues]