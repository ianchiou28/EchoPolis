"""
Unity客户端专用API路由
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import json
import asyncio
from typing import Dict, List
import time

from app.models.unity_models import *
from app.services.game_service import GameService

router = APIRouter(prefix="/unity", tags=["Unity"])

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message(self, user_id: str, message: WebSocketMessage):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message.json())
            except:
                self.disconnect(user_id)

manager = ConnectionManager()
game_service = GameService()

@router.post("/auth/login", response_model=UnityResponse)
async def login(request: LoginRequest):
    """用户登录"""
    try:
        # 这里应该验证用户凭据
        user_data = {
            "user_id": request.username,
            "token": f"token_{request.username}_{int(time.time())}"
        }
        
        return UnityResponse(
            status=ResponseStatus.SUCCESS,
            message="登录成功",
            data=user_data
        )
    except Exception as e:
        return UnityResponse(
            status=ResponseStatus.ERROR,
            message=f"登录失败: {str(e)}",
            error_code="LOGIN_FAILED"
        )

@router.post("/avatar/create", response_model=UnityResponse)
async def create_avatar(request: CreateAvatarRequest):
    """创建AI化身"""
    try:
        # 创建新的AI化身
        avatar_data = AvatarData(
            name=request.name,
            mbti_type=request.mbti_type,
            trust_level=50,
            current_emotion=EmotionType.NEUTRAL,
            health=100,
            energy=100,
            stress=0
        )
        
        return UnityResponse(
            status=ResponseStatus.SUCCESS,
            message="AI化身创建成功",
            data=avatar_data.dict()
        )
    except Exception as e:
        return UnityResponse(
            status=ResponseStatus.ERROR,
            message=f"创建化身失败: {str(e)}",
            error_code="CREATE_AVATAR_FAILED"
        )

@router.get("/game/state/{user_id}", response_model=UnityResponse)
async def get_game_state(user_id: str):
    """获取游戏状态"""
    try:
        # 模拟游戏状态数据
        game_state = GameState(
            user_id=user_id,
            avatar=AvatarData(
                name="Alex",
                mbti_type=MBTIType.INTP,
                trust_level=65,
                current_emotion=EmotionType.CONFIDENT,
                health=85,
                energy=70,
                stress=30
            ),
            finances=FinancialData(
                cash=25000.0,
                total_assets=45000.0,
                monthly_income=8000.0,
                monthly_expenses=3500.0,
                investment_value=20000.0,
                debt=0.0
            ),
            game_month=3,
            is_game_over=False
        )
        
        return UnityResponse(
            status=ResponseStatus.SUCCESS,
            message="获取游戏状态成功",
            data=game_state.dict()
        )
    except Exception as e:
        return UnityResponse(
            status=ResponseStatus.ERROR,
            message=f"获取游戏状态失败: {str(e)}",
            error_code="GET_STATE_FAILED"
        )

@router.get("/game/situation/{user_id}", response_model=UnityResponse)
async def get_current_situation(user_id: str):
    """获取当前情况"""
    try:
        # 模拟AI生成的情况
        situation = SituationData(
            id=f"situation_{int(time.time())}",
            title="投资机会出现",
            description="作为INTP型的Alex，你收到了一个量化投资课程的邀请...",
            context="当前现金充足，但需要考虑长期发展",
            options=[
                DecisionOption(
                    id=1,
                    title="投资教育",
                    description="支付12,000元参加量化投资课程",
                    consequence="提升投资能力，但短期现金减少",
                    risk_level=RiskLevel.LOW,
                    financial_impact=-12000.0
                ),
                DecisionOption(
                    id=2,
                    title="保守储蓄",
                    description="将资金存入银行获得稳定收益",
                    consequence="安全但收益有限",
                    risk_level=RiskLevel.LOW,
                    financial_impact=0.0
                ),
                DecisionOption(
                    id=3,
                    title="高风险投资",
                    description="投资新兴科技股票",
                    consequence="可能获得高收益，但风险很大",
                    risk_level=RiskLevel.HIGH,
                    financial_impact=0.0
                )
            ]
        )
        
        return UnityResponse(
            status=ResponseStatus.SUCCESS,
            message="获取情况成功",
            data=situation.dict()
        )
    except Exception as e:
        return UnityResponse(
            status=ResponseStatus.ERROR,
            message=f"获取情况失败: {str(e)}",
            error_code="GET_SITUATION_FAILED"
        )

@router.post("/game/decision", response_model=UnityResponse)
async def submit_decision(request: DecisionRequest):
    """提交决策"""
    try:
        # 处理决策逻辑
        result = DecisionResult(
            success=True,
            result_description=f"你选择了选项{request.option_id}，AI正在分析结果...",
            financial_change={"cash": -12000.0 if request.option_id == 1 else 0.0},
            avatar_change={"trust_level": 2, "current_emotion": "confident"},
            trust_change=2
        )
        
        return UnityResponse(
            status=ResponseStatus.SUCCESS,
            message="决策提交成功",
            data=result.dict()
        )
    except Exception as e:
        return UnityResponse(
            status=ResponseStatus.ERROR,
            message=f"决策提交失败: {str(e)}",
            error_code="SUBMIT_DECISION_FAILED"
        )

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket实时通信"""
    await manager.connect(websocket, user_id)
    try:
        # 发送连接成功消息
        welcome_msg = WebSocketMessage(
            type="connection",
            data={"message": "WebSocket连接成功", "user_id": user_id},
            timestamp=time.time()
        )
        await manager.send_message(user_id, welcome_msg)
        
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的消息
            if message.get("type") == "ping":
                pong_msg = WebSocketMessage(
                    type="pong",
                    data={"timestamp": time.time()},
                    timestamp=time.time()
                )
                await manager.send_message(user_id, pong_msg)
            
            elif message.get("type") == "request_situation":
                # 模拟AI生成新情况
                await asyncio.sleep(1)  # 模拟AI思考时间
                situation_msg = WebSocketMessage(
                    type="new_situation",
                    data={
                        "situation": {
                            "title": "新的挑战出现",
                            "description": "AI正在为你生成新的决策情况..."
                        }
                    },
                    timestamp=time.time()
                )
                await manager.send_message(user_id, situation_msg)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        manager.disconnect(user_id)

@router.get("/health")
async def health_check():
    """健康检查"""
    return UnityResponse(
        status=ResponseStatus.SUCCESS,
        message="API服务正常运行",
        data={"timestamp": time.time(), "active_connections": len(manager.active_connections)}
    )