"""
API路由定义
"""
from fastapi import APIRouter, HTTPException
from app.models.requests import CreateAvatarRequest, GenerateSituationRequest, EchoRequest, AutoDecisionRequest
from app.models.auth import LoginRequest, RegisterRequest, AuthResponse
from app.services.game_service import GameService

router = APIRouter()
game_service = GameService()

@router.get("/mbti-types")
async def get_mbti_types():
    return game_service.get_mbti_types()

@router.get("/fate-wheel")
async def get_fate_wheel():
    return game_service.get_fate_wheel()

@router.post("/create-avatar")
async def create_avatar(request: CreateAvatarRequest):
    try:
        print(f"Creating avatar: name={request.name}, mbti={request.mbti}, session_id={request.session_id}")
        result = await game_service.create_avatar(request.name, request.mbti, request.session_id)
        print(f"Avatar created successfully: {result}")
        return {"success": True, "avatar": result}
    except Exception as e:
        print(f"Error creating avatar: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate-situation")
async def generate_situation(request: GenerateSituationRequest):
    try:
        return await game_service.generate_situation(request.session_id, request.context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/echo")
async def send_echo(request: EchoRequest):
    try:
        return await game_service.send_echo(request.session_id, request.echo_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auto-decision")
async def auto_decision(request: AutoDecisionRequest):
    try:
        return await game_service.auto_decision(request.session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(request: LoginRequest):
    try:
        success = game_service.verify_account(request.username, request.password)
        if success:
            return AuthResponse(success=True, message="登录成功", username=request.username)
        else:
            return AuthResponse(success=False, message="用户名或密码错误")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register")
async def register(request: RegisterRequest):
    try:
        success = game_service.create_account(request.username, request.password)
        if success:
            return AuthResponse(success=True, message="注册成功", username=request.username)
        else:
            return AuthResponse(success=False, message="用户名已存在")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/investments/{username}")
async def get_investments(username: str):
    try:
        return game_service.get_user_investments(username)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions/{username}")
async def get_transactions(username: str, limit: int = 10):
    try:
        return game_service.get_user_transactions(username, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{username}")
async def get_user_info(username: str):
    try:
        user_info = game_service.get_user_info(username)
        if user_info:
            return user_info
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
    except Exception as e:
        print(f"Error getting user info: {e}")
        raise HTTPException(status_code=400, detail=str(e))