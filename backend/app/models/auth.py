"""
认证相关的数据模型
"""
from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    username: str = None

# ============ 管理员模型 ============

class AdminLoginRequest(BaseModel):
    admin_key: str

class AdminAuthResponse(BaseModel):
    success: bool
    message: str
    is_admin: bool = False

class UpdateCreditsRequest(BaseModel):
    session_id: str
    credits: int

class UpdateStatusRequest(BaseModel):
    session_id: str
    happiness: Optional[int] = None
    energy: Optional[int] = None
    health: Optional[int] = None

class DeleteAccountRequest(BaseModel):
    username: str

class DeleteUserRequest(BaseModel):
    session_id: str