"""
认证管理器
"""
from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    def __init__(self):
        self.secret_key = "your-secret-key"
        self.algorithm = "HS256"
        self.users_db = {}  # 简化版用户存储
    
    async def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """用户注册"""
        if username in self.users_db:
            raise ValueError("用户名已存在")
        
        hashed_password = pwd_context.hash(password)
        user = {
            "id": f"user_{len(self.users_db) + 1}",
            "username": username,
            "email": email,
            "password_hash": hashed_password,
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        self.users_db[username] = user
        return {k: v for k, v in user.items() if k != "password_hash"}
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        user = self.users_db.get(username)
        if not user or not pwd_context.verify(password, user["password_hash"]):
            raise ValueError("用户名或密码错误")
        
        token = self._create_access_token({"sub": user["id"], "username": username})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {k: v for k, v in user.items() if k != "password_hash"}
        }
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username = payload.get("username")
            if username and username in self.users_db:
                user = self.users_db[username]
                return {k: v for k, v in user.items() if k != "password_hash"}
        except jwt.PyJWTError:
            pass
        return None
    
    def _create_access_token(self, data: Dict[str, Any]) -> str:
        """创建访问token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)