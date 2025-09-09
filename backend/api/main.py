"""
Echopolis API 主入口
FastAPI 应用程序
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.game_manager import GameManager
from backend.core.auth import AuthManager
from backend.api.models import *
from config import settings

# 创建FastAPI应用
app = FastAPI(
    title="Echopolis API",
    description="回声都市 - AI驱动的社会金融模拟器",
    version="1.0.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全认证
security = HTTPBearer()
auth_manager = AuthManager()
game_manager = GameManager()


# 依赖注入
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    token = credentials.credentials
    user = await auth_manager.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="无效的认证令牌")
    return user


# 根路径
@app.get("/")
async def root():
    return {
        "message": "欢迎来到 Echopolis (回声都市)",
        "version": "1.0.0",
        "status": "running"
    }


# 健康检查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": settings.APP_VERSION
    }


# 用户认证相关
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserRegistration):
    """用户注册"""
    try:
        user = await auth_manager.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        return UserResponse(**user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=LoginResponse)
async def login(login_data: UserLogin):
    """用户登录"""
    try:
        result = await auth_manager.login(
            username=login_data.username,
            password=login_data.password
        )
        return LoginResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=401, detail="用户名或密码错误")


# 人格评估相关
@app.post("/assessment/start", response_model=AssessmentResponse)
async def start_assessment(current_user: dict = Depends(get_current_user)):
    """开始人格评估"""
    try:
        assessment = await game_manager.start_personality_assessment(current_user["id"])
        return AssessmentResponse(**assessment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assessment/submit", response_model=AgentCreationResponse)
async def submit_assessment(
    assessment_data: AssessmentSubmission,
    current_user: dict = Depends(get_current_user)
):
    """提交评估结果并创建AI化身"""
    try:
        agent = await game_manager.create_agent_from_assessment(
            user_id=current_user["id"],
            answers=assessment_data.answers,
            fq_answers=assessment_data.fq_answers
        )
        return AgentCreationResponse(**agent)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# AI化身相关
@app.get("/agent/status", response_model=AgentStatusResponse)
async def get_agent_status(current_user: dict = Depends(get_current_user)):
    """获取AI化身状态"""
    try:
        status = await game_manager.get_agent_status(current_user["id"])
        return AgentStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=404, detail="AI化身不存在")


@app.post("/agent/intervention", response_model=InterventionResponse)
async def send_intervention(
    intervention_data: InterventionRequest,
    current_user: dict = Depends(get_current_user)
):
    """发送玩家干预（回响）"""
    try:
        result = await game_manager.process_player_intervention(
            user_id=current_user["id"],
            message=intervention_data.message,
            intervention_type=intervention_data.intervention_type
        )
        return InterventionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/decisions/history", response_model=List[DecisionRecord])
async def get_decision_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """获取决策历史"""
    try:
        history = await game_manager.get_decision_history(
            user_id=current_user["id"],
            limit=limit
        )
        return [DecisionRecord(**record) for record in history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 经济系统相关
@app.get("/economy/indicators", response_model=EconomicIndicatorsResponse)
async def get_economic_indicators():
    """获取宏观经济指标"""
    try:
        indicators = await game_manager.get_economic_indicators()
        return EconomicIndicatorsResponse(**indicators)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/economy/market", response_model=MarketDataResponse)
async def get_market_data():
    """获取市场数据"""
    try:
        market_data = await game_manager.get_market_data()
        return MarketDataResponse(**market_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/wallet/balance", response_model=WalletResponse)
async def get_wallet_balance(current_user: dict = Depends(get_current_user)):
    """获取钱包余额"""
    try:
        balance = await game_manager.get_wallet_balance(current_user["id"])
        return WalletResponse(**balance)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/wallet/transactions", response_model=List[TransactionRecord])
async def get_transaction_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """获取交易历史"""
    try:
        transactions = await game_manager.get_transaction_history(
            user_id=current_user["id"],
            limit=limit
        )
        return [TransactionRecord(**tx) for tx in transactions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 事件系统相关
@app.get("/events/current", response_model=List[EventResponse])
async def get_current_events():
    """获取当前事件"""
    try:
        events = await game_manager.get_current_events()
        return [EventResponse(**event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events/history", response_model=List[EventResponse])
async def get_event_history(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """获取事件历史"""
    try:
        events = await game_manager.get_event_history(
            user_id=current_user["id"],
            days=days
        )
        return [EventResponse(**event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 新闻系统相关
@app.get("/news/feed", response_model=List[NewsItem])
async def get_news_feed(
    limit: int = 20,
    category: Optional[str] = None
):
    """获取新闻流"""
    try:
        news = await game_manager.get_news_feed(limit=limit, category=category)
        return [NewsItem(**item) for item in news]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 社交系统相关
@app.get("/social/relationships", response_model=List[RelationshipInfo])
async def get_relationships(current_user: dict = Depends(get_current_user)):
    """获取社交关系"""
    try:
        relationships = await game_manager.get_agent_relationships(current_user["id"])
        return [RelationshipInfo(**rel) for rel in relationships]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 启示结晶商店相关
@app.get("/shop/catalog", response_model=List[ShopItem])
async def get_shop_catalog():
    """获取商店目录"""
    try:
        catalog = await game_manager.get_shop_catalog()
        return [ShopItem(**item) for item in catalog]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/shop/purchase", response_model=PurchaseResponse)
async def purchase_item(
    purchase_data: PurchaseRequest,
    current_user: dict = Depends(get_current_user)
):
    """购买商店物品"""
    try:
        result = await game_manager.purchase_shop_item(
            user_id=current_user["id"],
            item_id=purchase_data.item_id
        )
        return PurchaseResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 游戏管理相关
@app.post("/game/pause")
async def pause_game(current_user: dict = Depends(get_current_user)):
    """暂停游戏时间"""
    try:
        result = await game_manager.pause_game_time(current_user["id"])
        return {"success": True, "message": "游戏已暂停"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/game/resume")
async def resume_game(current_user: dict = Depends(get_current_user)):
    """恢复游戏时间"""
    try:
        result = await game_manager.resume_game_time(current_user["id"])
        return {"success": True, "message": "游戏已恢复"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/game/stats", response_model=GameStatsResponse)
async def get_game_stats(current_user: dict = Depends(get_current_user)):
    """获取游戏统计"""
    try:
        stats = await game_manager.get_game_statistics(current_user["id"])
        return GameStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 后台任务
@app.post("/admin/trigger-event")
async def trigger_event(
    event_data: EventTriggerRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """手动触发事件（管理员功能）"""
    # 这里应该添加管理员权限检查
    try:
        background_tasks.add_task(
            game_manager.trigger_specific_event,
            event_data.event_id,
            event_data.target_users
        )
        return {"success": True, "message": "事件触发任务已添加到队列"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket 支持（实时更新）
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # 连接已断开，移除
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )