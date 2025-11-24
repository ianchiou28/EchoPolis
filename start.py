import subprocess
import time
import sys
import os

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    backend_process = subprocess.Popen(
        [sys.executable, "backend/start_backend_only.py"],
        cwd=os.getcwd()
    )
    return backend_process

def start_frontend():
    """启动前端服务"""
    print("🎨 启动前端服务...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=os.path.join(os.getcwd(), "frontend"),
        shell=True
    )
    return frontend_process

if __name__ == "__main__":
    print("=" * 50)
    print("🌆 FinAI - 金融模拟沙盘")
    print("=" * 50)
    
    backend = start_backend()
    time.sleep(3)
    
    frontend = start_frontend()
    
    print("\n✅ 服务启动完成！")
    print("📱 前端地址: http://localhost:3001")
    print("🔧 后端地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("\n按 Ctrl+C 停止所有服务")
    
    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务...")
        backend.terminate()
        frontend.terminate()
        print("✅ 服务已停止")