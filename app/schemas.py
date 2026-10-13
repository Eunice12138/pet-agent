"""请求响应模型"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ---------- 注册 ----------
class RegisterRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=30)
    account: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=64)


class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None


# ---------- 登录 ----------
class LoginRequest(BaseModel):
    account: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    nickname: Optional[str] = None


# ---------- 当前用户（新增字段）----------
class UserInfo(BaseModel):
    id: int
    nickname: str
    account: str
    created_at: datetime

# ---------- 对话 ----------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    success: bool
    reply: str


# ---------- Agent 对话 ----------
class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class AgentChatResponse(BaseModel):
    success: bool
    reply: str
    intent: str = ""
    sources: list = []