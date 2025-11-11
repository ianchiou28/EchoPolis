"""
API请求模型定义
"""
from pydantic import BaseModel
from typing import Optional

class CreateAvatarRequest(BaseModel):
    name: str
    mbti: str
    session_id: str
    username: Optional[str] = None  # 新增：账号用户名（可选）

class GenerateSituationRequest(BaseModel):
    session_id: str
    context: str = ""

class EchoRequest(BaseModel):
    session_id: str
    echo_text: str

class AutoDecisionRequest(BaseModel):
    session_id: str

class StartSessionRequest(BaseModel):
    avatar_id: str
    session_id: str
