"""
简单启动脚本 - 使用原有的web_minimal.py
"""
import sys
import os
import subprocess

def main():
    print("🚀 启动Echopolis简单版本...")
    print("🐍 后端: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("-" * 50)
    
    # 检查依赖
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI依赖已安装")
    except ImportError:
        print("📦 安装后端依赖...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'fastapi', 'uvicorn'])
    
    # 启动简单版本
    print("🚀 启动服务器...")
    
    # 检查是否存在web_minimal.py
    if os.path.exists('web_minimal.py'):
        subprocess.run([sys.executable, 'web_minimal.py'])
    else:
        print("❌ 未找到web_minimal.py文件")
        print("   请确保在正确的目录中运行此脚本")

if __name__ == "__main__":
    main()