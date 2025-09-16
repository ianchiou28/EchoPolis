"""
同时启动前后端服务器
"""
import sys
import os
import subprocess
import threading
import time

# 设置UTF-8编码
os.environ['PYTHONIOENCODING'] = 'utf-8'


def start_backend():
    """启动后端服务器"""
    backend_path = os.path.join(os.path.dirname(__file__), 'backend_new')
    print(f"📁 切换到后端目录: {backend_path}")
    
    # 检查依赖
    requirements_file = os.path.join(backend_path, 'requirements.txt')
    if os.path.exists(requirements_file):
        print("📦 检查后端依赖...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         cwd=backend_path, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("⚠️  依赖安装可能有问题，继续启动...")
    
    os.chdir(backend_path)
    print("🚀 启动后端服务器...")
    subprocess.run([sys.executable, 'app/main.py'])

def start_frontend():
    """启动前端服务器"""
    time.sleep(3)  # 等待后端启动
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend_vue')
    
    print(f"📁 切换到前端目录: {frontend_path}")
    
    # 检查Node.js是否安装
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True, shell=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 未找到Node.js，请先安装Node.js")
        print("   下载地址: https://nodejs.org/")
        return
    
    os.chdir(frontend_path)
    
    # 检查依赖
    if not os.path.exists('node_modules'):
        print("📦 安装前端依赖...")
        try:
            subprocess.run(['npm', 'install'], check=True, shell=True)
        except subprocess.CalledProcessError:
            print("❌ npm install 失败")
            return
    
    print("🚀 启动前端开发服务器...")
    try:
        subprocess.run(['npm', 'run', 'dev'], shell=True)
    except subprocess.CalledProcessError:
        print("❌ 前端启动失败")

def main():
    print("🚀 启动Echopolis完整应用...")
    print("🐍 后端: http://localhost:8000")
    print("🌐 前端: http://localhost:3000")
    print("📖 API文档: http://localhost:8000/docs")
    print("-" * 50)
    
    # 创建线程
    backend_thread = threading.Thread(target=start_backend)
    frontend_thread = threading.Thread(target=start_frontend)
    
    # 启动线程
    backend_thread.start()
    frontend_thread.start()
    
    # 等待线程完成
    backend_thread.join()
    frontend_thread.join()

if __name__ == "__main__":
    main()