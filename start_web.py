#!/usr/bin/env python3
"""
Echopolis Web版本启动器
"""
import os
import sys
import webbrowser
import time
import threading

def start_web_version():
    print("Starting Echopolis Web Version")
    print("=" * 40)
    
    # 启动服务器
    server_thread = threading.Thread(target=start_server_thread)
    server_thread.daemon = True
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    # 自动打开浏览器
    try:
        webbrowser.open('http://localhost:8000/index.html')
        print("[OK] Browser opened automatically")
    except:
        print("[INFO] Please open browser: http://localhost:8000/index.html")
    
    print("\n[FEATURES]")
    print("- Perfect Chinese support")
    print("- No installation required")
    print("- Cross-platform compatible")
    print("- Real-time AI interaction")
    print("\nPress Ctrl+C to stop server")
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nGame exited")

def start_server_thread():
    """在单独线程中启动服务器"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from web.server import start_server
    start_server(8000)

if __name__ == "__main__":
    start_web_version()