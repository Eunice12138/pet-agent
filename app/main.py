from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db.database import Base, engine, get_db
from app.db import models  # ⚠️ 注册模型
from app.db import crud
from app.core.security import create_access_token
from app.api.deps import get_current_user
from app.api.routes import chat as chat_router
from app.schemas import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    UserInfo,
)
from app.api.routes import agent as agent_router

# 建表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PetAgent API",
    description="智能宠物服务平台后端（第三阶段：JWT 鉴权）",
    version="0.4.0",
)
app.include_router(chat_router.router)
app.include_router(agent_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "PetAgent API is running 🐾", "version": "0.4.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- 注册 ----------
@app.post("/auth/register", response_model=RegisterResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if crud.get_user_by_account(db, req.account):
        raise HTTPException(status_code=400, detail="该账号已被注册")

    user = crud.create_user(
        db=db,
        nickname=req.nickname,
        account=req.account,
        password=req.password,
    )

    return RegisterResponse(
        success=True,
        message="注册成功",
        user_id=user.id,
    )


# ---------- 登录（返回真 JWT）----------
@app.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, req.account, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="账号或密码错误")

    # 生成真 JWT
    token = create_access_token(user_id=user.id)

    return LoginResponse(
        success=True,
        message="登录成功",
        token=token,
        nickname=user.nickname,
    )


# ---------- 当前用户（受保护）----------
@app.get("/auth/me", response_model=UserInfo)
def me(current_user: models.User = Depends(get_current_user)):
    return UserInfo(
        id=current_user.id,
        nickname=current_user.nickname,
        account=current_user.account,
        created_at=current_user.created_at,
    )