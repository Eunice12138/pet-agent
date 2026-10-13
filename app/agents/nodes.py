"""
Agent 节点函数：每个节点是 LangGraph 图里的一个处理步骤
"""
import json
from typing import Dict, Any

from app.llm.client import get_llm
from app.agents.state import AgentState
from app.agents.tools.rag_tool import search_knowledge
from app.agents.tools.pet_tool import get_my_pets, get_pet_info
from app.agents.tools.appointment_tool import (
    get_my_appointments,
    get_upcoming_appointments,
)
from app.agents.tools.product_tool import search_products


# ========== 节点 1：意图识别 ==========
def intent_recognition_node(state: AgentState) -> Dict[str, Any]:
    """节点 1：识别意图，决定调哪些工具（用 f-string 拼 prompt，避免模板变量解析问题）"""
    llm = get_llm()
    query = state["query"]

    prompt = f"""你是一个意图识别助手。根据用户的问题，判断应该调用哪些工具。

可选的工具：
1. search_knowledge - 查询宠物护理知识（健康、症状、疫苗、养护）
2. get_my_pets - 查询用户的宠物列表
3. get_pet_info - 查询指定宠物的详细信息（需要 pet_name）
4. get_my_appointments - 查询用户所有预约
5. get_upcoming_appointments - 查询用户未来预约
6. search_products - 查询店铺商品
7. direct_answer - 无需工具，直接回答（闲聊、问候）

请只输出 JSON，不要输出其他内容，不要用 markdown 代码块：
{{"intent": "简要描述用户意图", "tools": [{{"name": "工具名", "args": {{"参数名": "参数值"}}}}]}}

用户问题：{query}
"""

    try:
        result = llm.invoke([("human", prompt)])
        text = result.content.strip()

        # 去掉可能的 markdown 代码块包裹
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(text)
        tools = parsed.get("tools", [])
        intent = parsed.get("intent", "unknown")

        # 兜底：如果 LLM 没给出工具，默认走 RAG
        if not tools:
            tools = [{"name": "search_knowledge", "args": {"query": query}}]

    except Exception as e:
        tools = [{"name": "search_knowledge", "args": {"query": query}}]
        intent = f"降级处理: {e}"

    return {
        "intent": intent,
        "tool_calls": tools,
        "iteration": state.get("iteration", 0) + 1,
    }


# ========== 节点 2：执行工具 ==========
TOOL_MAP = {
    "search_knowledge": search_knowledge,
    "get_my_pets": get_my_pets,
    "get_pet_info": get_pet_info,
    "get_my_appointments": get_my_appointments,
    "get_upcoming_appointments": get_upcoming_appointments,
    "search_products": search_products,
}


def execute_tools_node(state: AgentState) -> Dict[str, Any]:
    """节点 2：执行所有要调的工具"""
    user_id = state["user_id"]
    tool_calls = state.get("tool_calls", [])
    results = []

    for call in tool_calls:
        name = call.get("name")
        args = call.get("args", {}) or {}

        if name not in TOOL_MAP:
            results.append({"tool": name, "result": f"未知工具: {name}"})
            continue

        tool_func = TOOL_MAP[name]

        # 自动注入 user_id（不让 LLM 编）
        if name in [
            "get_my_pets",
            "get_pet_info",
            "get_my_appointments",
            "get_upcoming_appointments",
        ]:
            args["user_id"] = user_id

        try:
            output = tool_func.invoke(args)
            results.append({"tool": name, "result": output})
        except Exception as e:
            results.append({"tool": name, "result": f"工具执行失败: {e}"})

    return {"tool_results": results}


# ========== 节点 3：生成回答 ==========
def generate_answer_node(state: AgentState) -> Dict[str, Any]:
    """节点 3：综合工具结果，生成最终回答"""
    llm = get_llm()

    results_text = ""
    sources = []
    for r in state.get("tool_results", []):
        results_text += f"\n【{r['tool']}】\n{r['result']}\n"
        if "【来源】" in r["result"]:
            src = r["result"].split("【来源】")[-1].strip()
            for s in src.split(","):
                s = s.strip()
                if s and s not in sources:
                    sources.append(s)

    prompt = f"""你是 PetAgent，一个专业的宠物护理顾问。请根据工具返回的信息回答用户问题。

【用户问题】
{state["query"]}

【工具返回的信息】
{results_text or "（无工具调用）"}

【回答要求】
1. 用温暖、专业的语气
2. 优先使用工具返回的信息，不要编造
3. 如果工具没有返回有用信息，坦诚说明
4. 回答简洁，控制在 300 字以内
5. 如果涉及医疗诊断，提醒用户咨询兽医
"""

    result = llm.invoke([("human", prompt)])

    return {
        "final_answer": result.content,
        "sources": sources,
    }


# ========== 条件路由 ==========
def should_execute_tools(state: AgentState) -> str:
    """判断是否需要执行工具"""
    tools = state.get("tool_calls", [])
    if not tools:
        return "generate"

    non_direct = [t for t in tools if t.get("name") != "direct_answer"]
    if not non_direct:
        return "generate"

    return "execute"