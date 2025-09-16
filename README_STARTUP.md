# 🚀 Echopolis 一键启动指南

## 🎯 最简单的启动方式

### 方式1: 双击启动 (推荐)
```
双击 start_app.bat 文件
```

### 方式2: 命令行启动
```bash
python start_app.py
```

## 🔧 启动过程

1. **检查环境** - 自动检查Node.js是否安装
2. **启动后端** - 启动FastAPI服务器 (端口8000)
3. **启动前端** - 启动Vue开发服务器 (端口3000)
4. **自动安装** - 首次运行自动安装前端依赖
5. **打开浏览器** - 自动打开游戏界面

## 🌐 访问地址

- **游戏界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## ⚡ 快速体验

1. **双击** `start_app.bat`
2. **等待** 服务启动 (约10秒)
3. **浏览器** 自动打开游戏
4. **创建** AI化身开始游戏

## 🛑 停止服务

在命令行窗口按 `Ctrl+C` 停止所有服务

## 🔧 故障排除

### Node.js未安装
- 下载安装: https://nodejs.org/
- 选择LTS版本

### 端口被占用
- 关闭占用8000或3000端口的程序
- 或修改配置文件中的端口

### 前端依赖安装失败
```bash
cd frontend_vue
npm install --registry https://registry.npmmirror.com
```

## 📝 开发模式

如需分别启动前后端进行开发:

**后端**:
```bash
python web_minimal.py
```

**前端**:
```bash
cd frontend_vue
npm run dev
```

现在你可以一键启动完整的Echopolis应用了！🎉