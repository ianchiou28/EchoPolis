"""
API路由定义
"""
from fastapi import APIRouter, HTTPException
from app.models.requests import CreateAvatarRequest, GenerateSituationRequest, EchoRequest, AutoDecisionRequest
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
        result = await game_service.create_avatar(request.name, request.mbti, request.session_id)
        return {"success": True, "avatar": result}
    except Exception as e:
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