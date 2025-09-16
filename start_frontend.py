"""
启动前端开发服务器
"""
import sys
import os
import subprocess

def start_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend_vue')
    
    print("🌐 启动Echopolis前端开发服务器...")
    print(f"📁 前端路径: {frontend_path}")
    print("🚀 服务地址: http://localhost:3000")
    print("🔗 API代理: http://localhost:8000")
    print("-" * 50)
    
    # 切换到前端目录
    os.chdir(frontend_path)
    
    # 检查是否已安装依赖
    if not os.path.exists('node_modules'):
        print("📦 安装前端依赖...")
        subprocess.run(['npm', 'install'])
    
    # 启动开发服务器
    print("🚀 启动开发服务器...")
    subprocess.run(['npm', 'run', 'dev'])

if __name__ == "__main__":
    start_frontend()