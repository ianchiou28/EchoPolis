#!/usr/bin/env python3
"""
EchoPolis Unity后端启动脚本
"""
import sys
import os
import subprocess
import time
import requests

# 添加项目根目录到Python路径
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import websockets
        import pydantic
        print("Python dependencies check passed")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_backend():
    """启动后端服务"""
    print("Starting EchoPolis Unity Backend Service...")
    
    # 切换到backend目录
    backend_dir = os.path.join(project_root, "backend")
    os.chdir(backend_dir)
    
    # 启动FastAPI服务
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ]
    
    try:
        process = subprocess.Popen(cmd)
        print("Waiting for service to start...")
        time.sleep(3)
        
        # 检查服务是否启动成功
        try:
            response = requests.get("http://localhost:8000/api/unity/health", timeout=5)
            if response.status_code == 200:
                print("Backend service started successfully!")
                print("API Address: http://localhost:8000")
                print("API Docs: http://localhost:8000/docs")
                print("Unity API: http://localhost:8000/api/unity")
                print("\nUnity Client Configuration:")
                print("   API Base URL: http://localhost:8000/api/unity")
                print("\nAvailable API Endpoints:")
                print("   POST /api/unity/auth/login")
                print("   POST /api/unity/avatar/create")
                print("   GET  /api/unity/game/state/{user_id}")
                print("   GET  /api/unity/game/situation/{user_id}")
                print("   POST /api/unity/game/decision")
                print("   WS   /api/unity/ws/{user_id}")
                print("\nTest Command:")
                print("   curl http://localhost:8000/api/unity/health")
                print("\nPress Ctrl+C to stop service")
                
                # 保持服务运行
                process.wait()
            else:
                print("Service startup failed")
                process.terminate()
        except requests.exceptions.RequestException:
            print("Cannot connect to service")
            process.terminate()
            
    except KeyboardInterrupt:
        print("\nStopping service...")
        process.terminate()
        print("Service stopped")
    except Exception as e:
        print(f"Startup failed: {e}")

def main():
    print("EchoPolis Unity Backend Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Start backend
    start_backend()

if __name__ == "__main__":
    main()