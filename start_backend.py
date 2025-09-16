"""
启动后端服务器
"""
import sys
import os
import subprocess

def start_backend():
    backend_path = os.path.join(os.path.dirname(__file__), 'backend_new')
    main_file = os.path.join(backend_path, 'app', 'main.py')
    
    print("🚀 启动Echopolis后端服务器...")
    print(f"📁 后端路径: {backend_path}")
    print(f"🐍 主文件: {main_file}")
    print("🌐 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("-" * 50)
    
    # 切换到后端目录并启动
    os.chdir(backend_path)
    subprocess.run([sys.executable, 'app/main.py'])

if __name__ == "__main__":
    start_backend()