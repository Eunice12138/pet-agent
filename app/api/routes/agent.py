from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas import AgentChatRequest, AgentChatResponse
from app.agents.graph import agent_graph
from app.memory.redis_memory import memory
from app.api.deps import get_current_user
from app.db.models import User
from app.db.database import get_db
from app.db import crud

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(
    req: AgentChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Agent 对话接口：意图识别 → 调工具 → 生成回答"""
    try:
        # 1. 取历史对话（让 Agent 有上下文）
        history = memory.get_history(current_user.id)

        # 2. 构造 query（含历史）
        query = req.message
        if history:
            recent = history[-4:]
            history_text = " | ".join(
                f"{m['role']}: {m['content']}" for m in recent
            )
            query = f"【历史对话】{history_text}\n【当前问题】{req.message}"

        # 3. 运行 Agent 图
        initial_state = {
            "user_id": current_user.id,
            "query": query,
            "intent": "",
            "tool_calls": [],
            "tool_results": [],
            "final_answer": "",
            "sources": [],
            "iteration": 0,
            "error": None,
        }

        result = await agent_graph.ainvoke(initial_state)

        reply = result.get("final_answer", "抱歉，我没能理解您的问题。")
        intent = result.get("intent", "")
        sources = result.get("sources", [])


        # 5. 存 Redis（短期）
        memory.append(current_user.id, "human", req.message)
        memory.append(current_user.id, "ai", reply)

        # 6. 存 MySQL（长期）
        conversation = crud.get_or_create_conversation(db, current_user.id)
        crud.add_message(db, conversation.id, "human", req.message)
        crud.add_message(db, conversation.id, "ai", reply)

        return AgentChatResponse(
            success=True,
            reply=reply,
            intent=intent,
            sources=sources,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 调用失败: {str(e)}")


@router.post("/clear")
async def clear_history(current_user: User = Depends(get_current_user)):
    """清空当前用户的 Redis 对话历史"""
    memory.clear(current_user.id)
    return {"success": True, "message": "Redis 对话历史已清空"}