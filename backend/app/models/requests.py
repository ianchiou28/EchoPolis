"""
API请求模型定义
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
class CreateAvatarRequest(BaseModel):
    name: str
    mbti: str
    session_id: str

class GenerateSituationRequest(BaseModel):
    session_id: str
    context: Optional[Any] = None

class EchoRequest(BaseModel):
    session_id: str
    echo_text: str

class AutoDecisionRequest(BaseModel):
    session_id: str

class SessionStartRequest(BaseModel):
    session_id: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None
    mbti: Optional[str] = None
class SessionAdvanceRequest(BaseModel):
    session_id: str
    echo_text: Optional[str] = None

class SessionFinishRequest(BaseModel):
    session_id: str

class AIChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
