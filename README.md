# PetAgent Backend

## 启动
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 接口文档
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 当前阶段
第一阶段：FastAPI 骨架 + 内存假数据库
- ✅ 注册 / 登录接口通
- ⚠️ 数据存在内存，重启就丢
- ⏭️ 下一步：接 MySQL + 密码哈希