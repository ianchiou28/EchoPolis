"""
API请求模型定义
"""
from pydantic import BaseModel

class CreateAvatarRequest(BaseModel):
    name: str
    mbti: str
    session_id: str

class GenerateSituationRequest(BaseModel):
    session_id: str
    context: str = ""

class EchoRequest(BaseModel):
    session_id: str
    echo_text: str

class AutoDecisionRequest(BaseModel):
    session_id: str