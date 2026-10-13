from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """
    Agent 状态：所有节点共享的数据

    数据流转：
    用户问题 → state["query"]
    ↓
    意图识别 → state["intent"]
    ↓
    工具调用 → state["tool_calls"] / state["tool_results"]
    ↓
    生成回答 → state["final_answer"]
    """
    # 输入
    user_id: int                   # 用户 ID
    query: str                     # 用户当前问题

    # 中间状态
    intent: str                    # 识别出的意图
    tool_calls: List[Dict[str, Any]]   # 要调用的工具列表
    tool_results: List[Dict[str, Any]] # 工具返回的结果

    # 输出
    final_answer: str              # 最终回答
    sources: List[str]             # 引用来源

    # 控制
    iteration: int                 # 迭代次数（防止死循环）
    error: Optional[str]           # 错误信息