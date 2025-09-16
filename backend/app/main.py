"""
Echopolis FastAPI 后端主入口
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

# 添加backend_new目录到Python路径
backend_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, backend_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import router
from app.services.game_service import GameService

app = FastAPI(title="Echopolis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化游戏服务
game_service = GameService()

# 注册路由
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Echopolis API Server", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)