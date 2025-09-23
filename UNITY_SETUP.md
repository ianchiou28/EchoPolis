# 🎮 Unity前端设置指南

## 📋 Unity项目配置

### 1. 创建Unity项目
- 打开Unity Hub
- 选择 "New Project"
- 模板选择 "2D Core"
- 项目位置设为: `EchoPolis/UnityFrontend`
- Unity版本: 2022.3 LTS

### 2. 必需包安装
在Package Manager中安装:
- **TextMeshPro** (UI文本显示)
- **UI Toolkit** (现代UI系统)

### 3. 项目设置
```
Player Settings:
- Company Name: EchoPolis
- Product Name: Echopolis
- Default Icon: (自定义图标)
- Resolution: 1920x1080
- Fullscreen Mode: Windowed
```

## 🏗️ 场景结构

### MainMenu场景
```
MainMenu
├── Canvas
│   ├── CreateAvatarPanel
│   │   ├── MBTIDropdown
│   │   ├── NameInput
│   │   └── CreateButton
│   └── StartGameButton
├── APIClient (Prefab)
└── GameManager (Prefab)
```

### GameScene场景
```
GameScene
├── Canvas
│   ├── StatusPanel
│   ├── EchoPanel
│   └── ResponsePanel
├── APIClient (Prefab)
└── GameManager (Prefab)
```

## 🔧 脚本配置

### APIClient设置
1. 创建空GameObject命名为"APIClient"
2. 添加APIClient.cs脚本
3. 设置Base URL为: `http://localhost:8000`
4. 制作成Prefab

### GameManager设置
1. 创建空GameObject命名为"GameManager"  
2. 添加GameManager.cs脚本
3. 制作成Prefab

## 🌐 HTTP通信架构

### 请求流程
```
Unity UI → GameManager → APIClient → FastAPI后端
    ↓         ↓           ↓            ↓
  用户交互   游戏逻辑    HTTP请求     业务处理
```

### API端点
- `POST /api/avatar/create` - 创建AI化身
- `GET /api/avatar/status` - 获取状态
- `POST /api/avatar/echo` - 发送意识回响

## 🚀 开发流程

1. **启动后端服务**
   ```bash
   cd backend_new
   python app/main.py
   ```

2. **在Unity中测试**
   - 运行MainMenu场景
   - 创建AI化身
   - 测试与后端通信

3. **调试技巧**
   - 查看Unity Console日志
   - 使用Postman测试API
   - 检查网络连接状态

## 📝 注意事项

- 确保后端服务运行在localhost:8000
- Unity需要允许HTTP请求(非HTTPS)
- 测试时关闭防火墙可能的阻拦
- 使用JSON格式进行数据交换