# FinAI 后端 API

基于 FastAPI 的 FinAI 游戏后端服务。

## 🚀 快速启动

### 安装依赖
```bash
cd backend_new
pip install -r requirements.txt
```

### 启动服务器
```bash
python app/main.py
```

服务器将在 `http://localhost:8000` 启动

## 📁 项目结构

```
backend_new/
├── app/
│   ├── api/
│   │   └── routes.py          # API路由定义
│   ├── models/
│   │   └── requests.py        # 请求模型
│   ├── services/
│   │   └── game_service.py    # 游戏业务逻辑
│   └── main.py               # 应用入口
├── requirements.txt          # 依赖包
└── README.md                # 说明文档
```

## 🔌 API 接口

### 基础接口
- `GET /` - 服务状态
- `GET /api/mbti-types` - 获取MBTI类型
- `GET /api/fate-wheel` - 获取命运轮盘

### 游戏接口
- `POST /api/create-avatar` - 创建AI化身
- `POST /api/generate-situation` - 生成决策情况
- `POST /api/echo` - 发送意识回响
- `POST /api/auto-decision` - AI自主决策

## 🎯 特性

- **模块化设计**: 清晰的分层架构
- **AI集成**: 支持DeepSeek AI引擎
- **降级机制**: AI不可用时自动降级到规则模式
- **CORS支持**: 支持跨域请求
- **类型安全**: 使用Pydantic进行数据验证