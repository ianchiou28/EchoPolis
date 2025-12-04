# 多项目部署指南

本指南说明如何在同一个域名下部署两个项目：
- **EchoPolis**: `https://yourdomain.com/echopolis/`
- **Wide-Research-for-Finance**: `https://yourdomain.com/information/`

## 1. 项目结构

```
/root/
├── EchoPolis/
│   ├── frontend/
│   │   └── dist/          # 前端构建输出
│   └── backend/
└── Wide-Research-for-Finance/
    ├── frontend/
    │   └── dist/          # 前端构建输出
    └── web_app.py
```

## 2. 修改前端 base path

### 2.1 EchoPolis (子路径 /echopolis/)

修改 `/root/EchoPolis/frontend/vite.config.js`:

```javascript
export default defineConfig({
  base: '/echopolis/',  // 添加这一行
  // ... 其他配置
})
```

### 2.2 Wide-Research-for-Finance (子路径 /information/)

修改 `/root/Wide-Research-for-Finance/frontend/vite.config.js`:

```javascript
export default defineConfig({
  base: '/information/',  // 添加这一行
  // ... 其他配置
})
```

或者如果是 Vue CLI 项目，修改 `vue.config.js`:

```javascript
module.exports = {
  publicPath: '/information/',
  // ... 其他配置
}
```

**重要**: 修改后需要重新构建前端！

## 3. 构建前端

### 3.1 构建 EchoPolis 前端

```bash
cd /root/EchoPolis/frontend
npm install
npm run build
```

### 3.2 构建 Wide-Research-for-Finance 前端

```bash
cd /root/Wide-Research-for-Finance/frontend
npm install
npm run build
```

## 4. 配置后端

### 4.1 启动 EchoPolis 后端 (端口 8000)

```bash
cd /root/EchoPolis
# 使用 systemd 或 pm2 管理
python start.py
# 或
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### 4.2 启动 Wide-Research-for-Finance 后端 (端口 5000)

```bash
cd /root/Wide-Research-for-Finance
python web_app.py
# 默认应该运行在 5000 端口
```

## 5. 配置 Nginx

### 5.1 复制配置文件

```bash
sudo cp /root/EchoPolis/nginx-multi-site.conf /etc/nginx/sites-available/multi-site
```

### 5.2 修改配置

编辑 `/etc/nginx/sites-available/multi-site`：
- 将 `yourdomain.com` 替换为你的实际域名
- 确认后端端口号正确（EchoPolis: 8000, Finance: 5000）

### 5.3 启用站点

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/multi-site /etc/nginx/sites-enabled/

# 删除默认站点（如果有冲突）
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重新加载 Nginx
sudo systemctl reload nginx
```

## 6. 配置 HTTPS (推荐)

使用 Certbot 自动获取 Let's Encrypt 证书：

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书并自动配置 Nginx
sudo certbot --nginx -d yourdomain.com

# 测试自动续期
sudo certbot renew --dry-run
```

## 7. 使用 systemd 管理后端服务

### 7.1 创建 EchoPolis 服务

创建文件 `/etc/systemd/system/echopolis.service`:

```ini
[Unit]
Description=EchoPolis Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/EchoPolis
ExecStart=/usr/bin/python3 start.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 7.2 创建 Finance 服务

创建文件 `/etc/systemd/system/finance.service`:

```ini
[Unit]
Description=Finance Research Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/Wide-Research-for-Finance
ExecStart=/usr/bin/python3 web_app.py
Restart=always
RestartSec=5
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
```

### 7.3 启动服务

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start echopolis
sudo systemctl start finance

# 设置开机自启
sudo systemctl enable echopolis
sudo systemctl enable finance

# 查看状态
sudo systemctl status echopolis
sudo systemctl status finance
```

## 8. 验证部署

打开浏览器访问：
- `https://yourdomain.com/echopolis/` - 应该看到 EchoPolis
- `https://yourdomain.com/information/` - 应该看到金融信息聚合平台
- `https://yourdomain.com/` - 会自动重定向到 `/echopolis/`

## 9. 常见问题

### Q: 前端页面刷新后 404？
A: 确保 Nginx 配置中有 `try_files $uri $uri/ /echopolis/index.html;`（对于 information 是 `/information/index.html`）

### Q: API 请求失败？
A: 
1. 检查后端服务是否运行：`sudo systemctl status echopolis`
2. 检查端口是否正确
3. 检查前端 API 请求路径是否正确

### Q: 子路径项目静态资源加载失败？
A: 确保前端构建时设置了正确的 `base` 路径

### Q: 查看 Nginx 错误日志
```bash
sudo tail -f /var/log/nginx/error.log
```

## 10. 快速部署脚本

创建 `/root/deploy.sh`:

```bash
#!/bin/bash

echo "=== 部署 EchoPolis ==="
cd /root/EchoPolis/frontend
npm install
npm run build

echo "=== 部署 Finance ==="
cd /root/Wide-Research-for-Finance/frontend
npm install
npm run build

echo "=== 重启服务 ==="
sudo systemctl restart echopolis
sudo systemctl restart finance
sudo systemctl reload nginx

echo "=== 部署完成 ==="
```

运行：`chmod +x /root/deploy.sh && /root/deploy.sh`
