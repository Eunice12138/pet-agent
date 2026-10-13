from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas import ChatRequest, ChatResponse
from app.memory.redis_memory import memory
from app.rag.retriever import rag_chat
from app.api.deps import get_current_user
from app.db.models import User
from app.db.database import get_db
from app.db import crud

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """带记忆 + RAG 的对话接口"""
    try:
        # 1. 取 Redis 历史
        history = memory.get_history(current_user.id)

        # 2. 如果历史存在，把历史拼进 query（让 LLM 有上下文）
        context_query = req.message
        if history:
            recent = history[-4:]   # 最近 2 轮
            history_text = " | ".join(
                f"{m['role']}: {m['content']}" for m in recent
            )
            context_query = f"【历史对话】{history_text}\n【当前问题】{req.message}"

        # 3. RAG 生成（检索 + 生成）
        reply, sources = await rag_chat(context_query)


        # 5. 存 Redis（短期）
        memory.append(current_user.id, "human", req.message)
        memory.append(current_user.id, "ai", reply)

        # 6. 存 MySQL（长期）
        conversation = crud.get_or_create_conversation(db, current_user.id)
        crud.add_message(db, conversation.id, "human", req.message)
        crud.add_message(db, conversation.id, "ai", reply)

        return ChatResponse(success=True, reply=reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG 调用失败: {str(e)}")


@router.post("/clear")
async def clear_history(current_user: User = Depends(get_current_user)):
    """清空当前用户的 Redis 对话历史"""
    memory.clear(current_user.id)
    return {"success": True, "message": "Redis 对话历史已清空（MySQL 保留）"}