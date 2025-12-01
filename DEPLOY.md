# EchoPolis 部署指南 (Linux)

本指南将帮助你在 Linux 服务器（如 Ubuntu/CentOS）上部署 EchoPolis 项目。

## 1. 环境准备

确保服务器已安装以下软件：
- **Python 3.10+**
- **Node.js 18+** (推荐使用 NodeSource 安装最新版)
- **Nginx**
- **Git**

### Ubuntu 安装示例 (更新 Node.js 到 18+):
```bash
# 1. 彻底移除旧版本及冲突库 (关键步骤)
sudo apt remove nodejs npm libnode-dev libnode72 -y
sudo apt autoremove -y

# 2. 设置 NodeSource 仓库 (Node.js 20)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# 3. 安装软件
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs nginx git -y

# 4. 验证版本
node -v  # 应显示 v18.x 或 v20.x
```

## 2. 获取代码

```bash
cd /var/www
# 克隆特定分支 (例如 change-style)
git clone -b change-style <your-repo-url> echopolis
cd echopolis
```

## 3. 后端部署 (Backend)

### 3.1 创建虚拟环境并安装依赖
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.2 测试运行
```bash
# 确保在 backend 目录下
python3 start_backend_only.py
# 如果看到 "Uvicorn running on http://0.0.0.0:8000" 说明成功
# 按 Ctrl+C 停止
```

### 3.3 配置 Systemd 服务 (后台运行)
直接复制并运行以下命令来创建服务文件 (无需使用编辑器):

```bash
sudo bash -c 'cat > /etc/systemd/system/echopolis-backend.service <<EOF
[Unit]
Description=EchoPolis Backend
After=network.target

[Service]
User=root
WorkingDirectory=/root/echopolis/backend
ExecStart=/root/echopolis/backend/venv/bin/python3 start_backend_only.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF'
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl start echopolis-backend
sudo systemctl enable echopolis-backend
```

## 4. 前端部署 (Frontend)

### 4.1 安装依赖并构建
```bash
cd ../frontend
npm install
npm run build
```
构建完成后，会在 `frontend/dist` 目录下生成静态文件。

## 5. Nginx 配置

配置 Nginx 以提供前端静态文件并反向代理 API 请求。

直接复制并运行以下命令 (请先将 `your_domain_or_ip` 替换为你的实际 IP 或域名，或者直接使用 `_` 代表所有域名):

```bash
# 设置你的域名或IP
DOMAIN_NAME="finai.org.cn"

# 使用 tee 命令写入配置 (自动处理权限)
sudo tee /etc/nginx/sites-available/echopolis > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    # 前端静态文件
    location / {
        root /root/echopolis/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF
```

启用配置并重启 Nginx:
```bash
# 1. 移除默认配置 (避免端口冲突)
sudo rm -f /etc/nginx/sites-enabled/default

# 2. 创建软链接 (使用 -sf 强制覆盖，避免重复或报错)
sudo ln -sf /etc/nginx/sites-available/echopolis /etc/nginx/sites-enabled/

# 3. 测试配置
sudo nginx -t
# 如果显示 "syntax is ok" 和 "test is successful" (即使有 warn 警告也可以忽略)，则继续

# 4. 重启服务
sudo systemctl restart nginx
```

## 6. 验证

访问 `http://your_domain_or_ip`。
你应该会看到 "正在初始化评委体验环境..." 的加载页面，随后自动进入游戏主界面。

## 7. 常见问题

### 🔴 遇到 500 Internal Server Error?

如果访问网站显示 500 错误，通常是因为**前端构建失败**导致文件缺失，或者**权限不足**。请依次执行以下命令修复：

1. **检查前端文件是否存在**:
   ```bash
   ls -l /var/www/echopolis/frontend/dist/index.html
   ```
   *如果报错 "No such file"，说明前端构建失败。请回到第 4 步重新运行 `npm install` 和 `npm run build`。*

2. **修复文件权限 (关键)**:
   由于你的项目在 `/root/echopolis`，默认情况下 Nginx (www-data) 无法访问 `/root` 目录。
   你需要赋予 Nginx 访问权限 (注意：这会允许其他用户访问你的 root 目录列表，请确保安全)：
   ```bash
   # 允许 Nginx 进入 /root 目录
   sudo chmod o+x /root
   
   # 确保项目目录可读
   sudo chmod -R 755 /root/echopolis
   ```

3. **查看具体报错**:
   如果上述步骤无效，查看 Nginx 日志寻找原因：
   ```bash
   sudo tail -n 20 /var/log/nginx/error.log
   ```

- **为什么不使用 `start.py`?**: 
  `start.py` 是为本地开发设计的，它会同时启动后端和**前端开发服务器** (`npm run dev`)。在服务器部署时，我们使用 Nginx 托管构建好的前端静态文件（性能更高），因此只需要单独启动后端服务 (`start_backend_only.py`)。

- **权限问题**: 确保 Nginx 有权限读取 `/var/www/echopolis/frontend/dist` 目录。
  ```bash
  sudo chown -R www-data:www-data /var/www/echopolis/frontend/dist
  sudo chmod -R 755 /var/www/echopolis
  ```
- **端口冲突**: 确保 8000 端口未被占用。
- **数据库**: 默认使用 SQLite，数据文件位于 `backend/core/database/game.db`。确保该目录有写入权限。

---
**评委体验模式说明**:
当前配置已启用自动登录功能。访问根路径 `/` 时，系统会自动创建一个独立的评委账号并直接进入游戏，无需手动注册。

## 8. 更新代码

当你有新代码提交到 GitHub 后，可以在服务器上执行以下命令更新：

```bash
cd /root/echopolis
# 拉取指定分支最新代码 (例如 change-style)
# 如果遇到 "local changes ... overwritten by merge" 错误，可以强制覆盖本地修改：
git checkout .
git pull origin change-style

# 如果有后端依赖变更
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart echopolis-backend

# 如果有前端变更
cd ../frontend
npm install
npm run build
```
