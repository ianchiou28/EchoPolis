"""
只启动前端开发服务器
"""
import sys
import os
import subprocess

def main():
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend_vue')
    
    print("🌐 启动Echopolis前端开发服务器...")
    print(f"📁 前端路径: {frontend_path}")
    print("🚀 服务地址: http://localhost:3000")
    print("🔗 API代理: http://localhost:8000")
    print("-" * 50)
    
    # 检查目录是否存在
    if not os.path.exists(frontend_path):
        print("❌ 前端目录不存在")
        return
    
    # 切换到前端目录
    os.chdir(frontend_path)
    
    # 检查package.json
    if not os.path.exists('package.json'):
        print("❌ 未找到package.json文件")
        return
    
    # 检查Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
        print(f"✅ Node.js版本: {result.stdout.strip()}")
    except:
        print("❌ 未找到Node.js")
        return
    
    # 安装依赖
    if not os.path.exists('node_modules'):
        print("📦 安装依赖...")
        try:
            subprocess.run(['npm', 'install'], check=True, shell=True)
            print("✅ 依赖安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return
    
    # 启动开发服务器
    print("🚀 启动开发服务器...")
    try:
        subprocess.run(['npm', 'run', 'dev'], shell=True)
    except KeyboardInterrupt:
        print("\n👋 前端服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()