"""
Echopolis 一键启动脚本
同时启动前后端并自动打开浏览器
"""
import sys
import os

# 设置UTF-8编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

import sys
import os
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

def check_node():
    """检查Node.js是否安装"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
        print(f"✅ Node.js版本: {result.stdout.strip()}")
        return True
    except:
        print("❌ 未找到Node.js，请先安装: https://nodejs.org/")
        return False

def start_backend():
    """启动后端服务器"""
    print("🐍 启动后端服务器...")
    try:
        subprocess.run([sys.executable, 'web_minimal.py'], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n🛑 后端服务器已停止")

def start_frontend():
    """启动前端服务器"""
    time.sleep(3)  # 等待后端启动
    
    frontend_path = Path('frontend_vue')
    if not frontend_path.exists():
        # 尝试其他可能的前端目录
        for possible_path in ['frontend', 'web', 'client']:
            if Path(possible_path).exists():
                frontend_path = Path(possible_path)
                break
    if not frontend_path.exists():
        print("❌ 前端目录不存在")
        return
    
    print("🌐 启动前端服务器...")
    
    # 检查并安装依赖
    if not (frontend_path / 'node_modules').exists():
        print("📦 安装前端依赖...")
        subprocess.run(['npm', 'install'], cwd=frontend_path, shell=True)
    
    # 启动前端
    try:
        subprocess.run(['npm', 'run', 'dev'], cwd=frontend_path, shell=True)
    except KeyboardInterrupt:
        print("\n🛑 前端服务器已停止")

def open_browser():
    """等待服务启动后打开浏览器"""
    time.sleep(8)  # 等待前后端都启动
    print("🌐 正在打开浏览器...")
    webbrowser.open('http://localhost:3000')

def main():
    print("🚀 启动Echopolis完整应用")
    print("=" * 50)
    
    # 检查Node.js
    if not check_node():
        input("按Enter键退出...")
        return
    
    print("🎯 启动信息:")
    print("   后端API: http://localhost:8008")
    print("   前端界面: http://localhost:3000")
    print("   API文档: http://localhost:8002/docs")
    print("=" * 50)
    
    # 创建线程
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    
    try:
        # 启动后端
        backend_thread.start()
        
        # 启动前端
        frontend_thread.start()
        
        # 启动浏览器
        browser_thread.start()
        
        print("✅ 服务启动中...")
        print("💡 按 Ctrl+C 停止所有服务")
        
        # 保持主线程运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 正在停止所有服务...")
        print("👋 Echopolis已关闭")

if __name__ == "__main__":
    main()