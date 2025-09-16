"""
Echopolis 一键启动脚本
同时启动前后端并自动打开浏览器
"""
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
        print(f"[OK] Node.js version: {result.stdout.strip()}")
        return True
    except:
        print("[ERROR] Node.js not found. Please install: https://nodejs.org/")
        return False

def start_backend():
    """启动后端服务器"""
    print("[BACKEND] Starting backend server...")
    try:
        subprocess.run([sys.executable, 'web_minimal.py'], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n[STOP] Backend server stopped")

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
        print("[ERROR] Frontend directory not found")
        return
    
    print("[FRONTEND] Starting frontend server...")
    
    # 检查并安装依赖
    if not (frontend_path / 'node_modules').exists():
        print("[INSTALL] Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], cwd=frontend_path, shell=True)
    
    # 启动前端
    try:
        subprocess.run(['npm', 'run', 'dev'], cwd=frontend_path, shell=True)
    except KeyboardInterrupt:
        print("\n[STOP] Frontend server stopped")

def open_browser():
    """等待服务启动后打开浏览器"""
    time.sleep(8)  # 等待前后端都启动
    print("[BROWSER] Opening browser...")
    webbrowser.open('http://localhost:3000')

def main():
    print("[START] Starting Echopolis Application")
    print("=" * 50)
    
    # 检查Node.js
    if not check_node():
        input("Press Enter to exit...")
        return
    
    print("[INFO] Service URLs:")
    print("   Backend API: http://localhost:8002")
    print("   Frontend UI: http://localhost:3000")
    print("   API Docs: http://localhost:8002/docs")
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
        
        print("[OK] Services starting...")
        print("[INFO] Press Ctrl+C to stop all services")
        
        # 保持主线程运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[STOP] Stopping all services...")
        print("[BYE] Echopolis closed")

if __name__ == "__main__":
    main()