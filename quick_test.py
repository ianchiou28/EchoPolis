#!/usr/bin/env python3
import sys
import os
import subprocess
import time
import requests

project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_api():
    """测试API端点"""
    base_url = "http://localhost:8000/api/unity"
    
    tests = [
        ("Health Check", f"{base_url}/health"),
        ("Login", f"{base_url}/auth/login", {"username": "test", "password": "123"}),
        ("Game State", f"{base_url}/game/state/test_user"),
        ("Situation", f"{base_url}/game/situation/test_user")
    ]
    
    for name, url, *data in tests:
        try:
            if data:
                response = requests.post(url, json=data[0], timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✓ {name}: OK")
            else:
                print(f"✗ {name}: {response.status_code}")
        except Exception as e:
            print(f"✗ {name}: {e}")

def start_server():
    """启动服务器"""
    try:
        import uvicorn
        from backend.app.main import app
        
        print("Starting EchoPolis Backend...")
        print("Unity API: http://localhost:8000/api/unity/health")
        print("Press Ctrl+C to stop")
        
        # 先测试一下API
        print("\nTesting APIs in 3 seconds...")
        import threading
        def delayed_test():
            time.sleep(3)
            test_api()
        
        threading.Thread(target=delayed_test, daemon=True).start()
        
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
        
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == "__main__":
    start_server()