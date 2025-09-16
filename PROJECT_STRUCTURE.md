# 🏗️ Echopolis 项目结构整理

## 📁 新的项目结构

```
EchoPolis/
├── backend_new/           # 🐍 Python FastAPI 后端
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py         # API路由定义
│   │   ├── models/
│   │   │   └── requests.py       # 请求模型
│   │   ├── services/
│   │   │   └── game_service.py   # 游戏业务逻辑
│   │   └── main.py              # 应用入口
│   ├── requirements.txt         # 依赖包
│   └── README.md               # 后端说明
│
├── frontend_vue/          # 🌐 Vue3 前端
│   ├── src/
│   │   ├── components/          # 可复用组件
│   │   ├── views/              # 页面组件
│   │   │   ├── Home.vue        # 首页 - 创建AI化身
│   │   │   └── Game.vue        # 游戏主界面
│   │   ├── stores/             # Pinia状态管理
│   │   │   └── game.js         # 游戏状态store
│   │   ├── router/             # Vue Router配置
│   │   ├── App.vue             # 根组件
│   │   ├── main.js             # 应用入口
│   │   └── style.css           # 全局样式
│   ├── package.json            # 依赖配置
│   ├── vite.config.js          # Vite配置
│   ├── index.html              # HTML入口
│   └── README.md               # 前端说明
│
├── core/                  # 🧠 核心游戏系统 (共享)
│   ├── ai/                     # AI引擎
│   ├── avatar/                 # AI化身系统
│   ├── systems/                # 游戏系统
│   └── entities/               # 游戏实体
│
└── 旧文件/                # 📦 原有文件 (保留)
    ├── frontend/               # 原Vue前端
    ├── backend/                # 原后端
    ├── web/                    # 原Web文件
    └── ...                     # 其他原有文件
```

## 🚀 启动方式

### 后端启动
```bash
cd backend_new
pip install -r requirements.txt
python app/main.py
# 运行在 http://localhost:8000
```

### 前端启动
```bash
cd frontend_vue
npm install
npm run dev
# 运行在 http://localhost:3000
```

## 🔄 数据流

```
Vue3前端 (3000) ←→ FastAPI后端 (8000) ←→ 核心系统 ←→ DeepSeek AI
     ↓                    ↓                ↓            ↓
   用户界面            API接口          游戏逻辑      AI决策
```

## 🎯 架构优势

### 🔧 模块化设计
- **前后端分离**: 独立开发和部署
- **清晰分层**: API层、服务层、数据层
- **代码复用**: 核心系统可被多个前端使用

### 🚀 现代化技术栈
- **后端**: Python + FastAPI + Pydantic
- **前端**: Vue3 + Vite + Pinia + Vue Router
- **AI**: DeepSeek API集成

### 📱 用户体验
- **响应式设计**: 适配各种屏幕
- **实时交互**: 流畅的用户界面
- **状态管理**: 统一的数据流

## 🔧 开发建议

1. **使用新结构**: 在 `backend_new/` 和 `frontend_vue/` 中开发
2. **保留旧文件**: 作为参考和备份
3. **共享核心**: `core/` 目录被前后端共同使用
4. **API优先**: 通过API接口进行前后端通信

## 📝 下一步

1. 测试新架构的完整功能
2. 逐步迁移旧功能到新结构
3. 优化性能和用户体验
4. 添加更多游戏功能