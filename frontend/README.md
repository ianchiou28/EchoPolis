# Echopolis Vue3 前端

基于Vue3 + Vite的Echopolis游戏前端界面。

## 🚀 快速开始

### 安装依赖
```bash
cd frontend_vue
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## 🏗️ 项目结构

```
frontend_vue/
├── src/
│   ├── components/     # 可复用组件
│   ├── views/         # 页面组件
│   │   ├── Home.vue   # 首页 - 创建AI化身
│   │   └── Game.vue   # 游戏主界面
│   ├── stores/        # Pinia状态管理
│   │   └── game.js    # 游戏状态store
│   ├── router/        # Vue Router配置
│   ├── App.vue        # 根组件
│   └── main.js        # 应用入口
├── package.json
└── vite.config.js     # Vite配置
```

## 🎮 功能特性

### ✅ 已实现
- [x] AI化身创建界面
- [x] MBTI人格类型选择
- [x] 命运轮盘系统
- [x] 游戏状态显示
- [x] 意识回响输入
- [x] AI决策结果展示
- [x] 响应式设计

## 🔧 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 快速构建工具
- **Vue Router** - 官方路由管理器
- **Pinia** - 状态管理库
- **Axios** - HTTP客户端

## 🌐 API集成

前端通过Axios与FastAPI后端通信：

- `GET /api/mbti-types` - 获取MBTI类型
- `POST /api/create-avatar` - 创建AI化身
- `POST /api/generate-situation` - 生成情况
- `POST /api/echo` - 发送意识回响
- `POST /api/auto-decision` - AI自主决策