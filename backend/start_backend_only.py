"""
只启动后端服务器
"""
import sys
import os
import subprocess

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# 添加backend_new目录到Python路径
backend_path = os.path.dirname(__file__)
sys.path.insert(0, backend_path)

def main():
    print("🚀 启动Echopolis后端服务器...")
    print("🐍 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("-" * 50)
    
    # 检查依赖
    requirements_file = os.path.join(backend_path, 'requirements.txt')
    if os.path.exists(requirements_file):
        print("📦 检查依赖...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         check=True, capture_output=True)
            print("✅ 依赖检查完成")
        except subprocess.CalledProcessError:
            print("⚠️  依赖安装可能有问题，继续启动...")
    
    # 启动服务器
    try:
        from app.main import app
        import uvicorn
        print("🚀 启动服务器...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请检查依赖是否正确安装")

if __name__ == "__main__":
    main()